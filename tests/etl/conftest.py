from pathlib import Path

import pandas as pd
import pytest

from garmin.etl.load import load_json, read_file

PATH_TO_TEST_FILES = Path("tests/etl/files")


@pytest.fixture
def get_activity_file() -> Path:
    return PATH_TO_TEST_FILES / "Activities.csv"


@pytest.fixture
def load_appropriate_garmin_df(get_activity_file) -> pd.DataFrame:
    file_path = get_activity_file
    return read_file(file_path)


@pytest.fixture
def load_wrong_header_garmin_df() -> pd.DataFrame:
    file_path = PATH_TO_TEST_FILES / "ActivitiesWrongHeaders.csv"
    return read_file(file_path)


@pytest.fixture
def get_missing_value_garmin_csv_file() -> Path:
    return PATH_TO_TEST_FILES / "ActivitiesMissing.csv"


@pytest.fixture
def get_empty_text_file() -> Path:
    return PATH_TO_TEST_FILES / "Activities.txt"


@pytest.fixture
def get_steps_data() -> list[dict[str, str | float]]:
    return load_json(PATH_TO_TEST_FILES / "steps.json")


@pytest.fixture
def get_records_data() -> list[dict[str, str | float]]:
    return load_json(PATH_TO_TEST_FILES / "records.json")


@pytest.fixture
def get_activity_data() -> list[dict[str, str | float]]:
    return load_json(PATH_TO_TEST_FILES / "activity.json")
