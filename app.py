"""
Streamlit interface for cotton-claims-agent.

Optional demonstration layer - not part of the project's core (chains/,
graphs/, tests/). It only consumes CLAIMS_AGENT, the same way main.py
already does.

Usage:
    uv run streamlit run app.py
"""

import logging
from typing import Any

import streamlit as st
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage

from example_claims import CLAIMS
from graphs.claims_agent import AGENT_RECURSION_LIMIT, CLAIMS_AGENT

logger = logging.getLogger(__name__)

TOOL_LABELS = {
    "triage_claim": "Claim triage",
    "forward_to_department": "Forwarded to another department",
}

EXAMPLE_LABELS = {
    0: "Example 0 — Contamination + HVI deviation (should escalate)",
    1: "Example 1 — Freight invoice (not a claim)",
    2: "Example 2 — Informal complaint, no technical vocabulary",
    3: "Example 3 — Weight discrepancy (checklist, no escalation)",
}


def extract_tool_call_and_output(
    messages: list[BaseMessage],
) -> tuple[str | None, str | None]:
    """Extracts the name of the tool called by the agent and the text it
    returned. Pure function, no side effects — isolated from the rest of
    the UI so it can be tested in isolation, if that ever makes sense.
    """
    tool_name = None
    for message in messages:
        if isinstance(message, AIMessage) and message.tool_calls:
            tool_name = message.tool_calls[0]["name"]
            break

    tool_output = None
    for message in messages:
        if isinstance(message, ToolMessage):
            if isinstance(message.content, str):
                tool_output = message.content
            else:
                tool_output = str(message.content)
            break

    return tool_name, tool_output


def render_result(result: dict[str, Any]) -> None:
    messages = result["messages"]
    tool_name, tool_output = extract_tool_call_and_output(messages)
    final_summary = messages[-1].content

    if tool_name:
        st.markdown(f"**{TOOL_LABELS.get(tool_name, tool_name)}**")

    if tool_output:
        st.info(tool_output)

    st.markdown("**Agent summary:**")
    st.write(final_summary)


def main() -> None:
    st.set_page_config(page_title="Cotton Claims Agent")
    st.title("Cotton Claims Agent")
    st.caption(
        "Mail triage for a cotton trading company — built with LangGraph. "
        "The agent decides on its own: quality claims go through full "
        "triage, everything else is forwarded to the right department."
    )

    example_choice = st.selectbox(
        "Try a ready-made example (optional)",
        options=[None, *EXAMPLE_LABELS.keys()],
        format_func=lambda i: "- select -" if i is None else EXAMPLE_LABELS[i],
    )

    default_text = CLAIMS[example_choice] if example_choice is not None else ""
    message = st.text_area(
        "Paste the email or claim text here",
        value=default_text,
        height=200,
    )

    if st.button("Run triage", type="primary", disabled=not message.strip()):
        with st.spinner("Agent evaluating the message..."):
            try:
                result = CLAIMS_AGENT.invoke(
                    {"messages": [HumanMessage(content=message)]},
                    config={"recursion_limit": AGENT_RECURSION_LIMIT},
                )
            except Exception:
                # Error detail goes only to the log (server-side); the end
                # user sees a generic message, without library/SDK internals.
                logger.exception("Failed to process the message")
                st.error(
                    "Could not process the message. "
                    "Please try again or contact support."
                )
                return
        render_result(result)


if __name__ == "__main__":
    main()
