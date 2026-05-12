select *
from {{ ref('mart_country_health_trends') }}
where
    life_expectancy < 0
    or life_expectancy > 130
    or diabetes_prevalence < 0
    or diabetes_prevalence > 100
    or obesity_rate < 0
    or obesity_rate > 100
    or health_spending_per_capita < 0
    or gdp_per_capita < 0
    or health_risk_score < -10
    or health_risk_score > 100
