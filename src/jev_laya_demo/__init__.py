import argparse
import threading

import httpx
from rich.console import Console

from . import laya_runner, llm_runner, race, report
from .results import Lane
from .tickets import TICKETS


def parse_args():
    p = argparse.ArgumentParser(prog="jev-laya-demo", description="Laya vs local LLMs: ticket triage race")
    p.add_argument("--tickets", type=int, default=20, help="number of tickets in the race (max 20)")
    p.add_argument("--models", default="mistral:latest,gemma:2b", help="comma-separated Ollama models")
    p.add_argument("--single-call", action="store_true",
                   help="ask the LLMs all three questions in one call (default: one call per question)")
    p.add_argument("--no-reason", action="store_true",
                   help="let the LLMs answer with JSON only (default: one sentence of reasoning first)")
    p.add_argument("--repeats", type=int, default=3,
                   help="reruns of the tricky tickets for the consistency check (0 to skip)")
    p.add_argument("--temperature", type=float, default=0.7, help="LLM sampling temperature")
    p.add_argument("--quality-only", action="store_true", help="skip the live race view")
    return p.parse_args()


def run_lanes(lanes_and_jobs, live: bool):
    if live:
        race.race(lanes_and_jobs)
        return
    threads = [threading.Thread(target=fn) for _, fn in lanes_and_jobs]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def main() -> None:
    args = parse_args()
    console = Console()
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    tickets = TICKETS[: args.tickets]
    tricky = [t for t in TICKETS if t.tricky]
    llm_opts = dict(single_call=args.single_call, reason=not args.no_reason,
                    temperature=args.temperature)

    with console.status("Loading Laya and warming up every model (not part of the race)..."):
        router = laya_runner.load_router()
        for m in models:
            llm_runner.warm_up(m)

    console.print(f"[bold]{len(tickets)} tickets x 3 questions.[/] "
                  f"LLMs: {'one call per ticket' if args.single_call else 'one call per question'}, "
                  f"{'JSON only' if args.no_reason else 'reason, then JSON'}, "
                  f"temperature {args.temperature}. Laya: one batched forward pass.")
    if not args.quality_only:
        console.input("[dim]Press Enter to start the race...[/]")

    laya_lane = Lane("Laya (395M encoder)", len(tickets), is_laya=True)
    lanes = [laya_lane] + [Lane(m, len(tickets)) for m in models]
    jobs = [(laya_lane, lambda: laya_runner.run(router, tickets, laya_lane))]
    for m, lane in zip(models, lanes[1:]):
        jobs.append((lane, lambda m=m, lane=lane: llm_runner.run(m, tickets, lane, **llm_opts)))
    run_lanes(jobs, live=not args.quality_only)

    console.rule("[bold]Quality")
    report.summary(console, lanes)
    report.failures(console, lanes[1:])
    laya_repeats = []
    for _ in range(max(args.repeats, 1)):
        lane = Lane("", len(tricky), is_laya=True)
        laya_runner.run(router, tricky, lane)
        laya_repeats.append(lane.results)
    console.print()
    report.probabilities(console, laya_repeats[0])

    if args.repeats > 1:
        console.print()
        runs = {laya_lane.name: laya_repeats}
        with console.status(f"Re-asking {len(tricky)} tricky tickets {args.repeats} times..."):
            def repeat(model, name):
                runs[name] = []
                with httpx.Client() as client:
                    for _ in range(args.repeats):
                        runs[name].append([
                            llm_runner.decide(client, model, t, args.single_call, not args.no_reason,
                                              args.temperature, None) for t in tricky])

            threads = [threading.Thread(target=repeat, args=(m, l.name)) for m, l in zip(models, lanes[1:])]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
        report.consistency(console, runs)

    console.print()
    report.cost(console, lanes)
