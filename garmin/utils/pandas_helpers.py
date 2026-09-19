from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any, Literal

from pandas import (
    DataFrame,
    Series,
    Timedelta,
    concat,
    cut,
    date_range,
    read_csv,
    to_datetime,
)

from garmin.utils.bucketing import create_bins_by_series
from garmin.utils.misc import create_label_pairs_from_values
from garmin.utils.pace_calculations import transform_pace_float_to_pace


def bin_label_heartbeat(
    values: list[float], number_of_bins: int
) -> tuple[list[int], list[str]]:
    bin_values = [
        int(value)
        for value in create_bins_by_series(
            values, number_of_bins=number_of_bins, bin_size=5
        )
    ]
    labels = create_label_pairs_from_values(bin_values)
    return (bin_values, labels)


def get_pace_bins_labels_for_dataframe(
    values: list[float], number_of_bins: int
) -> tuple[list[float], list[str]]:
    bins = create_bins_by_series(
        values, number_of_bins=number_of_bins, bin_size=0.1, enhancer=0.01
    )
    pace_bins = [transform_pace_float_to_pace(bin) for bin in bins]
    labels = create_label_pairs_from_values(pace_bins)
    return (bins, labels)


def categorize_df_column(
    df: DataFrame,
    trg_column: str,
    number_of_bins: int,
    bins_labels_func: Callable[[list[float], int], tuple[list, list]],
) -> DataFrame:
    bins, labels = bins_labels_func(df[trg_column].tolist(), number_of_bins)
    df = df.copy()
    df.loc[:, f"new_{trg_column}"] = cut(df[trg_column], bins=bins, labels=labels)
    df[trg_column] = df[f"new_{trg_column}"]
    return df


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
    df["date_end"] = df[date_column] + Timedelta(days=1)
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


def update_data(df_existing: DataFrame, df_new: DataFrame) -> DataFrame:
    df_difference = df_new.merge(df_existing, how="left", indicator=True)
    df_difference = df_difference[df_difference["_merge"] == "left_only"].drop(
        columns="_merge"
    )
    return concat([df_difference, df_existing], ignore_index=True)


def update_data_on_column(
    df_existing: DataFrame, df_new: DataFrame, column: str
) -> DataFrame:
    ids = df_new[column].tolist()
    df_base = df_existing[~df_existing[column].isin(ids)]
    return concat([df_new, df_base], ignore_index=True)


def save_df_to_csv(
    df: DataFrame,
    filename: str | Path,
    *,
    sep: str = ",",
    encoding: str = "utf-8",
    index: bool = False,
    header: bool = True,
) -> None:
    df.to_csv(filename, sep=sep, encoding=encoding, index=index, header=header)


def read_file(
    filename: str | Path,
    *,
    sep: str = ",",
    encoding: str = "utf-8",
    header: int = 0,
    index_col: int | None = None,
) -> DataFrame:
    return read_csv(
        filename, sep=sep, encoding=encoding, header=header, index_col=index_col
    )
