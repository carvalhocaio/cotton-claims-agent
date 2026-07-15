"""
Chain de respostas binárias (sim/não): usada para responder perguntas de
qualificação sobre uma reclamação, com base na mensagem original.

Independente de `claim_extraction.py` e `escalation_check.py` - recebe
qualquer pergunta e qualquer texto, sem conhecer a estrutura de nenhuma
das outras chains. É essa independência que permite reutilizá-la dentro
do ciclo de follow-up do ticket de arbitragem.
"""

from typing import Literal

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

load_dotenv()

class BinaryAnswer(BaseModel):
    answer: bool = Field(
        description="A resposta sim/não para a pergunta, com base apenas na mensagem"
    )
    confidence: Literal["alta", "média", "baixa"] = Field(
        description="""Confiança na resposta. 'baixa' quando a mensagem não
        traz informação suficiente para responder com segurança"""
    )
    justification: str = Field(
        description="Justificativa breve (1 frase) citando o trecho relevante de mensagem"
    )


binary_question_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Responda à pergunta fornecida com base exclusivamente no conteúdo
            da mensagem enviada. Se a mensagem não contiver informação
            suficiente para responder com segurança, retorne a resposta
            mais provável e marque a confiança como 'baixa'.
            """,
        ),
        (
            "human",
            """
            Pergunta: {question}

            Mensagem:
            {message}
            """,
        ),
    ]
)

binary_question_model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

BINARY_QUESTION_CHAIN = (
    binary_question_prompt
    | binary_question_model.with_structured_output(BinaryAnswer)
)
