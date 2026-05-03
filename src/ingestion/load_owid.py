from __future__ import annotations

import argparse
from datetime import date
from dataclasses import dataclass
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

from src.config import PROCESSED_DATASET, RAW_DIR
from src.validation import validate_health_indicators


@dataclass(frozen=True)
class OwidIndicator:
    slug: str
    output_column: str
    source_column: str | None = None

    @property
    def csv_url(self) -> str:
        return f"https://ourworldindata.org/grapher/{self.slug}.csv"

    @property
    def raw_path(self) -> Path:
        return RAW_DIR / f"{self.slug}.csv"


OWID_INDICATORS = (
    OwidIndicator("life-expectancy", "life_expectancy", "Life expectancy"),
    OwidIndicator("diabetes-prevalence", "diabetes_prevalence", "Diabetes prevalence"),
    OwidIndicator("obesity-prevalence-adults-who-gho", "obesity_rate"),
    OwidIndicator(
        "annual-healthcare-expenditure-per-capita",
        "health_spending_per_capita",
    ),
    OwidIndicator("gdp-per-capita-worldbank", "gdp_per_capita", "GDP per capita"),
)


def download_indicator(indicator: OwidIndicator) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    response = requests.get(
        indicator.csv_url,
        headers={"User-Agent": "healthcare-data-platform/1.0"},
        timeout=60,
    )
    response.raise_for_status()
    indicator.raw_path.write_text(response.text, encoding="utf-8")
    return indicator.raw_path


def load_indicator_frame(indicator: OwidIndicator, csv_text: str | None = None) -> pd.DataFrame:
    if csv_text is None:
        df = pd.read_csv(indicator.raw_path)
    else:
        df = pd.read_csv(StringIO(csv_text))

    ignored_columns = {"Entity", "Code", "Year", "World region according to OWID"}
    value_columns = [column for column in df.columns if column not in ignored_columns]
    if indicator.source_column is not None and indicator.source_column in df.columns:
        value_columns = [indicator.source_column]

    if len(value_columns) != 1:
        raise ValueError(
            f"Expected one value column for {indicator.slug}, found {len(value_columns)}"
        )

    value_column = value_columns[0]
    result = df.rename(
        columns={
            "Entity": "country",
            "Code": "iso_code",
            "Year": "year",
            value_column: indicator.output_column,
        }
    )[["country", "iso_code", "year", indicator.output_column]]

    result = result[result["iso_code"].astype(str).str.len() == 3]
    result[indicator.output_column] = pd.to_numeric(result[indicator.output_column], errors="coerce")
    result["year"] = pd.to_numeric(result["year"], errors="coerce")
    return result.dropna(subset=["country", "iso_code", "year", indicator.output_column])


def merge_indicator_frames(
    frames: list[pd.DataFrame],
    start_year: int = 2000,
    end_year: int | None = None,
) -> pd.DataFrame:
    if not frames:
        raise ValueError("No indicator frames were provided")

    if end_year is None:
        end_year = date.today().year

    merged = frames[0]
    for frame in frames[1:]:
        merged = merged.merge(frame, on=["country", "iso_code", "year"], how="outer")

    merged["year"] = merged["year"].astype(int)
    merged = merged.sort_values(["country", "iso_code", "year"])
    countries = merged[["country", "iso_code"]].drop_duplicates()
    country_years = countries.merge(
        pd.DataFrame({"year": range(start_year, end_year + 1)}),
        how="cross",
    )
    merged = country_years.merge(merged, on=["country", "iso_code", "year"], how="left")
    value_columns = [
        column
        for column in merged.columns
        if column not in {"country", "iso_code", "year"}
    ]
    merged[value_columns] = merged.groupby(["country", "iso_code"], sort=False)[
        value_columns
    ].ffill()
    merged = merged.dropna(subset=value_columns)
    merged = merged.sort_values(["country", "year"]).reset_index(drop=True)
    validate_health_indicators(merged)
    return merged


def build_owid_health_indicators(start_year: int = 2000, end_year: int | None = None) -> pd.DataFrame:
    frames = []
    for indicator in OWID_INDICATORS:
        download_indicator(indicator)
        frames.append(load_indicator_frame(indicator))
    return merge_indicator_frames(frames, start_year=start_year, end_year=end_year)


def save_processed_dataset(df: pd.DataFrame, path: Path = PROCESSED_DATASET) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Load OWID healthcare indicators")
    parser.add_argument("--start-year", type=int, default=2000)
    parser.add_argument("--end-year", type=int, default=date.today().year)
    parser.add_argument("--write-db", action="store_true")
    args = parser.parse_args()

    df = build_owid_health_indicators(start_year=args.start_year, end_year=args.end_year)
    save_processed_dataset(df)

    if args.write_db:
        from src.database import write_health_indicators_to_postgres

        write_health_indicators_to_postgres(df)

    print(f"Saved {len(df)} rows to {PROCESSED_DATASET}")


if __name__ == "__main__":
    main()
