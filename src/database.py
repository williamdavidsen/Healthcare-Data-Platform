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
        if connection.dialect.has_table(connection, table_name, schema=schema):
            connection.execute(text(f"truncate table {schema}.{table_name}"))
            if_exists = "append"
        else:
            if_exists = "fail"
        df.to_sql(
            table_name,
            connection,
            schema=schema,
            if_exists=if_exists,
            index=False,
        )


def read_health_indicators_mart(
    database_url: str = DATABASE_URL,
    schema: str = "analytics",
    table_name: str = "mart_country_health_trends",
) -> pd.DataFrame:
    engine = create_engine(database_url)
    query = f"""
        select
            country,
            iso_code,
            year,
            life_expectancy,
            diabetes_prevalence,
            obesity_rate,
            health_spending_per_capita,
            gdp_per_capita,
            health_risk_score
        from {schema}.{table_name}
    """
    return pd.read_sql_query(query, engine)
