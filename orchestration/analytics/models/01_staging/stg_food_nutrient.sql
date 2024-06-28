with source as (select * from {{source("raw_usda", "food_nutrient") }})

select
    id::bigint as id,
    fdc_id::bigint as fdc_id,
    nutrient_id::bigint as nutrient_id,
    amount::float as amount,
    data_points::int as data_points,
    derivation_id::int as derivation_id,
    min::float as min_value,
    max::float as max_value,
    median::float as median_value,
    loq::float as loq,
    footnote::varchar as footnote,
    min_year_acquired::int as min_year_acquired,
    percent_daily_value::float as percent_daily_value
from source
