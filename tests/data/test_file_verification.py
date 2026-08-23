import pytest

from garmin.etl.file_verification import (
    analyze_lines,
    check_for_valid_container,
    validate_csv_file,
    validate_file_type,
    validate_structure_of_csv_file,
)


@pytest.mark.data
@pytest.mark.parametrize(
    "container,expected",
    [
        ("container", False),
        (set(), False),
        (["1", "4", "7"], True),
    ],
)
def test_check_for_valid_container_iterable_no_container(
    container: str | list | set, expected: bool
):
    assert check_for_valid_container(container) is expected


@pytest.mark.data
@pytest.mark.parametrize(
    "lines,expected",
    [
        (["1,3,4", "1,34"], False),
        (["1;3;4", "1,3;4;5"], False),
        (["1,3,4", "1,3,4"], True),
    ],
)
def test_analyze_lines_different_amount_per_lines(lines: list[str], expected: bool):
    assert analyze_lines(lines) is expected


@pytest.mark.data
def test_validate_csv_file_type_success(get_missing_value_garmin_csv_file):
    assert validate_file_type(get_missing_value_garmin_csv_file)


@pytest.mark.data
def test_validate_csv_file_type_incorrect(get_empty_text_file):
    assert not validate_file_type(get_empty_text_file)


@pytest.mark.data
def test_validate_structure_of_csv_file_incorrect(get_missing_value_garmin_csv_file):
    assert not validate_structure_of_csv_file(get_missing_value_garmin_csv_file)


@pytest.mark.data
def test_validate_csv_file_failure(get_missing_value_garmin_csv_file):
    with pytest.raises(ValueError):
        validate_csv_file(get_missing_value_garmin_csv_file)


@pytest.mark.data
@pytest.mark.xfail(
    reason="Old Format. ',' in Steps probably causing issues compared to new version"
)
def test_validate_csv_success(get_activity_file):
    assert validate_csv_file(get_activity_file)
