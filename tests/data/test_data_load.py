from garmin.data.data_load import rename_df_columns, transform_dataframe,import_file
import pytest


@pytest.mark.fast
def test_import_filter_columns_success(load_appropriate_garmin_df):
    df = load_appropriate_garmin_df
    df = rename_df_columns(df)
    assert "AVERAGE_PACE" in df.columns


def test_import_filter_columns_fail(load_wrong_header_garmin_df):
    df = load_wrong_header_garmin_df
    with pytest.raises(KeyError):
        df = rename_df_columns(df)


def test_transform_dataframe(load_appropriate_garmin_df):
    df = rename_df_columns(load_appropriate_garmin_df)
    df = transform_dataframe(df)
    additional_columns = ["HOUR","MONTH","SPEED","PACE_FLOAT"]
    for col in additional_columns:
        assert col in df.columns

def test_import_file_fail(get_missing_value_garmin_csv_file):
    with pytest.raises(ValueError):
        import_file(get_missing_value_garmin_csv_file)