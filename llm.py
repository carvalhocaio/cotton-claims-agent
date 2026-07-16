"""
Factory única do modelo de linguagem usado por todo o projeto.

Centraliza o nome do modelo, a temperatura, a chave de API e o
carregamento das variáveis de ambiente (`.env`) num só lugar. As chains e
o agente pedem o modelo por aqui em vez de instanciar
`ChatGoogleGenerativeAI` diretamente — isso remove a duplicação (DRY) e
cria um único ponto de injeção/troca do provedor de LLM (Dependency
Inversion).
"""

import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

MODEL_NAME = "gemini-2.5-flash"
"""Modelo padrão do projeto. Única fonte de verdade — trocar aqui troca
em todas as chains e no agente."""

TEMPERATURE = 0
"""Temperatura 0 para respostas determinísticas na extração/roteamento."""

API_KEY_ENV_VAR = "GEMINI_API_KEY"
"""Nome canônico da variável de ambiente com a chave da API. Mantém
`GOOGLE_API_KEY` como fallback para compatibilidade com o padrão do
`langchain-google-genai`."""


def _resolve_api_key() -> str | None:
    return os.environ.get(API_KEY_ENV_VAR) or os.environ.get("GOOGLE_API_KEY")


def get_model(
    *,
    model: str = MODEL_NAME,
    temperature: float = TEMPERATURE,
) -> ChatGoogleGenerativeAI:
    """Retorna um modelo configurado, pronto para receber
    `.with_structured_output(...)` ou `.bind_tools(...)` conforme o uso.

    A chave é lida de `GEMINI_API_KEY` (ou `GOOGLE_API_KEY` como fallback)
    e passada explicitamente, para que o nome usado no `.env`/README seja
    o mesmo efetivamente consumido pelo cliente.
    """
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        google_api_key=_resolve_api_key(),
    )
