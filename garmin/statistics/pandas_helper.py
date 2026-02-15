import pandas as pd
from typing import List, Any


def get_overview_table(df: pd.DataFrame, column: str) -> pd.DataFrame:
    df = df[column].agg(["mean", "median", "min", "max"]).T
    df.index = df.index.map(
        {
            "mean": "Average",
            "median": "Median",
            "min": "Min",
            "max": "Max",
        }
    )
    return pd.DataFrame(df)


def get_grouped_table(
    df: pd.DataFrame, group_columns: List[str], agg_columns: List[str]
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


def get_highlights_data(df: pd.DataFrame, columns: List[str], idx: int):
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
        fill_value=0
    )
