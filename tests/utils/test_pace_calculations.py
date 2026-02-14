from garmin.utils.pace_calculations import (
    transform_pace_to_speed,
    transform_pace_to_pace_float,
    transform_pace_float_to_pace,
    verify_pace_format,
    transform_pace_to_minutes_seconds,
    transform_speed_to_pace,
)
import pytest


def test_transform_pace_to_speed():
    pace_str = "5:00"
    assert transform_pace_to_speed(pace_str) == pytest.approx(12)


def test_transform_pace_to_speed_approx():
    pace_str = "5:15"
    assert transform_pace_to_speed(pace_str) == pytest.approx(11.43)


def test_transform_pace_str_to_pace_float():
    pace_str = "4:30"
    assert transform_pace_to_pace_float(pace_str) == pytest.approx(4.5)


def test_transform_pace_float_to_pace_str():
    pace_float = 4.95
    assert transform_pace_float_to_pace(pace_float) == "4:57"


def test_transform_pace_str_pace_float_conversion_cycle():
    pace_float = 4.95
    assert (
        transform_pace_to_pace_float(transform_pace_float_to_pace(pace_float)) == 4.95
    )


def test_transform_pace_float_pace_str_conversion_cycle():
    pace_str = "4:30"
    assert (
        transform_pace_float_to_pace(transform_pace_to_pace_float(pace_str)) == pace_str
    )


def test_transform_speed_to_pace():
    speed = 5.5
    assert transform_speed_to_pace(speed) == "10:54"


def test_verify_pace_format_correct():
    pace_str = "14:53"
    assert verify_pace_format(pace_str)


def test_verify_pace_format_leading_zero_digit():
    pace_str = "04:53"
    assert verify_pace_format(pace_str)


def test_verify_pace_format_incorrect():
    pace_str = "a14:53"
    assert not verify_pace_format(pace_str)
