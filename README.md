# Healthcare Data Platform

An end-to-end healthcare data engineering project that ingests public health datasets, stores raw data, models analytics tables, and serves insights through a dashboard and API.

## Why This Project

Healthcare data is often fragmented across organizations, formats, and country-level reporting standards. This project shows how to build a reliable analytics platform around public health indicators such as life expectancy, diabetes prevalence, obesity, population, and health spending.

The goal is not medical diagnosis. The goal is clean data engineering: ingestion, validation, modeling, analytics, and reproducible delivery.

## Architecture

```text
Public datasets
  OWID CSV + WHO/CDC extension connectors
        |
        v
Python ingestion
        |
        v
Raw files + PostgreSQL raw schema
        |
        v
dbt transformations
        |
        v
Analytics marts
        |
        +--> FastAPI analytics API
        +--> React dashboard
        +--> Streamlit legacy dashboard
```

Mermaid architecture source: [docs/architecture.mmd](docs/architecture.mmd)

## Tech Stack

- Python: ingestion, validation, analytics helpers
- PostgreSQL: raw and modeled data storage
- dbt: transformations and data modeling
- FastAPI: lightweight analytics API
- React + Vite: modern interactive dashboard
- Streamlit: legacy dashboard
- Docker Compose: local infrastructure
- pytest: automated tests
- GitHub Actions: CI checks and scheduled pipeline run

## Project Roadmap

### Phase 1: Portfolio MVP

- Load a small sample health indicator dataset
- Validate required columns and data types
- Build Streamlit charts for country and year comparisons
- Add tests for ingestion and validation

### Phase 2: Real Pipeline

- Add OWID CSV ingestion: complete
- Store raw data in PostgreSQL: complete
- Add dbt staging and mart models: complete
- Add data quality checks: complete
- Serve dbt mart data through the API: complete

### Phase 3: Production Polish

- Add CI checks for frontend and dbt: complete
- Add Docker Compose full-stack services: complete
- Add one-command pipeline scripts: complete
- Add screenshots and architecture diagram: complete
- Add Prefect orchestration or equivalent workflow layer: local orchestration entrypoint added

### Phase 4: Advanced Extensions

- Add WHO and CDC source connectors: complete
- Add correlation analysis, risk index, year-over-year changes, anomaly detection: complete
- Add data freshness and data quality endpoints: complete
- Add API pagination and filtering: complete
- Add PostgreSQL backup/restore scripts: complete
- Add scheduled GitHub Actions pipeline validation: complete

## How To Run

Create and activate a virtual environment, then install dependencies:

```bash
pip install -r requirements.txt
```

Run everything with one command on Windows:

```powershell
.\start.ps1
```

This loads the current OWID dataset, starts the API and React frontend, then opens the frontend in your browser. If OWID is unavailable, the script falls back to the sample dataset.

Local URLs:

- React dashboard: http://127.0.0.1:5173
- FastAPI docs: http://127.0.0.1:8002/docs

Optional PostgreSQL run:

```powershell
.\start.ps1 -WithPostgres
```

Write OWID data to PostgreSQL and build dbt models:

```powershell
.\start.ps1 -WithPostgres -WriteDb
```

When `-WriteDb` is used, the API reads from the dbt mart table:
`analytics.mart_country_health_trends`.

The database pipeline creates:

- `raw.health_indicators`
- `analytics.stg_health_indicators`
- `analytics.mart_country_health_trends`

Run dbt manually:

```powershell
.\scripts\run_dbt.ps1
```

Run only the data pipeline:

```powershell
.\scripts\run_pipeline.ps1
```

Run local project checks:

```powershell
.\scripts\check_project.ps1
```

Run the full Docker stack with one command:

```powershell
.\scripts\start_docker.ps1
```

Run with Docker Compose:

```bash
docker compose up -d postgres
docker compose --profile pipeline run --rm pipeline
docker compose up -d api frontend
```

Run the Python orchestration entrypoint:

```bash
python -m src.orchestration.pipeline
```

