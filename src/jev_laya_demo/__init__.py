import argparse
import sys
import threading

import httpx
from rich.console import Console

from . import laya_runner, llm_runner, race, report
from .results import Lane
from .tickets import TICKETS


def parse_args():
    p = argparse.ArgumentParser(prog="jev-laya-demo", description="Laya vs. lokale LLM-er: kundeservice-race")
    p.add_argument("--tickets", type=int, default=12, help="antall saker i racet (maks 20, standard 12)")
    p.add_argument("--models", default="mistral:latest,gemma:2b", help="kommaseparerte Ollama-modeller")
    p.add_argument("--single-call", action="store_true",
                   help="la LLM-ene svare på alle tre spørsmål i ett kall (standard: ett kall per spørsmål)")
    p.add_argument("--no-reason", action="store_true",
                   help="la LLM-ene svare kun med JSON (standard: én setning begrunnelse først)")
    p.add_argument("--repeats", type=int, default=3,
                   help="antall omkjøringer av de vriene sakene for konsistenssjekk (0 for å hoppe over)")
    p.add_argument("--temperature", type=float, default=0.7, help="temperatur for LLM-ene")
    p.add_argument("--quality-only", action="store_true", help="hopp over selve live-racet")
    p.add_argument("--no-pause", action="store_true", help="vis alle tabeller uten å vente på Enter")
    return p.parse_args()


CHATBOTS = {
    "mistral:latest": ("Mistral 7B", "System 2 LLM — skriver begrunnelse + JSON"),
    "gemma:2b": ("Gemma 2B", "mindre System 2 LLM — raskere, men slurvete"),
}


def chatbot_name(model: str) -> str:
    return CHATBOTS.get(model, (model, ""))[0]


def chatbot_lane(model: str, n: int) -> Lane:
    name, role = CHATBOTS.get(model, (model, "System 2 LLM — skriver svaret"))
    return Lane(name, n, role=role)


def run_lanes(lanes_and_jobs, live: bool):
    if live:
        race.race(lanes_and_jobs)
        return
    threads = [threading.Thread(target=fn) for _, fn in lanes_and_jobs]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def pause(console: Console, enabled: bool, prompt: str) -> None:
    if enabled and sys.stdin.isatty():
        console.print()
        try:
            console.input(f"[dim]{prompt}[/]")
        except EOFError:
            pass


def main() -> None:
    args = parse_args()
    console = Console()
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    tickets = TICKETS[: args.tickets]
    tricky = [t for t in TICKETS if t.tricky]
    llm_opts = dict(single_call=args.single_call, reason=not args.no_reason,
                    temperature=args.temperature)
    interactive = not args.quality_only and not args.no_pause

    with console.status("Laster inn Laya og varmer opp alle modeller (teller ikke med i racet)..."):
        router = laya_runner.load_router()
        for m in models:
            llm_runner.warm_up(m)

    report.briefing(console, len(tickets), [chatbot_name(m) for m in models],
                    args.single_call, not args.no_reason)
    pause(console, interactive, "Trykk Enter for å starte racet...")

    laya_lane = Lane("Laya (395M)", len(tickets), role="System 1 beslutningsmodell — skriver 0 ord", is_laya=True)
    lanes = [laya_lane] + [chatbot_lane(m, len(tickets)) for m in models]
    jobs = [(laya_lane, lambda: laya_runner.run(router, tickets, laya_lane))]
    for m, lane in zip(models, lanes[1:]):
        jobs.append((lane, lambda m=m, lane=lane: llm_runner.run(m, tickets, lane, **llm_opts)))
    run_lanes(jobs, live=not args.quality_only)

    pause(console, interactive, "Trykk Enter for å se hastighet og kvalitet...")
    console.rule("[bold]Resultater fra racet")
    report.summary(console, lanes)
    report.failures(console, lanes[1:])

    laya_repeats = []
    for _ in range(max(args.repeats, 1)):
        lane = Lane("", len(tricky), is_laya=True)
        laya_runner.run(router, tricky, lane)
        laya_repeats.append(lane.results)

    pause(console, interactive, "Trykk Enter for å se sannsynligheter på de vriene sakene...")
    console.print()
    report.probabilities(console, laya_repeats[0])

    if args.repeats > 1:
        pause(console, interactive, f"Trykk Enter for å teste konsistens ({args.repeats} kjøringer av samme saker)...")
        console.print()
        runs = {laya_lane.name: laya_repeats}
        with console.status(f"Kjører de {len(tricky)} vriene sakene {args.repeats} ganger for å sjekke om svarene vipper..."):
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

    pause(console, interactive, "Trykk Enter for å se hva 1 million saker per dag ville kostet...")
    console.print()
    report.cost(console, lanes)
