# Makefile for ghvault development

.PHONY: help install install-dev test test-unit test-integration test-cov clean lint format type-check pre-commit run-example

# Default target
help:
	@echo "Available targets:"
	@echo "  install       - Install package in development mode"
	@echo "  install-dev   - Install with development dependencies"
	@echo "  test          - Run all tests"
	@echo "  test-unit     - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-cov      - Run tests with coverage report"
	@echo "  lint          - Run linting (flake8)"
	@echo "  format        - Format code (black + isort)"
	@echo "  type-check    - Run type checking (mypy)"
	@echo "  pre-commit    - Run all pre-commit checks"
	@echo "  clean         - Clean up build artifacts"
	@echo "  run-example   - Run example commands (requires GH_TOKEN)"

# Installation targets
install:
	uv sync

install-dev:
	uv sync --extra dev --extra test

# Test targets
test:
	pytest

test-unit:
	pytest -m "unit or not integration"

test-integration:
	pytest -m integration

test-cov:
	pytest --cov=ghvault --cov-report=html --cov-report=term-missing

test-verbose:
	pytest -v -s

test-fast:
	pytest -x --ff

# Code quality targets
lint:
	flake8 ghvault tests

format:
	black ghvault tests
	isort ghvault tests

type-check:
	mypy ghvault

pre-commit: format lint type-check test

# Cleanup targets
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Development targets
run-example:
	@echo "Running example commands (make sure GH_TOKEN is set)..."
	@echo "1. Creating test .env file..."
	@echo "TEST_SECRET_1=value1" > .env.example
	@echo "TEST_SECRET_2=value2" >> .env.example
	@echo "2. Running dry-run bulk upload..."
	python -m ghvault bulk staging --file .env.example --owner example --repo example --dry-run
	@echo "3. Cleaning up..."
	@rm -f .env.example

# Build targets
build:
	python -m build

publish-test:
	python -m twine upload --repository testpypi dist/*

publish:
	python -m twine upload dist/*

# Docker targets (if needed)
docker-build:
	docker build -t ghvault .

docker-test:
	docker run --rm ghvault pytest

# Documentation targets
docs:
	@echo "Generating documentation..."
	@echo "README.md is the main documentation"

# Security check
security-check:
	pip-audit

# Performance test
perf-test:
	pytest tests/ -m "not slow" --durations=0

# Watch mode for development
watch-test:
	pytest-watch

# Install pre-commit hooks
setup-pre-commit:
	pre-commit install

# Update dependencies
update-deps:
	uv sync --upgrade
