.PHONY: venv install demo test clean help

# Default Python executable
PYTHON := python3
VENV := venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "RegimeSplit Development Commands"
	@echo "================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

venv: ## Create virtual environment
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created at: $(VENV)/"
	@echo "To activate: source $(VENV)/bin/activate"

install: ## Install package in development mode with dependencies
	@echo "Installing package in development mode..."
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .
	@echo "Package installed successfully!"

install-dev: install ## Install development dependencies
	@echo "Installing development dependencies..."
	$(VENV_PIP) install pytest pytest-cov black flake8 mypy
	@echo "Development dependencies installed!"

demo: ## Run synthetic data generation and regime splitting demo
	@echo "Running synthetic data generation demo..."
	$(PYTHON) examples/synth_make.py
	@echo "Running regime splitting analysis..."
	regimesplit folds --config.csv-path examples/series.csv --config.ret-col ret --config.n-splits 5 --config.embargo 15 --config.purge 5 --config.vol-window 60 --config.k-regimes 3 --config.method quantiles --config.output-dir out/
	@echo "Demo completed! Check the out/ directory for results."

test: ## Run test suite
	@echo "Running test suite..."
	$(PYTHON) -m pytest -q
	@echo "Tests completed!"

test-cov: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Run 'make install-dev' first."; \
		exit 1; \
	fi
	$(VENV_PYTHON) -m pytest tests/ -v --cov=src/regimesplit --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/"

lint: ## Run code linting
	@echo "Running linting checks..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Run 'make install-dev' first."; \
		exit 1; \
	fi
	$(VENV_PYTHON) -m flake8 src/ tests/ examples/
	@echo "Linting completed!"

format: ## Format code with black
	@echo "Formatting code with black..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Run 'make install-dev' first."; \
		exit 1; \
	fi
	$(VENV_PYTHON) -m black src/ tests/ examples/
	@echo "Code formatting completed!"

type-check: ## Run type checking with mypy
	@echo "Running type checking..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Run 'make install-dev' first."; \
		exit 1; \
	fi
	$(VENV_PYTHON) -m mypy src/regimesplit --ignore-missing-imports
	@echo "Type checking completed!"

clean: ## Clean up generated files and directories
	@echo "Cleaning up..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf output/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Cleanup completed!"

clean-venv: clean ## Remove virtual environment and clean up
	@echo "Removing virtual environment..."
	rm -rf $(VENV)/
	@echo "Virtual environment removed!"

build: ## Build package distributions
	@echo "Building package..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi
	$(VENV_PIP) install --upgrade build
	$(VENV_PYTHON) -m build
	@echo "Package built! Check dist/ directory."

check: lint type-check test ## Run all quality checks (lint, type-check, test)
	@echo "All quality checks completed!"

setup: install install-dev ## Complete development setup (create venv, install package and dev deps)
	@echo "Development environment setup completed!"
	@echo "To get started:"
	@echo "  1. Activate environment: source $(VENV)/bin/activate"
	@echo "  2. Run demo: make demo"
	@echo "  3. Run tests: make test"

# Development workflow targets
dev: format lint type-check test ## Full development workflow (format, lint, type-check, test)
	@echo "Development workflow completed!"

# Quick targets for common operations
quick-test: ## Run tests without full setup check
	@$(VENV_PYTHON) -m pytest tests/ -x --tb=short

quick-demo: ## Run demo without full setup check
	@$(VENV_PYTHON) examples/synth_make.py

# Information targets
info: ## Show project information
	@echo "RegimeSplit Project Information"
	@echo "=============================="
	@echo "Project: regimesplit"
	@echo "Version: 0.1.0"
	@echo "Python: $(PYTHON)"
	@echo "Virtual env: $(VENV)/"
	@echo ""
	@echo "Directory structure:"
	@find . -name "*.py" | head -10 | sed 's/^/  /'
	@echo "  ..."