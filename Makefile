.PHONY: lint format-check test cov check migrations-check ci

lint:
	ruff check apps config

# May report drift on legacy files; prefer formatting only new/edited code until a dedicated format PR.
format-check:
	ruff format --check apps config

test:
	pytest -q

cov:
	pytest --cov=apps --cov-report=term-missing -q

check:
	python manage.py check

migrations-check:
	python manage.py makemigrations --check --dry-run

# CI-aligned local gate (format-check omitted to keep legacy green).
ci: lint check migrations-check cov
