from contextlib import nullcontext
from datetime import datetime

import pytest

from garmin.utils.misc import (
    calculate_bins_from_min_max_value,
    calculate_minutes,
    get_all_regex_matches,
    get_regex_match,
    parse_activity_duration_to_minutes,
    parse_hours_from_activity_duration,
    parse_indoor_cycling_title,
    parse_minutes_from_activity_duration,
    parse_seconds_from_activity_duration,
    parse_str_to_int,
    replace_comma_in_number,
    search_with_regex,
    transform_activity_minutes_to_duration_format,
    transform_str_to_date,
    verify_activity_duration,
)

REGEX_TEXT = "545 343 754"


def test_parse_str_to_int_identity():
    value = 5
    assert parse_str_to_int(value) == 5


def test_parse_str_to_int_str_with_comma():
    value = "5,453"
    parsed_value = parse_str_to_int(value)
    assert parsed_value == 5453


@pytest.mark.parametrize(
    "pattern,expected",
    [
        (r"\d{3}", list(REGEX_TEXT.split())),  # simply get all numbers
        (r"\d{4}", []),  # nothing found, empty list
    ],
)
def test_get_all_regex_match(pattern: str, expected: list[str]):
    assert get_all_regex_matches(pattern, REGEX_TEXT) == expected


@pytest.mark.parametrize(
    "pattern,idx,expected,expected_context",
    [
        (
            r"\d{3}",
            1,
            "343",
            nullcontext(),
        ),  # simply get all numbers
        (
            r"\d{3}",
            3,
            "343",
            pytest.raises(IndexError),
        ),  # not enough matches
        (
            r"\d{4}",
            0,
            "545",
            pytest.raises(IndexError),
        ),  # no match
    ],
)
def test_get_regex_match(pattern: str, idx: int, expected: str, expected_context):
    with expected_context:
        value = get_regex_match(pattern, REGEX_TEXT, idx)
        assert value == expected


@pytest.mark.parametrize(
    "pattern,idx,expected,expected_context",
    [
        (
            r"(\d{3})\s\d{3}\s(\d{3})",
            0,
            REGEX_TEXT,
            nullcontext(),
        ),  # full string
        (
            r"(\d{3})\s\d{3}\s(\d{3})",
            1,
            "545",
            nullcontext(),
        ),  # first match
        (
            r"(\d{3})\s\d{3}\s(\d{3})",
            4,
            None,
            pytest.raises(IndexError),
        ),  # not enough matched values
    ],
)
def test_search_with_regex(pattern: str, idx: int, expected: str, expected_context):
    with expected_context:
        assert search_with_regex(pattern, REGEX_TEXT, idx) == expected


def test_transform_str_to_date_correct_format():
    date_str = "2025-05-03 18:05:04"
    assert transform_str_to_date(date_str) == datetime(2025, 5, 3, 18, 5, 4)


def test_transform_str_to_date_failure():
    date_str = "2025.05.03 18:05:04"
    with pytest.raises(ValueError):
        transform_str_to_date(date_str)


def test_calculate_bins_values_from_min_max():
    bins = 5
    min_value = 1
    max_value = 6
    assert calculate_bins_from_min_max_value(min_value, max_value, bins) == list(
        range(1, 7)
    )


@pytest.mark.parametrize(
    "line,expected",
    [
        (
            'Laufen,"10,454",10,654,87',
            'Laufen,"10454",10654,87',
        ),  # Transform Number to comma
        (
            'Laufen,"10,454",10,45,87',
            'Laufen,"10454",10,45,87',
        ),  # Transform First Number, Second remains untouched
        (
            'Laufen,"10,454",10,45,874',
            'Laufen,"10454",10,45874',
        ),  # Transform First Number, Sideeffect for Second number
    ],
)
def test_transform_number_to_comma(line: str, expected: str):
    assert replace_comma_in_number(line) == expected


def test_verify_duration_correct(get_duration_str):
    assert verify_activity_duration(get_duration_str)


@pytest.mark.parametrize(
    "duration_str,expected",
    [
        ("04:61:56.8", False),  # Minutes Part incorrect
        ("04:51:65.8", False),  # Seconds Part incorrect
        ("04:51:54", True),  # Simple Time Display
        ("04:51:60", True),  # Full 60 Seconds Fine, if no dot
        ("04:51:60.5", False),  # Cannot be 60 seconds and a bit
        ("04:60:00", True),  # Full 60 Minutes Fine, if no seconds
        ("04:60:01.5", False),  # Cannot be 60 Minutes and a second
        ("04:60:00.0", True),  # Full 60 Minutes Fine, if no seconds, hundreth
    ],
)
def test_verify_duration_minutes_part_incorrect(duration_str, expected):
    assert verify_activity_duration(duration_str) is expected


def test_parse_hours_from_activity_duration(get_duration_str):
    assert parse_hours_from_activity_duration(get_duration_str) == 4


def test_parse_minutes_from_activity_duration(get_duration_str):
    assert parse_minutes_from_activity_duration(get_duration_str) == 2


def test_parse_seconds_from_activity_duration(get_duration_str):
    assert parse_seconds_from_activity_duration(get_duration_str) == 56


def test_calculate_minutes():
    hours, minutes, seconds = (2, 54, 40)
    assert calculate_minutes(hours, minutes, seconds) == pytest.approx(174.66667)


def test_parse_activity_duration_to_minutes(get_duration_str):
    assert parse_activity_duration_to_minutes(get_duration_str) == pytest.approx(
        242.93333
    )
    # "04:02:56.8"


def test_transform_activity_minutes_to_duration_format(get_duration_str):
    duration_in_minutes = parse_activity_duration_to_minutes(get_duration_str)
    assert (
        transform_activity_minutes_to_duration_format(duration_in_minutes) == "04:02:56"
    )


@pytest.mark.parametrize(
    "title,expected",
    [
        ("24,5 km", 24.5),
        ("23 km", 23),
        ("km", ""),
        ("27.5 KM", 27.5),
        ("Something Else", ""),
        ("Something 28", ""),
    ],
)
def test_parse_indoor_cycling_title(title: str, expected: str | float):
    assert parse_indoor_cycling_title(title) == expected
