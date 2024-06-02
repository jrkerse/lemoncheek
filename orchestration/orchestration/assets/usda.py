import os

from dagster import asset, MetadataValue, MaterializeResult, AssetExecutionContext, Output
import zipfile

import requests

from . import constants


@asset(
    group_name="raw_files",
    compute_kind="Python",
)
def usda_raw_files() -> Output:
    """
    The raw files from the USDA FoodData Central (https://fdc.nal.usda.gov/download-datasets.html)
    """

    local_filename = constants.USDA_FILE_PATH_URL.split('/')[-1]
    full_path = constants.USDA_RAW_FILE_PATH.format(local_filename)

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
    group_name="raw_files",
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

    extracted_file_paths = [os.path.join(output_filepath)]

    return MaterializeResult(
        metadata={
            "Extracted to": MetadataValue.path(constants.USDA_EXTRACTED_FILE_PATH),
            "Number of files": MetadataValue.int(len(extracted_files)),
            "Extracted files": MetadataValue.json({"files": extracted_file_paths}),
        }
    )