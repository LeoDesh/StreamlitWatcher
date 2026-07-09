from datetime import date
from itertools import pairwise
from typing import Any, Literal

from pandas import DataFrame, Series, Timedelta, date_range, to_datetime

from garmin.utils.misc import (
    calculate_bins_from_min_max_value,
    calculate_ticker_values,
    categorize_df_column,
)
from garmin.utils.pace_calculations import transform_pace_float_to_pace


def bin_label_heartbeat(
    df: DataFrame, number_of_bins: int, trg_column: str
) -> tuple[list[int], list[str]]:
    values = df[trg_column].tolist()
    bin_values = [
        int(value) for value in calculate_ticker_values(values, number_of_bins)
    ]
    labels = [
        f"{current_value}-{next_value}"
        for current_value, next_value in pairwise(bin_values)
    ]
    return (bin_values, labels)


def calculate_bins_values_dataframe(
    df: DataFrame, number_of_bins: int, column: str
) -> list[float]:
    min_value, max_value = max(df[column].min() - 0.2, 0), df[column].max() + 0.2
    return calculate_bins_from_min_max_value(min_value, max_value, number_of_bins)


def get_pace_bins_labels_for_dataframe(
    df: DataFrame, number_of_bins: int, pace_float_column: str
) -> tuple[list[float], list[str]]:
    bins = calculate_bins_values_dataframe(df, number_of_bins, pace_float_column)
    pace_str_bins = [transform_pace_float_to_pace(bin) for bin in bins]
    labels = [
        f"{current_pace}-{next_pace}"
        for current_pace, next_pace in pairwise(pace_str_bins)
    ]
    return (bins, labels)


def create_df_pivot_hpm_pace(df: DataFrame) -> DataFrame:
    df = categorize_df_column(df, "pace_float", 8, get_pace_bins_labels_for_dataframe)
    df = categorize_df_column(df, "average_heart_rate", 8, bin_label_heartbeat)
    df = df.pivot_table(
        index="average_heart_rate",
        columns="pace_float",
        values="distance",
        aggfunc="count",
        observed=False,
    )
    df = ((df / df.sum(axis=0)) * 100).round(2)
    df = df.dropna(axis=1, how="all").fillna(0)
    return df


def get_grouped_table(
    df: DataFrame, group_columns: list[str], agg_columns: list[str]
) -> DataFrame:
    sum_df = df.groupby(group_columns)[agg_columns].sum()
    count_df = df.groupby(group_columns).size().to_frame("Count")
    return count_df.join(sum_df).reset_index()


def get_unique_values_per_column(
    df: DataFrame, columns: list[str]
) -> dict[str, list[Any]]:
    return {column: df[column].unique().tolist() for column in columns}


def generate_dates_df(
    min_date: date,
    max_date: date,
    freq: Literal["D", "MS"] = "D",
    date_column: str = "Date",
) -> DataFrame:
    return DataFrame({date_column: date_range(min_date, max_date, freq=freq).date})


def filter_dataframe(df: DataFrame, filter_kwargs: dict[str, Any]) -> DataFrame:
    df = df.copy()
    mask = Series(True, index=df.index)
    for col, val in filter_kwargs.items():
        if isinstance(val, (list, tuple, set)):
            mask &= df[col].isin(val)
        else:
            mask &= df[col] == val
    return df[mask].copy()


def get_gantt_df(df: DataFrame, date_column: str) -> DataFrame:
    df[date_column] = to_datetime(df[date_column])
    df["Date End"] = df[date_column] + Timedelta(days=1)
    return df


def get_pivot_dataframe(
    df: DataFrame,
    groupby_columns: list[str] | str,
    agg_columns: list[str] | str,
    value_column: str,
    agg_func: list[str] | str,
    filters: dict[list, Any] | None = None,
) -> DataFrame:
    filters = filters if filters else {}
    df = filter_dataframe(df, filters)
    return df.pivot_table(
        index=groupby_columns,
        columns=agg_columns,
        values=value_column,
        aggfunc=agg_func,
        fill_value=0,
    )


def aggregate_df_named_column(
    df: DataFrame,
    groupby_col: str,
    value_col: str,
    col_name: str | None = None,
    agg_func: str = "sum",
    sort_asc: bool | None = None,
) -> DataFrame:
    col_name = col_name if col_name else value_col
    agg_dict = {col_name: (value_col, agg_func)}
    df = aggregrate_df_by_dict(df, groupby_col, agg_dict)
    return df if sort_asc is None else df.sort_values(by=col_name, ascending=sort_asc)


def aggregrate_df_by_dict(
    df: DataFrame,
    groupby_col: str,
    agg_dict: dict[str, tuple[str, str]],
) -> DataFrame:
    return df.groupby(by=groupby_col, as_index=False).agg(**agg_dict)
