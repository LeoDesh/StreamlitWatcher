import streamlit as st
from garmin.constants import DATA
from garmin.plots.visualization import get_df_bar_chart, get_df_distributions
from matplotlib.figure import Figure
from streamlit_utils.chart_helpers import place_figure
import pandas as pd
import math

def construct_header():
    st.title("Distance Overview")


def setup_bar_chart(df: pd.DataFrame, groupby_column: str) -> Figure:
    value_column = "DISTANCE"
    return get_df_bar_chart(df, groupby_column, value_column)
    

def calculate_bins(min_value:int,max_value:int,factor:int):
    steps = int(float(max_value-min_value) // factor)
    return [min_value + factor*idx for idx in range(steps+2)]

def setup_histogram(df:pd.DataFrame):
    distance_min = math.floor(df["DISTANCE"].min())
    distance_max = math.ceil(df["DISTANCE"].max())
    bins = calculate_bins(distance_min,distance_max,2)
    return get_df_distributions(df,"DISTANCE",bins)

def main():
    construct_header()
    df = DATA
    histogram_km,barchart_km_year,barchart_km_month = st.tabs(["Histogram by 'km'","'km' per Year","'km' per Month"])
    with histogram_km:
        fig = setup_histogram(df)
        place_figure(fig)
    with barchart_km_year:
        fig = setup_bar_chart(df, "YEAR")
        place_figure(fig)
    with barchart_km_month:
        fig = setup_bar_chart(df, "MONTH")
        place_figure(fig)
    

if __name__ == "__main__":
    main()
