import streamlit as st
from pandas import DataFrame

from garmin.streamlit_helpers.components import construct_year_statistics
from garmin.streamlit_helpers.config import Icons
from garmin.streamlit_helpers.constants import ACTIVITY_ATTR_COLUMNS
from garmin.streamlit_helpers.load import load_running_df
from garmin.streamlit_helpers.model import (
    Metric,
    create_metrics_container,
    stream_metrics,
)
from garmin.streamlit_helpers.nagivation import breadcrumbs
from garmin.utils.misc import filter_mapping
from garmin.utils.pandas_helpers import aggregrate_df_by_dict, filter_dataframe
from garmin.utils.time_utils import get_current_year


def get_year_overview_table(df: DataFrame) -> DataFrame:
    aggregation_mapping = {
        "Distance": ("distance", "sum"),
        "Time": ("time_in_minutes", "sum"),
        "Units": ("distance", "count"),
        "Average Time": ("time_in_minutes", "mean"),
        "Average Distance": ("distance", "mean"),
    }
    df = aggregrate_df_by_dict(df, "year", aggregation_mapping)
    df["Time"] = df["Time"].apply(lambda x: round(x / 60, 2))
    return df


def construct_column_highlights(df: DataFrame, column: str, amount: int = 3) -> None:
    df = df.sort_values(by=column, ascending=False)
    df = df.head(amount).reset_index()
    activity_records = df.to_dict(orient="records")
    for activity in activity_records:
        date_str = f"{activity['date'].strftime('%d.%m.%Y')}"
        activity = filter_mapping(activity, ACTIVITY_ATTR_COLUMNS)
        create_metrics_container(date_str, activity)


def render_metrics(df: DataFrame) -> None:
    current_year = get_current_year()
    st.header("Overview")
    df = filter_dataframe(df, {"year": current_year})
    running_record = df.to_dict(orient="records")[0]
    description_mapping = {
        "Units": ("Total Runs", "Units"),
        "Distance": ("Distance Covered by Runs", "km"),
        "Time": ("Time Spent Running", "hours"),
    }
    metrics = [
        Metric(
            label=f"{description} in {current_year}",
            value=f"{running_record[attr]} {suffix}",
        )
        for attr, (description, suffix) in description_mapping.items()
    ]
    stream_metrics(metrics, num_cols=3)


def render_year_statistics(df: DataFrame) -> None:
    mapping = {
        "Units": ("Total Runs", "%{y} Runs"),
        "Distance": ("Distance Covered", "%{y} km covered "),
        "Time": ("Time Spent", "%{y} hours spent "),
        "Average Time": (
            "Average Time in minutes spent on a run",
            "Average of %{y:.2f} minutes per run",
        ),
        "Average Distance": (
            "Average kilometre amount of a run",
            "Average of %{y:.2f} km per run",
        ),
    }
    construct_year_statistics(df, mapping, "Units")


def main() -> None:
    breadcrumbs(__file__)
    df = load_running_df()
    overview_df = get_year_overview_table(df)
    render_metrics(overview_df)
    home_tab, distance_tab, speed_tab = st.tabs(
        [
            f"{Icons.ANALYTICS} Statistics",
            f"{Icons.ROUTE} Top Distance Runs",
            f"{Icons.SPEED} Top Speed Runs",
        ]
    )
    with home_tab:
        render_year_statistics(overview_df)
    with distance_tab:
        construct_column_highlights(df, "distance", 5)
    with speed_tab:
        construct_column_highlights(df, "speed", 5)


if __name__ == "__main__":
    main()
