from __future__ import annotations

import pandas as pd
from sqlalchemy import create_engine, text

from src.config import DATABASE_URL


def write_health_indicators_to_postgres(
    df: pd.DataFrame,
    database_url: str = DATABASE_URL,
    schema: str = "raw",
    table_name: str = "health_indicators",
) -> None:
    engine = create_engine(database_url)
    with engine.begin() as connection:
        connection.execute(text(f"create schema if not exists {schema}"))
        df.to_sql(
            table_name,
            connection,
            schema=schema,
            if_exists="replace",
            index=False,
        )
