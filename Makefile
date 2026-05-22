VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
CELERY := $(PYTHON) -m celery

.PHONY: help venv install setup run celery-beat download test

help:
	@echo "Available commands:"
	@echo "  make venv          # Create a virtual environment"
	@echo "  make install       # Install Python dependencies"
	@echo "  make setup         # Create venv and install dependencies"
	@echo "  make run           # Run the Flask API"
	@echo "  make celery-beat   # Start Celery beat (requires broker)"
	@echo "  make download      # Run the download_rates task manually"
	@echo "  make test          # Run the project tests"

venv:
	python3 -m venv $(VENV)

install: $(VENV)
	$(PIP) install -r requirements.txt

setup: venv install

run: $(VENV)
	$(PYTHON) main.py

celery-beat: $(VENV)
	@echo "Using CELERY_BROKER_URL=$(CELERY_BROKER_URL)"
	CELERY_BROKER_URL=$(CELERY_BROKER_URL) $(CELERY) -A cron_tasks.celer.app beat

download: $(VENV)
	$(PYTHON) -m cron_tasks.download_rates

test: $(VENV)
	$(PYTHON) test.py
