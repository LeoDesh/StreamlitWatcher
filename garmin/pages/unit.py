import streamlit as st
from garmin.constants import DATA
from garmin.plots.visualization import (
    get_df_count_year_month_histogram,
    get_df_count_from_column_histogram,
    get_empty_figure,
)
from typing import Tuple
import pandas as pd
import math




def setup_date_range_selection(df: pd.DataFrame) -> Tuple[int, int]:
    min_year: int = df["YEAR"].min()
    max_year: int = df["YEAR"].max()
    start_year, end_year = st.sidebar.slider(
        "Select date range:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
    )
    return (start_year, end_year)


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




def setup_running_year_month_histogram(df: pd.DataFrame):
    if df.empty:
        fig = get_empty_figure()
    else:
        fig = get_df_count_year_month_histogram(df)
    st.pyplot(fig)


def setup_running_year_histogram(df: pd.DataFrame):
    if df.empty:
        fig = get_empty_figure()
    else:
        fig = get_df_count_from_column_histogram(df,"YEAR")
    st.pyplot(fig)

def setup_running_month_histogram(df: pd.DataFrame):
    if df.empty:
        fig = get_empty_figure()
    else:
        fig = get_df_count_from_column_histogram(df,"MONTH")
    st.pyplot(fig)


def main():
    df = DATA
    st.title("Unit Plots")
    start_year, end_year = setup_date_range_selection(df)
    df = df[(df["YEAR"] >= start_year) & (df["YEAR"] <= end_year)]
    setup_running_year_histogram(df)
    setup_running_month_histogram(df)
    setup_running_year_month_histogram(df)
    


if __name__ == "__main__":
    main()
