from rich.console import Console
from rich.table import Table

from .questions import QUESTIONS
from .results import Lane, TicketResult

# USD per million tokens, list prices checked 15 Oct 2026.
GPT5_MINI_IN, GPT5_MINI_OUT = 0.25, 2.00  # developers.openai.com/api/docs/pricing
JEV_IN = 0.042  # docs.typesafe.ai/models, output tokens free

PURPLE = "#8B1D82"


def pct(n: int, d: int) -> str:
    return f"{100 * n / d:.0f}%" if d else "-"


def summary(console: Console, lanes: list[Lane]) -> None:
    t = Table(title="Results", title_style=f"bold {PURPLE}", header_style="bold")
    t.add_column("model")
    for col in ("time", "/ticket", "out tok", "valid",
                "dept", "urgency±1", "refund", "overall", "probs"):
        t.add_column(col, justify="right")
    for lane in lanes:
        rs = lane.results
        answers = [a for r in rs for a in r.answers.values()]
        secs = (lane.finished or 0) - (lane.started or 0)
        acc = {q: pct(sum(r.correct(q) for r in rs), len(rs)) for q in QUESTIONS}
        overall = pct(sum(r.correct(q) for r in rs for q in QUESTIONS), len(answers))
        t.add_row(
            lane.name,
            f"{secs:,.2f} s",
            f"{secs / len(rs) * 1000:,.0f} ms",
            f"{sum(r.output_tokens for r in rs):,}",
            pct(sum(a.valid for a in answers), len(answers)),
            acc["department"], acc["urgency"], acc["wants_refund"], overall,
            "yes" if lane.is_laya else "no",
            style="bold" if lane.is_laya else None,
        )
    console.print(t)
    console.print("[dim]Accuracy is against hand-written labels. Invalid outputs count as wrong. "
                  "Urgency counts as correct within one level of the label.[/]")


def failures(console: Console, lanes: list[Lane], limit: int = 6) -> None:
    for lane in lanes:
        bad = [(r.ticket.id, q, a.error) for r in lane.results
               for q, a in r.answers.items() if not a.valid]
        if bad:
            console.print(f"\n[bold]{lane.name}[/] invalid outputs ({len(bad)}):")
            for tid, q, err in bad[:limit]:
                console.print(f"  {tid} {q}: [red]{err}[/]")


def probabilities(console: Console, results: list[TicketResult]) -> None:
    t = Table(title="Laya on the tricky tickets: answers come with probabilities",
              title_style=f"bold {PURPLE}", header_style="bold")
    t.add_column("ticket")
    t.add_column("department")
    t.add_column("urgency (0-3)")
    t.add_column("wants refund")
    for r in results:
        d, u, f = (r.answers[q] for q in QUESTIONS)
        dp = d.probabilities[d.value]
        up = max(u.probabilities.values())
        t.add_row(
            f"{r.ticket.id} [dim]{r.ticket.text[:38]}...[/]",
            f"{d.value} [dim]{dp:.0%}[/]",
            f"{u.value} [dim]{up:.0%}[/]",
            f"{'yes' if f.value else 'no'} [dim]p={f.probabilities['yes']:.2f}[/]",
        )
    console.print(t)


def consistency(console: Console, runs: dict[str, list[list[TicketResult]]]) -> None:
    t = Table(title="Ask the same question again: how often does the answer change?",
              title_style=f"bold {PURPLE}", header_style="bold")
    t.add_column("model")
    t.add_column("runs", justify="right")
    t.add_column("answers that flipped", justify="right")
    for name, repeats in runs.items():
        flips = total = 0
        for per_ticket in zip(*repeats):
            for q in QUESTIONS:
                values = {(r.answers[q].value if r.answers[q].valid else "invalid") for r in per_ticket}
                flips += len(values) > 1
                total += 1
        t.add_row(name, str(len(repeats)), f"{flips} / {total}")
    console.print(t)


def cost(console: Console, lanes: list[Lane], tickets_per_day: int = 1_000_000) -> None:
    t = Table(title=f"If this ran on {tickets_per_day:,} tickets per day (hosted list prices)",
              title_style=f"bold {PURPLE}", header_style="bold")
    t.add_column("approach")
    t.add_column("tokens in / out per ticket", justify="right")
    t.add_column("cost per day", justify="right")
    t.add_column("compute time per day", justify="right")
    for lane in lanes:
        rs = lane.results
        tin = sum(r.input_tokens for r in rs) / len(rs)
        tout = sum(r.output_tokens for r in rs) / len(rs)
        secs = sum(r.latency_s for r in rs) / len(rs) * tickets_per_day
        if lane.is_laya:
            label = "Jev API (same calls as Laya)"
            usd = tin * tickets_per_day * JEV_IN / 1e6
        else:
            label = f"{lane.name} prompts at GPT-5 mini prices"
            usd = (tin * GPT5_MINI_IN + tout * GPT5_MINI_OUT) * tickets_per_day / 1e6
        t.add_row(label, f"{tin:,.0f} / {tout:,.0f}", f"${usd:,.0f}", f"{secs / 3600:,.0f} h")
    console.print(t)
    console.print("[dim]Laya self-hosted: no per-token cost at all. "
                  "Compute time is single-stream on this laptop.[/]")
