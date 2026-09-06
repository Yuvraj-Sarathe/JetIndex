.PHONY: setup up down logs migrate revision seed mock-data test lint fmt scrape pipeline index backtest shell psql

setup:
	cp -n .env.example .env || true
	pip install -r requirements-dev.txt
	pre-commit install
	cd frontend && npm install && cd ..

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	docker compose exec api alembic -c db/migrations/alembic.ini upgrade head

revision:
	docker compose exec api alembic -c db/migrations/alembic.ini revision --autogenerate -m $(MSG)

seed:
	docker compose exec api python -m db.seed

mock-data:
	python scripts/generate_mock_data.py

test:
	pytest

test-cov:
	pytest --cov --cov-report=term-missing

lint:
	ruff check .
	cd frontend && npm run lint

fmt:
	ruff format .
	cd frontend && npx prettier --write "src/**/*.{js,jsx,json,css}"

scrape:
	python -m app.tasks.scrape_tasks --route $(ROUTE) --lead $(LEAD) --source $(SOURCE)

pipeline:
	python -m pipeline.run --date $(DATE)

index:
	python -m engine.run --date $(DATE)

backtest:
	python -m engine.run --backtest

shell:
	docker compose exec api bash

psql:
	docker compose exec db psql -U apix -d apix
