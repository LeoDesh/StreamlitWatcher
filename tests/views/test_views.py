import pytest
from streamlit.testing.v1 import AppTest

from streamlit_utils.nagivation import VIEW_FOLDER, get_folders

FOLDERS = [VIEW_FOLDER, *get_folders(VIEW_FOLDER)]
page_files = [str(p) for folder in FOLDERS for p in folder.glob("*.py")]


@pytest.mark.streamlit
@pytest.mark.parametrize("page_file", page_files)
def test_streamlit_pages(page_file: str):
    at = AppTest.from_file("app.py").run()

    # Simuliere den Wechsel auf die dynamische Unterseite
    at.switch_page(page_file)
    at.run()

    # Überprüfe, ob während des Renderns eine Exception geworfen wurde
    assert not at.exception, f"Error on '{page_file}': {at.exception}"
