with
    source as (select * from {{ source("raw_usda", "food_portion") }}),

final as (
    select
        id::bigint as id,
        fdc_id::bigint as fdc_id,
        seq_num::int as seq_num,
        amount::float as amount,
        measure_unit_id::bigint as measure_unit_id,
        portion_description::varchar as portion_description,
        modifier::varchar as modifier,
        gram_weight::float as gram_weight,
        data_points::int as data_points,
        footnote::varchar as footnote,
        min_year_acquired::int as min_year_acquired
    from source
)

select * from final