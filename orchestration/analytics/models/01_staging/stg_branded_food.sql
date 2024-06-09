with
    source as (select * from {{ source("raw_usda", "branded_food") }}),

final as (
    select
        fdc_id::bigint as fdc_id,
        brand_owner::varchar as brand_owner,
        brand_name::varchar as brand_name,
        subbrand_name::varchar as subbrand_name,
        gtin_upc::varchar as gtin_upc,
        ingredients::varchar as ingredients,
        not_a_significant_source_of::varchar as not_a_significant_source_of,
        serving_size::varchar as serving_size,
        serving_size_unit::varchar as serving_size_unit,
        household_serving_fulltext::varchar as household_serving_fulltext,
        branded_food_category::varchar as branded_food_category,
        data_source::varchar as data_source,
        package_weight::varchar as package_weight,
        modified_date::date as modified_date,
        available_date::date as available_date,
        market_country::varchar as market_country,
        discontinued_date::date as discontinued_date,
        preparation_state_code::varchar as preparation_state_code,
        trade_channel::varchar as trade_channel,
        short_description::varchar as short_description
    from source
)

select * from final