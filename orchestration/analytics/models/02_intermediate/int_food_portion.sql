with
    food_portion as (select * from {{ ref("stg_food_portion") }}),

    subset as (
        select
            id,
            fdc_id,
            amount,
            measure_unit_id,
            gram_weight
        from food_portion
    )

select * from food_portion