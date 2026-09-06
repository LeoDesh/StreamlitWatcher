from typing import Any

import streamlit as st
from pandas import DataFrame

from garmin.constants import ACTIVITY_ATTR_COLUMNS, ACTIVITY_DF
from garmin.utils.pandas_helpers import (
    aggregate_df_named_column,
    filter_dataframe,
    get_unique_values_per_column,
)
from garmin.utils.time_utils import get_current_month
from streamlit_utils.utils import Metric, create_metrics_container, stream_metrics


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


def get_activity_filter(df: DataFrame) -> dict[str, list[str] | None]:
    activity_options = get_activities(df)
    activity_col, year_col, _ = st.columns([1, 1, 2])
    activity_list = activity_col.multiselect(
        "Activity Type",
        options=activity_options,
        placeholder="Choose an activity",
        default=None,
    )
    activity_year = year_col.multiselect(
        "Activity Year",
        options=df["year"].unique().tolist(),
        placeholder="Choose a year",
        default=None,
    )
    initial_filters = {"activity_type": activity_list, "year": activity_year}
    return {
        filter_col: values for filter_col, values in initial_filters.items() if values
    }


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
        Metric(label=f"Activities in {description}", value=current_activity_count),
        Metric(
            label=f"Top Activity in {description}",
            value=f"{top_activity}: {count}",
        ),
    ]


def render_activities_metrics(df: DataFrame) -> None:
    current_month = get_current_month()
    current_month_df = filter_dataframe(df, {"monthly_date": current_month})
    current_year_df = filter_dataframe(df, {"year": current_month.year})
    stream_metrics(
        [
            *get_metrics(current_month_df, current_month.strftime("%B, %Y")),
            *get_metrics(current_year_df, str(current_month.year)),
        ]
    )


def main() -> None:
    st.header("Activity Overview", text_alignment="center")
    df = ACTIVITY_DF.copy()
    render_activities_metrics(df)
    filters = get_activity_filter(df)
    activity_df = filter_dataframe(df, filters)
    show_latest_activities(activity_df)


if __name__ == "__main__":
    main()
