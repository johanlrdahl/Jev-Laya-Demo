import json
import re
import time

import httpx

from .questions import QUESTIONS
from .results import Answer, Lane, TicketResult
from .tickets import Ticket

OLLAMA_URL = "http://localhost:11434/api/generate"
KEEP_ALIVE = "30m"


def describe(qid: str, q: dict) -> str:
    if q["type"] == "choice":
        options = "\n".join(f"  - {k}: {v}" for k, v in q["criteria"].items())
        return f'"{qid}": {q["instructions"]} Options:\n{options}\n  Answer with one option key as a string.'
    if q["type"] == "score":
        levels = "\n".join(f"  {i}: {v}" for i, v in enumerate(q["criteria"]))
        return f'"{qid}": {q["instructions"]} Levels:\n{levels}\n  Answer with the level number.'
    return f'"{qid}": True or false? {q["instructions"]}\n  Answer with true or false.'


def build_prompt(ticket: Ticket, qids: list[str], reason: bool) -> str:
    questions = "\n".join(describe(q, QUESTIONS[q]) for q in qids)
    example = ", ".join(f'"{q}": ...' for q in qids)
    if reason:
        finish = (
            "First write one short sentence explaining your reasoning. "
            f"Then, on the last line, write only the JSON object {{{example}}}."
        )
    else:
        finish = f"Respond with only the JSON object {{{example}}} and nothing else."
    return (
        "You are a customer-support triage system.\n\n"
        f"Ticket:\n\"\"\"\n{ticket.text}\n\"\"\"\n\n"
        f"Questions:\n{questions}\n\n{finish}"
    )


def validate(q: dict, value) -> Answer:
    if q["type"] == "choice":
        if isinstance(value, str) and value.strip().lower() in q["criteria"]:
            return Answer(value.strip().lower(), True)
        return Answer(error=f"not an option: {value!r}")
    if q["type"] == "score":
        if isinstance(value, str) and value.strip().isdigit():
            value = int(value.strip())
        if isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value < len(q["criteria"]):
            return Answer(round(value), True)
        return Answer(error=f"not a level: {value!r}")
    if isinstance(value, str) and value.strip().lower() in ("true", "false", "yes", "no"):
        value = value.strip().lower() in ("true", "yes")
    if isinstance(value, bool):
        return Answer(value, True)
    return Answer(error=f"not true/false: {value!r}")


def parse(text: str, qids: list[str]) -> dict[str, Answer]:
    data = None
    for candidate in reversed(re.findall(r"\{[^{}]*\}", text)):
        try:
            data = json.loads(candidate)
            break
        except json.JSONDecodeError:
            continue
    if not isinstance(data, dict):
        return {q: Answer(error="no valid JSON") for q in qids}
    return {
        q: validate(QUESTIONS[q], data[q]) if q in data else Answer(error="missing key")
        for q in qids
    }


def generate(client: httpx.Client, model: str, prompt: str, temperature: float, lane: Lane | None):
    """Stream one completion. Returns (text, prompt_tokens, output_tokens)."""
    text, final = "", {}
    body = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "keep_alive": KEEP_ALIVE,
        "options": {"temperature": temperature, "num_predict": 256},
    }
    with client.stream("POST", OLLAMA_URL, json=body, timeout=300) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line:
                continue
            chunk = json.loads(line)
            text += chunk.get("response", "")
            if lane is not None:
                lane.stream = text
                lane.output_tokens += 1 if chunk.get("response") else 0
            if chunk.get("done"):
                final = chunk
    return text, final.get("prompt_eval_count", 0), final.get("eval_count", 0)


def warm_up(model: str) -> None:
    with httpx.Client() as client:
        generate(client, model, "Reply with OK.", 0.0, None)


def decide(client, model: str, ticket: Ticket, single_call: bool, reason: bool,
           temperature: float, lane: Lane | None) -> TicketResult:
    groups = [list(QUESTIONS)] if single_call else [[q] for q in QUESTIONS]
    answers, tin, tout = {}, 0, 0
    start = time.perf_counter()
    for qids in groups:
        if lane is not None:
            lane.current = f"{ticket.id} - {', '.join(qids)}"
        text, i, o = generate(client, model, build_prompt(ticket, qids, reason), temperature, lane)
        answers.update(parse(text, qids))
        tin, tout = tin + i, tout + o
    return TicketResult(ticket, answers, time.perf_counter() - start, tin, tout)


def run(model: str, tickets: list[Ticket], lane: Lane, single_call: bool, reason: bool,
        temperature: float) -> None:
    lane.status = "generating"
    lane.started = time.perf_counter()
    with httpx.Client() as client:
        for t in tickets:
            result = decide(client, model, t, single_call, reason, temperature, lane)
            lane.results.append(result)
            lane.done += 1
    lane.finished = time.perf_counter()
    lane.status = "done"
    lane.current = ""
