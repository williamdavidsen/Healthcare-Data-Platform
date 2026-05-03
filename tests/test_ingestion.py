import pandas as pd
import pytest

from src.analytics import add_health_risk_score
from src.ingestion.load_sample import load_sample_dataset
from src.ingestion.load_owid import OwidIndicator, load_indicator_frame, merge_indicator_frames
from src.validation import validate_health_indicators


def test_load_sample_dataset_has_expected_rows():
    df = load_sample_dataset()

    assert len(df) == 12
    assert set(df["country"]) == {"Norway", "Turkey", "United States"}


def test_validate_health_indicators_rejects_missing_columns():
    df = pd.DataFrame({"country": ["Norway"]})

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_health_indicators(df)


def test_add_health_risk_score_creates_numeric_column():
    df = load_sample_dataset()
    result = add_health_risk_score(df)

    assert "health_risk_score" in result.columns
    assert pd.api.types.is_numeric_dtype(result["health_risk_score"])


def test_load_indicator_frame_normalizes_owid_csv():
    indicator = OwidIndicator("example-indicator", "life_expectancy")
    csv_text = (
        "Entity,Code,Year,Life expectancy\n"
        "Norway,NOR,2020,83.1\n"
        "World,OWID_WRL,2020,72.5\n"
    )

    result = load_indicator_frame(indicator, csv_text=csv_text)

    assert result.to_dict(orient="records") == [
        {
            "country": "Norway",
            "iso_code": "NOR",
            "year": 2020,
            "life_expectancy": 83.1,
        }
    ]


def test_merge_indicator_frames_creates_valid_health_indicators():
    base = pd.DataFrame(
        {
            "country": ["Norway", "Norway"],
            "iso_code": ["NOR", "NOR"],
            "year": [1999, 2020],
        }
    )
    frames = [
        base.assign(life_expectancy=[78.0, 83.1]),
        base.assign(diabetes_prevalence=[3.9, 4.8]),
        base.assign(obesity_rate=[18.0, 23.1]),
        base.assign(health_spending_per_capita=[3000.0, 7200.0]),
        base.assign(gdp_per_capita=[52000.0, 68000.0]),
    ]

    result = merge_indicator_frames(frames, start_year=2000)

    assert len(result) == 1
    assert result.loc[0, "country"] == "Norway"
    assert result.loc[0, "year"] == 2020


def test_merge_indicator_frames_carries_latest_known_values_forward():
    frames = [
        pd.DataFrame(
            {
                "country": ["Norway", "Norway"],
                "iso_code": ["NOR", "NOR"],
                "year": [2021, 2024],
                "life_expectancy": [83.2, 83.6],
            }
        ),
        pd.DataFrame(
            {
                "country": ["Norway"],
                "iso_code": ["NOR"],
                "year": [2021],
                "diabetes_prevalence": [5.4],
            }
        ),
        pd.DataFrame(
            {
                "country": ["Norway"],
                "iso_code": ["NOR"],
                "year": [2022],
                "obesity_rate": [23.7],
            }
        ),
        pd.DataFrame(
            {
                "country": ["Norway"],
                "iso_code": ["NOR"],
                "year": [2024],
                "health_spending_per_capita": [8500.0],
            }
        ),
        pd.DataFrame(
            {
                "country": ["Norway"],
                "iso_code": ["NOR"],
                "year": [2024],
                "gdp_per_capita": [90000.0],
            }
        ),
    ]

    result = merge_indicator_frames(frames, start_year=2020)

    latest = result[result["year"] == 2024].iloc[0]
    assert latest["diabetes_prevalence"] == 5.4
    assert latest["obesity_rate"] == 23.7
