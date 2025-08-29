# Makefile for slugkit-py-sdk

.PHONY: build
build:
	rm -rf dist/*
	uv run hatchling build

.PHONY: publish
publish: build
	uv run twine upload --repository pypi dist/*

.PHONY: test
test:
	uv run --group test pytest

.PHONY: test-verbose
test-verbose:
	uv run --group test pytest -v

.PHONY: test-coverage
test-coverage:
	uv run --group test pytest --cov=slugkit --cov-report=term-missing

.PHONY: install-test-deps
install-test-deps:
	uv sync --group test
