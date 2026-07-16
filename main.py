"""
Ponto de entrada do cotton-claims-agent.

Uso:
    uv run python main.py --demo
    uv run python main.py --message "texto da reclamação aqui"
"""

import argparse

from langchain_core.messages import AIMessage, HumanMessage

from example_claims import CLAIMS
from graphs.claims_agent import CLAIMS_AGENT


def run_message(message: str) -> None:
    result = CLAIMS_AGENT.invoke({"messages": [HumanMessage(content=message)]})
    final_message = result["messages"][-1]
    content = final_message.content if isinstance(final_message, AIMessage) else final_message
    print(content)


def run_demo() -> None:
    for index, claim in enumerate(CLAIMS):
        print(f"\n=== CLAIM {index} ===")
        run_message(claim)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Triagem de correspondência da Cerrado Cotton Trading Co."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--demo",
        action="store_true",
        help="Roda o agente sobre as mensagens de exemplo em example_claims.py",
    )
    group.add_argument(
        "--message",
        type=str,
        help="Roda o agente sobre uma mensagem única, passada como texto",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.demo:
        run_demo()
    else:
        run_message(args.message)


if __name__ == "__main__":
    main()
