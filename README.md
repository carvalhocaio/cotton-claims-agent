# cotton-claims-agent

Agente de triagem de correspondência para uma trading de algodão,
construído com [LangGraph](https://langchain-ai.github.io/langgraph/),
como projeto de estudo baseado no artigo
[LangGraph: Build Stateful AI Agents in Python](https://realpython.com/langgraph-python/)
da Real Python — adaptando o exemplo original (extração de avisos
regulatórios por e-mail) para o domínio de reclamações de qualidade,
contaminação e divergência de embarque no comércio de algodão.

## Cenário

A Cerrado Cotton Trading Co. recebe e-mails variados: reclamações de
compradores sobre contaminação ou desvio de HVI, faturas de transporte,
dúvidas comerciais, divergências de peso de algodoeiras parceiras. O
agente decide o que é reclamação (e trata com o rigor que o caso exige)
e o que deve ser encaminhado para outro departamento.

## Conceitos do LangGraph, mapeados por fase

| Fase | Conceito do artigo | Implementação aqui |
|---|---|---|
| 1 | Chains + saída estruturada (Pydantic) | `chains/claim_extraction.py`, `chains/escalation_check.py`, `chains/binary_questions.py` |
| 2 | `StateGraph` linear | `parse_claim` → `check_escalation` em `graphs/claim_extraction.py` |
| 3 | Aresta condicional (`add_conditional_edges`) | Escalonamento imediato vs. checklist de qualificação |
| 4 | Ciclo (node apontando para si mesmo) | `ask_next_qualifying_question`, até a lista de pendências esvaziar |
| 5 | Agente com `MessagesState` + `ToolNode` | `graphs/claims_agent.py`, decidindo entre `triage_claim` e `forward_to_department` |

## Estrutura

```
.
├── chains/                  # unidades de LLM independentes entre si
│   ├── claim_extraction.py  # ClaimExtract + extração estruturada
│   ├── escalation_check.py  # decide se precisa escalonamento imediato
│   └── binary_questions.py  # perguntas sim/não usadas no ciclo (Fase 4)
├── graphs/
│   ├── claim_extraction.py  # StateGraph das Fases 2–4
│   └── claims_agent.py      # agente completo (Fase 5)
├── llm.py                   # factory única do modelo (get_model)
├── actions.py               # ações de negócio (efeitos colaterais via logging)
├── example_claims.py        # mensagens de exemplo, sem dependências internas
├── main.py                  # ponto de entrada (CLI)
├── app.py                   # interface Streamlit opcional (demonstração)
├── .github/workflows/ci.yml # lint + testes no GitHub Actions
└── tests/
    ├── unit/                # lógica determinística, sem chamadas de API
    └── integration/         # chains, grafo e agente, com marker @pytest.mark.integration
```

Princípio seguido em todo o projeto: nenhum arquivo depende de outro que
ainda não existia no momento em que foi escrito. `chains/` não sabe da
existência de `graphs/`; as três chains são independentes entre si;
`graphs/claim_extraction.py` depende só das chains; `graphs/claims_agent.py`
é o único módulo que depende de outro grafo.

Dois módulos transversais concentram responsabilidades que antes ficavam
espalhadas:

- **`llm.py`** — factory `get_model()`, ponto único de configuração e
  troca do provedor de LLM (nome do modelo, temperatura e chave de API).
  As chains e o agente pedem o modelo por aqui, sem instanciar o cliente
  diretamente (DRY + Dependency Inversion).
- **`actions.py`** — ações de negócio (notificar a mesa de trading, abrir
  ticket, encaminhar para outro departamento, registrar respostas do
  checklist). Os nós do grafo decidem *o que* fazer; este módulo decide
  *como* comunicar, hoje via `logging`. Trocar por integrações reais
  (e-mail, ticket, fila) é uma mudança local, sem tocar nos grafos.

## Setup

```bash
uv sync
echo "GEMINI_API_KEY=sua-chave-aqui" >> .env
```

A chave é lida de `GEMINI_API_KEY` (com `GOOGLE_API_KEY` como fallback) e
passada explicitamente ao cliente em `llm.py`.

## Uso

```bash
# CLI
uv run python main.py --demo
uv run python main.py --message "texto de uma reclamação ou e-mail qualquer"

# Interface Streamlit (extra opcional: uv sync --extra app)
uv run streamlit run app.py
```

## Testes

```bash
uv run pytest                  # só unitários (rápido, sem rede, sem custo)
uv run pytest -m integration   # chama a API do Gemini de verdade
uv run pytest -m ""            # roda tudo
```

## Qualidade de código

Lint e formatação com [Ruff](https://docs.astral.sh/ruff/):

```bash
uv run ruff check              # lint
uv run ruff check --fix        # lint + correções automáticas
uv run ruff format            # formatação
```

O [GitHub Actions](.github/workflows/ci.yml) roda `ruff check`,
`ruff format --check` e os testes unitários a cada push/PR na `main`. Os
testes unitários não chamam a API, mas usam uma chave fictícia no CI
porque os modelos são construídos no import.

## Limitações conhecidas

- `response_deadline` só é preenchido quando a mensagem menciona uma
  data absoluta. Prazos relativos ("5 dias úteis a partir desta data")
  não são resolvidos — isso exigiria uma função determinística de
  cálculo de dias úteis, deliberadamente fora do escopo do LLM.
- O checklist de qualificação (`QUALIFYING_QUESTIONS`) é fixo; não se
  adapta ao tipo de reclamação.
- As ações de negócio em `actions.py` (notificar a mesa, abrir ticket,
  encaminhar) são simuladas via `logging` — ainda não integram com um
  sistema real de tickets ou e-mail.

## Créditos

Estrutura de código inspirada no tutorial
[LangGraph: Build Stateful AI Agents in Python](https://realpython.com/langgraph-python/),
adaptado para o domínio de comércio de algodão.
