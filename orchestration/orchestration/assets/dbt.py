import os
from dagster import AssetExecutionContext, AssetKey
from dagster_dbt import dbt_assets, DbtCliResource, DagsterDbtTranslator

from .constants import DBT_DIRECTORY
from ..resources import dbt_resource


class CustomDagsterDbtTranslator(DagsterDbtTranslator):

    def get_asset_key(self, dbt_resource_props):
        resource_type = dbt_resource_props["resource_type"]
        name = dbt_resource_props["name"]
        if resource_type == "source":
            return AssetKey(f"usda_{name}")
        else:
            return super().get_asset_key(dbt_resource_props)


# Builds the dbt manifest
dbt_resource.cli(["--quiet", "parse"]).wait()


if os.getenv("DAGSTER_DBT_PARSE_PROJECT_ON_LOAD"):
    dbt_manifest_path = (
        dbt_resource.cli(["--quiet", "parse"])
        .wait()
        .target_path.joinpath("manifest.json")
    )
else:
    dbt_manifest_path = DBT_DIRECTORY.joinpath("target", "manifest.json")


@dbt_assets(
    manifest=dbt_manifest_path,
    dagster_dbt_translator=CustomDagsterDbtTranslator()
)
def dbt_analytics(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()
