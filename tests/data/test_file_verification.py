from garmin.data.file_verification import (
    analyze_lines,
    validate_file_type,
    validate_csv_file,
    validate_structure_of_csv_file,
    check_for_valid_container,
)
import pytest


def test_check_for_valid_container_iterable_no_container():
    container = "container"
    assert not check_for_valid_container(container)


def test_check_for_valid_container_iterable_empty_container():
    container = set()
    assert not check_for_valid_container(container)


def test_check_for_valid_container_iterable_container():
    container = ["1", "4", "7"]
    assert check_for_valid_container(container)


def test_analyze_lines_different_amount_per_lines():
    lines = ["1,3,4", "1,34"]
    assert not analyze_lines(lines)


def test_analyze_lines_wrong_delimiter():
    lines = ["1;3;4", "1,3;4;5"]
    assert not analyze_lines(lines)


def test_analyze_lines_success():
    lines = ["1,3,4", "1,3,4"]
    assert analyze_lines(lines)


def test_validate_csv_file_type_success(get_missing_value_garmin_csv_file):
    assert validate_file_type(get_missing_value_garmin_csv_file)


def test_validate_csv_file_type_incorrect(get_empty_text_file):
    assert not validate_file_type(get_empty_text_file)


def test_validate_structure_of_csv_file_incorrect(get_missing_value_garmin_csv_file):
    assert not validate_structure_of_csv_file(get_missing_value_garmin_csv_file)


def test_validate_csv_file_failure(get_missing_value_garmin_csv_file):
    with pytest.raises(ValueError):
        validate_csv_file(get_missing_value_garmin_csv_file)

def test_validate_csv_success(get_activity_file):
    assert validate_csv_file(get_activity_file)