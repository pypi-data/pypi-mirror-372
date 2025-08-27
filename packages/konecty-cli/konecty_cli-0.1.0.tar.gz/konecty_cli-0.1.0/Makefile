.PHONY: help install install-dev test test-cov format lint type-check clean build

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package mode
	uv pip install -e .

install-dev: ## Install development dependencies
	uv sync --extra dev

test: ## Run tests
	uv run pytest

test-cov: ## Run tests with coverage
	uv run pytest --cov=konecty_cli --cov-report=html --cov-report=term-missing

format: ## Format code with black and isort
	uv run black .
	uv run isort .

lint: ## Run flake8 linter
	uv run flake8 konecty_cli/ tests/

type-check: ## Run mypy type checker
	uv run mypy .

check: format lint type-check test ## Run all checks (format, lint, type-check, test)

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .mypy_cache/
	rm -rf .pytest_cache/

build: ## Build the package
	uv build

run: ## Run the CLI
	uv run konecty-cli --help
