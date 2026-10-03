import pytest

from garmin.etl.verification import (
    analyze_lines,
    validate_activities_file,
    validate_file_structure,
    validate_file_type,
)


@pytest.mark.etl
@pytest.mark.parametrize(
    "lines,sep,expected",
    [
        (["1,3,4", "1,34"], ",", False),
        (["1;3;4", "1,3;4;5"], ",", False),
        (["1,3,4", "1,3,4"], ",", True),
        ([], ",", False),
        (["1;3,,2;4", "1;3,4;5"], ";", True),
    ],
)
def test_analyze_lines(lines: list[str], sep: str, expected: bool):
    assert analyze_lines(lines, sep) is expected


@pytest.mark.etl
def test_validate_activities_file_type_success(get_missing_value_garmin_csv_file):
    assert validate_file_type(get_missing_value_garmin_csv_file)


@pytest.mark.etl
def test_validate_file_type_incorrect(get_empty_text_file):
    assert not validate_file_type(get_empty_text_file)


@pytest.mark.etl
def test_validate_file_structure_failure(get_missing_value_garmin_csv_file):
    assert not validate_file_structure(get_missing_value_garmin_csv_file)


@pytest.mark.etl
def test_validate_activities_file_failure(get_missing_value_garmin_csv_file):
    with pytest.raises(ValueError):
        validate_activities_file(get_missing_value_garmin_csv_file)


@pytest.mark.etl
def test_validate_activities_file_success(get_activity_file):
    assert validate_activities_file(get_activity_file)
