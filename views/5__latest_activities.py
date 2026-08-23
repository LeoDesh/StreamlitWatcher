from datetime import date
from typing import Any

import streamlit as st
from pandas import DataFrame

from garmin.constants import ACTIVITY_ATTR_COLUMNS, COMPLETE_ACTIVITY_DF
from garmin.plots.visualization import create_gantt_chart, create_heat_map_monthly_axis
from garmin.utils.pandas_helpers import (
    aggregate_df_named_column,
    filter_dataframe,
    generate_dates_df,
    get_gantt_df,
    get_pivot_dataframe,
    get_unique_values_per_column,
)
from garmin.utils.time_utils import get_current_month
from streamlit_utils.chart_helpers import place_figure
from streamlit_utils.config import Icons
from streamlit_utils.utils import Metric, create_metrics_container, stream_metrics


def clean_up_dict(data: dict[str, Any]) -> dict[str, Any]:
    pace = data["average_pace"]
    data["speed"] = "--" if pace == "--" else data["speed"]


def construct_activity_header(date_str: str, activity_type: str) -> str:
    return f"{date_str} -- {activity_type}"


def get_activities(df: DataFrame) -> list[str]:
    return get_unique_values_per_column(df, ["activity_type"])["activity_type"]


def show_latest_activities(df: DataFrame, rows: int = 20) -> None:
    df = df.head(rows)
    df_dict = df.to_dict(orient="records")
    for idx, row_dict in enumerate(df_dict):
        clean_up_dict(row_dict)
        date = row_dict["date"].date()
        date_str = date.strftime("%d.%m.%Y")
        activity_title = construct_activity_header(date_str, row_dict["activity_type"])
        header = f"{idx + 1}: {activity_title}"
        activity = {
            attr: value
            for attr, value in row_dict.items()
            if attr in ACTIVITY_ATTR_COLUMNS
        }
        create_metrics_container(header, activity)


def get_activity_filter(df: DataFrame) -> dict[str, list[str]]:
    activity_list = get_activity_list(df)
    return {"activity_type": activity_list}


def get_activity_list(df: DataFrame) -> list[str]:
    with st.expander("Activity Filter", expanded=False):
        activity_options = get_activities(df)
        return st.multiselect(
            "activity_type",
            options=activity_options,
            default=activity_options,
            label_visibility="hidden",
        )


def get_gantt_filters(df: DataFrame) -> dict[str, Any]:
    unique_values_dict = get_unique_values_per_column(df, ["year"])
    filters = {}
    with st.expander("Chart Filter", expanded=False):
        for key, groups in unique_values_dict.items():
            filters[key] = st.multiselect(
                key, options=groups, default=groups[0], label_visibility="hidden"
            )
    return filters


def show_activities_timeline(df: DataFrame) -> None:
    gantt_df = get_gantt_df(df, "date")
    fig = create_gantt_chart(gantt_df, "date", "date_end", "activity_type")
    place_figure(fig)


def prepare_heatmap_df(df: DataFrame, category: str | list[str]) -> DataFrame:
    filters = {"activity_type": category}
    df["time_in_hours"] = round(df["time_in_hours"], 2)
    date_df = generate_dates_df(
        df["month_start"].min(), df["month_start"].max(), "MS", "month_start"
    )
    filtered_df = filter_dataframe(df, filters)
    df = date_df.merge(filtered_df, on="month_start", how="left")
    df["month"] = df["month_start"].apply(lambda x: x.month)
    df["year"] = df["month_start"].apply(lambda x: x.year)
    df["time_in_hours"] = df["time_in_hours"].fillna(0)
    df["speed"] = df["speed"].fillna(0)
    return df


def show_heat_map(df: DataFrame, category: str | list[str], unit_choice: bool) -> None:
    df = prepare_heatmap_df(df, category)
    pivot_df = get_pivot_dataframe(
        df,
        "year",
        "month",
        value_column="activity_type" if unit_choice else "time_in_hours",
        agg_func="count" if unit_choice else "sum",
    ).reset_index()
    pivot_df = pivot_df.set_index("year")
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


def heatmap_filter(df: DataFrame) -> tuple[list[str], bool]:
    metric_col, selection_col, _ = st.columns([2, 8, 2], gap="large")
    activity_options = get_activities(df)
    selection = selection_col.multiselect(
        "Category",
        activity_options,
        activity_options,
        placeholder="Choose a category",
        label_visibility="collapsed",
    )
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
    if df.empty:
        return []
    current_activity_count = get_activity_count(df)
    top_activity, count = get_top_activity(df)
    return [
        Metric(label=f"Current {description} Activites", value=current_activity_count),
        Metric(
            label=f"Current {description} Top Activity",
            value=f"{top_activity}: {count}",
        ),
    ]


def render_activities_metrics(df: DataFrame) -> None:
    current_month = get_current_month()
    current_month_df = filter_dataframe(df.copy(), {"month_start": current_month})
    current_year_df = filter_dataframe(df.copy(), {"year": current_month.year})
    stream_metrics(
        [*get_metrics(current_month_df, "Month"), *get_metrics(current_year_df, "Year")]
    )


def main() -> None:
    st.header("Latest Activities", text_alignment="center")
    df = COMPLETE_ACTIVITY_DF.copy()
    df["month_start"] = df["date"].apply(lambda x: date(x.year, x.month, 1))
    render_activities_metrics(df)
    activity_tab, gantt_chart_tab, heat_tab = st.tabs(
        [
            f"{Icons.table} Activity Overview",
            f"{Icons.timeline} Activity Breakdown",
            f"{Icons.apps} Activity Frequency",
        ]
    )
    with activity_tab:
        filters = get_activity_filter(df)
        activity_df = filter_dataframe(df, filters)
        show_latest_activities(activity_df)
    with gantt_chart_tab:
        gantt_filters = get_gantt_filters(df)
        gantt_df = filter_dataframe(df, gantt_filters)
        show_activities_timeline(gantt_df)
    with heat_tab:
        category, unit_choice = heatmap_filter(df)
        show_heat_map(df, category, unit_choice)


if __name__ == "__main__":
    main()
