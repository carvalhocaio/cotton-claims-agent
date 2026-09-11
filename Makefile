.PHONY: help install run run-app test test-integration test-all lint lint-fix format format-check audit precommit-install precommit ci clean

help: ## Lists the available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Installs the project dependencies (including extras and dev)
	uv sync --all-extras --dev

run: ## Runs the agent in demo mode (use: make run-message MSG="..." for a free-form message)
	uv run python main.py --demo

run-app: ## Runs the Streamlit interface
	uv run streamlit run app.py

test: ## Runs the unit tests (excludes integration by default)
	uv run pytest

test-integration: ## Runs the integration tests (calls the real Gemini API)
	uv run pytest -m integration

test-all: ## Runs all tests, unit and integration
	uv run pytest -m ""

lint: ## Checks the code with ruff
	uv run ruff check

lint-fix: ## Checks and automatically fixes with ruff
	uv run ruff check --fix

format: ## Formats the code with ruff
	uv run ruff format

format-check: ## Checks formatting without modifying files
	uv run ruff format --check

audit: ## Audits dependencies for vulnerabilities
	uv run pip-audit

precommit-install: ## Installs the pre-commit hook in the local repository
	uv run pre-commit install

precommit: ## Runs all pre-commit hooks against all files
	uv run pre-commit run --all-files

ci: lint format-check audit test ## Runs the same pipeline as CI locally

clean: ## Removes caches (.ruff_cache, .pytest_cache, __pycache__)
	rm -rf .ruff_cache .pytest_cache
	find . -type d -name '__pycache__' -exec rm -rf {} +
