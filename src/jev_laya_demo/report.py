from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .questions import QUESTION_LABEL, QUESTIONS, explain_error, format_answer
from .results import Lane, TicketResult

# USD per million tokens, listepriser sjekket nov 2026.
HAIKU_IN, HAIKU_OUT = 0.10, 0.50            # Claude Haiku 5.5 (<=100k), platform.claude.com/docs/en/about-claude/pricing
LUNA_IN, LUNA_OUT = 0.20, 1.20              # GPT-5.6 Luna, developers.openai.com/api/docs/models/gpt-5.6-luna
SONNET_IN, SONNET_OUT = 2.00, 10.00         # Claude Sonnet 5.5, platform.claude.com/docs/en/about-claude/pricing
TERRA_IN, TERRA_OUT = 2.00, 12.00           # GPT-5.6 Terra, developers.openai.com/api/docs/pricing
JEV_IN = 0.042                              # docs.typesafe.ai/models, output-tokens er gratis

PURPLE = "#8B1D82"


def pct(n: int, d: int) -> str:
    return f"{100 * n / d:.0f}%" if d else "-"


def note(console: Console, *lines: str) -> None:
    console.print(Text("\n".join(lines), style="dim"))


def briefing(console: Console, n: int, names: list[str], single_call: bool, reason: bool) -> None:
    """Vises før racet, slik at alle i rommet vet hva de ser på."""
    how = "alle tre spørsmål i ett kall" if single_call else "ett spørsmål av gangen"
    write = "kun selve JSON-svaret" if not reason else "én setning begrunnelse før JSON-svaret"
    chatbots = " og ".join(names) if names else "LLM-ene"
    body = Group(
        Text.from_markup(f"[bold]Oppgaven: {n} kundehenvendelser.[/] Alle modeller skal svare på de samme tre spørsmålene:"),
        Text("    1. Hvilken avdeling?  (Choice)  billing, technical, sales eller other"),
        Text("    2. Hvor mye haster?   (Score)   0 = ingen hast, 1 = denne uken, 2 = blokkert, 3 = kritisk"),
        Text("    3. Vil ha refusjon?   (Noul)    ber kunden om å få penger tilbake? (ja / nei)"),
        Text(""),
        Text.from_markup("[bold #009688]Laya (System 1)[/] er en beslutningsmodell: den scorer alternativene i ett steg og skriver [bold]0 ord[/]."),
        Text.from_markup(f"[bold #8B1D82]{chatbots} (System 2)[/] er språkmodeller: de skriver {write}, {how}."),
        Text(""),
        Text("Se etter to ting: hvem som blir ferdig først, og hvor mange output-tokens språkmodellene må skrive."),
    )
    console.print(Panel(body, title="[bold]Slik fungerer demoen[/]", border_style=PURPLE, padding=(1, 2)))


def summary(console: Console, lanes: list[Lane]) -> None:
    speed = Table(title="Del 1 — Hastighet og mengde tekst som måtte skrives",
                  title_style=f"bold {PURPLE}", header_style="bold", expand=True)
    speed.add_column("modell")
    speed.add_column("type modell")
    for col in ("total tid", "tid per sak", "skrevne output-tokens"):
        speed.add_column(col, justify="right")

    accuracy = Table(title="Del 2 — Kvalitet: traff modellen riktig svar (sammenlignet med fasit)?",
                     title_style=f"bold {PURPLE}", header_style="bold", expand=True)
    accuracy.add_column("modell")
    for col in ("gyldig format", "riktig avdeling", "riktig hastegrad (±1)",
                "riktig om refusjon", "riktig totalt"):
        accuracy.add_column(col, justify="right")

    for lane in lanes:
        rs = lane.results
        answers = [a for r in rs for a in r.answers.values()]
        secs = (lane.finished or 0) - (lane.started or 0)
        acc = {q: pct(sum(r.correct(q) for r in rs), len(rs)) for q in QUESTIONS}
        overall = pct(sum(r.correct(q) for r in rs for q in QUESTIONS), len(answers))
        style = "bold" if lane.is_laya else None
        speed.add_row(
            lane.name, lane.role,
            f"{secs:,.1f} s", f"{secs / len(rs) * 1000:,.0f} ms",
            f"{sum(r.output_tokens for r in rs):,} tokens",
            style=style,
        )
        accuracy.add_row(
            lane.name,
            pct(sum(a.valid for a in answers), len(answers)),
            acc["department"], acc["urgency"], acc["wants_refund"], overall,
            style=style,
        )
    console.print(speed)
    note(console,
         "• Tid per sak = total tid delt på antall saker.",
         "• Skrevne output-tokens = ord/tekstbitene modellen måtte generere ett og ett. Det er dette som tar tid og koster penger. Laya skriver 0.")
    console.print()
    console.print(accuracy)
    note(console,
         "• Gyldig format = svaret kunne tolkes av koden og brukte kun tillatte alternativer (Laya er alltid 100 %).",
         "• Riktig avdeling / refusjon = eksakt treff mot håndlaget fasit. Hastegrad (0–3) teller som riktig innenfor ±1 nivå.",
         "• Ugyldig format teller som feil svar.")


def failures(console: Console, lanes: list[Lane], limit: int = 6) -> None:
    for lane in lanes:
        bad = [(r.ticket.id, q, a.error) for r in lane.results
               for q, a in r.answers.items() if not a.valid]
        if not bad:
            continue
        console.print(f"\n[bold]{lane.name}[/] ga {len(bad)} svar som koden ikke kunne bruke:")
        for tid, q, err in bad[:limit]:
            console.print(f"    sak {tid}, {QUESTION_LABEL[q].lower()}: [red]{explain_error(err)}[/]")
        if len(bad) > limit:
            console.print(f"    … og {len(bad) - limit} til")


