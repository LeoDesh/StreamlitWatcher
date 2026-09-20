from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from garmin.utils.time_utils import (
    get_current_date_str,
    get_current_month,
    get_current_year,
    get_first_of_given_year,
    get_month_previous_year,
    transform_str_to_datetime,
)


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


@pytest.mark.time_utils
def test_get_current_month(mock_get_current_date: None):
    assert get_current_month() == date(2026, 7, 1)


@pytest.mark.time_utils
def testget_current_year(mock_get_current_date: None):
    assert get_current_year() == 2026


@pytest.mark.time_utils
def test_get_month_previous_year(mock_get_current_date: None):
    assert get_month_previous_year() == date(2025, 7, 1)


@pytest.mark.time_utils
def test_get_first_of_given_year():
    assert get_first_of_given_year(2026) == date(2026, 1, 1)


@pytest.mark.time_utils
def test_get_current_date_str(mock_get_current_date: None):
    assert get_current_date_str() == "20260704"
