from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

page_files = [str(p) for p in Path("views").glob("*.py")]


@pytest.mark.streamlit
@pytest.mark.parametrize("page_file", page_files)
def test_streamlit_pages(page_file: str):
    at = AppTest.from_file("app.py").run()

    # Simuliere den Wechsel auf die dynamische Unterseite
    at.switch_page(page_file)
    at.run()

    # Überprüfe, ob während des Renderns eine Exception geworfen wurde
    assert not at.exception, f"Error on '{page_file}': {at.exception}"
