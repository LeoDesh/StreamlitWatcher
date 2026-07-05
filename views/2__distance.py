import math
from datetime import date, timedelta

import streamlit as st
from pandas import DataFrame

from garmin.constants import DATA
from garmin.plots.visualization import (
    create_bar_chart_ordinary_axis,
    create_heat_map_monthly_axis,
    get_df_km_histogram,
)
from garmin.utils.misc import calculate_int_bins, prettify
from garmin.utils.pandas_helpers import filter_dataframe, generate_dates_df
from streamlit_utils.chart_helpers import place_figure
from streamlit_utils.config import Icons
from streamlit_utils.utils import Metric, stream_metrics


def get_current_month() -> date:
    today = date.today()
    return date(today.year, today.month, 1)


def get_month_previous_year() -> date:
    current_month = get_current_month()
    return date(current_month.year - 1, current_month.month, 1)


def get_previous_month() -> date:
    current_month = get_current_month()
    last_of_month = current_month + timedelta(days=-1)
    return date(last_of_month.year, last_of_month.month, 1)


def construct_header() -> None:
    st.title("Distance Overview")


def setup_histogram(df: DataFrame) -> None:
    distance_min = math.floor(df["DISTANCE"].min())
    distance_max = math.ceil(df["DISTANCE"].max())
    bins = calculate_int_bins(distance_min, distance_max, 2)
    fig = get_df_km_histogram(df, "DISTANCE", bins)
    place_figure(fig)


def compute_delta(src: float, trg: float):
    if src and trg:
        return round((trg - src) / src * 100, 2)
    if src:
        return -100
    if trg:
        return 100
    return 0


def setup_heatmap(df: DataFrame) -> None:
    df = df.copy()
    df.columns = [prettify(col) for col in df.columns]
    pivot_df = df.pivot_table(
        values="Distance", index="Year", columns="Month", aggfunc="sum"
    ).fillna(0)
    fig = create_heat_map_monthly_axis(
        pivot_df,
        "Distance in km per (Month, Year)",
        hovertemplate="%{y}, %{x}: %{z:.2f} km <extra></extra>",
    )
    place_figure(fig)


def compute_monthly_distance(df: DataFrame) -> DataFrame:
    df = df.copy()
    df["DATE"] = df["DATE"].dt.date
    df["date"] = df["DATE"].apply(lambda x: date(x.year, x.month, 1))
    return (
        df.groupby(by="date")
        .agg(total=("DISTANCE", "sum"))
        .sort_values(by="date")
        .reset_index()
    )


def get_current_month_metric(df: DataFrame) -> Metric:
    current_month = get_current_month()
    previous_year_month = get_month_previous_year()
    date_km_dict = dict(zip(df["date"], df["total"]))
    current_km, previous_km = (
        date_km_dict.get(current_month, 0),
        date_km_dict.get(previous_year_month, 0),
    )
    delta = compute_delta(previous_km, current_km)
    return Metric(
        label="Distance Covered Current Month",
        value=f"{round(current_km, 2)} km",
        delta=f"{delta} %",
        help=f"Comparison with {previous_year_month.strftime('%d.%m.%Y')}",
    )


def get_distance_before_given_date(df: DataFrame, selected_date: date) -> float:
    df_current_year = filter_dataframe(df, {"year": selected_date.year})
    df_filtered = df_current_year[df_current_year["date"] <= selected_date]
    return 0 if df_filtered.empty else df_filtered["total"].sum()


def get_current_year_metric(df: DataFrame) -> Metric:
    df["year"] = df["date"].apply(lambda x: x.year)
    current_year_km = get_distance_before_given_date(df, get_current_month())
    last_year_km = get_distance_before_given_date(df, get_month_previous_year())
    delta = compute_delta(last_year_km, current_year_km)
    previous_year_month = get_month_previous_year()
    return Metric(
        label="Distance Covered Year To Date",
        value=f"{round(current_year_km, 2)} km",
        delta=f"{delta} %",
        help=f"Comparison with Timespan: 01.01.{previous_year_month.year}-{previous_year_month.strftime('%d.%m.%Y')}",
    )


def render_distance_metrics(df: DataFrame) -> None:
    month_metric = get_current_month_metric(df)
    year_metric = get_current_year_metric(df)
    stream_metrics([month_metric, year_metric])


def setup_progress_plot(df: DataFrame) -> None:
    date_df = generate_dates_df(
        df["date"].min(), df["date"].max(), freq="MS", date_column="date"
    )
    df = date_df.merge(df, how="left", on="date").fillna(0)
    df["distance"] = df["total"].cumsum()
    fig = create_bar_chart_ordinary_axis(
        df,
        "date",
        "distance",
        "Total Distance covered per",
        hovertemplate="%{y} km distance covered up to %{x} <extra></extra>",
    )
    place_figure(fig)


def main() -> None:
    construct_header()
    df = DATA.copy()
    monthly_distance_df = compute_monthly_distance(df)
    render_distance_metrics(monthly_distance_df)
    progress_tab, histogram_tab, heatmap_tab = st.tabs(
        [
            f"{Icons.monitoring} Progress per Month",
            f"{Icons.bar_chart} Histogram by Distance Ranges",
            f"{Icons.analytics} Month Year Distribution",
        ]
    )
    with progress_tab:
        setup_progress_plot(monthly_distance_df)
    with histogram_tab:
        setup_histogram(df)
    with heatmap_tab:
        setup_heatmap(df)


if __name__ == "__main__":
    main()
