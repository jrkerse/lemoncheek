with
    source as (select * from {{ source("raw_usda", "food_nutrient_conversion_factor") }}),

    preprocessed as (
        select
            id::bigint as id,
            fdc_id::bigint as fdc_id
        from source
    )

select * from preprocessed