import pytest
from pandas import DataFrame

from garmin.utils.pandas_helpers import (
    aggregate_df_named_column,
    aggregrate_df_by_dict,
    extend_df_by_columns,
    extend_df_by_id,
    filter_dataframe,
)


@pytest.mark.pandas_helpers
def test_filter_dataframe_value(get_test_data: DataFrame):
    df = get_test_data.copy()
    filters = {"Datum": "2026-01-01", "Menge": 2}
    df = filter_dataframe(df, filters)
    assert len(df) == 2


@pytest.mark.pandas_helpers
def test_filter_dataframe_list(get_test_data: DataFrame):
    df = get_test_data.copy()
    filters = {"Datum": ["2026-01-01", "2026-01-02"], "Menge": [1, 2, 3, 4]}
    df = filter_dataframe(df, filters)
    assert len(df) == 6


@pytest.mark.pandas_helpers
def test_aggregate_df_named_column(get_test_data: DataFrame):
    df = get_test_data.copy()
    filters = {"Datum": ["2026-01-01", "2026-01-02"]}
    df = filter_dataframe(df, filters)
    df = aggregate_df_named_column(
        df, groupby_col="Datum", value_col="Umsatz", col_name="Anzahl", agg_func="count"
    )
    assert list(df.columns) == ["Datum", "Anzahl"]
    assert len(df) == 2
    _, revenue = df.loc[0, :]
    assert revenue == 10


@pytest.mark.pandas_helpers
def test_aggregrate_df_by_dict(get_test_data: DataFrame):
    df = get_test_data.copy()
    filters = {"Datum": ["2026-01-01", "2026-01-02"]}
    df = filter_dataframe(df, filters)
    aggregation_mapping = {"Umsatz": ("Umsatz", "sum")}
    df = aggregrate_df_by_dict(
        df, groupby_col="Datum", aggregation_mapping=aggregation_mapping
    )
    assert list(df.columns) == ["Datum", "Umsatz"]
    assert len(df) == 2
    _, revenue = df.loc[0, :]
    assert revenue == 31460.95


@pytest.mark.pandas_helpers
def test_extend_df_by_id(get_test_data: DataFrame):
    # 3 Distinct column values (Datum), therefore only 3 rows
    df = get_test_data.copy()
    current_df = filter_dataframe(df, {"ID": [3, 10]})
    misisng_data_df = filter_dataframe(df, {"ID": [11, 21]})
    combined_df = extend_df_by_id(current_df, misisng_data_df, column="Datum")
    assert len(combined_df) == 3


@pytest.mark.pandas_helpers
def test_extend_df_by_columns(get_test_data: DataFrame):
    # 4 Distinct rows, therefore 4 rows
    df = get_test_data.copy()
    current_df = filter_dataframe(df, {"ID": [3, 11]})
    misisng_data_df = filter_dataframe(df, {"ID": [10, 21]})
    combined_df = extend_df_by_columns(current_df, misisng_data_df)
    assert len(combined_df) == 4
