.PHONY: install test frontend-build dbt-parse dbt-run pipeline check docker-start who-catalog cdc-catalog backup

install:
	pip install -r requirements.txt
	npm ci --prefix frontend

test:
	pytest

frontend-build:
	npm run build --prefix frontend

dbt-parse:
	dbt parse --project-dir dbt --profiles-dir dbt

dbt-run:
	dbt run --project-dir dbt --profiles-dir dbt
	dbt test --project-dir dbt --profiles-dir dbt

pipeline:
	python -m src.orchestration.pipeline

check:
	pytest
	npm run build --prefix frontend
	dbt parse --project-dir dbt --profiles-dir dbt

docker-start:
	docker compose build api frontend pipeline
	docker compose up -d postgres
	docker compose --profile pipeline run --rm pipeline
	docker compose up -d api frontend

who-catalog:
	python -m src.ingestion.load_who --limit 100

cdc-catalog:
	python -m src.ingestion.load_cdc --limit 100

backup:
	pwsh -File scripts/backup_postgres.ps1
