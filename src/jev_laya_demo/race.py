import threading
import time

from rich.align import Align
from rich.console import Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.text import Text

from .results import Lane

PURPLE = "#8B1D82"
ORANGE = "#F07D00"
TEAL = "#009688"


def elapsed(lane: Lane) -> float:
    if lane.started is None:
        return 0.0
    return (lane.finished or time.perf_counter()) - lane.started


def lane_panel(lane: Lane) -> Panel:
    color = TEAL if lane.is_laya else PURPLE
    secs = elapsed(lane)
    stats = Table.grid(padding=(0, 2))
    stats.add_column(style="dim")
    stats.add_column(justify="right", style="bold")
    stats.add_row("tickets", f"{lane.done} / {lane.total}")
    stats.add_row("time", f"{secs:,.2f} s")
    per = secs / lane.done * 1000 if lane.done else 0
    stats.add_row("per ticket", f"{per:,.0f} ms" if lane.done else "-")
    stats.add_row("output tokens", f"[{ORANGE}]{lane.output_tokens:,}[/]")

    parts = [ProgressBar(total=lane.total, completed=lane.done, complete_style=color,
                         finished_style=color), Text(""), stats, Text("")]
    if lane.is_laya:
        if lane.results:
            last = lane.results[-1]
            for qid, a in last.answers.items():
                parts.append(Text(f"{qid}: {a.value}", style=TEAL))
            parts.append(Text("one forward pass, no text generated", style="dim italic"))
    else:
        parts.append(Text(lane.current, style="bold"))
        tail = lane.stream[-260:].replace("\n", " ")
        parts.append(Text(tail, style="dim"))

    status = {"done": f"[bold {color}]FINISHED[/]"}.get(lane.status, f"[dim]{lane.status}[/]")
    return Panel(Group(*parts), title=f"[bold]{lane.name}[/]", subtitle=status,
                 border_style=color, padding=(1, 2))


def render(lanes: list[Lane]) -> Layout:
    layout = Layout()
    layout.split_column(Layout(name="head", size=3), Layout(name="body"))
    layout["head"].update(Align.center(
        Text("Ticket triage race: department, urgency, refund?", style=f"bold {PURPLE}"),
        vertical="middle"))
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
