import os
import glob

from dagster import (
    asset,
    MetadataValue,
    MaterializeResult,
    AssetExecutionContext,
    Output
)
from dagster_duckdb import DuckDBResource
import zipfile
from datetime import datetime, timedelta
import requests

from . import constants


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


@asset(
    deps=["usda_extracted_files"],
    group_name="source",
    compute_kind="DuckDB"
)
def usda_files(context: AssetExecutionContext, database: DuckDBResource) -> MaterializeResult:
    """
    Extract all
    """
    # Get list of csv files from the extracted directory
    raw_files = glob.glob(f"{constants.USDA_EXTRACTED_FILE_PATH}/**/*.csv", recursive=True)

    # loop through each file, creating a table in the resource file location
    with database.get_connection() as conn:
        for rf in raw_files:
            context.log.info(f"Extracting {rf}")
            filename_ext = os.path.basename(rf)
            table_name = os.path.splitext(filename_ext)[0]
            query = f"""
                create or replace table {table_name} as (
                    select *
                    from read_csv_auto('{rf}', all_varchar=true)
                )
            """
            conn.execute(query)

    with database.get_connection() as conn:
        query = "show tables;"
        tables = conn.execute(query).fetch_df().to_dict("records")

    return MaterializeResult(
        metadata={
            "Extracted files": MetadataValue.json({"tables": tables})
        }
    )
