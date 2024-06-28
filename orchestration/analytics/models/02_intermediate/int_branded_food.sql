with
    branded_food as (select * from {{  ref("stg_branded_food")  }}),

    subset as (
        select
            fdc_id,
            brand_owner,
            brand_name,
            subbrand_name,
            ingredients,
            serving_size,
            serving_size_unit,
            household_serving_fulltext,
            short_description,
        from stg_branded_food
    )

select * from subset