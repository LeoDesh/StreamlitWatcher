import streamlit as st
from garmin.constants import DATA
from garmin.plots.visualization import get_df_bar_chart, get_df_distributions
import pandas as pd
import math

def construct_header():
    st.title("Distance Overview")


def setup_bar_chart(df: pd.DataFrame, groupby_column: str):
    value_column = "DISTANCE"
    fig = get_df_bar_chart(df, groupby_column, value_column)
    st.pyplot(fig)

def calculate_bins(min_value:int,max_value:int,factor:int):
    steps = int(float(max_value-min_value) // factor)
    return [min_value + factor*idx for idx in range(steps+2)]

def setup_histogram(df:pd.DataFrame):
    distance_min = math.floor(df["DISTANCE"].min())
    distance_max = math.ceil(df["DISTANCE"].max())
    bins = calculate_bins(distance_min,distance_max,2)
    fig = get_df_distributions(df,"DISTANCE",bins)
    st.pyplot(fig)

def main():
    construct_header()
    df = DATA
    setup_histogram(df)
    setup_bar_chart(df, "YEAR")
    setup_bar_chart(df, "MONTH")
    

if __name__ == "__main__":
    main()
