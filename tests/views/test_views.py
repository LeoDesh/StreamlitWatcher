from unittest.mock import patch

import pytest
from streamlit.testing.v1 import AppTest

import garmin.streamlit_helpers.load as garmin_load
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
page_files = [
    p for folder in FOLDERS for p in folder.glob("*.py") if p.stem == "0__home"
]


@pytest.mark.streamlit
@pytest.mark.parametrize(
    "page_file", page_files, ids=lambda p: str(p.relative_to(VIEW_FOLDER))
)
def test_streamlit_pages(page_file: str):
    df_running = load_running_data(EXAMPLE_PATH / "Activities.csv")
    df_activity = load_activity_file(EXAMPLE_PATH / "Activities.csv")
    df_records = load_records_file(EXAMPLE_PATH / "PersonalRecords.csv", df_activity)
    df_steps = load_steps_file(EXAMPLE_PATH / "Steps.csv")

    # 2. Wir patchen das bereits importierte Modul-Objekt direkt im sys.modules Cache.
    # Das zwingt Streamlits AppTest, diese präparierte Instanz zu verwenden.
    with (
        patch.object(garmin_load, "load_running_df", return_value=df_running),
        patch.object(garmin_load, "load_activity_df", return_value=df_activity),
        patch.object(garmin_load, "load_records_df", return_value=df_records),
        patch.object(garmin_load, "load_steps_df", return_value=df_steps),
        patch("sys.argv", ["../../app.py"]),
    ):
        at = AppTest.from_file("../../app.py")
        # used to not track the page, in my logging
        at.session_state["is_automated_test"] = True
        at.run()
        at.switch_page(page_file)
        at.run()
    assert not at.exception, f"Error on '{page_file}': {at.exception}"
