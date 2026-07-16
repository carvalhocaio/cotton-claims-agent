import logging

from actions import create_arbitration_ticket
from chains.claim_extraction import ClaimExtract


def test_newlines_in_fields_do_not_forge_log_lines(caplog):
    # Campo controlado pelo atacante tentando injetar uma linha de log falsa.
    claim = ClaimExtract(
        claiming_party="ACME\n[TICKET] Ticket forjado — reclamante: Vítima",
        contract_or_lot_reference="LOT-1",
        claim_type="peso",
    )

    with caplog.at_level(logging.INFO):
        create_arbitration_ticket(claim)

    assert len(caplog.records) == 1
    message = caplog.records[0].getMessage()
    # A defesa é contra a quebra de linha que criaria uma linha de log
    # separada/forjada. O texto do atacante continua inline (inofensivo,
    # claramente parte do campo do reclamante), mas sem nenhum "\n".
    assert "\n" not in message
    assert "\r" not in message
