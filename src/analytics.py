from __future__ import annotations

import pandas as pd

METRIC_COLUMNS = [
    "life_expectancy",
    "diabetes_prevalence",
    "obesity_rate",
    "health_spending_per_capita",
    "gdp_per_capita",
    "health_risk_score",
]


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


def add_country_risk_index(df: pd.DataFrame) -> pd.DataFrame:
    result = add_health_risk_score(df)
    risk = result["health_risk_score"]
    if risk.max() == risk.min():
        result["country_risk_index"] = 50.0
    else:
        result["country_risk_index"] = ((risk - risk.min()) / (risk.max() - risk.min()) * 100).round(1)
    return result


def add_year_over_year_changes(df: pd.DataFrame) -> pd.DataFrame:
    result = df.sort_values(["country", "year"]).copy()
    for column in METRIC_COLUMNS:
        if column in result.columns:
            result[f"{column}_yoy_change"] = result.groupby("country")[column].diff().round(2)
    return result


def detect_anomalies(
    df: pd.DataFrame,
    metric: str = "health_risk_score",
    z_threshold: float = 2.5,
) -> pd.DataFrame:
    if metric not in df.columns:
        raise ValueError(f"Unknown metric: {metric}")

    result = df[["country", "iso_code", "year", metric]].copy()
    result["metric"] = metric
    result["country_mean"] = result.groupby("country")[metric].transform("mean")
    result["country_std"] = result.groupby("country")[metric].transform("std").fillna(0)
    result["z_score"] = 0.0
    nonzero_std = result["country_std"] > 0
    result.loc[nonzero_std, "z_score"] = (
        (result.loc[nonzero_std, metric] - result.loc[nonzero_std, "country_mean"])
        / result.loc[nonzero_std, "country_std"]
    ).round(2)
    return result[result["z_score"].abs() >= z_threshold].sort_values("z_score", ascending=False)


def data_freshness(df: pd.DataFrame) -> dict:
    latest_year = int(df["year"].max())
    latest = df[df["year"] == latest_year]
    return {
        "latest_year": latest_year,
        "earliest_year": int(df["year"].min()),
        "row_count": int(len(df)),
        "country_count": int(df["country"].nunique()),
        "latest_country_count": int(latest["country"].nunique()),
        "uses_carried_forward_values": True,
    }


def data_quality_report(df: pd.DataFrame) -> dict:
    required_columns = ["country", "iso_code", "year", *[c for c in METRIC_COLUMNS if c in df.columns]]
    missing_values = {column: int(df[column].isna().sum()) for column in required_columns}
    duplicate_rows = int(df.duplicated(subset=["country", "iso_code", "year"]).sum())
    return {
        "row_count": int(len(df)),
        "country_count": int(df["country"].nunique()),
        "year_min": int(df["year"].min()),
        "year_max": int(df["year"].max()),
        "duplicate_country_year_rows": duplicate_rows,
        "missing_values": missing_values,
        "passed": duplicate_rows == 0 and all(count == 0 for count in missing_values.values()),
    }


def correlation_records(df: pd.DataFrame) -> list[dict]:
    matrix = correlation_matrix(add_health_risk_score(df))
    records = []
    for left in matrix.index:
        for right in matrix.columns:
            records.append(
                {
                    "metric_a": left,
                    "metric_b": right,
                    "correlation": round(float(matrix.loc[left, right]), 3),
                }
            )
    return records


def top_insights(df: pd.DataFrame) -> list[dict]:
    enriched = add_country_risk_index(add_year_over_year_changes(add_health_risk_score(df)))
    latest_year = enriched["year"].max()
    latest = enriched[enriched["year"] == latest_year].copy()
    best_life = latest.sort_values("life_expectancy", ascending=False).iloc[0]
    lowest_risk = latest.sort_values("country_risk_index").iloc[0]
    highest_risk = latest.sort_values("country_risk_index", ascending=False).iloc[0]
    life_gain_rows = enriched.dropna(subset=["life_expectancy_yoy_change"]).sort_values(
        "life_expectancy_yoy_change", ascending=False
    )
    insights = [
        {
            "title": "Highest life expectancy",
            "country": best_life["country"],
            "year": int(best_life["year"]),
            "value": round(float(best_life["life_expectancy"]), 1),
            "unit": "years",
        },
        {
            "title": "Lowest risk index",
            "country": lowest_risk["country"],
            "year": int(lowest_risk["year"]),
            "value": round(float(lowest_risk["country_risk_index"]), 1),
            "unit": "index",
        },
        {
            "title": "Highest risk index",
            "country": highest_risk["country"],
            "year": int(highest_risk["year"]),
            "value": round(float(highest_risk["country_risk_index"]), 1),
            "unit": "index",
        },
    ]
    if not life_gain_rows.empty:
        biggest_life_gain = life_gain_rows.iloc[0]
        insights.append(
            {
            "title": "Largest life expectancy gain",
            "country": biggest_life_gain["country"],
            "year": int(biggest_life_gain["year"]),
            "value": round(float(biggest_life_gain["life_expectancy_yoy_change"]), 2),
            "unit": "YoY years",
            }
        )
    return insights
