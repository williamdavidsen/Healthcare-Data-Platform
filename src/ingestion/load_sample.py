from __future__ import annotations

import pandas as pd

from src.config import PROCESSED_DATASET, SAMPLE_DATASET
from src.validation import validate_health_indicators


def load_sample_dataset() -> pd.DataFrame:
    df = pd.read_csv(SAMPLE_DATASET)
    validate_health_indicators(df)
    return df.sort_values(["country", "year"]).reset_index(drop=True)


def save_processed_dataset(df: pd.DataFrame) -> None:
    PROCESSED_DATASET.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DATASET, index=False)


def main() -> None:
    df = load_sample_dataset()
    save_processed_dataset(df)
    print(f"Saved {len(df)} rows to {PROCESSED_DATASET}")


if __name__ == "__main__":
    main()
