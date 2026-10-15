"""The three typed questions asked about every ticket, in Jev/Laya wire format."""

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
