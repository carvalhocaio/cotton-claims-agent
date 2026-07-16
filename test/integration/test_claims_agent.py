from typing import cast
import pytest
from langchain_core.messages import AIMessage
from langgraph.graph import MessagesState

from graphs.claims_agent import CLAIMS_AGENT

pytestmark = pytest.mark.integration


def _tool_names_called(messages: list) -> list[str]:
    names = []
    for message in messages:
        if isinstance(message, AIMessage) and message.tool_calls:
            names.extend(call["name"] for call in message.tool_calls)
    return names


def test_contamination_claim_routes_to_triage(claims):
    result = CLAIMS_AGENT.invoke(cast(MessagesState, {"messages": [("user", claims[0])]}))
    assert "triage_claim" in _tool_names_called(result["messages"])


def test_invoice_routes_to_forward_department(claims):
    result = CLAIMS_AGENT.invoke(cast(MessagesState, {"messages": [("user", claims[1])]}))
    assert "forward_to_department" in _tool_names_called(result["messages"])


def test_informal_complaint_still_routes_to_triage(claims):
    result = CLAIMS_AGENT.invoke(cast(MessagesState, {"messages": [("user", claims[2])]}))
    assert "triage_claim" in _tool_names_called(result["messages"])


def test_weight_dispute_routes_to_triage(claims):
    result = CLAIMS_AGENT.invoke(cast(MessagesState, {"messages": [("user", claims[3])]}))
    assert "triage_claim" in _tool_names_called(result["messages"])
