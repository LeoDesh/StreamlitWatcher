import pytest

from garmin.etl.data_load import (
    add_distance,
    add_pace,
    load_activity_file,
    rename_df_columns,
    transform_activity,
    transform_dataframe,
)


@pytest.mark.data
def test_import_filter_columns_success(load_appropriate_garmin_df):
    df = load_appropriate_garmin_df
    df = rename_df_columns(df)
    assert "average_pace" in df.columns


@pytest.mark.data
def test_import_filter_columns_fail(load_wrong_header_garmin_df):
    df = load_wrong_header_garmin_df
    with pytest.raises(KeyError):
        df = rename_df_columns(df)


@pytest.mark.data
def test_transform_dataframe(load_appropriate_garmin_df):
    df = rename_df_columns(load_appropriate_garmin_df)
    df = transform_dataframe(df)
    additional_columns = [
        "hour",
        "month",
        "speed",
        "pace_float",
        "speed",
        "time_in_minutes",
        "time_in_hours",
    ]
    for col in additional_columns:
        assert col in df.columns


@pytest.mark.data
def test_import_file_fail(get_missing_value_garmin_csv_file):
    with pytest.raises(ValueError):
        load_activity_file(get_missing_value_garmin_csv_file)


@pytest.mark.data
@pytest.mark.parametrize(
    "activity, title, expected",
    [
        ("Cardio", "FB Training 28.05.2024", "Football"),
        ("Cardio", "Bad Gams Schwimmen", "Swimming"),
        ("Cardio", "Fußball", "Cardio"),
        ("Laufen", "FB Training 28.05.2024", "Laufen"),
        ("Cardio", "Heute Tenis", "Cardio"),
        ("Cardio", "Tennis", "Tennis"),
        ("Cardio", "Padel Tennis", "Padel Tennis"),
    ],
)
def test_transform_activity(activity: str, title: str, expected: str):
    assert transform_activity(activity, title) == expected


@pytest.mark.data
@pytest.mark.parametrize(
    "activity,pace,distance,time_in_hours,expected",
    [
        ("Indoor Cycling", "--", 15, 0.5, "2:00"),
        ("Indoor Cycling", "--", 0.0, 0.5, "--"),
    ],
)
def test_add_pace(
    activity: str,
    pace: str,
    distance: float,
    time_in_hours: float,
    expected: str,
):
    assert add_pace(activity, pace, distance, time_in_hours) == expected


@pytest.mark.data
@pytest.mark.parametrize(
    "activity,title,distance,expected",
    [
        ("Indoor Cycling", "21,5 km", 0.0, 21.5),
        ("Indoor Cycling", "24.745 km", 0.0, 24.745),
        ("Indoor Cycling", "Niente", 0.0, 0.0),
        ("Swimming", "Niente", 0.0, 0.0),
        ("Running", "9.45 km", 8.5, 8.5),
    ],
)
def test_add_distance(activity: str, title: str, distance: float, expected: float):
    assert add_distance(activity, title, distance) == expected
