from dagster import Definitions, load_assets_from_modules

from .assets import usda

usda_assets = load_assets_from_modules([usda])

defs = Definitions(
    assets=usda_assets,
)
