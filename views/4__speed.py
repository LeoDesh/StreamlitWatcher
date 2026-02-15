import streamlit as st
from garmin.constants import DATA
from garmin.plots.visualization import (
    get_df_pace_histogram,
    get_empty_figure,
    create_plotly_pace_chart
)
from streamlit_utils.chart_helpers import place_figure
from typing import Tuple
import pandas as pd
from datetime import date, timedelta
import math



def setup_date_range_selection(df: pd.DataFrame) -> Tuple[date, date]:
    date_min = df["DATE"].min().date()
    date_max: date = df["DATE"].max().date()
    date_max = date_max + timedelta(days=1)
    start_date, end_date = st.slider(
        "Select date range:",
        min_value=date_min,
        max_value=date_max,
        value=(date_min, date_max),
        format="DD.MM.YYYY",
    )
    return (start_date, end_date)


def setup_pace_range_selection() -> Tuple[int, int]:
    pace_min = 1
    pace_max = 30
    chosen_pace_min, chosen_pace_max = st.slider(
        "Select pace range (min/km):",
        min_value=pace_min,
        max_value=pace_max,
        value=(pace_min, pace_max),
    )
    return (chosen_pace_min, chosen_pace_max)


def setup_distance_range_selection(df: pd.DataFrame) -> Tuple[int, int]:
    distance_min = 0
    distance_max = math.ceil(df["DISTANCE"].max())
    chosen_distance_min, chosen_distance_max = st.slider(
        "Select distance range (km):",
        min_value=distance_min,
        max_value=distance_max,
        value=(distance_min, distance_max),
    )
    return (chosen_distance_min, chosen_distance_max)


def setup_number_of_bins() -> int:
    return st.number_input("Number of Bins", 5, 30, 15)


def setup_line_plot(df: pd.DataFrame) -> None:
    return create_plotly_pace_chart(df, x_col="DATE", y_col="SPEED",y_text_col="AVERAGE_PACE",y_col_2="AVG_HEART_RATE")
    


def setup_pace_histogram(df: pd.DataFrame, number_of_bins: int) -> None:
    if df.empty:
        fig = get_empty_figure()
    else:
        fig = get_df_pace_histogram(df, "PACE_FLOAT", number_of_bins)
    return fig


def main():
    df = DATA
    st.title("Speed Overview")
    with st.expander("Filters"):
        date_range_col,pace_col,distance_col,bins_col = st.columns(4)
        with date_range_col:
            start_date, end_date = setup_date_range_selection(df)
        with pace_col:
            min_pace, max_pace = setup_pace_range_selection()
        with distance_col:
            min_distance, max_distance = setup_distance_range_selection(df)
        with bins_col:
            number_of_bins = setup_number_of_bins()

    df = df[
        (df["DATE"] >= pd.Timestamp(start_date))
        & (df["DATE"] <= pd.Timestamp(end_date))
        & (df["PACE_FLOAT"] <= max_pace)
        & (df["PACE_FLOAT"] >= min_pace)
        & (df["DISTANCE"] <= max_distance)
        & (df["DISTANCE"] >= min_distance)
    ]
    line_plot_tab,histogram_tab = st.tabs([":material/multiline_chart: Speed Chart",":material/bar_chart: Histogram Chart"])
    with line_plot_tab:
        fig = setup_line_plot(df)
        place_figure(fig)
    with histogram_tab:
        fig= setup_pace_histogram(df, number_of_bins)
        place_figure(fig)

if __name__ == "__main__":
    main()
