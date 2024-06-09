with
    food as (select * from {{  ref("int_food") }}),
    branded_food as (select * from {{  ref("stg_branded_food") }}),

    final as (
        select
            f.fdc_id as fdc_id,
            data_type,
            description,
            food_category_id,
            publication_date,
            brand_owner,
            brand_name,
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
            modified_date,
            available_date,
            market_country,
            discontinued_date,
            preparation_state_code,
            trade_channel,
            short_description
        from food f
            inner join branded_food bf
            on f.fdc_id=bf.fdc_id
    )

select * from final