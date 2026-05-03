select
    country,
    iso_code,
    year,
    life_expectancy,
    diabetes_prevalence,
    obesity_rate,
    health_spending_per_capita,
    gdp_per_capita
from {{ source('raw', 'health_indicators') }}
