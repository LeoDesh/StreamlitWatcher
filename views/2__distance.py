import math

import pandas as pd
import streamlit as st

from garmin.constants import DATA
from garmin.plots.visualization import (
    create_heat_map_monthly_axis,
    get_df_km_histogram,
)
from garmin.utils.misc import calculate_int_bins, prettify
from streamlit_utils.chart_helpers import place_figure
from streamlit_utils.config import Icons


def construct_header() -> None:
    st.title("Distance Overview")


def setup_histogram(df: pd.DataFrame):
    distance_min = math.floor(df["DISTANCE"].min())
    distance_max = math.ceil(df["DISTANCE"].max())
    bins = calculate_int_bins(distance_min, distance_max, 2)
    return get_df_km_histogram(df, "DISTANCE", bins)


def setup_heatmap(df: pd.DataFrame):
    df = df.copy()
    df.columns = [prettify(col) for col in df.columns]
    pivot_df = df.pivot_table(
        values="Distance", index="Year", columns="Month", aggfunc="sum"
    ).fillna(0)
    return create_heat_map_monthly_axis(
        pivot_df,
        "Distance in km per (Month, Year)",
        hovertemplate="%{y}, %{x}: %{z:.2f} km <extra></extra>",
    )


def main():
    construct_header()
    df = DATA
    histogram_tab, heatmap_tab = st.tabs(
        [
            f"{Icons.bar_chart} Histogram by 'km'",
            f"{Icons.analytics} Month Year Distribution",
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
