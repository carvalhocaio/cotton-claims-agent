.PHONY: help install run run-app test test-integration test-all lint lint-fix format format-check audit ci clean

help: ## Lista os comandos disponíveis
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Instala as dependências do projeto (incluindo extras e dev)
	uv sync --all-extras --dev

run: ## Roda o agente em modo demo (uso: make run-message MSG="..." para mensagem livre)
	uv run python main.py --demo

run-app: ## Roda a interface Streamlit
	uv run streamlit run app.py

test: ## Roda os testes unitários (exclui integration por padrão)
	uv run pytest

test-integration: ## Roda os testes de integração (chamam a API real do Gemini)
	uv run pytest -m integration

test-all: ## Roda todos os testes, unitários e de integração
	uv run pytest -m ""

lint: ## Verifica o código com ruff
	uv run ruff check

lint-fix: ## Verifica e corrige automaticamente com ruff
	uv run ruff check --fix

format: ## Formata o código com ruff
	uv run ruff format

format-check: ## Verifica a formatação sem alterar arquivos
	uv run ruff format --check

audit: ## Audita dependências em busca de vulnerabilidades
	uv run pip-audit

ci: lint format-check audit test ## Roda o mesmo pipeline da CI localmente

clean: ## Remove caches (.ruff_cache, .pytest_cache, __pycache__)
	rm -rf .ruff_cache .pytest_cache
	find . -type d -name '__pycache__' -exec rm -rf {} +
