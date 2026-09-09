"""
Entry point for cotton-claims-agent.

Usage:
    uv run python main.py --demo
    uv run python main.py --message "claim text here"
"""

import argparse
import logging

from langchain_core.messages import AIMessage, HumanMessage

from example_claims import CLAIMS
from graphs.claims_agent import AGENT_RECURSION_LIMIT, CLAIMS_AGENT


def run_message(message: str) -> None:
    try:
        result = CLAIMS_AGENT.invoke(
            {"messages": [HumanMessage(content=message)]},
            config={"recursion_limit": AGENT_RECURSION_LIMIT},
        )
    except Exception as exc:
        # CLI boundary: report the error instead of raising a traceback.
        print(f"[ERROR] Failed to process the message: {exc}")
        return
    final_message = result["messages"][-1]
    content = (
        final_message.content
        if isinstance(final_message, AIMessage)
        else str(final_message)
    )
    print(content)


def run_demo() -> None:
    for index, claim in enumerate(CLAIMS):
        print(f"\n=== CLAIM {index} ===")
        run_message(claim)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Mail triage for Cerrado Cotton Trading Co."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--demo",
        action="store_true",
        help="Runs the agent over the sample messages in example_claims.py",
    )
    group.add_argument(
        "--message",
        type=str,
        help="Runs the agent over a single message, passed as text",
    )
    return parser


def main() -> None:
    # Entry point configures logging; business actions (actions.py) only
    # emit via logging, without knowing where the output goes.
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = build_parser().parse_args()
    if args.demo:
        run_demo()
    else:
        run_message(args.message)


if __name__ == "__main__":
    main()
