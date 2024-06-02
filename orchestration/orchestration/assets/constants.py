import os
from pathlib import Path

S3_BUCKET_PREFIX = os.getenv("S3_BUCKET_PREFIX", "")


def get_path_for_env(path: str) -> str:
    """A utility method. Generates a path based on the environment.

    Args:
        path (str): The local path to the file.

    Returns:
        result_path (str): The path to the file, based on the environment.
    """
    if os.getenv("DAGSTER_ENVIRONMENT") == "prod":
        return S3_BUCKET_PREFIX + path
    else:
        return path


USDA_FILE_PATH_URL = "https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_csv_2024-04-18.zip"
USDA_RAW_FILE_PATH=get_path_for_env("data/raw/{}")
USDA_EXTRACTED_FILE_PATH = get_path_for_env("data/raw/extract")

# DBT
DBT_DIRECTORY = Path(__file__).joinpath("..", "..", "..", "analytics").resolve()