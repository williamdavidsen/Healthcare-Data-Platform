from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import add_health_risk_score, correlation_matrix
from src.config import PROCESSED_DATASET, SAMPLE_DATASET
from src.validation import validate_health_indicators

st.set_page_config(page_title="Healthcare Data Platform", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    path = PROCESSED_DATASET if PROCESSED_DATASET.exists() else SAMPLE_DATASET
    df = pd.read_csv(path)
    validate_health_indicators(df)
    return add_health_risk_score(df)


df = load_data()

st.title("Healthcare Data Platform")

countries = sorted(df["country"].unique())
selected_countries = st.sidebar.multiselect(
    "Countries",
    options=countries,
    default=countries,
)

year_min = int(df["year"].min())
year_max = int(df["year"].max())
selected_years = st.sidebar.slider("Year range", year_min, year_max, (year_min, year_max))

filtered = df[
    df["country"].isin(selected_countries)
    & df["year"].between(selected_years[0], selected_years[1])
]

metric_options = {
    "Life expectancy": "life_expectancy",
    "Diabetes prevalence": "diabetes_prevalence",
    "Obesity rate": "obesity_rate",
    "Health spending per capita": "health_spending_per_capita",
    "GDP per capita": "gdp_per_capita",
    "Health risk score": "health_risk_score",
}

metric_label = st.selectbox("Trend metric", list(metric_options.keys()))
metric = metric_options[metric_label]

left, right = st.columns(2)

with left:
    st.plotly_chart(
        px.line(
            filtered,
            x="year",
            y=metric,
            color="country",
            markers=True,
            title=f"{metric_label} over time",
        ),
        use_container_width=True,
    )

with right:
    latest_year = int(filtered["year"].max()) if not filtered.empty else year_max
    latest = filtered[filtered["year"] == latest_year]
    st.plotly_chart(
        px.bar(
            latest,
            x="country",
            y=metric,
            title=f"{metric_label} by country in {latest_year}",
        ),
        use_container_width=True,
    )

st.plotly_chart(
    px.imshow(
        correlation_matrix(filtered),
        text_auto=True,
        title="Indicator correlation matrix",
        aspect="auto",
    ),
    use_container_width=True,
)

st.dataframe(filtered.sort_values(["country", "year"]), use_container_width=True)
