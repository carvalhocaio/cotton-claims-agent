"""
Interface Streamlit para o cotton-claims-agent.

Camada de demonstração, opcional - não faz parte do core do projeto
(chains/, graphs/, tests/). Só consome CLAIMS_AGENT, do mesmo jeito
que main.py já faz.

Uso:
    uv run streamlit run app.py
"""

from typing import Any

import streamlit as st
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage

from example_claims import CLAIMS
from graphs.claims_agent import CLAIMS_AGENT

TOOL_LABELS = {
    "triage_claim": "Triagem de reclamação",
    "forward_to_department": "Encaminhado para outro departamento",
}

EXAMPLE_LABELS = {
    0: "Exemplo 0 — Contaminação + desvio de HVI (deve escalar)",
    1: "Exemplo 1 — Fatura de frete (não é reclamação)",
    2: "Exemplo 2 — Reclamação informal, sem vocabulário técnico",
    3: "Exemplo 3 — Divergência de peso (checklist, sem escalonar)",
}


def extract_tool_call_and_output(
    messages: list[BaseMessage],
) -> tuple[str | None, str | None]:
    """Extrai o nome da tool chamada pelo agente e o texto que ela
    retornou. Função pura, sem efeitos colaterais — isolada do resto
    da UI para poder ser testada isoladamente, se um dia fizer sentido.
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

    st.markdown("**Resumo do agente:**")
    st.write(final_summary)


def main() -> None:
    st.set_page_config(page_title="Cotton Claims Agent")
    st.title("Cotton Claims Agent")
    st.caption(
        "Triagem de correspondência de uma trading de algodão — construído "
        "com LangGraph. O agente decide sozinho: reclamação de qualidade "
        "vira triagem completa, o resto é encaminhado para o departamento certo."
    )

    example_choice = st.selectbox(
        "Testar com um exemplo pronto (opcional)",
        options=[None, *EXAMPLE_LABELS.keys()],
        format_func=lambda i: "- selecione -" if i is None else EXAMPLE_LABELS[i],
    )

    default_text = CLAIMS[example_choice] if example_choice is not None else ""
    message = st.text_area(
        "Cole aqui o texto do e-mail ou reclamação",
        value=default_text,
        height=200,
    )

    if st.button("Rodar triagem", type="primary", disabled=not message.strip()):
        with st.spinner("Agente avaliando a mensagem..."):
            try:
                result = CLAIMS_AGENT.invoke(
                    {"messages": [HumanMessage(content=message)]}
                )
            except Exception as exc:
                st.error(f"Falha ao processar a mensagem: {exc}")
                return
        render_result(result)


if __name__ == "__main__":
    main()
