from dataclasses import dataclass, field
from typing import Any

from .questions import QUESTIONS
from .tickets import Ticket


@dataclass
class Answer:
    value: Any = None  # str for choice, int level for score, bool for noul
    valid: bool = False
    probabilities: dict | None = None
    error: str = ""


@dataclass
class TicketResult:
    ticket: Ticket
    answers: dict[str, Answer]
    latency_s: float
    input_tokens: int = 0
    output_tokens: int = 0

    def correct(self, question: str) -> bool:
        """Scores are ordinal, so being within one level of the label counts as correct."""
        a = self.answers[question]
        gold = getattr(self.ticket, question)
        if not a.valid:
            return False
        if QUESTIONS[question]["type"] == "score":
            return abs(a.value - gold) <= 1
        return a.value == gold


@dataclass
class Lane:
    """Live state of one contestant, shared between its worker thread and the UI."""

    name: str
    total: int
    role: str = ""
    is_laya: bool = False
    status: str = "waiting"
    done: int = 0
    started: float | None = None
    finished: float | None = None
    output_tokens: int = 0
    current: str = ""
    stream: str = ""
    results: list[TicketResult] = field(default_factory=list)