Capture a dashboard screenshot:

```powershell
.\scripts\capture_screenshots.ps1
```

Use the bundled sample dataset:

```powershell
.\start.ps1 -UseSample
```

Run the legacy Streamlit dashboard instead:

```powershell
.\start.ps1 -UseStreamlit
```

Run the sample ingestion:

```bash
python -m src.ingestion.load_sample
```

Run the OWID ingestion:

```bash
python -m src.ingestion.load_owid
```

Download WHO Global Health Observatory metadata:

```bash
python -m src.ingestion.load_who --limit 100
```

Download CDC Data catalog metadata:

```bash
python -m src.ingestion.load_cdc --limit 100
```

Start PostgreSQL:

```bash
docker compose up -d postgres
```

Load OWID data and write it to PostgreSQL:

```bash
python -m src.ingestion.load_owid --write-db
```

Run tests:

```bash
pytest
```

Run frontend build:

```bash
npm run build --prefix frontend
```

Run dbt after PostgreSQL is up and raw data is loaded:

```powershell
.\scripts\run_dbt.ps1
```

Run the dashboard:

```bash
streamlit run dashboard/app.py
```

Run the React frontend:

```bash
cd frontend
npm install
npm run dev
```

Run the API:

```bash
uvicorn api.main:app --reload
```

Useful API endpoints:

- `GET /summary?limit=100&offset=0&sort_by=life_expectancy&sort_dir=desc`
- `GET /indicators?country=Norway&metric=life_expectancy`
- `GET /trend?country=Norway`
- `GET /freshness`
- `GET /quality`
- `GET /correlations`
- `GET /insights`
- `GET /anomalies?metric=health_risk_score`

Back up PostgreSQL:

```powershell
.\scripts\backup_postgres.ps1
```

Restore PostgreSQL from a backup dump:

```powershell
.\scripts\restore_postgres.ps1 -BackupPath .\backups\healthcare-YYYYMMDD_HHMMSS.dump
```

## Data Sources

- Our World in Data: life expectancy, diabetes prevalence, adult obesity prevalence, health spending per capita, GDP per capita
- World Health Organization Global Health Observatory metadata and indicator connector
- Centers for Disease Control and Prevention Data catalog and Socrata resource connector

## Portfolio Notes

This repository is designed to show practical data engineering skills:

- Clear pipeline architecture
- Reproducible local setup
- Realistic public data sources
- Tested ingestion and validation code
- React dashboard and API as user-facing outputs
- PostgreSQL + dbt staging/mart modeling
- Repeatable local pipeline with one-command startup
- Full-stack Docker Compose services
- Expanded CI for lint, tests, frontend build, and dbt
- Advanced analytics endpoints for correlations, risk index, year-over-year changes, anomaly detection, freshness, and quality
- Scheduled GitHub Actions pipeline workflow
- PostgreSQL backup and restore scripts

## Screenshots

![Healthcare Data Platform dashboard](docs/screenshots/dashboard.png)

Capture it locally with:

```powershell
.\scripts\capture_screenshots.ps1
```

## Current Status

Phase 2 and Phase 3 are complete. Phase 4 advanced extensions are implemented.
The project can ingest OWID data,
write it to PostgreSQL, run dbt staging and mart transformations, validate dbt
models, and serve the analytics mart through FastAPI to the React dashboard.

Production polish now includes Docker Compose services for PostgreSQL, API,
frontend, and a one-shot pipeline container, plus expanded CI checks for Python,
frontend, and dbt. Advanced extensions add WHO/CDC connector entrypoints,
correlation analysis, country risk index, year-over-year changes, anomaly
detection, data freshness checks, a data quality dashboard section, API
filtering/pagination, backup/restore scripts, and a scheduled GitHub Actions
pipeline.

The generated dataset is annual, not daily. For the current year, the pipeline
uses the nearest published values available from the source datasets.

## Medical Disclaimer

This project is for educational and analytics portfolio purposes only. It does not provide medical advice, diagnosis, or treatment recommendations.
