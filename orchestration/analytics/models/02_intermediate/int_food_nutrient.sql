with food_nutrient as (select * from {{ ref("stg_food_nutrient") }}),

     subset as (
         select
            fdc_id,
            nutrient_id,
            amount
         from food_nutrient
     )

select * from subset