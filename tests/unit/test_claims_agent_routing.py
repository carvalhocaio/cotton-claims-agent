from typing import cast

from langchain_core.messages import AIMessage
from langgraph.graph import END, MessagesState

from graphs.claims_agent import should_continue


def test_should_continue_routes_to_tools_when_tool_calls_present():
    message = AIMessage(
        content="",
        tool_calls=[{"name": "triage_claim", "args": {"message": "x"}, "id": "1"}],
    )
    state = {"messages": [message]}

    assert should_continue(cast(MessagesState, state)) == "tools"


def test_should_continue_ends_when_no_tool_calls():
    message = AIMessage(content="Resumo final.")
    state = {"messages": [message]}

    assert should_continue(cast(MessagesState, state)) == END
