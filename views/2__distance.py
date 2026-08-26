import math
from datetime import date

import streamlit as st
from pandas import DataFrame

from garmin.constants import RUNNING_DF
from garmin.plots.visualization import (
    create_bar_chart_ordinary_axis,
    create_heat_map_monthly_axis,
    get_df_km_histogram,
)
from garmin.utils.misc import (
    calculate_int_bins,
    compute_delta,
    get_last_day_of_date,
    prettify,
)
from garmin.utils.pandas_helpers import filter_dataframe, generate_dates_df
from garmin.utils.time_utils import get_current_month, get_month_previous_year
from streamlit_utils.chart_helpers import place_figure
from streamlit_utils.config import Icons
from streamlit_utils.utils import Metric, stream_metrics


def construct_header() -> None:
    st.title("Distance Overview")


def setup_histogram(df: DataFrame) -> None:
    distance_min = math.floor(df["distance"].min())
    distance_max = math.ceil(df["distance"].max())
    bins = calculate_int_bins(distance_min, distance_max, 2)
    fig = get_df_km_histogram(df, "distance", bins)
    place_figure(fig)


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
    return (
        df.groupby(by="monthly_date")
        .agg(total=("distance", "sum"))
        .sort_values(by="monthly_date")
        .reset_index()
    )


def get_current_month_metric(df: DataFrame) -> Metric:
    current_month = get_current_month()
    previous_year_month = get_month_previous_year()
    date_km_dict = dict(zip(df["monthly_date"], df["total"]))
    current_km, previous_km = (
        date_km_dict.get(current_month, 0),
        date_km_dict.get(previous_year_month, 0),
    )
    delta = compute_delta(previous_km, current_km)
    return Metric(
        label="Distance Covered Current Month",
        value=f"{round(current_km, 2)} km",
        delta=f"{delta} %",
        help=f"Comparison with {previous_year_month.strftime('%b, %Y')}",
    )


def get_distance_before_given_date(df: DataFrame, selected_date: date) -> float:
    df_current_year = filter_dataframe(df, {"year": selected_date.year})
    df_filtered = df_current_year[df_current_year["monthly_date"] <= selected_date]
    return 0 if df_filtered.empty else df_filtered["total"].sum()


def get_current_year_metric(df: DataFrame) -> Metric:
    df["year"] = df["monthly_date"].apply(lambda x: x.year)
    current_year_km = get_distance_before_given_date(df, get_current_month())
    last_year_km = get_distance_before_given_date(df, get_month_previous_year())
    delta = compute_delta(last_year_km, current_year_km)
    previous_year_month = get_last_day_of_date(get_month_previous_year())
    return Metric(
        label="Distance Covered Year To Date",
        value=f"{round(current_year_km, 2)} km",
        delta=f"{delta} %",
        help=f"Comparison with Timespan: 01.01.{previous_year_month.year}-{previous_year_month.strftime('%d.%m.%Y')}",
    )


def render_distance_metrics(df: DataFrame) -> None:
    monthly_distance_df = compute_monthly_distance(df)
    month_metric = get_current_month_metric(monthly_distance_df)
    year_metric = get_current_year_metric(monthly_distance_df)
    latest_run_metric = render_latest_run_metric(df)
    stream_metrics([month_metric, year_metric, latest_run_metric])


def setup_progress_plot(df: DataFrame) -> None:
    df = compute_monthly_distance(df)
    date_df = generate_dates_df(
        df["monthly_date"].min(),
        df["monthly_date"].max(),
        freq="MS",
        date_column="monthly_date",
    )
    df = date_df.merge(df, how="left", on="monthly_date").fillna(0)
    df["distance"] = df["total"].cumsum()
    df["month"] = df["monthly_date"].apply(get_last_day_of_date)
    fig = create_bar_chart_ordinary_axis(
        df,
        "month",
        "distance",
        "Total Distance covered per",
        hovertemplate="%{y} km distance covered up to %{x} <extra></extra>",
        show_x_title=False,
    )
    place_figure(fig)


def get_latest_run(df: DataFrame) -> tuple[date, float]:
    df = df.copy().sort_values(by="date", ascending=False)
    run_date, distance = df.loc[0, ["date", "distance"]]
    return (run_date.date(), distance)


def render_run_metric(run_date: date, distance: float) -> Metric:
    return Metric(
        label=f"Distance Covered On Last Run ({run_date.strftime('%d.%m.%Y')})",
        value=f"{distance} km",
    )


def render_latest_run_metric(df: DataFrame) -> Metric:
    run_time, distance = get_latest_run(df)
    return render_run_metric(run_time, distance)


def main() -> None:
    construct_header()
    df = RUNNING_DF.copy()
    render_distance_metrics(df)
    progress_tab, histogram_tab, heatmap_tab = st.tabs(
        [
            f"{Icons.monitoring} Progress per Month",
            f"{Icons.bar_chart} Histogram by Distance Ranges",
            f"{Icons.analytics} Month Year Distribution",
        ]
    )
    with progress_tab:
        setup_progress_plot(df)
    with histogram_tab:
        setup_histogram(df)
    with heatmap_tab:
        setup_heatmap(df)


if __name__ == "__main__":
    main()
