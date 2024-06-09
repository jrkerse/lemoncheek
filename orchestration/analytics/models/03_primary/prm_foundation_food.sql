with
    food as (select * from {{  ref("int_food") }}),
    foundation_food as (select * from {{ ref("stg_foundation_food") }}),

    final as (
        select
            f.fdc_id as fdc_id,
            ndb_number,
            data_type,
            description,
            food_category_id,
            footnote,
            publication_date
        from foundation_food ff
            inner join food f
            on ff.fdc_id=f.fdc_id
    )

select * from final
