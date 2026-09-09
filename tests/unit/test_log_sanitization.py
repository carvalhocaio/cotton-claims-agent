import logging

import pytest

from actions import create_arbitration_ticket
from chains.claim_extraction import ClaimExtract

LINE_BREAKING_CHARS = ["\n", "\r", "\x0b", "\x0c", "\x85", "\u2028", "\u2029"]


@pytest.mark.parametrize("char", LINE_BREAKING_CHARS)
def test_line_breaking_chars_do_not_forge_log_lines(caplog, char):
    claim = ClaimExtract(
        claiming_party=f"ACME{char}[TICKET] Forged ticket — claimant: Victim",
        contract_or_lot_reference="LOT-1",
        claim_type="weight",
    )

    with caplog.at_level(logging.INFO):
        create_arbitration_ticket(claim)

    assert len(caplog.records) == 1
    message = caplog.records[0].getMessage()
    # splitlines() is the right criterion: it covers \n, \r, \x85,
    # \u2028 and \u2029 — a substring assertion would let the last
    # three through.
    assert len(message.splitlines()) == 1
    # Functional assertions: sanitization neutralizes the control
    # character without destroying the data. Without this, a _clean
    # that returns None passes the security test — that's exactly
    # what happened.
    assert "ACME" in message
    assert "None" not in message
