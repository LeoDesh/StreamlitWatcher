import streamlit as st
from garmin.constants import DATA
from garmin.plots.visualization import (
    get_df_km_histogram,
    create_bar_chart,
    create_heat_map,
)
from matplotlib.figure import Figure
from streamlit_utils.chart_helpers import place_figure
import pandas as pd
import math


def construct_header() -> None:
    st.title("Distance Overview")


def setup_bar_chart(df: pd.DataFrame, groupby_column: str, month: bool) -> Figure:
    value_column = "DISTANCE"
    df = df.groupby(by=groupby_column, as_index=False).agg(
        amount=(value_column, "count")
    )
    return create_bar_chart(df, groupby_column, "amount", month)


def calculate_bins(min_value: int, max_value: int, factor: int) -> list[float]:
    steps = int(float(max_value - min_value) // factor)
    return [min_value + factor * idx for idx in range(steps + 2)]


def setup_histogram(df: pd.DataFrame):
    distance_min = math.floor(df["DISTANCE"].min())
    distance_max = math.ceil(df["DISTANCE"].max())
    bins = calculate_bins(distance_min, distance_max, 2)
    return get_df_km_histogram(df, "DISTANCE", bins)


def setup_heatmap(df: pd.DataFrame):
    pivot_df = df.pivot_table(
        values="DISTANCE", index="YEAR", columns="MONTH", aggfunc="sum"
    ).fillna(0)
    return create_heat_map(pivot_df,"")


def main():
    construct_header()
    df = DATA
    histogram_tab, heatmap_tab = st.tabs(
        [
            ":material/bar_chart: Histogram by 'km'",
            ":material/analytics: Month Year Distribution",
        ]
    )
    with histogram_tab:
        fig = setup_histogram(df)
        place_figure(fig)
    with heatmap_tab:
        fig = setup_heatmap(df)
        place_figure(fig)

if __name__ == "__main__":
    main()
