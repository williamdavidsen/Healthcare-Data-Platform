# Healthcare Data Platform

This is my end-to-end healthcare data pipeline project.
It takes public health data, validates it, stores it in PostgreSQL, models it with dbt, and shows the result through a FastAPI API and a React dashboard.

The goal is not medical diagnosis.
The goal is to show a real data engineering workflow with ingestion, quality checks, modeling, API delivery, and a dashboard.

## Employer Summary

This project shows that I can build a data pipeline from source data to a usable product.

Main result:

- Public healthcare data is ingested from source files and connectors.
- Data quality checks run before the data is used.
- Raw data can be stored in PostgreSQL.
- dbt creates staging and analytics mart models.
- FastAPI serves the modeled data.
- React dashboard makes the data easy to explore.
- Tests, CI, and Docker make the project reproducible.

In a real company, this is similar to a health analytics pipeline.
A team collects data from different public sources, turns it into one trusted analytics table, and exposes it to analysts, product teams, or dashboards.

## What I Learned

I learned that a pipeline is not only about moving data from A to B.
The hard part is making sure the data is clean, tested, and easy to use again later.

Main things I practiced:

- Writing modular ingestion code.
- Validating required columns and data types.
- Keeping raw data and analytics data separate.
- Using dbt for staging and mart models.
- Serving mart data through an API.
- Connecting the same data to a dashboard.
- Running checks in CI so broken data or code is caught early.

## Pipeline Steps

```text
Public datasets
  OWID CSV + WHO/CDC connector
        |
        v
Python ingestion
        |
        v
Raw files + PostgreSQL raw schema
        |
        v
dbt staging models
        |
        v
dbt analytics mart
        |
        +--> FastAPI
        +--> React dashboard
        +--> Streamlit old dashboard
```

Architecture diagram source: [docs/architecture.mmd](docs/architecture.mmd)

The pipeline works like this:

1. OWID healthcare data is downloaded.
2. Required columns and numeric fields are validated.
3. Data is saved locally and can also be written to PostgreSQL.
4. dbt staging models clean and prepare the raw table.
5. dbt mart models create dashboard-ready analytics data.
6. FastAPI exposes summary, trend, quality, and insight endpoints.
7. React dashboard reads from the API.

## Data Quality

Data quality is checked in more than one place.

- Python validation checks required columns.
- Empty datasets are rejected.
- Missing `country` and `year` values are rejected.
- Numeric columns are checked for correct types.
- Metric ranges are checked so impossible values are caught.
- pytest covers ingestion, analytics, and API behavior.
- dbt tests check duplicate country-year rows and invalid metric ranges.
- API endpoints like `/quality` and `/freshness` show the current data status.

I did not want this to be only a nice dashboard.
If the data breaks, the project should catch it early.

## Tech Stack

- Python: ingestion, validation, analytics
- PostgreSQL: raw and modeled data storage
- dbt: staging and mart models
- FastAPI: analytics API
- React + Vite: main dashboard
- Streamlit: legacy dashboard
- Docker Compose: local full-stack setup
- pytest: automated tests
- GitHub Actions: CI and scheduled pipeline checks

## How To Run

Install dependencies:

```bash
pip install -r requirements.txt
```

The easiest Windows start:

```powershell
.\start.ps1
```

This command tries to load OWID data, starts the API and React frontend, and opens the app.
If OWID is not available, it falls back to the sample dataset.

Local URLs:

- React dashboard: http://127.0.0.1:5173
- FastAPI docs: http://127.0.0.1:8002/docs

Run with PostgreSQL:

```powershell
.\start.ps1 -WithPostgres
```

Write OWID data to PostgreSQL and build dbt models:

```powershell
.\start.ps1 -WithPostgres -WriteDb
```

When `-WriteDb` is used, the API reads from this dbt mart table:

```text
analytics.mart_country_health_trends
```

Main database tables:

- `raw.health_indicators`
- `analytics.stg_health_indicators`
- `analytics.mart_country_health_trends`

## Useful Commands

Run only the pipeline:

```powershell
.\scripts\run_pipeline.ps1
```

Run dbt:

```powershell
.\scripts\run_dbt.ps1
```

Run local checks:

```powershell
.\scripts\check_project.ps1
```

Run the Docker full stack:

```powershell
.\scripts\start_docker.ps1
```

Run Docker Compose manually:

```bash
docker compose up -d postgres
docker compose --profile pipeline run --rm pipeline
docker compose up -d api frontend
```

Run the Python orchestration entrypoint:

```bash
python -m src.orchestration.pipeline
```

Download WHO metadata:

```bash
python -m src.ingestion.load_who --limit 100
```

Download CDC catalog metadata:

```bash
python -m src.ingestion.load_cdc --limit 100
```

Use the sample dataset:

```powershell
.\start.ps1 -UseSample
```

Run the legacy Streamlit dashboard:

```powershell
.\start.ps1 -UseStreamlit
```

Run tests:

```bash
pytest
```

Build the frontend:

```bash
npm run build --prefix frontend
```

Run the API:

```bash
uvicorn api.main:app --reload
```

Run the React frontend:

```bash
cd frontend
npm install
npm run dev
```

Back up PostgreSQL:

```powershell
.\scripts\backup_postgres.ps1
```

Restore PostgreSQL from backup:

```powershell
.\scripts\restore_postgres.ps1 -BackupPath .\backups\healthcare-YYYYMMDD_HHMMSS.dump
```

## API Endpoints

Useful endpoints:

- `GET /summary?limit=100&offset=0&sort_by=life_expectancy&sort_dir=desc`
- `GET /indicators?country=Norway&metric=life_expectancy`
- `GET /trend?country=Norway`
- `GET /metrics`
- `GET /freshness`
- `GET /quality`
- `GET /correlations`
- `GET /insights`
- `GET /anomalies?metric=health_risk_score`

## Data Sources

- Our World in Data: life expectancy, diabetes prevalence, obesity, health spending, GDP
- World Health Organization Global Health Observatory metadata connector
- Centers for Disease Control and Prevention catalog / Socrata connector

## Project Features

- OWID ingestion
- WHO and CDC connector entrypoints
- PostgreSQL raw table
- dbt staging and mart models
- FastAPI analytics API
- React dashboard
- Streamlit legacy dashboard
- Correlation analysis
- Risk index
- Year-over-year changes
- Anomaly detection
- Freshness and quality endpoints
- Metric catalog endpoint
- Pagination and filtering
- Backup and restore scripts
- Docker Compose
- GitHub Actions CI
- Scheduled pipeline workflow

## Screenshot

![Healthcare Data Platform dashboard](docs/screenshots/dashboard.png)

Capture a screenshot locally:

```powershell
.\scripts\capture_screenshots.ps1
```

## Current Status

The project is working now.
Python tests, ruff check, frontend build, and dbt parse all passed.
Data quality checks now cover missing values, duplicate country-year rows, and invalid metric ranges.

Phase 2 and Phase 3 are complete.
Phase 4 advanced features are complete.

The pipeline can ingest OWID data.
It can write to PostgreSQL.
It can run dbt staging and mart models.
FastAPI serves the mart data to the React dashboard.

Note: the dataset is annual, not daily.
For the current year, the pipeline uses the nearest published values from the source datasets.

## Medical Disclaimer

This project is only for education and portfolio use.
It does not provide medical advice, diagnosis, or treatment recommendations.
