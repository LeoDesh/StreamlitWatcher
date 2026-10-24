import pytest
from streamlit.testing.v1 import AppTest

from garmin.streamlit_helpers.nagivation import VIEW_FOLDER
from garmin.utils.path_utils import get_folders

FOLDERS = [VIEW_FOLDER, *get_folders(VIEW_FOLDER)]
page_files = [p for folder in FOLDERS for p in folder.glob("*.py")]


@pytest.mark.streamlit
@pytest.mark.parametrize(
    "page_file", page_files, ids=lambda p: str(p.relative_to(VIEW_FOLDER))
)
def test_streamlit_pages(page_file: str):
    at = AppTest.from_file("../../app.py")
    at.session_state["is_automated_test"] = True
    at.run()
    at.switch_page(page_file)
    at.run()
    assert not at.exception, f"Error on '{page_file}': {at.exception}"
