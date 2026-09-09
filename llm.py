"""
Single factory for the language model used throughout the project.

Centralizes the model name, temperature, API key, and environment
variable loading (`.env`) in one place. The chains and the agent request
the model from here instead of instantiating `ChatGoogleGenerativeAI`
directly — this removes duplication (DRY) and creates a single
injection/swap point for the LLM provider (Dependency Inversion).
"""

import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

MODEL_NAME = "gemini-2.5-flash"
"""Default model for the project. Single source of truth — changing it
here changes it across all chains and the agent."""

TEMPERATURE = 0
"""Temperature 0 for deterministic responses in extraction/routing."""

API_KEY_ENV_VAR = "GEMINI_API_KEY"
"""Canonical name of the environment variable holding the API key. Keeps
`GOOGLE_API_KEY` as a fallback for compatibility with the
`langchain-google-genai` default."""


def _resolve_api_key() -> str | None:
    return os.environ.get(API_KEY_ENV_VAR) or os.environ.get("GOOGLE_API_KEY")


def get_model(
    *,
    model: str = MODEL_NAME,
    temperature: float = TEMPERATURE,
) -> ChatGoogleGenerativeAI:
    """Returns a configured model, ready to receive
    `.with_structured_output(...)` or `.bind_tools(...)` depending on
    usage.

    The key is read from `GEMINI_API_KEY` (or `GOOGLE_API_KEY` as a
    fallback) and passed explicitly, so the name used in `.env`/README is
    the same one effectively consumed by the client.
    """
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        google_api_key=_resolve_api_key(),
    )
