from typing import cast
from chains.escalation_check import EscalationCheck
from graphs.claim_extraction import (
    QUALIFYING_QUESTIONS,
    GraphState,
    has_pending_questions,
    prepare_qualification,
    route_by_escalation
)

def test_route_by_escalation_when_required():
    state = {
        "escalation": EscalationCheck(
            requires_escalation=True, escalation_triggers=["x"], reasoning="r"
        )
    }
    assert route_by_escalation(cast(GraphState, state)) == "escalate_to_trading_desk"


def test_route_by_escalation_when_not_required():
    state = {
        "escalation": EscalationCheck(
            requires_escalation=False, escalation_triggers=[], reasoning="r"
        )
    }

    assert route_by_escalation(cast(GraphState, state)) == "prepare_qualification"


def test_prepare_qualification_initializes_pending_questions():
    result = prepare_qualification(cast(GraphState, {}))

    assert result["pending_questions"] == QUALIFYING_QUESTIONS
    assert result["pending_questions"] is not QUALIFYING_QUESTIONS
    assert result["qualifying_answers"] == {}


def test_has_pending_questions_with_items_continues_loop():
    state = {"pending_questions": ["some question"]}
    assert has_pending_questions(cast(GraphState, state)) == "ask_next_qualifying_question"



def test_has_pending_questions_when_empty_exits_loop():
    state = {"pending_questions": []}
    assert has_pending_questions(cast(GraphState, state)) == "create_arbitration_ticket"
