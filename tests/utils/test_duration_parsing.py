import pytest

from garmin.utils.duration_parsing import (
    parse_activity_duration_to_minutes,
    parse_hours_from_activity_duration,
    parse_indoor_cycling_title,
    parse_minutes_from_activity_duration,
    parse_seconds_from_activity_duration,
    transform_activity_minutes_to_duration_format,
    verify_activity_duration,
)


@pytest.mark.duration_parsing
def test_parse_hours_from_activity_duration(get_duration_str):
    assert parse_hours_from_activity_duration(get_duration_str) == 4


@pytest.mark.duration_parsing
def test_parse_minutes_from_activity_duration(get_duration_str):
    assert parse_minutes_from_activity_duration(get_duration_str) == 2


@pytest.mark.duration_parsing
def test_parse_seconds_from_activity_duration(get_duration_str):
    assert parse_seconds_from_activity_duration(get_duration_str) == 56


@pytest.mark.duration_parsing
def test_parse_activity_duration_to_minutes(get_duration_str):
    assert parse_activity_duration_to_minutes(get_duration_str) == pytest.approx(
        242.93333
    )
    # "04:02:56.8"


@pytest.mark.duration_parsing
def test_transform_activity_minutes_to_duration_format(get_duration_str):
    duration_in_minutes = parse_activity_duration_to_minutes(get_duration_str)
    assert (
        transform_activity_minutes_to_duration_format(duration_in_minutes) == "04:02:56"
    )


@pytest.mark.duration_parsing
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


@pytest.mark.duration_parsing
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
        ("04:02:56.8", True),  # Ordinary Time
    ],
)
def test_verify_duration_minutes_part_incorrect(duration_str, expected):
    assert verify_activity_duration(duration_str) is expected
