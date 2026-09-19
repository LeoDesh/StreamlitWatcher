from contextlib import nullcontext

import pytest

from garmin.utils.misc import (
    calculate_minutes,
    compute_delta,
    find_regex_match,
    get_all_regex_matches,
    parse_steps_number,
    replace_comma_in_number,
)

REGEX_TEXT = "545 343 754"


@pytest.mark.misc
def test_parse_steps_number_identity():
    value = 5
    assert parse_steps_number(value) == 5


@pytest.mark.misc
def test_parse_steps_number_str_with_comma():
    value = "5,453"
    parsed_value = parse_steps_number(value)
    assert parsed_value == 5453


@pytest.mark.misc
@pytest.mark.parametrize(
    "pattern,expected",
    [
        (r"\d{3}", list(REGEX_TEXT.split())),  # simply get all numbers
        (r"\d{4}", []),  # nothing found, empty list
    ],
)
def test_get_all_regex_match(pattern: str, expected: list[str]):
    assert get_all_regex_matches(pattern, REGEX_TEXT) == expected


@pytest.mark.misc
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
def test_find_regex_match(pattern: str, idx: int, expected: str, expected_context):
    with expected_context:
        assert find_regex_match(pattern, REGEX_TEXT, idx) == expected


@pytest.mark.misc
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


@pytest.mark.misc
def test_calculate_minutes():
    hours, minutes, seconds = (2, 54, 40)
    assert calculate_minutes(hours, minutes, seconds) == pytest.approx(174.66667)


@pytest.mark.misc
@pytest.mark.parametrize(
    "src,trg,expected",
    [
        (100, 100, 0.0),
        (200, 100, -50),
        (100, 200, 100),
        (100, 0, -100),
        (0, 100, 100),
        (0, 0, 0),
    ],
)
def test_compute_delta(src: float, trg: float, expected: float):
    assert compute_delta(src, trg) == expected
