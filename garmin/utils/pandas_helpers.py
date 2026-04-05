import pandas as pd
from typing import Callable
from itertools import pairwise
from garmin.utils.misc import calculate_ticker_values
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


def get_pace_bins_labels_for_dataframe(
    df: pd.DataFrame, number_of_bins: int, pace_float_column: str
) -> tuple[list[float], list[str]]:
    bins = calculate_bins_values_dataframe(df, number_of_bins, pace_float_column)
    pace_str_bins = [transform_pace_float_to_pace(bin) for bin in bins]
    pins_set = set()
    chosen_nums = []
    for idx, pace_bin in enumerate(pace_str_bins):
        if pace_bin not in pins_set:
            chosen_nums.append(idx)
        pins_set.add(pace_bin)
    calc_bins = [bins[idx] for idx in chosen_nums]
    labels = [
        f"{transform_pace_float_to_pace(calc_bins[idx])}-{transform_pace_float_to_pace(calc_bins[idx + 1])}"
        for idx in range(len(calc_bins) - 1)
    ]
    return (calc_bins, labels)


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
