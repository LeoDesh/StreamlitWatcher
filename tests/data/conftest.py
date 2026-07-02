from pathlib import Path

import pandas as pd
import pytest

from garmin.data.data_load import read_file

PATH_TO_CSV_FILES = Path("tests/data/files")


@pytest.fixture
def get_activity_file() -> Path:
    return PATH_TO_CSV_FILES / "Activities.csv"


@pytest.fixture
def load_appropriate_garmin_df(get_activity_file) -> pd.DataFrame:
    file_path = get_activity_file
    return read_file(file_path)


@pytest.fixture
def load_wrong_header_garmin_df() -> pd.DataFrame:
    file_path = PATH_TO_CSV_FILES / "ActivitiesWrongHeaders.csv"
    return read_file(file_path)


@pytest.fixture
def get_missing_value_garmin_csv_file() -> Path:
    return PATH_TO_CSV_FILES / "ActivitiesMissing.csv"


@pytest.fixture
def get_empty_text_file() -> Path:
    return PATH_TO_CSV_FILES / "Activities.txt"
