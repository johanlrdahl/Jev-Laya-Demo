import threading
import time

from rich.align import Align
from rich.console import Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.text import Text

from .questions import QUESTION_LABEL, format_answer
from .results import Lane

PURPLE = "#8B1D82"
ORANGE = "#F07D00"
TEAL = "#009688"

STATUS = {
    "waiting": "klar til start",
    "deciding": "beslutter alle saker i ett steg",
    "generating": "skriver svar ord for ord",
    "done": "FERDIG",
}


def elapsed(lane: Lane) -> float:
    if lane.started is None:
        return 0.0
    return (lane.finished or time.perf_counter()) - lane.started


def lane_panel(lane: Lane) -> Panel:
    color = TEAL if lane.is_laya else PURPLE
    secs = elapsed(lane)
    per = f"{secs / lane.done * 1000:,.0f} ms per sak" if lane.done else "ikke startet ennå"

    parts = [
        Text(lane.role, style="italic"),
        Text(""),
        ProgressBar(total=lane.total, completed=lane.done, complete_style=color, finished_style=color),
        Text(""),
        Text(f"{lane.done} av {lane.total} saker ferdig"),
        Text(f"{secs:,.1f} sekunder brukt"),
        Text(per),
        Text(f"{lane.output_tokens:,} output-tokens skrevet", style=ORANGE),
        Text(""),
    ]
    if lane.is_laya:
        if lane.results:
            last = lane.results[-1]
            parts.append(Text(f"Eksempel fra siste sak ({last.ticket.id}):", style="bold"))
            for qid, answer in last.answers.items():
                parts.append(Text(f"{QUESTION_LABEL[qid]}: {format_answer(qid, answer)}", style=TEAL))
            parts.append(Text("Alle tre svar i ett steg — 0 ord skrevet.", style="dim italic"))
        else:
            parts.append(Text("Tar beslutninger direkte uten å skrive tekst...", style="dim italic"))
    elif lane.status == "done":
        parts.append(Text("Ferdig. Siste tekst den skrev:", style="bold"))
        parts.append(Text(lane.stream[-220:].replace("\n", " "), style="dim"))
    elif lane.current or lane.stream:
        parts.append(Text(lane.current, style="bold"))
        parts.append(Text("Skriver svaret ett ord (token) av gangen:", style="dim italic"))
        parts.append(Text(lane.stream[-220:].replace("\n", " "), style="dim"))
    else:
        parts.append(Text("Venter på startskuddet.", style="dim italic"))

    status = STATUS.get(lane.status, lane.status)
    style = f"bold {color}" if lane.status == "done" else "dim"
    return Panel(Group(*parts), title=f"[bold]{lane.name}[/]", subtitle=f"[{style}]{status}[/]",
                 border_style=color, padding=(1, 2))


def render(lanes: list[Lane]) -> Layout:
    n = lanes[0].total if lanes else 0
    header = Text.assemble(
        (f"Kundeservice-race: {n} henvendelser × 3 spørsmål (Avdeling, Hastegrad 0–3, Refusjon?)\n",
         f"bold {PURPLE}"),
        ("System 1 (Laya) velger direkte i ett steg. System 2 (LLM-ene) må skrive seg frem til svaret ord for ord.",
         "dim"),
    )
    layout = Layout()
    layout.split_column(Layout(name="head", size=5), Layout(name="body"))
    layout["head"].update(Align.center(header, vertical="middle"))
    layout["body"].split_row(*[Layout(lane_panel(l)) for l in lanes])
    return layout


def race(jobs: list[tuple[Lane, callable]]) -> None:
    lanes = [lane for lane, _ in jobs]
    threads = [threading.Thread(target=fn, daemon=True) for _, fn in jobs]
    with Live(render(lanes), refresh_per_second=12, screen=False) as live:
        for t in threads:
            t.start()
        while any(t.is_alive() for t in threads):
            live.update(render(lanes))
            time.sleep(0.08)
        live.update(render(lanes))
