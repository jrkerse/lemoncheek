with
    source as (select * from {{  source("raw_usda", "food_calorie_conversion_factor") }}),

    preprocessed as (
        select
            food_nutrient_conversion_factor_id,
            protein_value::float as protein_value,
            fat_value::float as fat_value,
            carbohydrate_value::float as carbohydrate_value,
        from source
    )

select * from preprocessed