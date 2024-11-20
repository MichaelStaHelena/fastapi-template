# Makefile
.PHONY: install install-dev format lint test run clean

install:
	pip install .

install-dev:
	pip install '.[dev]'

format:
	black app tests
	isort app tests

lint:
	flake8 app tests
	mypy app tests
	black --check app tests
	isort --check-only app tests

test:
	pytest -v --cov=app

run:
	uvicorn app.main:app --reload

clean:
	rm -rf __pycache__ .pytest_cache .coverage .mypy_cache
