.PHONY: help lint format check test install clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with Python 3.13
	python3.13 -m pip install --break-system-packages -e .

install-dev: ## Install development dependencies
	python3.13 -m pip install --break-system-packages "pytest>=7.4.0" "pytest-asyncio>=0.21.0" "mypy>=1.7.0" "ruff>=0.1.0" "black>=23.0.0"

lint: ## Run all linting checks
	python3.13 lint.py check

lint-fix: ## Run linting with automatic fixes
	python3.13 lint.py format

ruff: ## Run ruff linter
	python3.13 -m ruff check dawnai examples

ruff-fix: ## Run ruff with automatic fixes
	python3.13 -m ruff check --fix dawnai examples

black: ## Check code formatting with black
	python3.13 -m black --check dawnai examples

black-fix: ## Format code with black
	python3.13 -m black dawnai examples

mypy: ## Run mypy type checking
	python3.13 -m mypy dawnai examples

test: ## Run tests
	python3.13 -m pytest tests/ -v

clean: ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

format: lint-fix ## Format all code (alias for lint-fix)

check: lint ## Check all code (alias for lint)

all: install-dev lint test ## Install, lint, and test everything
