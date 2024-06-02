from dagster import Definitions, load_assets_from_modules

from .assets import usda
from .resources import database_resource

usda_assets = load_assets_from_modules([usda])

defs = Definitions(
    assets=usda_assets,
    resources={
        "database": database_resource,
        # "dbt": dbt_resource
    }
)
