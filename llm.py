"""
Factory única do modelo de linguagem usado por todo o projeto.

Centraliza o nome do modelo, a temperatura e o carregamento das variáveis
de ambiente (`.env`) num só lugar. As chains e o agente pedem o modelo por
aqui em vez de instanciar `ChatGoogleGenerativeAI` diretamente — isso
remove a duplicação (DRY) e cria um único ponto de injeção/troca do
provedor de LLM (Dependency Inversion).
"""

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

MODEL_NAME = "gemini-2.5-flash"
"""Modelo padrão do projeto. Única fonte de verdade — trocar aqui troca
em todas as chains e no agente."""

TEMPERATURE = 0
"""Temperatura 0 para respostas determinísticas na extração/roteamento."""


def get_model(
    *,
    model: str = MODEL_NAME,
    temperature: float = TEMPERATURE,
) -> ChatGoogleGenerativeAI:
    """Retorna um modelo configurado, pronto para receber
    `.with_structured_output(...)` ou `.bind_tools(...)` conforme o uso."""
    return ChatGoogleGenerativeAI(model=model, temperature=temperature)
