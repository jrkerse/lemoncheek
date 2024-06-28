with
    source as (select * from {{ source("raw_usda", "nutrient") }})

select
    id::bigint as id,
    name::varchar as name,
    unit_name::varchar as unit_name,
    nutrient_nbr::int as nutrient_nbr,
    rank::int as rank
from source