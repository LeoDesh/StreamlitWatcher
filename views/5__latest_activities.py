import streamlit as st
from garmin.constants import FULL_DATA
from garmin.statistics.pandas_helper import (
    filter_dataframe,
    get_unique_values_per_column,
    get_gantt_df,
    get_pivot_dataframe,
)
from garmin.plots.visualization import create_gantt_chart, create_heat_map
from streamlit_utils.chart_helpers import place_figure
import pandas as pd
from datetime import date
from typing import Any


def clean_up_dict(data: dict[str, Any]) -> dict[str, Any]:
    pace = data["AVERAGE_PACE"]
    if pace == "--":
        data["SPEED"] = "--"


def construct_activity_header(date_str: str, activity_type: str, activity_title: str):
    if activity_title.find(activity_type) > -1:
        return f"{date_str} -- {activity_type}"
    return f"{date_str} -- {activity_type} -- {activity_title}"


def show_latest_activities(df: pd.DataFrame, rows: int = 20):
    attrs_columns = [
        "DISTANCE",
        "AVERAGE_PACE",
        "SPEED",
        "CALORIES",
        "TIME",
        "AVG_HEART_RATE",
    ]
    df: pd.DataFrame = df.head(rows)
    df_dict = df.to_dict(orient="records")
    for idx, row_dict in enumerate(df_dict):
        clean_up_dict(row_dict)
        date = row_dict["DATE"].date()
        date_str = date.strftime("%d.%m.%Y")
        activity_title = construct_activity_header(
            date_str, row_dict["ACTIVITY_TYPE"], row_dict["TITLE"]
        )
        with st.container(border=True, horizontal_alignment="center"):
            st.header(f"{idx + 1}: {activity_title}")
            cols = st.columns(len(attrs_columns))
            for col, description in zip(cols, attrs_columns):
                value = row_dict.get(description, "")
                col.metric(description, value)


def get_activity_filters():
    unique_values_dict = get_unique_values_per_column(FULL_DATA, ["ACTIVITY_TYPE"])
    filters = {}
    with st.expander("Activity Filter", expanded=False):
        for key, groups in unique_values_dict.items():
            filters[key] = st.multiselect(key, options=groups, default=groups)
    return filters


def get_gantt_filters():
    unique_values_dict = get_unique_values_per_column(FULL_DATA, ["YEAR"])
    filters = {}
    with st.expander("Chart Filter", expanded=False):
        for key, groups in unique_values_dict.items():
            filters[key] = st.multiselect(key, options=groups, default=groups)
    return filters


def get_heatmap_filters():
    unique_values_dict = get_unique_values_per_column(FULL_DATA, ["ACTIVITY_TYPE"])
    filters = {}
    with st.expander("Heatmap Choice", expanded=False):
        for key, groups in unique_values_dict.items():
            filters[key] = st.selectbox(
                key, options=groups, index=groups.index("Laufen")
            )
    return filters


def show_activities_timeline(df: pd.DataFrame):
    gantt_df = get_gantt_df(df, "DATE")
    fig = create_gantt_chart(gantt_df, "DATE", "DATE_END", "ACTIVITY_TYPE")
    place_figure(fig)


def show_heat_map(df: pd.DataFrame, category: str):
    if category == "Gesamt":
        filters = {}
    else:
        filters = {"ACTIVITY_TYPE": "Laufen"}
    pivot_df = get_pivot_dataframe(
        df,
        "YEAR",
        "MONTH",
        value_column="SPEED",
        agg_func="size",
        filters=filters,
    ).reset_index()
    pivot_df = pivot_df.set_index("YEAR")
    fig = create_heat_map(pivot_df, category)
    place_figure(fig)


def heatmap_filter() -> str:
    return st.selectbox("Category", ["Laufen", "Gesamt"], index=0)


def main():
    st.header("Latest Activities", text_alignment="center")
    df = FULL_DATA.copy()
    activity_tab, gantt_chart_tab, heat_tab = st.tabs(
        [":material/table_view: Activity", ":material/view_timeline: Gantt Chart", ":material/apps: Heat Map"]
    )
    with activity_tab:
        filters = get_activity_filters()
        activity_df = filter_dataframe(FULL_DATA, filters)
        show_latest_activities(activity_df)
    with gantt_chart_tab:
        gantt_filters = get_gantt_filters()
        gantt_df = filter_dataframe(df, gantt_filters)
        show_activities_timeline(gantt_df)
    with heat_tab:
        category = heatmap_filter()
        show_heat_map(df, category)


if __name__ == "__main__":
    main()
