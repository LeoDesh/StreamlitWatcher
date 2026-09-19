import math
from datetime import date

import streamlit as st
from pandas import DataFrame, cut

from garmin.charts.tools import create_histogram
from garmin.streamlit_helpers.load import load_running_df
from garmin.streamlit_helpers.model import GridConfig
from garmin.streamlit_helpers.utils import (
    Metric,
    breadcrumbs,
    create_grid,
    get_current_month_metric,
    render_monthly_progression,
    setup_heatmap,
    stream_metrics,
)
from garmin.utils.bucketing import create_bins_by_bounds
from garmin.utils.misc import compute_delta, create_label_pairs_from_values
from garmin.utils.pandas_helpers import aggregate_df_named_column, filter_dataframe
from garmin.utils.time_utils import (
    get_current_month,
    get_last_day_of_date,
    get_month_previous_year,
)


def construct_header() -> None:
    st.title("Distance Overview")


def setup_histogram(df: DataFrame) -> None:
    df = create_histogram_distance_df(df)
    fig = create_histogram(
        df,
        "Distribution of kilometres run per unit",
        hovertemplate="%{y} units exercised within range of %{x} km<extra></extra>",
    )
    st.plotly_chart(fig, width="stretch")


def create_histogram_distance_df(df: DataFrame) -> DataFrame:
    distance_min = math.floor(df["distance"].min())
    distance_max = math.ceil(df["distance"].max())
    bins = create_bins_by_bounds(distance_min, distance_max, bin_size=2)
    labels = create_label_pairs_from_values(bins, suffix="km")
    df = df.copy()
    df.loc[:, "binned"] = cut(df["distance"], bins=bins, labels=labels)
    counts = df["binned"].value_counts().sort_index().reset_index()
    counts.columns = ["km", "Amount"]
    return counts


def compute_monthly_distance(df: DataFrame) -> DataFrame:
    return aggregate_df_named_column(df, "monthly_date", "distance")


def get_current_month_distance_metric(df: DataFrame) -> Metric:
    return get_current_month_metric(df, "distance", ".2f", "km")


def get_distance_before_given_date(df: DataFrame, selected_date: date) -> float:
    df_current_year = filter_dataframe(df, {"year": selected_date.year})
    df_filtered = df_current_year[df_current_year["monthly_date"] <= selected_date]
    return 0 if df_filtered.empty else df_filtered["distance"].sum()


def get_current_year_distance_metric(df: DataFrame) -> Metric:
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
    month_metric = get_current_month_distance_metric(monthly_distance_df)
    year_metric = get_current_year_distance_metric(monthly_distance_df)
    latest_run_metric = render_latest_run_metric(df)
    stream_metrics([month_metric, year_metric, latest_run_metric])


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
    breadcrumbs(__file__)
    construct_header()
    df = load_running_df()
    render_distance_metrics(df)
    grid_config = [GridConfig(1, height=550), GridConfig(2)]
    grid = create_grid(grid_config)
    with grid[0][0]:
        monthly_df = compute_monthly_distance(df)
        render_monthly_progression(monthly_df, "distance", "km")
    with grid[1][0]:
        setup_histogram(df)
    with grid[1][1]:
        setup_heatmap(df, "Distance", "km")


if __name__ == "__main__":
    main()
