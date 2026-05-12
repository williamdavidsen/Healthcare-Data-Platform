from __future__ import annotations

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.analytics import (
    METRIC_COLUMNS,
    QUALITY_RANGES,
    add_country_risk_index,
    add_health_risk_score,
    add_year_over_year_changes,
    correlation_records,
    country_summary,
    data_freshness,
    data_quality_report,
    detect_anomalies,
    top_insights,
)
from src.config import MART_SCHEMA, MART_TABLE, PROCESSED_DATASET, SAMPLE_DATASET, USE_DATABASE
from src.validation import validate_health_indicators

app = FastAPI(title="Healthcare Data Platform API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_dataset() -> pd.DataFrame:
    if USE_DATABASE:
        from src.database import read_health_indicators_mart

        df = read_health_indicators_mart(schema=MART_SCHEMA, table_name=MART_TABLE)
        validate_health_indicators(df)
        return df

    path = PROCESSED_DATASET if PROCESSED_DATASET.exists() else SAMPLE_DATASET
    df = pd.read_csv(path)
    validate_health_indicators(df)
    return add_health_risk_score(df)


def enrich_dataset(df: pd.DataFrame) -> pd.DataFrame:
    return add_year_over_year_changes(add_country_risk_index(add_health_risk_score(df)))


def records(df: pd.DataFrame) -> list[dict]:
    return df.where(pd.notna(df), None).to_dict(orient="records")


def paginate(df: pd.DataFrame, limit: int, offset: int) -> pd.DataFrame:
    return df.iloc[offset : offset + limit]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/countries")
def countries() -> list[str]:
    df = load_dataset()
    return sorted(df["country"].unique().tolist())


@app.get("/metrics")
def metrics() -> list[dict]:
    return [
        {
            "name": metric,
            "quality_min": QUALITY_RANGES.get(metric, (None, None))[0],
            "quality_max": QUALITY_RANGES.get(metric, (None, None))[1],
        }
        for metric in METRIC_COLUMNS
    ]


@app.get("/summary")
def summary(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("life_expectancy"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
) -> list[dict]:
    df = country_summary(enrich_dataset(load_dataset()))
    if sort_by not in df.columns:
        raise HTTPException(status_code=400, detail=f"Unknown sort column: {sort_by}")

    ascending = sort_dir == "asc"
    sorted_df = df.sort_values(sort_by, ascending=ascending)
    return records(paginate(sorted_df, limit, offset))


@app.get("/indicators")
def indicators(
    country: str | None = None,
    year: int | None = None,
    metric: str | None = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> list[dict]:
    df = enrich_dataset(load_dataset())
    if country:
        df = df[df["country"].str.lower() == country.lower()]
    if year:
        df = df[df["year"] == year]
    if metric:
        allowed_metrics = [*METRIC_COLUMNS, "country_risk_index"]
        if metric not in allowed_metrics:
            raise HTTPException(status_code=400, detail=f"Unknown metric: {metric}")
        columns = ["country", "iso_code", "year", metric]
        df = df[columns]
    return records(paginate(df.sort_values(["country", "year"]), limit, offset))


@app.get("/freshness")
def freshness() -> dict:
    return data_freshness(load_dataset())


@app.get("/quality")
def quality() -> dict:
    return data_quality_report(load_dataset())


@app.get("/correlations")
def correlations() -> list[dict]:
    return correlation_records(load_dataset())


@app.get("/insights")
def insights() -> list[dict]:
    return top_insights(load_dataset())


@app.get("/anomalies")
def anomalies(
    metric: str = Query("health_risk_score"),
    z_threshold: float = Query(2.5, ge=0.1, le=10),
) -> list[dict]:
    df = enrich_dataset(load_dataset())
    if metric not in df.columns:
        raise HTTPException(status_code=400, detail=f"Unknown metric: {metric}")
    return records(detect_anomalies(df, metric=metric, z_threshold=z_threshold))


@app.get("/trend")
def trend(country: str) -> list[dict]:
    df = enrich_dataset(load_dataset())
    country_df = df[df["country"].str.lower() == country.lower()]
    if country_df.empty:
        raise HTTPException(status_code=404, detail=f"Country not found: {country}")
    return records(country_df.sort_values("year"))
