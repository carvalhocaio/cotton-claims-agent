from typing import cast

import pytest

from graphs.claim_extraction import CLAIM_EXTRACTION_GRAPH, GraphState

pytestmark = pytest.mark.integration


def test_contamination_claim_is_escalated_directly(claims):
    result = CLAIM_EXTRACTION_GRAPH.invoke(cast(GraphState, {"message": claims[0]}))

    assert result["resolution"] == "escalated_to_trading_desk"
    assert result["escalation"].requires_escalation is True


def test_weight_dispute_completes_checklist_then_opens_ticket(claims):
    result = CLAIM_EXTRACTION_GRAPH.invoke(cast(GraphState, {"message": claims[3]}))

    assert result["resolution"] == "arbitration_ticket_created"
    assert result["pending_questions"] == []
    assert len(result["qualifying_answers"]) == 3
