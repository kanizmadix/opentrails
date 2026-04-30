.PHONY: install dev test lint format docker-build docker-run init-db clean

PY ?= python3
VENV ?= .venv
PIP := $(VENV)/bin/pip
PYTHON := $(VENV)/bin/python

install:
	$(PY) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

dev:
	$(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

format:
	$(PYTHON) -m ruff check --fix .

init-db:
	$(PYTHON) -c "from app.db import init_db; init_db()"

docker-build:
	docker build -t opentrails:latest .

docker-run:
	docker run --rm -p 8000:8000 --env-file .env -v $(PWD)/data:/app/data opentrails:latest

clean:
	rm -rf $(VENV) .pytest_cache .ruff_cache **/__pycache__
