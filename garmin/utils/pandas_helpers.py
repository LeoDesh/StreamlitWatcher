from itertools import pairwise
from typing import Any, Callable

import pandas as pd

from garmin.utils.misc import calculate_bins_from_min_max_value, calculate_ticker_values
from garmin.utils.pace_calculations import transform_pace_float_to_pace


def get_df_sum_from_column(
    df: pd.DataFrame, groupby_column: str, value_column: str
) -> pd.DataFrame:
    return df.groupby(groupby_column)[[value_column]].sum()


def bin_label_heartbeat(df: pd.DataFrame, number_of_bins: int, trg_column: str):
    values = df[trg_column].tolist()
    bin_values = [
        int(value) for value in calculate_ticker_values(values, number_of_bins)
    ]
    labels = [
        f"{current_value}-{next_value}"
        for current_value, next_value in pairwise(bin_values)
    ]
    return (bin_values, labels)


def categorize_df_column(
    df: pd.DataFrame,
    trg_column: str,
    number_of_bins: int,
    bins_labels_func: Callable[[pd.DataFrame, int, str], tuple[list, list]],
):
    bins, labels = bins_labels_func(df, number_of_bins, trg_column)
    df = df.copy()
    df.loc[:, f"new_{trg_column}"] = pd.cut(df[trg_column], bins=bins, labels=labels)
    df[trg_column] = df[f"new_{trg_column}"]
    return df


def calculate_bins_values_dataframe(
    df: pd.DataFrame, number_of_bins: int, column: str
) -> list[float]:
    min_value, max_value = max(df[column].min() - 0.2, 0), df[column].max() + 0.2
    return calculate_bins_from_min_max_value(min_value, max_value, number_of_bins)


def get_pace_bins_labels_for_dataframe(
    df: pd.DataFrame, number_of_bins: int, pace_float_column: str
) -> tuple[list[float], list[str]]:
    bins = calculate_bins_values_dataframe(df, number_of_bins, pace_float_column)
    pace_str_bins = [transform_pace_float_to_pace(bin) for bin in bins]
    labels = [
        f"{current_pace}-{next_pace}"
        for current_pace, next_pace in pairwise(pace_str_bins)
    ]
    return (bins, labels)


def create_df_pivot_hpm_pace(df) -> pd.DataFrame:
    df = categorize_df_column(df, "PACE_FLOAT", 8, get_pace_bins_labels_for_dataframe)
    df = categorize_df_column(df, "AVG_HEART_RATE", 8, bin_label_heartbeat)
    df = df.pivot_table(
        index="AVG_HEART_RATE",
        columns="PACE_FLOAT",
        values="DISTANCE",
        aggfunc="count",
        observed=False,
    )
    return ((df / df.sum(axis=0)) * 100).round(2)


def get_overview_table(df: pd.DataFrame, column: str) -> pd.DataFrame:
    df = df[column].agg(["mean", "median", "max"]).T
    df.index = df.index.map(
        {
            "mean": "Average",
            "median": "Median",
            "max": "Max",
        }
    )
    return pd.DataFrame(df)


def get_grouped_table(
    df: pd.DataFrame, group_columns: list[str], agg_columns: list[str]
):
    sum_df = df.groupby(group_columns)[agg_columns].sum()
    count_df = df.groupby(group_columns).size().to_frame("Count")
    return count_df.join(sum_df).reset_index()


def get_unique_values_per_column(
    df: pd.DataFrame, columns: list[str]
) -> dict[str, list[Any]]:
    return {column: df[column].unique().tolist() for column in columns}


def filter_dataframe(df: pd.DataFrame, filter_kwargs: dict[str, Any]) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)
    for col, val in filter_kwargs.items():
        if isinstance(val, (list, tuple, set)):
            mask &= df[col].isin(val)
        else:
            mask &= df[col] == val
    return df[mask].copy()


def get_highlights_data(df: pd.DataFrame, columns: list[str], idx: int):
    return df.loc[idx, columns].values


def get_gantt_df(df: pd.DataFrame, date_column: str) -> pd.DataFrame:
    df[date_column] = pd.to_datetime(df[date_column])
    df["DATE_END"] = df[date_column] + pd.Timedelta(days=1)
    return df


def get_pivot_dataframe(
    df: pd.DataFrame,
    groupby_columns: list[str] | str,
    agg_columns: list[str] | str,
    value_column: str,
    agg_func: list[str] | str,
    filters: dict[list, Any] = {},
):
    df = filter_dataframe(df, filters)
    return df.pivot_table(
        index=groupby_columns,
        columns=agg_columns,
        values=value_column,
        aggfunc=agg_func,
        fill_value=0,
    )
