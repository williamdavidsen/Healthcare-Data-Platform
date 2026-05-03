from __future__ import annotations

import pandas as pd
from fastapi import FastAPI, HTTPException

from src.analytics import add_health_risk_score, country_summary
from src.config import PROCESSED_DATASET, SAMPLE_DATASET
from src.validation import validate_health_indicators


app = FastAPI(title="Healthcare Data Platform API")


def load_dataset() -> pd.DataFrame:
    path = PROCESSED_DATASET if PROCESSED_DATASET.exists() else SAMPLE_DATASET
    df = pd.read_csv(path)
    validate_health_indicators(df)
    return add_health_risk_score(df)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/countries")
def countries() -> list[str]:
    df = load_dataset()
    return sorted(df["country"].unique().tolist())


@app.get("/summary")
def summary() -> list[dict]:
    df = load_dataset()
    return country_summary(df).to_dict(orient="records")


@app.get("/trend")
def trend(country: str) -> list[dict]:
    df = load_dataset()
    country_df = df[df["country"].str.lower() == country.lower()]
    if country_df.empty:
        raise HTTPException(status_code=404, detail=f"Country not found: {country}")
    return country_df.sort_values("year").to_dict(orient="records")
