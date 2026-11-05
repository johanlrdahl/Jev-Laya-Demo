import os
import time
import warnings
from pathlib import Path

from .questions import QUESTIONS
from .results import Answer, Lane, TicketResult
from .tickets import TICKETS, Ticket

HF_CACHE = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface")) / "hub"


def load_router():
    # Once downloaded, never touch the network: the demo must work on conference wifi.
    if (HF_CACHE / "models--convaiinnovations--laya").exists():
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
    warnings.filterwarnings("ignore", module="laya")
    from laya import Router

    router = Router(device="mps")
    router.preload(["english", "multilingual"])
    # The first forward pass on MPS compiles kernels; pay that before the race.
    for text in (TICKETS[0].text, TICKETS[7].text):
        router.predict(text, QUESTIONS)
    return router


def parse(raw: dict) -> dict[str, Answer]:
    out = {}
    for qid, a in raw["answers"].items():
        if a["type"] == "choice":
            out[qid] = Answer(a["choice"], True, a["probabilities"])
        elif a["type"] == "score":
            out[qid] = Answer(round(a["score"]), True, a["probabilities"])
        else:
            out[qid] = Answer(a["noul"] >= 0.5, True, {"yes": a["noul"]})
    return out


def run(router, tickets: list[Ticket], lane: Lane) -> None:
    lane.status = "deciding"
    lane.started = time.perf_counter()
    raws = router.predict_batch([{"state": t.text, "questions": QUESTIONS} for t in tickets])
    elapsed = time.perf_counter() - lane.started
    for t, raw in zip(tickets, raws):
        lane.results.append(
            TicketResult(t, parse(raw), elapsed / len(tickets), raw["usage"]["input_tokens"], 0)
        )
    lane.done = len(tickets)
    lane.finished = time.perf_counter()
    lane.status = "done"
