"""
Agente de correspondência: recebe qualquer mensagem recebida pela
trading e decide se ela é uma reclamação de qualidade/peso/embarque
(roteia para o grafo de triagem) ou outra coisa (encaminha para o
departamento correto).

Depende de graphs.claim_extraction - este é o módulo de mais alto nível
do projeto, o único que expõe o grafo de triagem completo como tool.
"""

from typing import cast

from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from graphs.claim_extraction import CLAIM_EXTRACTION_GRAPH, GraphState


@tool
def triage_claim(message: str) -> str:
    """Executa o fluxo completo de triagem para uma reclamação de
    qualidade, contaminação, desvio de HVI, divergência de peso ou
    embarque de algodão: extrai os dados, decide se precisa de
    escalonamento imediato e, se não precisar, roda o checklist de
    qualificação antes de abrir um ticket de arbitragem. Use esta tool
    sempre que a mensagem for uma reclamação sobre um lote ou embarque."""
    result = CLAIM_EXTRACTION_GRAPH.invoke(cast(GraphState, {"message": message}))
    claim = result["claim_data"]
    return (
        f"Triagem concluída. Resultado: {result['resolution']}. "
        f"Reclamante: {claim.claiming_party}. "
        f"Contrato/lote: {claim.contract_or_lot_reference}. "
        f"Tipo: {claim.claim_type}."
    )

@tool
def forward_to_department(department: str, reason: str) -> str:
    """Encaminha a mensagem atual para o departamento interno correto
    quando ela NÃO é uma reclamação de qualidade, contaminação, HVI ou
    peso (ex: fatura -> 'financeiro', dúvida de transporte ->
    'logística', negociação de preço -> 'comercial'). Informe o
    departamento e o motivo do encaminhamento."""
    print(f"[ENCAMINHAMENTO] Mensagem enviada para {department}. Motivo: {reason}")
    return f"Mensagem encaminhada para o departamento: {department}."

TOOLS = [triage_claim, forward_to_department]

AGENT_SYSTEM_PROMPT = """
Você é o assistente de triagem de correspondência da Cerrado Cotton
Trading Co. Toda mensagem recebida precisa ser roteada corretamente:

- Se for uma reclamação sobre qualidade, contaminação, desvio de HVI,
  divergência de peso ou embarque de algodão: use a tool triage_claim.
- Se for qualquer outro assunto (fatura, dúvida comercial, logística
  etc.): use forward_to_department, indicando o departamento correto.

Use exatamente uma tool por mensagem recebida. Depois do resultado da
tool, responda com um resumo breve em português do que foi feito.
"""

agent_model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0).bind_tools(
    TOOLS
)


def call_model(state: MessagesState) -> dict:
    messages = state["messages"]
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=AGENT_SYSTEM_PROMPT), *messages]
    response = agent_model.invoke(messages)
    return {"messages": [response]}


def should_continue(state: MessagesState) -> str:
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END


agent_workflow = StateGraph(MessagesState)
agent_workflow.add_node("call_model", call_model)
agent_workflow.add_node("tools", ToolNode(TOOLS))

agent_workflow.add_edge(START, "call_model")
agent_workflow.add_conditional_edges(
    "call_model", should_continue, {"tools": "tools", END: END}
)
agent_workflow.add_edge("tools", "call_model")

CLAIMS_AGENT = agent_workflow.compile()
