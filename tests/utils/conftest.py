from datetime import date
from pathlib import Path

import pytest
from pandas import DataFrame

from garmin.etl.load import read_file


@pytest.fixture
def get_regex_text() -> str:
    return "545 343 754"


@pytest.fixture
def get_duration_str() -> str:
    return "04:02:56.8"


@pytest.fixture
def mock_get_current_date(monkeypatch):
    monkeypatch.setattr(
        "garmin.utils.time_utils.get_current_date",
        lambda *args, **kwargs: date(2026, 7, 4),
    )


@pytest.fixture(scope="session")
def get_test_data() -> DataFrame:
    return read_file(Path("tests/utils/test_data.csv"))


@pytest.fixture
def get_test_path(tmp_path) -> Path:
    """Creates a folder structure simulating the view"""
    outside_dir = tmp_path / "outside"
    base_dir = tmp_path / "views"
    running_dir = base_dir / "1__Running"
    steps_dir = base_dir / "2__Steps"
    folders = [outside_dir, base_dir, running_dir, steps_dir]
    for folder in folders:
        folder.mkdir()

    # 2. Populate files
    (running_dir / "1__running.py").touch()
    (running_dir / "2__running__distance.py").touch()
    (running_dir / "3__pace.py").touch()
    (outside_dir / "4_test.py").touch()
    (outside_dir / "utils.py").touch()
    (base_dir / "1__t.txt").touch()
    (outside_dir / "x__t.txt").touch()

    return tmp_path
