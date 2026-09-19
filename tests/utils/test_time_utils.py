from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from garmin.utils.time_utils import transform_str_to_datetime


@pytest.mark.time_utils
def test_transform_str_to_datetime_correct_format():
    date_str = "2025-05-03 18:05:04"
    assert transform_str_to_datetime(date_str) == datetime(
        2025, 5, 3, 18, 5, 4, tzinfo=ZoneInfo("UTC")
    )


@pytest.mark.time_utils
def test_transform_str_to_datetime_failure():
    date_str = "2025.05.03 18:05:04"
    with pytest.raises(ValueError):
        transform_str_to_datetime(date_str)
