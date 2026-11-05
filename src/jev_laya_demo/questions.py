"""De tre typede spørsmålene som stilles om hver henvendelse, i Jev/Laya-format."""

# Instruksjonene til modellene holdes på engelsk fordi både Laya (engelsk + flerspråklig router)
# og de lokale LLM-ene er trent primært på engelske instruksjoner. Visningstekst i UI er på norsk.
DEPARTMENTS = {
    "billing": "invoices, charges, payments, refunds, subscriptions",
    "technical": "bugs, errors, outages, login problems, integrations",
    "sales": "pricing, quotes, upgrades, buying more seats or plans",
    "other": "anything that is not billing, technical or sales",
}

URGENCY = [
    "no rush, just information or feedback",
    "should be handled this week",
    "urgent, the customer is blocked",
    "critical, the business is down or losing money right now",
]

# Norske visningsnavn i terminalen
DEPT_NO = {
    "billing": "fakturering",
    "technical": "teknisk",
    "sales": "salg",
    "other": "annet",
}

URGENCY_SHORT = ["0 (ingen hast)", "1 (denne uken)", "2 (blokkert)", "3 (kritisk)"]

QUESTION_LABEL = {
    "department": "Avdeling (Choice)",
    "urgency": "Hastegrad (Score)",
    "wants_refund": "Refusjon? (Noul)",
}

NOW_WRITING = {
    "department": "hvilken avdeling som skal ta saken",
    "urgency": "hvor mye det haster (0-3)",
    "wants_refund": "om kunden ber om pengene tilbake",
}


def format_value(qid: str, value) -> str:
    if qid == "department":
        return DEPT_NO.get(str(value), str(value))
    if qid == "urgency":
        return URGENCY_SHORT[value]
    if qid == "wants_refund":
        return "ja" if value else "nei"
    return str(value)


def format_answer(qid: str, answer) -> str:
    if not answer.valid:
        return "ugyldig svar"
    return format_value(qid, answer.value)


def explain_error(error: str) -> str:
    if error == "no valid JSON":
        return "skrev tekst som ikke kunne tolkes som gyldig JSON"
    if error == "missing key":
        return "glemte å svare på spørsmålet i JSON-objektet"
    if error.startswith("not an option:"):
        return f"fant på kategorien {error.split(':', 1)[1].strip()} (ikke blant de 4 tillatte)"
    if error.startswith("not a level:"):
        return f"svarte {error.split(':', 1)[1].strip()} (må være 0, 1, 2 eller 3)"
    if error.startswith("not true/false:"):
        return f"svarte {error.split(':', 1)[1].strip()} (må være true eller false)"
    return error


QUESTIONS = {
    "department": {
        "type": "choice",
        "instructions": "Which team should handle this support ticket?",
        "criteria": DEPARTMENTS,
    },
    "urgency": {
        "type": "score",
        "instructions": "How urgent is this support ticket?",
        "criteria": URGENCY,
    },
    "wants_refund": {
        "type": "noul",
        "instructions": "The customer is asking to get money back (a refund, credit or chargeback).",
    },
}
