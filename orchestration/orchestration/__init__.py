from dagster import Definitions, load_assets_from_modules

from .assets import usda, dbt
from .resources import database_resource, dbt_resource

usda_assets = load_assets_from_modules([usda])
dbt_analytics_assets = load_assets_from_modules(modules=[dbt])

defs = Definitions(
    assets=usda_assets + dbt_analytics_assets,
    resources={
        "database": database_resource,
        "dbt": dbt_resource
    }
)
