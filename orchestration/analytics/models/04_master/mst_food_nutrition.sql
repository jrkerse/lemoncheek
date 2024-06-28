{{ config(
    materialized='table'
) }}

with
    branded_food as (select * from {{  ref("prm_branded_food") }}),
    food_nutrient as (select * from {{  ref("stg_food_nutrient") }}),
    calories as (select * from {{  ref("stg_food_calorie_conversion_factor") }}),
    conversion as (select * from {{  ref("stg_food_nutrient_conversion_factor") }}),
    nutrient as (select * from {{ ref("stg_nutrient") }}),

final as (
    select
        bf.fdc_id as fdc_id,
        nutrient_id,
        food_nutrient_conversion_factor_id,
        conv.id as nutrient_conversion_id,
        data_type,
        description,
        food_category_id,
        publication_date,
        brand_owner,
        subbrand_name,
        gtin_upc,
        ingredients,
        not_a_significant_source_of,
        serving_size,
        serving_size_unit,
        household_serving_fulltext,
        branded_food_category,
        data_source,
        package_weight,
        amount
    from branded_food bf
        inner join nutrients n
            on bf.fdc_id=n.fdc_id
        inner join calories c
            on c.food_nutrient_conversion_factor_id=n.nutrient_id
        inner join conversion conv
            on bf.fdc_id=conv.fdc_id

select * from final