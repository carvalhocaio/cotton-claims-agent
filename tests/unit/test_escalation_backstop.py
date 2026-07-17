from chains.claim_extraction import ClaimExtract
from chains.escalation_check import ESCALATION_EXPOSURE_THRESHOLD_USD
from graphs.claim_extraction import deterministic_escalation_triggers


def test_exposure_at_or_above_threshold_forces_escalation():
    claim = ClaimExtract(max_potential_exposure=ESCALATION_EXPOSURE_THRESHOLD_USD)
    triggers = deterministic_escalation_triggers(claim)

    assert triggers  # não vazio
    assert any("exposição" in t for t in triggers)


def test_below_threshold_returns_no_triggers():
    claim = ClaimExtract(max_potential_exposure=ESCALATION_EXPOSURE_THRESHOLD_USD - 1)
    triggers = deterministic_escalation_triggers(claim)

    assert triggers == []


def test_missing_exposure_is_treated_as_zero():
    claim = ClaimExtract()
    triggers = deterministic_escalation_triggers(claim)

    assert triggers == []


def test_contamination_wording_alone_does_not_trigger_backstop():
    # O backstop não faz busca de palavra-chave no texto: menções (mesmo
    # negadas, ex.: "não houve contaminação") não devem escalar por si só.
    # A avaliação de contaminação é responsabilidade do LLM.
    claim = ClaimExtract(claim_type="contaminação", max_potential_exposure=0.0)
    triggers = deterministic_escalation_triggers(claim)

    assert triggers == []
