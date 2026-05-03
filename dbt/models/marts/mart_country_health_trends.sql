select
    country,
    iso_code,
    year,
    life_expectancy,
    diabetes_prevalence,
    obesity_rate,
    health_spending_per_capita,
    gdp_per_capita,
    round(
        diabetes_prevalence * 0.45
        + obesity_rate * 0.35
        - life_expectancy * 0.05,
        2
    ) as health_risk_score
from {{ ref('stg_health_indicators') }}
