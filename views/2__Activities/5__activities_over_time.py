from typing import Any

import streamlit as st
from pandas import DataFrame

from garmin.constants import ACTIVITY_ATTR_COLUMNS, ACTIVITY_DF
from garmin.plots.visualization import create_gantt_chart, create_heat_map_monthly_axis
from garmin.utils.pandas_helpers import (
    aggregate_df_named_column,
    filter_dataframe,
    generate_dates_df,
    get_gantt_df,
    get_pivot_dataframe,
    get_unique_values_per_column,
)
from garmin.utils.time_utils import get_current_year
from streamlit_utils.chart_helpers import place_figure
from streamlit_utils.utils import (
    GridConfig,
    Metric,
    create_grid,
    create_metrics_container,
    stream_metrics,
)


def clean_up_dict(data: dict[str, Any]) -> dict[str, Any]:
    pace = data["average_pace"]
    data["speed"] = "--" if pace == "--" else data["speed"]


def construct_activity_header(activity: dict[str, Any]) -> str:
    date = activity["date"].date()
    date_str = date.strftime("%d.%m.%Y")
    activity_type = activity["activity_type"]
    return f"{date_str} -- {activity_type}"


def get_activities(df: DataFrame) -> list[str]:
    return get_unique_values_per_column(df, ["activity_type"])["activity_type"]


def show_latest_activities(df: DataFrame, rows: int = 20) -> None:
    df = df.head(rows)
    df_dict = df.to_dict(orient="records")
    for idx, activity in enumerate(df_dict):
        clean_up_dict(activity)
        activity_title = construct_activity_header(activity)
        header = f"{idx + 1}: {activity_title}"
        activity = {
            attr: value
            for attr, value in activity.items()
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
    year_selection_col, _ = st.columns([1, 1])
    values = unique_values_dict["year"]
    years = year_selection_col.multiselect(
        label="Year Selection",
        options=values,
        default=values[0],
        # label_visibility="hidden",
    )
    return {"year": years}


def show_activities_timeline(df: DataFrame) -> None:
    gantt_df = get_gantt_df(df, "date")
    fig = create_gantt_chart(gantt_df, "date", "date_end", "activity_type")
    place_figure(fig)


def prepare_heatmap_df(df: DataFrame, category: str | list[str]) -> DataFrame:
    filters = {"activity_type": category} if category else {}
    df["time_in_hours"] = round(df["time_in_hours"], 2)
    date_df = generate_dates_df(
        df["monthly_date"].min(), df["monthly_date"].max(), "MS", "monthly_date"
    )
    filtered_df = filter_dataframe(df, filters)
    df = date_df.merge(filtered_df, on="monthly_date", how="left")
    df["month"] = df["monthly_date"].apply(lambda x: x.month)
    df["year"] = df["monthly_date"].apply(lambda x: x.year)
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
    metric_col, selection_col = st.columns([1, 3], gap="large")
    activity_options = get_activities(df)
    selection = selection_col.multiselect(
        "Category",
        activity_options,
        default=None,
        placeholder="Choose an Activity",
        label_visibility="collapsed",
    )
    metric_choice = metric_col.toggle("Units", value=True)
    return (selection, metric_choice)


def render_activities_metrics(df: DataFrame) -> None:
    current_year = get_current_year()
    df = filter_dataframe(df, {"year": current_year})
    metric_func = [
        get_time_spent_metric,
        get_different_activities_metric,
        get_average_activities_per_month_metric,
    ]
    stream_metrics([func(df, current_year) for func in metric_func])


def get_time_spent_metric(df: DataFrame, current_year: int) -> Metric:
    hours = df["time_in_minutes"].sum()
    return Metric(
        label=f"Hours spent on Activities in {current_year}", value=f"{hours / 60:.0f}"
    )


def get_different_activities_metric(df: DataFrame, current_year: int) -> Metric:
    number = df["activity_type"].nunique()
    return Metric(
        label=f"Number of different Activities in {current_year}", value=str(number)
    )


def get_average_activities_per_month_metric(df: DataFrame, current_year: int) -> Metric:
    agg_df = aggregate_df_named_column(
        df,
        groupby_col="monthly_date",
        col_name="total",
        value_col="activity_type",
        agg_func="count",
    )
    average_activities_per_month = agg_df["total"].mean()
    return Metric(
        label=f"Number of average monthly Activities in {current_year}",
        value=f"{average_activities_per_month:.0f}",
    )


def main() -> None:
    st.header("Activities over time", text_alignment="center")
    df = ACTIVITY_DF.copy()
    render_activities_metrics(df)
    grid = create_grid([GridConfig(columns=2)])
    with grid[0][0]:
        gantt_filters = get_gantt_filters(df)
        gantt_df = filter_dataframe(df, gantt_filters)
        show_activities_timeline(gantt_df)
    with grid[0][1]:
        category, unit_choice = heatmap_filter(df)
        show_heat_map(df, category, unit_choice)


if __name__ == "__main__":
    main()