def probabilities(console: Console, results: list[TicketResult]) -> None:
    t = Table(title="Del 3 — De vriene sakene: Laya gir også sannsynlighet for hvert svar",
              title_style=f"bold {PURPLE}", header_style="bold", expand=True)
    t.add_column("kundehenvendelse", ratio=3)
    t.add_column("avdeling (Choice)", ratio=1)
    t.add_column("hastegrad (Score)", ratio=1)
    t.add_column("refusjon? (Noul)", ratio=1)
    for r in results:
        team, urgency, refund = (r.answers[q] for q in QUESTIONS)
        team_sure = team.probabilities[team.value] if team.probabilities and team.valid else 0
        urgency_sure = max(urgency.probabilities.values()) if urgency.probabilities else 0
        refund_p = refund.probabilities["yes"] if refund.probabilities else 0
        txt = r.ticket.text if len(r.ticket.text) <= 95 else r.ticket.text[:95].rstrip() + "…"
        t.add_row(
            f"[bold]{r.ticket.id}[/]  {txt}",
            f"{format_answer('department', team)}  [dim]({team_sure:.0%} sikker)[/]",
            f"{format_answer('urgency', urgency)}  [dim]({urgency_sure:.0%} sikker)[/]",
            f"{format_answer('wants_refund', refund)}  [dim](p={refund_p:.0%} for ja)[/]",
        )
    console.print(t)
    note(console,
         "• Prosenten er Layas egen konfidens (sannsynlighet), ikke vår fasit.",
         "• En vanlig LLM gir deg bare tekst uten en slik sannsynlighetsfordeling.",
         "• I kode kan du sette en terskel: håndter automatisk når modellen er >85 % sikker, og send tvilstilfellene (som T20) til en LLM eller et menneske.")


def consistency(console: Console, runs: dict[str, list[list[TicketResult]]]) -> None:
    sample = next(iter(runs.values()))
    n_runs = len(sample)
    n_emails = len(sample[0])
    t = Table(title=f"Del 4 — Konsistens: vi stilte de {n_emails} vriene sakene {n_runs} ganger på rad",
              title_style=f"bold {PURPLE}", header_style="bold", expand=True)
    t.add_column("modell")
    t.add_column("antall kjøringer", justify="right")
    t.add_column("svar som vippet (endret seg)", justify="right")
    for name, repeats in runs.items():
        flips = total = 0
        for per_ticket in zip(*repeats):
            for q in QUESTIONS:
                values = {(r.answers[q].value if r.answers[q].valid else "ugyldig") for r in per_ticket}
                flips += len(values) > 1
                total += 1
        t.add_row(name, str(len(repeats)), f"{flips} av {total}")
    console.print(t)
    note(console,
         f"• {n_emails} vriene saker × 3 spørsmål = {n_emails * 3} beslutninger, kjørt {n_runs} ganger.",
         "• Laya er deterministisk og gir alltid nøyaktig samme svar (0 av 21 vippet). En LLM trekker ord med temperatur og kan ombestemme seg.")


def cost(console: Console, lanes: list[Lane], tickets_per_day: int = 1_000_000) -> None:
    t = Table(title=f"Del 5 — Økonomi: hva ville {tickets_per_day:,} saker per dag kostet i skyen?",
              title_style=f"bold {PURPLE}", header_style="bold", expand=True)
    t.add_column("oppsett")
    t.add_column("tokens per sak", justify="right")
    t.add_column("System 1\nJev API", justify="right")
    t.add_column("Små, raske LLM-er\nHaiku 5.5 / Luna", justify="right")
    t.add_column("Standard LLM-er\nSonnet 5.5 / Terra", justify="right")
    t.add_column("regnetid (1 strøm)", justify="right")
    for lane in lanes:
        rs = lane.results
        tin = sum(r.input_tokens for r in rs) / len(rs)
        tout = sum(r.output_tokens for r in rs) / len(rs)
        secs = sum(r.latency_s for r in rs) / len(rs) * tickets_per_day
        tokens = f"{tin:,.0f} inn / {tout:,.0f} ut"
        hours = f"{secs / 3600:,.0f} timer"
        if lane.is_laya:
            jev = f"${tin * tickets_per_day * JEV_IN / 1e6:,.0f}"
            t.add_row("Laya / Jev", tokens, jev, "–", "–", hours)
        else:
            def usd(p_in: float, p_out: float) -> str:
                return f"${(tin * p_in + tout * p_out) * tickets_per_day / 1e6:,.0f}"
            small = f"{usd(HAIKU_IN, HAIKU_OUT)} / {usd(LUNA_IN, LUNA_OUT)}"
            std = f"{usd(SONNET_IN, SONNET_OUT)} / {usd(TERRA_IN, TERRA_OUT)}"
            t.add_row(lane.name, tokens, "–", small, std, hours)
    console.print(t)
    note(console,
         f"• Listepriser per 1M tokens (inn / ut): Jev ${JEV_IN:.3f} / $0 · "
         f"Claude Haiku 5.5 ${HAIKU_IN:.2f} / ${HAIKU_OUT:.2f} · GPT-5.6 Luna ${LUNA_IN:.2f} / ${LUNA_OUT:.2f} · "
         f"Claude Sonnet 5.5 ${SONNET_IN:.0f} / ${SONNET_OUT:.0f} · GPT-5.6 Terra ${TERRA_IN:.0f} / ${TERRA_OUT:.0f}.",
         "• Kjører du Laya selv (open-source Apache 2.0), er token-prisen $0.")
