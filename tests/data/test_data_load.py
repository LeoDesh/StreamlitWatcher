import pytest

from garmin.data.data_load import (
    import_file,
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
    additional_columns = ["hour", "month", "speed", "pace_float"]
    for col in additional_columns:
        assert col in df.columns


@pytest.mark.data
def test_import_file_fail(get_missing_value_garmin_csv_file):
    with pytest.raises(ValueError):
        import_file(get_missing_value_garmin_csv_file)


@pytest.mark.data
@pytest.mark.parametrize(
    "activity, title, expected",
    [
        ("Cardio", "FB Training 28.05.2024", "Fußball"),
        ("Cardio", "Bad Gams Schwimmen", "Schwimmen"),
        ("Cardio", "Fußball", "Cardio"),
        ("Laufen", "FB Training 28.05.2024", "Laufen"),
        ("Cardio", "Heute Tenis", "Cardio"),
        ("Cardio", "Tennis", "Tennis"),
        ("Cardio", "Padel Tennis", "Tennis"),
    ],
)
def test_transform_activity(activity: str, title: str, expected: str):
    assert transform_activity(activity, title) == expected
