import math
from datetime import date

import streamlit as st
from pandas import DataFrame, Timestamp
from plotly.graph_objects import Figure

from garmin.charts.tools import (
    create_histogram,
    create_hpm_heatmap,
    create_pace_chart,
    get_empty_figure,
)
from garmin.streamlit_helpers.load import load_running_df
from garmin.streamlit_helpers.utils import (
    GridConfig,
    Metric,
    breadcrumbs,
    create_grid,
    stream_metrics,
    time_options_provider,
)
from garmin.utils.pace_calculations import transform_speed_to_pace_prettified
from garmin.utils.pandas_helpers import (
    categorize_df_column,
    create_df_pivot_hpm_pace,
    filter_dataframe,
    get_pace_bins_labels_for_dataframe,
)
from garmin.utils.time_utils import get_current_year

type FilterParameters = list[
    tuple[date, date], tuple[float, float], tuple[float, float]
]


def setup_pace_range_selection() -> tuple[int, int]:
    pace_min = 1
    pace_max = 30
    chosen_pace_min, chosen_pace_max = st.slider(
        "Select pace range (min/km):",
        min_value=pace_min,
        max_value=pace_max,
        value=(pace_min, 8),
    )
    return (chosen_pace_min, chosen_pace_max)


def setup_distance_range_selection(df: DataFrame) -> tuple[int, int]:
    distance_min = 0
    distance_max = math.ceil(df["distance"].max())
    chosen_distance_min, chosen_distance_max = st.slider(
        "Select distance range (km):",
        min_value=distance_min,
        max_value=distance_max,
        value=(distance_min, distance_max),
    )
    return (chosen_distance_min, chosen_distance_max)


def create_pace_histogram_df(df: DataFrame, number_of_bins: int) -> DataFrame:
    column = "pace_float"
    df = categorize_df_column(
        df, column, number_of_bins, get_pace_bins_labels_for_dataframe
    )
    counts_df = df[column].value_counts().sort_index().reset_index()
    counts_df.columns = ["Minute per km", "Amount"]
    return counts_df


def setup_pace_histogram(df: DataFrame, number_of_bins: int) -> Figure:
    if df.empty:
        fig = get_empty_figure()
    else:
        df = create_pace_histogram_df(df, number_of_bins)
        fig = create_histogram(
            df,
            "Pace Distribution",
            hovertemplate="%{y} units exercised within pace of %{x} min/km<extra></extra>",
        )
    return fig


def render_filter_parameters(
    df: DataFrame,
) -> FilterParameters:
    with st.expander("Filters"):
        date_range = time_options_provider()
        pace_col, distance_col = st.columns(2)
        with pace_col:
            pace_range = setup_pace_range_selection()
        with distance_col:
            distance_range = setup_distance_range_selection(df)
    return [date_range, pace_range, distance_range]


def filter_dataframe_by_parameters(
    df: DataFrame, filters: FilterParameters
) -> DataFrame:
    date_range, pace_range, distance_range = filters
    start_date, end_date = date_range
    min_pace, max_pace = pace_range
    min_distance, max_distance = distance_range
    df = df[
        (df["date"] >= Timestamp(start_date).tz_localize("UTC"))
        & (df["date"] <= Timestamp(end_date).tz_localize("UTC"))
        & (df["pace_float"] <= max_pace)
        & (df["pace_float"] >= min_pace)
        & (df["distance"] <= max_distance)
        & (df["distance"] >= min_distance)
    ]
    return df


def get_current_year_median_pace(df: DataFrame) -> Metric:
    speed = df["speed"].median() if not df.empty else 0.0
    return Metric(
        label="Current Year Median Pace",
        value=transform_speed_to_pace_prettified(speed),
    )


def get_current_year_best_pace(df: DataFrame) -> Metric:
    speed = df["speed"].max() if not df.empty else 0.0
    return Metric(
        label="Current Year Highest Pace",
        value=transform_speed_to_pace_prettified(speed),
    )


def get_most_recent_pace(df: DataFrame) -> Metric:
    df = df.sort_values(by="date", ascending=False)
    speed, last_date = df.loc[0, ["speed", "date"]]
    return Metric(
        label=f"Pace Most Recent Run ({last_date.strftime('%d.%m.%Y')})",
        value=transform_speed_to_pace_prettified(speed),
    )


def render_pace_metrics(df: DataFrame) -> None:
    current_year_df = filter_dataframe(df.copy(), {"year": get_current_year()})
    most_recent_pace_metric = get_most_recent_pace(df)
    current_year_median_pace_metric = get_current_year_median_pace(current_year_df)
    current_year_highest_pace = get_current_year_best_pace(current_year_df)
    stream_metrics(
        [
            current_year_median_pace_metric,
            current_year_highest_pace,
            most_recent_pace_metric,
        ]
    )


def has_df_too_few_rows(df: DataFrame) -> bool:
    return len(df) <= 3


def main() -> None:
    df = load_running_df()
    breadcrumbs(__file__)
    st.title("Pace Overview")
    render_pace_metrics(df)
    filters = render_filter_parameters(df)
    df = filter_dataframe_by_parameters(df, filters)
    if has_df_too_few_rows(df):
        st.info(
            f"In the chosen time range must be at least 4 runs! There are {len(df)} runs."
        )
        st.stop()
    grid = create_grid([GridConfig(columns=2), GridConfig(columns=1)])
    with grid[0][0]:
        fig = setup_pace_histogram(df, 15)
        st.plotly_chart(fig)
    with grid[1][0]:
        fig = create_pace_chart(df)
        st.plotly_chart(fig)
    with grid[0][1]:
        pivot_df = create_df_pivot_hpm_pace(df)
        pivot_df.columns.name = "Pace km/min"
        fig = create_hpm_heatmap(pivot_df, "Pace & HPM Correlation in %")
        st.plotly_chart(fig)


if __name__ == "__main__":
    main()
