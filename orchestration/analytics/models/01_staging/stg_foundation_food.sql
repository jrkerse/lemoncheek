with source as (select * from {{ source("raw_usda", "foundation_food") }})

select
    fdc_id::bigint as fdc_id,
    ndb_number::bigint as ndb_number,
    footnote::varchar as footnote
from source