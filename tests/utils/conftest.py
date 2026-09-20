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
