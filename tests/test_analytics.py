from __future__ import annotations

import pandas as pd

from src.analytics import (
    add_country_risk_index,
    add_health_risk_score,
    add_year_over_year_changes,
    correlation_records,
    data_freshness,
    data_quality_report,
    detect_anomalies,
    top_insights,
)


def sample_health_data() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "country": "Norway",
                "iso_code": "NOR",
                "year": 2023,
                "life_expectancy": 83.1,
                "diabetes_prevalence": 4.8,
                "obesity_rate": 20.0,
                "health_spending_per_capita": 8200,
                "gdp_per_capita": 89000,
            },
            {
                "country": "Norway",
                "iso_code": "NOR",
                "year": 2024,
                "life_expectancy": 83.4,
                "diabetes_prevalence": 4.7,
                "obesity_rate": 20.1,
                "health_spending_per_capita": 8400,
                "gdp_per_capita": 91000,
            },
            {
                "country": "Japan",
                "iso_code": "JPN",
                "year": 2023,
                "life_expectancy": 84.4,
                "diabetes_prevalence": 8.2,
                "obesity_rate": 4.5,
                "health_spending_per_capita": 5200,
                "gdp_per_capita": 43000,
            },
            {
                "country": "Japan",
                "iso_code": "JPN",
                "year": 2024,
                "life_expectancy": 84.7,
                "diabetes_prevalence": 8.1,
                "obesity_rate": 4.6,
                "health_spending_per_capita": 5300,
                "gdp_per_capita": 44000,
            },
        ]
    )


def test_country_risk_index_is_normalized() -> None:
    result = add_country_risk_index(sample_health_data())

    assert "country_risk_index" in result.columns
    assert result["country_risk_index"].between(0, 100).all()


def test_year_over_year_changes_are_added_by_country() -> None:
    scored = add_health_risk_score(sample_health_data())
    result = add_year_over_year_changes(scored)
    norway_2024 = result[(result["country"] == "Norway") & (result["year"] == 2024)].iloc[0]

    assert norway_2024["life_expectancy_yoy_change"] == 0.3
    assert "health_risk_score_yoy_change" in result.columns


def test_freshness_and_quality_reports() -> None:
    data = sample_health_data()

    assert data_freshness(data)["latest_year"] == 2024
    quality = data_quality_report(data)
    assert quality["passed"] is True
    assert quality["invalid_ranges"]["life_expectancy"] == 0


def test_quality_report_fails_for_invalid_metric_ranges() -> None:
    data = sample_health_data()
    data.loc[0, "obesity_rate"] = 140.0

    quality = data_quality_report(data)

    assert quality["passed"] is False
    assert quality["invalid_ranges"]["obesity_rate"] == 1


def test_correlation_records_and_insights_are_available() -> None:
    data = sample_health_data()

    assert correlation_records(data)
    assert len(top_insights(data)) >= 3


def test_detect_anomalies_marks_large_country_level_changes() -> None:
    data = add_health_risk_score(sample_health_data())
    extra = data.iloc[[0]].copy()
    extra["year"] = 2025
    extra["health_risk_score"] = 99.0
    spiked = pd.concat([data, extra], ignore_index=True)

    anomalies = detect_anomalies(spiked, metric="health_risk_score", z_threshold=1.0)

    assert not anomalies.empty
    assert anomalies.iloc[0]["country"] == "Norway"
