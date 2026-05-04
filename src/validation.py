from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = {
    "country",
    "iso_code",
    "year",
    "life_expectancy",
    "diabetes_prevalence",
    "obesity_rate",
    "health_spending_per_capita",
    "gdp_per_capita",
}


def validate_health_indicators(df: pd.DataFrame) -> None:
    missing_columns = REQUIRED_COLUMNS.difference(df.columns)
    if missing_columns:
        columns = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {columns}")

    if df.empty:
        raise ValueError("Dataset is empty")

    if df["country"].isna().any():
        raise ValueError("Country column contains missing values")

    if df["year"].isna().any():
        raise ValueError("Year column contains missing values")

    numeric_columns = REQUIRED_COLUMNS.difference({"country", "iso_code"})
    invalid_numeric = [
        column
        for column in numeric_columns
        if not pd.api.types.is_numeric_dtype(df[column])
    ]
    if invalid_numeric:
        columns = ", ".join(sorted(invalid_numeric))
        raise ValueError(f"Expected numeric columns: {columns}")
