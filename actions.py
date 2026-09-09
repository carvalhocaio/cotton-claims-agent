"""
Business actions (side effects) of the triage flow.

Concentrates in one place all the I/O that used to be embedded as `print`
inside the graph nodes and the agent's tools. Separating these actions
from the orchestration logic restores the Single Responsibility
Principle: the nodes decide *what* to do, this module decides *how* to
communicate/record it.

Today the actions only write to `logging`; swapping them for real
integrations (email, ticket, queue) is a local change, without touching
the graphs.
"""

import logging
import re

from chains.binary_questions import BinaryAnswer
from chains.claim_extraction import ClaimExtract

logger = logging.getLogger(__name__)

_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f-\x9f  ]")


def _clean(value: object) -> str:
    """Neutralizes line breaks and control characters in text coming
    from the LLM/sender before it goes to the log (CS-1: prevents log
    line forging by injecting `\\n[TICKET] ...` into fields such as the
    claimant's name).

    Covers C0 (`\\x00-\\x1f`), DEL, the C1 block (`\\x7f-\\x9f`, which
    includes NEL `\\x85`) and the Unicode line separators `\\u2028`/
    `\\u2029` — the last three are treated as line breaks by
    `str.splitlines()`.
    """
    return _CONTROL_CHARS.sub(" ", str(value))


def _claim_summary(claim: ClaimExtract) -> str:
    """Short identification summary of the claim, reused in the
    escalation and ticket-opening messages (DRY)."""
    return (
        f"claimant: {_clean(claim.claiming_party)}, "
        f"contract/lot: {_clean(claim.contract_or_lot_reference)}"
    )


def notify_trading_desk(claim: ClaimExtract, triggers: list[str]) -> None:
    """Notifies the trading desk about an escalated claim."""
    exposure = f"{claim.max_potential_exposure or 0:,.2f}"
    logger.info(
        "[ESCALATION] Notifying trading desk — %s, "
        "estimated exposure: USD %s, reasons: %s.",
        _claim_summary(claim),
        exposure,
        _clean(", ".join(triggers)),
    )


def log_qualification_answer(question: str, answer: BinaryAnswer) -> None:
    """Records the answer to a qualification checklist question."""
    logger.info(
        "[QUALIFICATION] %s -> %s (%s)",
        question,
        answer.answer,
        answer.confidence,
    )


def create_arbitration_ticket(claim: ClaimExtract) -> None:
    """Opens an arbitration ticket for the qualified claim."""
    logger.info(
        "[TICKET] Arbitration ticket opened — %s, type: %s.",
        _claim_summary(claim),
        _clean(claim.claim_type),
    )


def forward_to_department(department: str, reason: str) -> None:
    """Forwards the message to another internal department."""
    logger.info(
        "[FORWARDING] Message sent to %s. Reason: %s",
        _clean(department),
        _clean(reason),
    )
