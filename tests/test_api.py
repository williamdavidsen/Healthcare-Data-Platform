from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_summary_supports_pagination_and_sorting() -> None:
    response = client.get("/summary?limit=3&offset=0&sort_by=life_expectancy&sort_dir=desc")
    rows = response.json()

    assert response.status_code == 200
    assert len(rows) == 3
    assert rows[0]["life_expectancy"] >= rows[1]["life_expectancy"]


def test_indicator_filter_returns_requested_metric() -> None:
    response = client.get("/indicators?metric=life_expectancy&limit=2")
    rows = response.json()

    assert response.status_code == 200
    assert rows
    assert set(rows[0]) == {"country", "iso_code", "year", "life_expectancy"}


def test_quality_freshness_and_insight_endpoints() -> None:
    quality = client.get("/quality")
    freshness = client.get("/freshness")
    insights = client.get("/insights")

    assert quality.status_code == 200
    assert freshness.status_code == 200
    assert insights.status_code == 200
    assert "passed" in quality.json()
    assert "latest_year" in freshness.json()
    assert insights.json()


def test_correlation_and_anomaly_endpoints() -> None:
    correlations = client.get("/correlations")
    anomalies = client.get("/anomalies?metric=health_risk_score&z_threshold=2.5")

    assert correlations.status_code == 200
    assert anomalies.status_code == 200
    assert correlations.json()
