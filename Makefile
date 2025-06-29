.PHONY: help test test-unit test-integration test-coverage test-fast install install-dev clean lint format setup run

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install all dependencies including testing"
	@echo "  setup        - Set up development environment"
	@echo "  test         - Run all tests"
	@echo "  test-unit    - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-coverage - Run tests with coverage report"
	@echo "  test-fast    - Run tests without coverage (faster)"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code"
	@echo "  clean        - Clean up temporary files"
	@echo "  run          - Start the application"

# Installation targets
install:
	pip install -r requirements.txt

install-dev: install
	pip install pytest pytest-asyncio pytest-cov pytest-mock coverage unittest-mock responses httpx

setup: install-dev
	@echo "Development environment setup complete!"
	@echo "Run 'make test' to verify everything is working."

# Testing targets
test:
	pytest

test-unit:
	pytest -m "unit or not integration"

test-integration:
	pytest -m "integration"

test-coverage:
	pytest --cov=backend --cov=app --cov-report=html:htmlcov --cov-report=term-missing --cov-fail-under=80

test-fast:
	pytest --no-cov -x

# Code quality targets
lint:
	@echo "Linting would go here (flake8, pylint, etc.)"
	@echo "Currently using IDE linting"

format:
	@echo "Code formatting would go here (black, autopep8, etc.)"
	@echo "Currently using IDE formatting"

# Utility targets
clean:
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete

run:
	./run.sh

# Coverage targets
coverage-html: test-coverage
	@echo "Coverage report generated in htmlcov/index.html"
	@command -v open >/dev/null 2>&1 && open htmlcov/index.html || echo "Open htmlcov/index.html in your browser"

coverage-report:
	coverage report -m

# Test specific components
test-document-processor:
	pytest tests/test_document_processor.py -v

test-groq-service:
	pytest tests/test_groq_service.py -v

test-milvus-service:
	pytest tests/test_milvus_service.py -v

test-app-integration:
	pytest tests/test_app_integration.py -v

# Development helpers
test-watch:
	@echo "File watching not implemented. Run 'make test' manually after changes."

test-debug:
	pytest -v -s --tb=long

test-failed:
	pytest --lf -v

# Environment setup
env-check:
	@echo "Checking environment..."
	@python -c "import sys; print(f'Python: {sys.version}')"
	@python -c "import pytest; print(f'Pytest: {pytest.__version__}')"
	@echo "Environment check complete!"

# Quick development cycle
dev: clean test-fast
	@echo "Quick development cycle complete!"

# Full CI pipeline simulation
ci: clean install-dev test-coverage
	@echo "CI pipeline simulation complete!" 