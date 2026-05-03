import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
SAMPLE_DATASET = DATA_DIR / "sample_health_indicators.csv"
PROCESSED_DATASET = PROCESSED_DIR / "health_indicators.csv"
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://healthcare:healthcare@localhost:5432/healthcare",
)
