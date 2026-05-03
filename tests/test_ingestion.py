import pandas as pd
import pytest

from src.analytics import add_health_risk_score
from src.ingestion.load_sample import load_sample_dataset
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
