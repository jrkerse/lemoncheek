with
    source as (select * from {{ ref("stg_food")}}),

    ranked as (
        select
            fdc_id,
            data_type,
            description,
            food_category_id,
            publication_date,
            row_number() over (partition by data_type, description order by publication_date desc) as rn
        from source
        where 1=1
            and data_type in ('foundation_food', 'branded_food')
    ),

    final as (
        select
            fdc_id,
            data_type,
            description,
            food_category_id,
            publication_date
        from ranked
        where 1=1
            and rn = 1
    )

select * from final
