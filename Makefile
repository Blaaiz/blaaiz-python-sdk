# Makefile for Blaaiz Python SDK

.PHONY: help install install-dev test test-unit test-integration test-coverage lint format type-check build clean publish

help:
	@echo "Available commands:"
	@echo "  install        Install the package"
	@echo "  install-dev    Install development dependencies"
	@echo "  test           Run all tests"
	@echo "  test-unit      Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-coverage  Run tests with coverage report"
	@echo "  lint           Run linting"
	@echo "  format         Format code"
	@echo "  type-check     Run type checking"
	@echo "  build          Build distribution packages"
	@echo "  clean          Clean build artifacts"
	@echo "  publish        Publish to PyPI"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	python -m pytest

test-unit:
	python -m pytest -m "not integration"

test-integration:
	python -m pytest -m integration

test-coverage:
	python -m pytest --cov=blaaiz --cov-report=html --cov-report=term-missing

lint:
	flake8 blaaiz/ tests/ examples/
	black --check blaaiz/ tests/ examples/

format:
	black blaaiz/ tests/ examples/

type-check:
	mypy blaaiz/

build:
	python setup.py sdist bdist_wheel

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

publish: clean build
	twine upload dist/*

# Example usage
example-basic:
	cd examples && python basic_usage.py

example-workflows:
	cd examples && python complete_workflows.py

example-files:
	cd examples && python file_upload.py

example-webhook:
	cd examples && python webhook_server.py

example-flask:
	cd examples && python flask_integration.py