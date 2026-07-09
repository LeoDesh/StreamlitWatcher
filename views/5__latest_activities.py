from datetime import date
from typing import Any

import streamlit as st
from pandas import DataFrame

from garmin.constants import ACTIVITY_ATTR_COLUMNS, FULL_DATA
from garmin.plots.visualization import create_gantt_chart, create_heat_map_monthly_axis
from garmin.utils.misc import get_current_month, prettify
from garmin.utils.pandas_helpers import (
    aggregate_df_named_column,
    filter_dataframe,
    get_gantt_df,
    get_pivot_dataframe,
    get_unique_values_per_column,
)
from streamlit_utils.chart_helpers import place_figure
from streamlit_utils.config import Icons
from streamlit_utils.utils import Metric, create_metrics_container, stream_metrics


def clean_up_dict(data: dict[str, Any]) -> dict[str, Any]:
    pace = data["Average Pace"]
    data["Speed"] = "--" if pace == "--" else data["Speed"]


def construct_activity_header(
    date_str: str, activity_type: str, activity_title: str
) -> str:
    if activity_title.find(activity_type) > -1:
        return f"{date_str} -- {activity_type}"
    return f"{date_str} -- {activity_type} -- {activity_title}"


def show_latest_activities(df: DataFrame, rows: int = 20) -> None:
    df = df.head(rows)
    df_dict = df.to_dict(orient="records")
    for idx, row_dict in enumerate(df_dict):
        clean_up_dict(row_dict)
        date = row_dict["Date"].date()
        date_str = date.strftime("%d.%m.%Y")
        activity_title = construct_activity_header(
            date_str, row_dict["Activity Type"], row_dict["Title"]
        )
        header = f"{idx + 1}: {activity_title}"
        activity = {
            attr: value
            for attr, value in row_dict.items()
            if attr in ACTIVITY_ATTR_COLUMNS
        }
        create_metrics_container(header, activity)


def get_activity_filters(df: DataFrame) -> dict[str, Any]:
    unique_values_dict = get_unique_values_per_column(df, ["Activity Type"])
    filters = {}
    with st.expander("Activity Filter", expanded=False):
        for key, groups in unique_values_dict.items():
            filters[key] = st.multiselect(key, options=groups, default=groups)
    return filters


def get_gantt_filters(df: DataFrame) -> dict[str, Any]:
    unique_values_dict = get_unique_values_per_column(df, ["Year"])
    filters = {}
    with st.expander("Chart Filter", expanded=False):
        for key, groups in unique_values_dict.items():
            filters[key] = st.multiselect(key, options=groups, default=groups[0])
    return filters


def show_activities_timeline(df: DataFrame) -> None:
    gantt_df = get_gantt_df(df, "Date")
    fig = create_gantt_chart(gantt_df, "Date", "Date End", "Activity Type")
    place_figure(fig)


def show_heat_map(df: DataFrame, category: str, unit_choice: bool) -> None:
    filters = {} if category == "Alle" else {"Activity Type": "Laufen"}
    df["Time In Hours"] = round(df["Time In Hours"], 2)
    pivot_df = get_pivot_dataframe(
        df,
        "Year",
        "Month",
        value_column="Speed" if unit_choice else "Time In Hours",
        agg_func="size" if unit_choice else "sum",
        filters=filters,
    ).reset_index()
    pivot_df = pivot_df.set_index("Year")
    template = "%{z:.0f} Units" if unit_choice else "%{z:.2f} Hours"
    title = (
        "Overview of Sports Units Done per Month"
        if unit_choice
        else "Overview of Hours spent on Sports per Month"
    )
    fig = create_heat_map_monthly_axis(
        pivot_df,
        title,
        hovertemplate="%{y}, %{x}: " + template + " <extra></extra>",
    )
    place_figure(fig)


def heatmap_filter() -> tuple[str, bool]:
    selection_col, metric_col, _ = st.columns([2, 2, 8], gap="large")
    selection = selection_col.selectbox("Category", ["Laufen", "Alle"], index=0)
    metric_choice = metric_col.toggle("Units", value=True)
    return (selection, metric_choice)


def get_top_activity(df: DataFrame) -> tuple[str, int]:
    agg_df = aggregate_df_named_column(
        df,
        "activity_type",
        "activity_type",
        col_name="Total",
        agg_func="count",
        sort_asc=False,
    ).reset_index(drop=True)
    return agg_df.loc[0, ["activity_type", "Total"]]


def get_activity_count(df: DataFrame) -> int:
    return len(df)


def get_metrics(df: DataFrame, description: str) -> list[Metric]:
    current_month_activity_count = get_activity_count(df)
    top_activity, count = get_top_activity(df)
    return [
        Metric(
            label=f"Current {description} Activites", value=current_month_activity_count
        ),
        Metric(
            label=f"Current {description} Top Activity",
            value=f"{top_activity}: {count}",
        ),
    ]


def render_activities_metrics(df: DataFrame) -> None:
    current_month = get_current_month()
    current_month_df = df[df["month_start"] == current_month]
    current_year_df = df[df["year"] == current_month.year]
    stream_metrics(
        [*get_metrics(current_month_df, "Month"), *get_metrics(current_year_df, "Year")]
    )


def main() -> None:
    st.header("Latest Activities", text_alignment="center")
    df = FULL_DATA.copy()
    df["month_start"] = df["date"].apply(lambda x: date(x.year, x.month, 1))
    render_activities_metrics(df)
    df.columns = [prettify(col) for col in df.columns]
    activity_tab, gantt_chart_tab, heat_tab = st.tabs(
        [
            f"{Icons.table} Activity Overview",
            f"{Icons.timeline} Activity Breakdown",
            f"{Icons.apps} Activity Frequency",
        ]
    )
    with activity_tab:
        filters = get_activity_filters(df)
        activity_df = filter_dataframe(df, filters)
        show_latest_activities(activity_df)
    with gantt_chart_tab:
        gantt_filters = get_gantt_filters(df)
        gantt_df = filter_dataframe(df, gantt_filters)
        show_activities_timeline(gantt_df)
    with heat_tab:
        category, unit_choice = heatmap_filter()
        show_heat_map(df, category, unit_choice)


if __name__ == "__main__":
    main()
