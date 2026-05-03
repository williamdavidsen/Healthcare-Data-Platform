from __future__ import annotations

import pandas as pd


def country_summary(df: pd.DataFrame) -> pd.DataFrame:
    latest_year = df["year"].max()
    latest = df[df["year"] == latest_year].copy()
    return latest.sort_values("life_expectancy", ascending=False)


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "life_expectancy",
        "diabetes_prevalence",
        "obesity_rate",
        "health_spending_per_capita",
        "gdp_per_capita",
    ]
    return df[columns].corr(numeric_only=True)


def add_health_risk_score(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["health_risk_score"] = (
        result["diabetes_prevalence"] * 0.45
        + result["obesity_rate"] * 0.35
        - result["life_expectancy"] * 0.05
    ).round(2)
    return result
