import math
from datetime import date, timedelta

import streamlit as st
from pandas import DataFrame, Timestamp

from garmin.constants import DATA
from garmin.plots.visualization import (
    create_heat_map_ordinary,
    create_plotly_pace_chart,
    get_df_pace_histogram,
    get_empty_figure,
)
from garmin.utils.pace_calculations import transform_speed_to_pace_prettified
from garmin.utils.pandas_helpers import create_df_pivot_hpm_pace, filter_dataframe
from garmin.utils.time_utils import get_current_year
from streamlit_utils.chart_helpers import place_figure
from streamlit_utils.config import Icons
from streamlit_utils.utils import Metric, stream_metrics

type FilterParameters = list[
    tuple[date, date], tuple[float, float], tuple[float, float]
]


def setup_date_range_selection(df: DataFrame) -> tuple[date, date]:
    date_min = df["date"].min().date()
    date_max: date = df["date"].max().date()
    date_max = date_max + timedelta(days=1)
    start_date, end_date = st.slider(
        "Select date range:",
        min_value=date_min,
        max_value=date_max,
        value=(date_min, date_max),
        format="DD.MM.YYYY",
    )
    return (start_date, end_date)


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


def setup_line_plot(df: DataFrame) -> None:
    return create_plotly_pace_chart(
        df,
        x_col="date",
        y_col="speed",
        y_text_col="average_pace",
        y_col_2="average_heart_rate",
    )


def setup_pace_histogram(df: DataFrame, number_of_bins: int) -> None:
    if df.empty:
        fig = get_empty_figure()
    else:
        fig = get_df_pace_histogram(df, "pace_float", number_of_bins)
    return fig


def render_filter_parameters(
    df: DataFrame,
) -> FilterParameters:
    with st.expander("Filters"):
        date_range_col, pace_col, distance_col = st.columns(3)
        with date_range_col:
            date_range = setup_date_range_selection(df)
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


def main() -> None:
    df = DATA.copy()
    st.title("Pace Overview")
    render_pace_metrics(df)
    filters = render_filter_parameters(df)
    df = filter_dataframe_by_parameters(df, filters)
    histogram_tab, line_plot_tab, pace_hpm_tab = st.tabs(
        [
            f"{Icons.bar_chart} Pace Histogram",
            f"{Icons.line_chart} Pace and HPM Comparison",
            f"{Icons.analytics} Pace and HPM Correlation",
        ]
    )
    with histogram_tab:
        fig = setup_pace_histogram(df, 15)
        place_figure(fig)
    with line_plot_tab:
        fig = setup_line_plot(df)
        place_figure(fig)
    with pace_hpm_tab:
        pivot_df = create_df_pivot_hpm_pace(df)
        pivot_df.columns.name = "Pace km/min"
        fig = create_heat_map_ordinary(pivot_df, "Pace & HPM Correlation in %")
        place_figure(fig)


if __name__ == "__main__":
    main()
