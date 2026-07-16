"""
Ações de negócio (efeitos colaterais) do fluxo de triagem.

Concentra num só lugar todo o I/O que antes ficava embutido como `print`
dentro dos nós do grafo e das tools do agente. Separar essas ações da
lógica de orquestração restaura o Single Responsibility Principle: os nós
decidem *o que* fazer, este módulo decide *como* comunicar/registrar.

Hoje as ações apenas escrevem no `logging`; trocá-las por integrações
reais (e-mail, ticket, fila) é uma mudança local, sem tocar nos grafos.
"""

import logging
import re

from chains.binary_questions import BinaryAnswer
from chains.claim_extraction import ClaimExtract

logger = logging.getLogger(__name__)

_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")


def _clean(value: object) -> str:
    """Neutraliza quebras de linha e caracteres de controle em texto vindo
    do LLM/remetente antes de ir para o log (CS-1: impede forja de linhas
    de log injetando `\\n[TICKET] ...` em campos como o nome do reclamante)."""
    return _CONTROL_CHARS.sub(" ", str(value))


def _claim_summary(claim: ClaimExtract) -> str:
    """Resumo curto de identificação da reclamação, reutilizado nas
    mensagens de escalonamento e de abertura de ticket (DRY)."""
    return (
        f"reclamante: {_clean(claim.claiming_party)}, "
        f"contrato/lote: {_clean(claim.contract_or_lot_reference)}"
    )


def notify_trading_desk(claim: ClaimExtract, triggers: list[str]) -> None:
    """Notifica a mesa de trading sobre uma reclamação escalada."""
    exposure = f"{claim.max_potential_exposure or 0:,.2f}"
    logger.info(
        "[ESCALAÇÃO] Notificando mesa de trading — %s, "
        "exposição estimada: USD %s, motivos: %s.",
        _claim_summary(claim),
        exposure,
        _clean(", ".join(triggers)),
    )


def log_qualification_answer(question: str, answer: BinaryAnswer) -> None:
    """Registra a resposta de uma pergunta do checklist de qualificação."""
    logger.info(
        "[QUALIFICAÇÃO] %s -> %s (%s)",
        question,
        answer.answer,
        answer.confidence,
    )


def create_arbitration_ticket(claim: ClaimExtract) -> None:
    """Abre um ticket de arbitragem para a reclamação qualificada."""
    logger.info(
        "[TICKET] Ticket de arbitragem aberto — %s, tipo: %s.",
        _claim_summary(claim),
        _clean(claim.claim_type),
    )


def forward_to_department(department: str, reason: str) -> None:
    """Encaminha a mensagem para outro departamento interno."""
    logger.info(
        "[ENCAMINHAMENTO] Mensagem enviada para %s. Motivo: %s",
        _clean(department),
        _clean(reason),
    )
