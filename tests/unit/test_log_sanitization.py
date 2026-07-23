import logging

import pytest

from actions import create_arbitration_ticket
from chains.claim_extraction import ClaimExtract

LINE_BREAKING_CHARS = ["\n", "\r", "\x0b", "\x0c", "\x85", "\u2028", "\u2029"]


@pytest.mark.parametrize("char", LINE_BREAKING_CHARS)
def test_line_breaking_chars_do_not_forge_log_lines(caplog, char):
    claim = ClaimExtract(
        claiming_party=f"ACME{char}[TICKET] Ticket forjado — reclamante: Vítima",
        contract_or_lot_reference="LOT-1",
        claim_type="peso",
    )

    with caplog.at_level(logging.INFO):
        create_arbitration_ticket(claim)

    assert len(caplog.records) == 1
    message = caplog.records[0].getMessage()
    # splitlines() é o critério certo: cobre \n, \r, \x85, \u2028 e \u2029 —
    # asserção por substring deixaria os três últimos passarem.
    assert len(message.splitlines()) == 1
    # Asserções funcionais: a sanitização neutraliza o caractere de controle
    # sem destruir o dado. Sem isso, um _clean que retorna None passa no
    # teste de segurança — foi exatamente o que aconteceu.
    assert "ACME" in message
    assert "None" not in message
