from unittest.mock import MagicMock, patch

import pytest
from pandas import DataFrame
from streamlit.testing.v1 import AppTest

from garmin.etl import (
    load_activity_file,
    load_records_file,
    load_running_data,
    load_steps_file,
)
from garmin.etl.config import EXAMPLE_PATH
from garmin.streamlit_helpers.nagivation import VIEW_FOLDER
from garmin.utils.path_utils import get_folders

FOLDERS = [VIEW_FOLDER, *get_folders(VIEW_FOLDER)]
page_files = [p for folder in FOLDERS for p in folder.glob("*.py")]


def load_running_df() -> DataFrame:
    return load_running_data(EXAMPLE_PATH / "Activities.csv")


def load_activity_df() -> DataFrame:
    return load_activity_file(EXAMPLE_PATH / "Activities.csv")


def load_records_df() -> DataFrame:
    return load_records_file(EXAMPLE_PATH / "PersonalRecords.csv", load_activity_df())


def load_steps_df() -> DataFrame:
    return load_steps_file(EXAMPLE_PATH / "Steps.csv")


@pytest.mark.streamlit
@pytest.mark.parametrize(
    "page_file",
    page_files,
    ids=lambda p: str(p.relative_to(VIEW_FOLDER)),
)
def test_streamlit_pages(page_file):
    running_load = MagicMock(return_value=load_running_df())
    activity_load = MagicMock(return_value=load_activity_df())
    records_load = MagicMock(return_value=load_records_df())
    steps_load = MagicMock(return_value=load_steps_df())

    with (
        patch("sys.argv", ["../../app.py"]),
        patch.multiple(
            "garmin.streamlit_helpers.load",
            load_running_df=running_load,
            load_activity_df=activity_load,
            load_records_df=records_load,
            load_steps_df=steps_load,
        ),
        patch.multiple(
            "garmin.streamlit_helpers.nagivation",
            load_activity_df=activity_load,
            load_running_df=running_load,
        ),
    ):
        at = AppTest.from_file("../../app.py")
        at.session_state["is_automated_test"] = True
        at.run()
        at.switch_page(str(page_file))
        at.run()

    assert not at.exception, f"Error on '{page_file}': {at.exception}"
