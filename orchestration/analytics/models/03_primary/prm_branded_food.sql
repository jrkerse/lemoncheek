{{ config(materialized='table') }}

with
    branded_food as (select * from {{  ref("int_branded_food") }}),
    food_nutrient as (select * from {{ ref("int_food_nutrient")  }}),
    nutrient as (select * from {{ ref("stg_nutrient") }}),

    joined as (
        select
            bf.fdc_id as fdc_id,
            bf.brand_owner as brand_owner,
            bf.brand_name as brand_name,
            bf.subbrand_name as subbrand_name,
            bf.ingredients as ingredients,
            n.name as nutrient,
            fn.amount as nutrient_amount,
            n.unit_name as unit_name,
            n.id as nutrient_id,
            n.nutrient_nbr as nutrient_nbr,
            n.rank as nutrient_rank
        from branded_food bf
            inner join food_nutrient fn
                on bf.fdc_id=fn.fdc_id
            inner join nutrient n
                on n.id=fn.nutrient_id
    )

select * from joined
order by fdc_id, nutrient_rank