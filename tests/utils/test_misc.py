from garmin.utils.misc import (
    parse_str_int,
    get_regex_match,
    get_all_regex_matches,
    transform_str_to_date,
    calculate_bins_from_min_max_value,
    replace_comma_in_number,
    verify_activity_duration,
    parse_activity_duration_to_minutes,
    calculate_minutes,
    parse_hours_from_activity_duration,
    parse_minutes_from_activity_duration,
    parse_seconds_from_activity_duration,
    transform_activity_minutes_to_duration_format,
    search_with_regex,
)
import pytest
from datetime import datetime
import sys 
print(sys.path)

def test_parse_str_int_identity():
    value = 5
    assert parse_str_int(value) == 5


def test_parse_str_int_str_with_comma():
    value = "5,453"
    parsed_value = parse_str_int(value)
    assert parsed_value == 5453


def test_get_all_regex_match(get_regex_text):
    text = get_regex_text
    pattern = r"\d{3}"
    assert get_all_regex_matches(pattern, text) == list(text.split(" "))


def test_get_all_regex_match_empty(get_regex_text):
    text = get_regex_text
    pattern = r"\d{4}"
    assert get_all_regex_matches(pattern, text) == []


def test_get_regex_match(get_regex_text):
    text = get_regex_text
    pattern = r"\d{3}"
    idx = 1
    assert get_regex_match(pattern, text, idx) == "343"


def test_get_regex_match_failure(get_regex_text):
    text = get_regex_text
    pattern = r"\d{4}"
    idx = 2
    with pytest.raises(IndexError):
        get_regex_match(pattern, text, idx) == "343"


def test_search_with_regex_default(get_regex_text):
    text = get_regex_text
    pattern = r"(\d{3})\s\d{3}\s(\d{3})"
    assert search_with_regex(pattern, text) == text


def test_search_with_regex_with_idx(get_regex_text):
    text = get_regex_text
    pattern = r"(\d{3})\s\d{3}\s(\d{3})"
    assert search_with_regex(pattern, text, 1) == "545"


def test_search_with_regex_out_of_range(get_regex_text):
    text = get_regex_text
    pattern = r"(\d{3})\s\d{3}\s(\d{3})"
    with pytest.raises(IndexError):
        search_with_regex(pattern, text, 4)


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


def test_transform_number_to_comma():
    line = 'Laufen,"10,454",10,654,87'
    new_line = replace_comma_in_number(line)
    assert new_line == 'Laufen,"10454",10654,87'


def test_transform_number_to_comma_untouched():
    line = 'Laufen,"10,454",10,45,87'
    new_line = replace_comma_in_number(line)
    assert new_line == 'Laufen,"10454",10,45,87'


def test_transform_number_to_comma_side_effect():
    line = 'Laufen,"10,454",10,45,874'
    new_line = replace_comma_in_number(line)
    assert new_line == 'Laufen,"10454",10,45874'


def test_verify_duration_correct(get_duration_str):
    assert verify_activity_duration(get_duration_str)


def test_verify_duration_minutes_part_incorrect():
    duration_str = "04:61:56.8"
    assert not verify_activity_duration(duration_str)


def test_verify_duration_seconds_part_incorrect():
    duration_str = "04:51:65.8"
    assert not verify_activity_duration(duration_str)


def test_verify_duration_without_dot():
    duration_str = "04:51:54"
    assert verify_activity_duration(duration_str)


def test_parse_hours_from_activity_duration(get_duration_str):
    assert parse_hours_from_activity_duration(get_duration_str) == 4


def test_parse_minutes_from_activity_duration(get_duration_str):
    assert parse_minutes_from_activity_duration(get_duration_str) == 2


def test_parse_seconds_from_activity_duration(get_duration_str):
    assert parse_seconds_from_activity_duration(get_duration_str) == 56

def test_calculate_minutes():
    hours,minutes,seconds = (2,54,40)
    assert calculate_minutes(hours,minutes,seconds) == pytest.approx(174.66667)

def test_parse_activity_duration_to_minutes(get_duration_str):
    assert parse_activity_duration_to_minutes(get_duration_str) == pytest.approx(242.93333)
    #"04:02:56.8"

def test_transform_activity_minutes_to_duration_format(get_duration_str):
    duration_in_minutes = parse_activity_duration_to_minutes(get_duration_str)
    assert transform_activity_minutes_to_duration_format(duration_in_minutes) == "04:02:56"