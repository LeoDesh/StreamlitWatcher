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
    _, umsatz = df.loc[0, :]
    assert umsatz == 10


@pytest.mark.pandas_helpers
def test_aggregrate_df_by_dict(get_test_data: DataFrame):
    df = get_test_data.copy()
    filters = {"Datum": ["2026-01-01", "2026-01-02"]}
    df = filter_dataframe(df, filters)
    agg_dict = {"Umsatz": ("Umsatz", "sum")}
    df = aggregrate_df_by_dict(df, groupby_col="Datum", agg_dict=agg_dict)
    assert list(df.columns) == ["Datum", "Umsatz"]
    assert len(df) == 2
    _, umsatz = df.loc[0, :]
    assert umsatz == 31460.95


@pytest.mark.pandas_helpers
def test_extend_df_by_id(get_test_data: DataFrame):
    # 3 Distinct column values (Datum), therefore only 3 rows
    df = get_test_data.copy()
    df_existing = filter_dataframe(df, {"ID": [3, 10]})
    df_new = filter_dataframe(df, {"ID": [11, 21]})
    combined_df = extend_df_by_id(df_existing, df_new, column="Datum")
    assert len(combined_df) == 3


@pytest.mark.pandas_helpers
def test_extend_df_by_columns(get_test_data: DataFrame):
    # 4 Distinct rows, therefore 4 rows
    df = get_test_data.copy()
    df_existing = filter_dataframe(df, {"ID": [3, 11]})
    df_new = filter_dataframe(df, {"ID": [10, 21]})
    combined_df = extend_df_by_columns(df_existing, df_new)
    assert len(combined_df) == 4
