select
    country,
    iso_code,
    year,
    count(*) as row_count
from {{ ref('mart_country_health_trends') }}
group by country, iso_code, year
having count(*) > 1
