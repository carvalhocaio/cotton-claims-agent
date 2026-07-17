"""
Grafo de triagem de reclamações: extrai dados estruturados da mensagem,
avalia se precisa de escalonamento imediato e roteia para o caminho
correspondente. Reclamações não escaladas passam por um checklist de
qualificação (ciclo) antes de virar ticket de arbitragem.

Depende de chains.claim_extraction, chains.escalation_check e
chains.binary_questions — este módulo orquestra as três, por design.
"""

from typing import Any, Literal, TypedDict, cast

from langgraph.graph import END, START, StateGraph

import actions
from chains.binary_questions import BINARY_QUESTION_CHAIN, BinaryAnswer
from chains.claim_extraction import CLAIM_PARSER_CHAIN, ClaimExtract
from chains.escalation_check import (
    ESCALATION_CHECK_CHAIN,
    ESCALATION_EXPOSURE_THRESHOLD_USD,
    EscalationCheck,
)

QUALIFYING_QUESTIONS = [
    "O embarque foi inspecionado por um surveyor independente?",
    "Houve contaminação confirmada no lote?",
    "O lote foi lacrado desde a origem até o destino?",
]
"""Checklist fixo usado antes de abrir um ticket de arbitragem. Única
fonte de verdade — se o checklist mudar, muda só aqui."""


class GraphState(TypedDict):
    message: str
    claim_data: ClaimExtract
    escalation: EscalationCheck
    pending_questions: list[str]
    qualifying_answers: dict[str, BinaryAnswer]
    resolution: str


def parse_claim(state: GraphState) -> dict[str, ClaimExtract]:
    claim_data = cast(
        ClaimExtract, CLAIM_PARSER_CHAIN.invoke({"message": state["message"]})
    )
    return {"claim_data": claim_data}


def deterministic_escalation_triggers(claim: ClaimExtract) -> list[str]:
    """Backstop determinístico de escalonamento, independente do LLM.

    Defesa contra prompt injection (PI-1/PI-4): mesmo que a mensagem
    instrua o modelo a "não escalar", uma exposição financeira extraída
    acima do limiar força o escalonamento. Usa apenas o campo estruturado
    `max_potential_exposure` (objetivo), não busca de palavras-chave no
    texto — esta produzia falsos positivos com menções negadas (ex.: "não
    houve contaminação"); a avaliação de contaminação fica a cargo do LLM.
    Função pura — testável sem chamar a API.
    """
    triggers: list[str] = []
    exposure = claim.max_potential_exposure or 0
    if exposure >= ESCALATION_EXPOSURE_THRESHOLD_USD:
        triggers.append("exposição financeira acima do limiar (backstop)")
    return triggers


def check_escalation(state: GraphState) -> dict[str, EscalationCheck]:
    escalation = cast(
        EscalationCheck, ESCALATION_CHECK_CHAIN.invoke({"message": state["message"]})
    )
    backstop = deterministic_escalation_triggers(state["claim_data"])
    if backstop:
        escalation = escalation.model_copy(
            update={
                "requires_escalation": True,
                "escalation_triggers": [
                    *escalation.escalation_triggers,
                    *backstop,
                ],
            }
        )
    return {"escalation": escalation}


def route_by_escalation(
    state: GraphState,
) -> Literal["escalate_to_trading_desk", "prepare_qualification"]:
    if state["escalation"].requires_escalation:
        return "escalate_to_trading_desk"
    return "prepare_qualification"


def escalate_to_trading_desk(state: GraphState) -> dict[str, str]:
    actions.notify_trading_desk(
        state["claim_data"], state["escalation"].escalation_triggers
    )
    return {"resolution": "escalated_to_trading_desk"}


def prepare_qualification(state: GraphState) -> dict[str, Any]:
    return {"pending_questions": list(QUALIFYING_QUESTIONS), "qualifying_answers": {}}


def ask_next_qualifying_question(state: GraphState) -> dict[str, Any]:
    pending = state["pending_questions"]
    question = pending[0]
    answer = cast(
        BinaryAnswer,
        BINARY_QUESTION_CHAIN.invoke(
            {"question": question, "message": state["message"]}
        ),
    )
    actions.log_qualification_answer(question, answer)
    return {
        "pending_questions": pending[1:],
        "qualifying_answers": {**state["qualifying_answers"], question: answer},
    }


def has_pending_questions(
    state: GraphState,
) -> Literal["ask_next_qualifying_question", "create_arbitration_ticket"]:
    if state["pending_questions"]:
        return "ask_next_qualifying_question"
    return "create_arbitration_ticket"


def create_arbitration_ticket(state: GraphState) -> dict[str, str]:
    actions.create_arbitration_ticket(state["claim_data"])
    return {"resolution": "arbitration_ticket_created"}


workflow = StateGraph(GraphState)
workflow.add_node("parse_claim", parse_claim)
workflow.add_node("check_escalation", check_escalation)
workflow.add_node("escalate_to_trading_desk", escalate_to_trading_desk)
workflow.add_node("prepare_qualification", prepare_qualification)
workflow.add_node("ask_next_qualifying_question", ask_next_qualifying_question)
workflow.add_node("create_arbitration_ticket", create_arbitration_ticket)

workflow.add_edge(START, "parse_claim")
workflow.add_edge("parse_claim", "check_escalation")
workflow.add_conditional_edges(
    "check_escalation",
    route_by_escalation,
    {
        "escalate_to_trading_desk": "escalate_to_trading_desk",
        "prepare_qualification": "prepare_qualification",
    },
)
workflow.add_edge("prepare_qualification", "ask_next_qualifying_question")
workflow.add_conditional_edges(
    "ask_next_qualifying_question",
    has_pending_questions,
    {
        "ask_next_qualifying_question": "ask_next_qualifying_question",
        "create_arbitration_ticket": "create_arbitration_ticket",
    },
)
workflow.add_edge("escalate_to_trading_desk", END)
workflow.add_edge("create_arbitration_ticket", END)

CLAIM_EXTRACTION_GRAPH = workflow.compile()
