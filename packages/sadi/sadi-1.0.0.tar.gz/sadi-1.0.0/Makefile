.PHONY: help install install-dev test test-compatibility test-comprehensive test-smoke clean build lint format check-format upload-test upload docs

# Default target
help:
	@echo "SADI Python Package - Development Commands"
	@echo "=========================================="
	@echo ""
	@echo "Setup:"
	@echo "  install         Install package in current environment"
	@echo "  install-dev     Install package with development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  test            Run all available tests"
	@echo "  test-compatibility  Run Python 3.12 compatibility tests only"
	@echo "  test-comprehensive  Run comprehensive SADI functionality tests"
	@echo "  test-smoke      Run basic smoke tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint            Run flake8 linter"
	@echo "  format          Format code with black and isort"
	@echo "  check-format    Check code formatting without making changes"
	@echo ""
	@echo "Build & Distribution:"
	@echo "  clean           Clean build artifacts"
	@echo "  build           Build package distributions"
	@echo "  upload-test     Upload to Test PyPI"
	@echo "  upload          Upload to PyPI (production)"
	@echo ""
	@echo "Documentation:"
	@echo "  docs            Generate documentation"

install:
	pip install -e .

install-dev:
	pip install -e .[dev]
	pip install black isort flake8 pytest pytest-cov build twine

test:
	python run_tests.py

test-compatibility:
	python test_compatibility.py

test-comprehensive:
	python test_sadi_comprehensive.py

test-smoke:
	python test_smoke.py

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

build: clean
	python -m build

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

format:
	black .
	isort .

check-format:
	black --check --diff .
	isort --check-only --diff .

upload-test: build
	twine check dist/*
	twine upload --repository testpypi dist/*

upload: build
	twine check dist/*
	twine upload dist/*

docs:
	@echo "Documentation generation not yet configured"
	@echo "Consider adding Sphinx or similar documentation tool"

# Development workflow targets
dev-setup: install-dev
	@echo "Development environment setup complete!"
	@echo "Run 'make test' to verify everything works."

ci-test: test-compatibility test lint
	@echo "CI-style testing complete"

check-all: check-format lint test
	@echo "All checks passed!"