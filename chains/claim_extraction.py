from datetime import date, datetime

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field, computed_field

load_dotenv()

class HVIFindings(BaseModel):
    """Parâmetros de HVI mencionados na reclamação, quando presentes."""

    micronaire: float | None = Field(
        default=None,
        description="Valor de micronaire reportado na reclamação, se mencionado",
    )
    staple_length: str | None = Field(
        default=None,
        description="""Comprimento de fibra (staple) reportado na reclamação,
        se mencionado (ex: '35' ou '1 3/32\"')""",
    )
    strength: float | None = Field(
        default=None,
        description="Resistência da fibra em g/tex, se mencionada",
    )
    uniformity: float | None = Field(
        default=None,
        description="Índice de uniformidade, se mencionado",
    )
    color_grade: str | None = Field(
        default=None,
        description="Grau de cor reportado, se mencionado",
    )
    leaf_grade: str | None = Field(
        default=None,
        description="Grau de folha (leaf grade) reportado, se mencionado",
    )


class ClaimExtract(BaseModel):
    claim_date_str: str | None = Field(
        default=None,
        exclude=True,
        repr=False,
        description="A data da reclamação (se houver), reformatada para YYYY-mm-dd",
    )
    claiming_party: str | None = Field(
        default=None,
        description="""Nome da entidade que está reclamando (comprador, fiação,
        algodoeira), se presente""",
    )
    contact_phone: str | None = Field(
        default=None,
        description="Telefone de contato da parte reclamante, se presente",
    )
    contact_email: str | None = Field(
        default=None,
        description="E-mail de contato da parte reclamante, se presente",
    )
    contract_or_lot_reference: str | None = Field(
        default=None,
        description="""Número de contrato e/ou identificador do lote/embarque
        mencionado na reclamação""",
    )
    origin_location: str | None = Field(
        default=None,
        description="""Origem do algodão (fazenda, algodoeira, região), se
        mencionada. Use o texto completo se possível.""",
    )
    claim_type: str | None = Field(
        default=None,
        description="""Tipo(s) de problema reportado: contaminação, desvio de
        HVI/qualidade, divergência de peso, reclamação de fibra, atraso de
        embarque, etc.""",
    )
    hvi_findings: HVIFindings | None = Field(
        default=None,
        description="Parâmetros de HVI estruturados mencionados na reclamação, se houver",
    )
    required_action: str | None = Field(
        default=None,
        description="Ação corretiva solicitada pela parte reclamante",
    )
    response_deadline_str: str | None = Field(
        default=None,
        exclude=True,
        repr=False,
        description="O prazo de resposta exigido (se houver), reformatado para YYYY-mm-dd",
    )
    max_potential_exposure: float | None = Field(
        default=None,
        description="""Exposição financeira máxima mencionada na reclamação
        (em USD, salvo indicação contrária), se houver""",
    )

    @staticmethod
    def _convert_string_to_date(date_str: str | None) -> date | None:
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception:
            return None

    @computed_field
    @property
    def claim_date(self) -> date | None:
        return self._convert_string_to_date(self.claim_date_str)

    @computed_field
    @property
    def response_deadline(self) -> date | None:
        return self._convert_string_to_date(self.response_deadline_str)


claim_parse_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Extraia da mensagem: data da reclamação, nome da parte
            reclamante, telefone e e-mail de contato, referência de
            contrato/lote, localização de origem, tipo(s) de reclamação,
            parâmetros de HVI mencionados (micronaire, staple, strength,
            uniformity, color grade, leaf grade), ação corretiva
            solicitada, prazo de resposta e exposição financeira máxima.
            Se algum campo não estiver presente, não o preencha. Tente
            converter datas para o formato YYYY-mm-dd.
            """,
        ),
        (
            "human",
            "Aqui está a mensagem:\n\n{message}",
        ),
    ]
)

claim_parser_model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

CLAIM_PARSER_CHAIN = (
    claim_parse_prompt
    | claim_parser_model.with_structured_output(ClaimExtract)
)
