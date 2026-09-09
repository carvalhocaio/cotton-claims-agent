from chains.claim_extraction import ClaimExtract
from chains.escalation_check import ESCALATION_EXPOSURE_THRESHOLD_USD
from graphs.claim_extraction import deterministic_escalation_triggers


def test_exposure_at_or_above_threshold_forces_escalation():
    claim = ClaimExtract(max_potential_exposure=ESCALATION_EXPOSURE_THRESHOLD_USD)
    triggers = deterministic_escalation_triggers(claim)

    assert triggers  # not empty
    assert any("exposure" in t for t in triggers)


def test_below_threshold_returns_no_triggers():
    claim = ClaimExtract(max_potential_exposure=ESCALATION_EXPOSURE_THRESHOLD_USD - 1)
    triggers = deterministic_escalation_triggers(claim)

    assert triggers == []


def test_missing_exposure_is_treated_as_zero():
    claim = ClaimExtract()
    triggers = deterministic_escalation_triggers(claim)

    assert triggers == []


def test_contamination_wording_alone_does_not_trigger_backstop():
    # The backstop does not do keyword search in the text: mentions (even
    # negated, e.g. "there was no contamination") should not escalate by
    # themselves. Contamination assessment is the LLM's responsibility.
    claim = ClaimExtract(claim_type="contamination", max_potential_exposure=0.0)
    triggers = deterministic_escalation_triggers(claim)

    assert triggers == []
