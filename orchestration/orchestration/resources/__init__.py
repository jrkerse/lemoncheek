from dagster import EnvVar
from dagster_duckdb import DuckDBResource
from dagster_dbt import DbtCliResource

from ..assets.constants import DBT_DIRECTORY

database_resource = DuckDBResource(
    database=EnvVar("DUCKDB_DATABASE"),
)

dbt_resource = DbtCliResource(project_dir=DBT_DIRECTORY)