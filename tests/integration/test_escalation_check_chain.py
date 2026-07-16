from typing import cast

import pytest

from chains.escalation_check import ESCALATION_CHECK_CHAIN, EscalationCheck

pytestmark = pytest.mark.integration


def test_contamination_claim_requires_escalation(claims):
    result = cast(
        EscalationCheck, ESCALATION_CHECK_CHAIN.invoke({"message": claims[0]})
    )
    assert result.requires_escalation is True


def test_weight_dispute_does_not_require_escalation(claims):
    result = cast(
        EscalationCheck, ESCALATION_CHECK_CHAIN.invoke({"message": claims[3]})
    )
    assert result.requires_escalation is False
