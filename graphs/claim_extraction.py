"""
Grafo de triagem de reclamações: extrai dados estruturados da mensagem,
avalia se precisa de escalonamento imediato e roteia para o caminho
correspondente.

Depende de chains.claim_extraction e chains.escalation_check - este é o
primeiro módulo de projeto que orquestra outros, por design.
"""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from chains.claim_extraction import CLAIM_PARSER_CHAIN, ClaimExtract
from chains.escalation_check import ESCALATION_CHECK_CHAIN, EscalationCheck


class GraphState(TypedDict):
    message: str
    claim_data: ClaimExtract
    escalation: EscalationCheck
    resolution: str


def parse_claim(state: GraphState) -> dict:
    claim_data = CLAIM_PARSER_CHAIN.invoke({"message": state["message"]})
    return {"claim_data": claim_data}


def check_escalation(state: GraphState) -> dict:
    escalation = ESCALATION_CHECK_CHAIN.invoke({"message": state["message"]})
    return {"escalation": escalation}


def route_by_escalation(state: GraphState) -> str:
    if state["escalation"].requires_escalation:
        return "escalate_to_trading_desk"
    return "create_arbitration_ticket"


def escalate_to_trading_desk(state: GraphState) -> dict:
    claim = state["claim_data"]
    print(
        f"[ESCALAÇÃO] Notificando mesa de trading - reclamante: "
        f"{claim.claiming_party}, contrato/lote: {claim.contract_or_lot_reference}, "
        f"exposição estimada: USD {claim.max_potential_exposure or 0:,.2f}, "
        f"motivos: {', '.join(state['escalation'].escalation_triggers)}."
    )

    return {"resolution": "escalated_to_trading_desk"}


def create_arbitration_ticket(state: GraphState) -> dict:
    claim = state["claim_data"]
    print(
        "[TICKET] Ticket de arbitragem aberto - reclamante: "
        f"{claim.claiming_party}, contrato/lote: {claim.contract_or_lot_reference}, "
        f"tipo: {claim.claim_type}."
    )

    return {"resolution": "arbitration_ticket_created"}


workflow = StateGraph(GraphState)
workflow.add_node("parse_claim", parse_claim)
workflow.add_node("check_escalation", check_escalation)
workflow.add_node("escalate_to_trading_desk", escalate_to_trading_desk)
workflow.add_node("create_arbitration_ticket", create_arbitration_ticket)

workflow.add_edge(START, "parse_claim")
workflow.add_edge("parse_claim", "check_escalation")
workflow.add_conditional_edges(
    "check_escalation",
    route_by_escalation,
    {
        "escalate_to_trading_desk": "escalate_to_trading_desk",
        "create_arbitration_ticket": "create_arbitration_ticket",
    },
)
workflow.add_edge("escalate_to_trading_desk", END)
workflow.add_edge("create_arbitration_ticket", END)

CLAIM_EXTRATION_GRAPH = workflow.compile()
