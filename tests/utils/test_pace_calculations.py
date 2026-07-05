import pytest

from garmin.utils.pace_calculations import (
    transform_pace_float_to_pace,
    transform_pace_to_pace_float,
    transform_pace_to_speed,
    transform_speed_to_pace,
    verify_pace_format,
)


@pytest.mark.pace
@pytest.mark.parametrize(
    "pace_str,expected",
    [
        ("5:00", pytest.approx(12)),
        ("5:15", pytest.approx(11.43)),
    ],
)
def test_transform_pace_to_speed(pace_str: str, expected):
    assert transform_pace_to_speed(pace_str) == expected


@pytest.mark.pace
def test_transform_pace_str_to_pace_float():
    pace_str = "4:30"
    assert transform_pace_to_pace_float(pace_str) == pytest.approx(4.5)


@pytest.mark.pace
def test_transform_pace_float_to_pace_str():
    pace_float = 4.95
    assert transform_pace_float_to_pace(pace_float) == "4:57"


@pytest.mark.pace
def test_transform_pace_str_pace_float_conversion_cycle():
    pace_float = 4.95
    assert (
        transform_pace_to_pace_float(transform_pace_float_to_pace(pace_float)) == 4.95
    )


@pytest.mark.pace
def test_transform_pace_float_pace_str_conversion_cycle():
    pace_str = "4:30"
    assert (
        transform_pace_float_to_pace(transform_pace_to_pace_float(pace_str)) == pace_str
    )


@pytest.mark.pace
def test_transform_speed_to_pace():
    speed = 5.5
    assert transform_speed_to_pace(speed) == "10:54"


@pytest.mark.pace
@pytest.mark.parametrize(
    "pace_str,expected",
    [
        ("14:53", True),
        ("04:53", True),
        ("a14:53", False),
    ],
)
def test_verify_pace_format_correct(pace_str: str, expected: bool):
    assert verify_pace_format(pace_str) is expected
