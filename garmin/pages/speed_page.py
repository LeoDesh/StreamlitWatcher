import streamlit as st
from garmin.constants import DATA
from garmin.plots.visualization import (
    create_plotly_line_chart,
    get_df_pace_histogram,
    get_empty_figure,
)
from typing import Tuple
import pandas as pd
from datetime import date, timedelta
import math



def setup_date_range_selection(df: pd.DataFrame) -> Tuple[date, date]:
    date_min = df["DATE"].min().date()
    date_max: date = df["DATE"].max().date()
    date_max = date_max + timedelta(days=1)
    start_date, end_date = st.sidebar.slider(
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
    chosen_pace_min, chosen_pace_max = st.sidebar.slider(
        "Select pace range:",
        min_value=pace_min,
        max_value=pace_max,
        value=(pace_min, pace_max),
    )
    return (chosen_pace_min, chosen_pace_max)


def setup_distance_range_selection(df: pd.DataFrame) -> Tuple[int, int]:
    distance_min = 0
    distance_max = math.ceil(df["DISTANCE"].max())
    chosen_distance_min, chosen_distance_max = st.sidebar.slider(
        "Select distance range:",
        min_value=distance_min,
        max_value=distance_max,
        value=(distance_min, distance_max),
    )
    return (chosen_distance_min, chosen_distance_max)


def setup_number_of_bins() -> int:
    return st.sidebar.number_input("Number of Bins", 5, 30, 15)


def setup_line_plot(df: pd.DataFrame):
    fig = create_plotly_line_chart(df, x_col="DATE", y_col="SPEED")
    st.plotly_chart(fig)


def setup_pace_histogram(df: pd.DataFrame, number_of_bins: int):
    if df.empty:
        fig = get_empty_figure()
    else:
        fig = get_df_pace_histogram(df, "PACE_FLOAT", number_of_bins)
    st.pyplot(fig)


def main():
    df = DATA
    st.title("Speed Overview")
    start_date, end_date = setup_date_range_selection(df)
    min_pace, max_pace = setup_pace_range_selection()
    min_distance, max_distance = setup_distance_range_selection(df)
    number_of_bins = setup_number_of_bins()

    df = df[
        (df["DATE"] >= pd.Timestamp(start_date))
        & (df["DATE"] <= pd.Timestamp(end_date))
        & (df["PACE_FLOAT"] <= max_pace)
        & (df["PACE_FLOAT"] >= min_pace)
        & (df["DISTANCE"] <= max_distance)
        & (df["DISTANCE"] >= min_distance)
    ]
    setup_line_plot(df)
    setup_pace_histogram(df, number_of_bins)


if __name__ == "__main__":
    main()
