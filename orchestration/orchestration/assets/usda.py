import os
import glob
from typing import Iterator

from dagster import (
    asset,
    AssetKey,
    AssetSpec,
    MetadataValue,
    MaterializeResult,
    AssetExecutionContext,
    Output,
    ObserveResult,
    multi_observable_source_asset,
)
from dagster_duckdb import DuckDBResource
import zipfile
from datetime import datetime, timedelta
import requests

from . import constants

# Warnings cleanup
import warnings
# noinspection PyProtectedMember
from dagster._utils.warnings import ExperimentalWarning

warnings.filterwarnings("ignore", category=ExperimentalWarning)

table_names = [
    # "branded_foods",
    "food",
    "branded_food",
    # "food_attribute",
    # "food_attribute_types",
    "food_calorie_conversion_factor",
    # "food_category",
    # "food_component",
    "food_nutrient",
    "food_nutrient_conversion_factor",
    # "food_nutrient_derivation",
    # "food_nutrient_source",
    "food_portion",
    "foundation_food",
    "nutrient"
]

table_names_to_asset_keys = {
    table_name: AssetKey(f"usda_{table_name.lower()}")
    for table_name in table_names
}
asset_keys_to_table_names = {v: k for k, v in table_names_to_asset_keys.items()}

asset_specs = [
    AssetSpec(
        key=table_names_to_asset_keys[table_name],
        deps=["usda_extracted_files"],
        description=f"USDA {table_name} table (synced)",
    )
    for table_name in table_names
]


@asset(
    group_name="raw",
    compute_kind="Python",
)
def usda_raw_files(context: AssetExecutionContext) -> Output:
    """
    The raw files from the USDA FoodData Central (https://fdc.nal.usda.gov/download-datasets.html)
    """

    local_filename = constants.USDA_FILE_PATH_URL.split('/')[-1]
    full_path = constants.USDA_RAW_FILE_PATH.format(local_filename)

    # TODO: freshness checks
    # Check if the file already exists and if it's fresh
    is_fresh = False
    if os.path.exists(full_path):
        last_modified = datetime.fromtimestamp(os.path.getmtime(full_path))
        if datetime.now() - last_modified < timedelta(days=30):
            context.log.info(f"File {full_path} is found and fresh")
            is_fresh = True

    if not is_fresh:
        with requests.get(constants.USDA_FILE_PATH_URL, stream=True) as r:
            r.raise_for_status()
            with open(full_path, 'wb') as output_file:
                for chunk in r.iter_content(chunk_size=8192):
                    output_file.write(chunk)

    filesize = os.path.getsize(full_path) / (1024 * 1024)  # get size in mb

    return Output(
        full_path,
        metadata={
            "Filesize (MBs)": MetadataValue.float(round(filesize, 2)),
            "Filename": MetadataValue.text(local_filename),
            "Filepath": MetadataValue.path(full_path),
        }
    )


@asset(
    deps=["usda_raw_files"],
    group_name="raw",
    compute_kind="Python",
)
def usda_extracted_files(context: AssetExecutionContext) -> MaterializeResult:
    """
    Extracted files from the bulk .zip download from USDA FoodData Central
    """
    latest_event = context.instance.get_latest_materialization_event(context.asset_key_for_input("usda_raw_files"))
    input_filepath = latest_event.dagster_event.event_specific_data.materialization.metadata["Filepath"].value
    output_filepath = constants.USDA_EXTRACTED_FILE_PATH

    os.makedirs(output_filepath, exist_ok=True)

    with zipfile.ZipFile(input_filepath, "r") as zip_ref:
        zip_ref.extractall(output_filepath)
        extracted_files = zip_ref.namelist()

    return MaterializeResult(
        metadata={
            "Extracted to": MetadataValue.path(output_filepath),
            "Number of files": MetadataValue.int(len(extracted_files)),
            "Extracted files": MetadataValue.json({"files": extracted_files}),
        }
    )


# @asset(
#     deps=["usda_extracted_files"],
#     group_name="source",
#     compute_kind="DuckDB"
# )
# def usda_files(context: AssetExecutionContext, database: DuckDBResource) -> MaterializeResult:
#     """
#     Extract all
#     """
#     # Get list of csv files from the extracted directory
#     raw_files = glob.glob(f"{constants.USDA_EXTRACTED_FILE_PATH}/**/*.csv", recursive=True)
#
#     # loop through each file, creating a table in the resource file location
#     with database.get_connection() as conn:
#         for rf in raw_files:
#             context.log.info(f"Extracting {rf}")
#             filename_ext = os.path.basename(rf)
#             table_name = os.path.splitext(filename_ext)[0]
#             query = f"""
#                 create or replace table {table_name} as (
#                     select *
#                     from read_csv_auto('{rf}', all_varchar=true)
#                 )
#             """
#             conn.execute(query)
#
#     with database.get_connection() as conn:
#         query = "show tables;"
#         tables = conn.execute(query).fetch_df().to_dict("records")
#
#     return MaterializeResult(
#         metadata={
#             "Extracted files": MetadataValue.json({"tables": tables})
#         }
#     )


@multi_observable_source_asset(
    specs=asset_specs,
    group_name="source",
    can_subset=True,
)
def usda_data_sync_assets(context: AssetExecutionContext, database: DuckDBResource) -> Iterator[ObserveResult]:
    with database.get_connection() as conn:
        for table_name in table_names:
            found_table = glob.glob(f"{constants.USDA_EXTRACTED_FILE_PATH}/**/{table_name}.csv", recursive=True)[0]
            query = f"""
                create or replace table {table_name} as (
                    select *
                    from read_csv_auto('{found_table}', all_varchar=true)
                )
            """
            context.log.info(f"Executing query: {query}")
            conn.execute(query)
            yield ObserveResult(
                asset_key=table_names_to_asset_keys[table_name],
                metadata={
                    "Extracted table": MetadataValue.text(table_name)
                }
            )
