from typing import Any

import streamlit as st
from pandas import DataFrame

from garmin.constants import STEPS_DF
from garmin.utils.misc import compute_delta
from garmin.utils.pandas_helpers import aggregate_df_named_column
from streamlit_utils.utils import create_metrics_container, stream_metrics


def render_metrics(df: DataFrame) -> None:
    metric_funcs = []
    metrics = [func(df) for func in metric_funcs]
    stream_metrics(metrics, num_cols=3)


def get_highlight_entry(df: DataFrame, groupby_col: list[str]) -> tuple[dict, Any]:
    agg_df = (
        aggregate_df_named_column(df, groupby_col, value_col="Steps")
        .sort_values(by="Steps", ascending=False)
        .reset_index()
    )
    median_steps = agg_df["Steps"].median()
    max_steps, column = agg_df.loc[0, ["Steps", *groupby_col]]
    delta = compute_delta(median_steps, max_steps)
    record = {
        "Record": f"{max_steps:,.0f}",
        "Median": f"{median_steps:,.0f}",
        "Difference": f"{delta:.2f} %",
    }
    return (record, column)


def get_year_highlights(df: DataFrame) -> None:
    part_data, year = get_highlight_entry(df, ["year"])
    data = {"Year": f"{year:.0f}"} | part_data
    create_metrics_container("Year Record", data)


def get_month_highlight(df: DataFrame) -> None:
    part_data, monthly_date = get_highlight_entry(df, ["monthly_date"])
    data = {"Month": f"{monthly_date.strftime('%B, %Y')}"} | part_data
    create_metrics_container("Month Record", data)


def get_day_highlight(df: DataFrame) -> None:
    part_data, day = get_highlight_entry(df, ["Date"])
    data = {"Day": f"{day.strftime('%d.%m.%Y')}"} | part_data
    create_metrics_container("Day Record", data)


def get_week_highlight(df: DataFrame) -> None:
    part_data, yr_week = get_highlight_entry(df, ["week"])
    yr, week = yr_week.split("_")
    data = {"Week": f"{week}, {yr}"} | part_data
    create_metrics_container("Week Record", data)


@st.dialog("Description")
def show_description():
    st.markdown(
        """  
        In the following individuel personal records on different *timeframes* will be shown.  
        **Record** is the highest amount of steps achieved in the corresponding timeframe.  
        **Median** shows the median steps amount.  
        The difference shows the relative difference between *record* and *median*.
        """
    )


# Monthly statistics as metrics for Progress/Month Distribution
def main() -> None:
    header_col, _, btn_col = st.columns([10, 1, 1])
    header_col.header("Personal Records")
    btn = btn_col.button(label="Info", icon=":material/info:", type="secondary")
    if btn:
        show_description()
    df = STEPS_DF.copy()
    get_day_highlight(df)
    get_week_highlight(df)
    get_month_highlight(df)
    get_year_highlights(df)


main()
