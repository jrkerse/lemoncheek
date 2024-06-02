with
    source as (select * from {{  source("raw_usda", "food" )}}),

    preprocessed as (
        select
            fdc_id,
            data_type,
            description,
            food_category_id,
            case
                when publication_date like '%-%-%'
                then strptime(publication_date, '%Y-%m-%d')::date
                else null
            end as publication_date_1,
            case
                when publication_date like '%/%/%'
                then strptime(publication_date, '%m/%d/%Y')::date
                else null
            end as publication_date_2,
        from source
    )

select
    fdc_id::bigint as fdc_id,
    data_type::varchar as data_type,
    description::varchar as description,
    food_category_id::bigint as food_category_id,
    coalesce(publication_date_1::date, publication_date_2::date) as publication_date,
from preprocessed