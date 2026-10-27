import math
from datetime import date

import streamlit as st
from pandas import DataFrame, cut

from garmin.charts.tools import create_histogram
from garmin.streamlit_helpers.components import (
    get_current_month_metric,
    get_heatmap,
    get_monthly_progression_figure,
    render_distance_range_dialog,
    render_run_dialog,
    track_visit,
    validate_streamlit_chart_selection,
)
from garmin.streamlit_helpers.load import load_running_df
from garmin.streamlit_helpers.model import (
    GridConfig,
    Metric,
    create_grid,
    stream_metrics,
)
from garmin.streamlit_helpers.nagivation import breadcrumbs
from garmin.streamlit_helpers.session_states import (
    ChartEvents,
    get_event_chart_name,
    get_event_state,
    set_event_state,
)
from garmin.utils.bucketing import create_bins_by_bounds
from garmin.utils.misc import compute_delta, create_label_pairs_from_values
from garmin.utils.pandas_helpers import aggregate_df_named_column, filter_dataframe
from garmin.utils.time_utils import (
    get_current_month,
    get_last_day_of_month,
    get_month_previous_year,
    parse_str_date,
)


def construct_header() -> None:
    st.title("Distance Overview")


def setup_histogram(df: DataFrame) -> None:
    df = categorize_df(df)
    chart_df = aggregate_categorization(df)
    fig = create_histogram(
        chart_df,
        "Distribution of kilometres run per unit",
        hovertemplate="%{y} units exercised within range of %{x} km<extra></extra>",
    )
    event = st.plotly_chart(
        fig,
        width="stretch",
        on_select="rerun",
        key=get_event_chart_name(ChartEvents.DISTANCE_RANGE_DIALOG),
        height=450,
    )
    distance_range, _ = validate_streamlit_chart_selection(event)
    if not distance_range:
        st.caption("Click on a distance range to view the runs.")
        return
    previous_selected_distance_range = get_event_state(
        ChartEvents.DISTANCE_RANGE_DIALOG
    )
    if distance_range != previous_selected_distance_range:
        set_event_state(ChartEvents.DISTANCE_RANGE_DIALOG)
        df = filter_dataframe(df, {"distance_range": distance_range})
        header = f"Runs for the distance range {distance_range}"
        render_distance_range_dialog(header, df, 10)


def categorize_df(df: DataFrame) -> DataFrame:
    distance_min = math.floor(df["distance"].min())
    distance_max = math.ceil(df["distance"].max())
    bins = create_bins_by_bounds(distance_min, distance_max, bin_size=2)
    labels = create_label_pairs_from_values(bins, suffix="km")
    df = df.copy()
    df.loc[:, "distance_range"] = cut(df["distance"], bins=bins, labels=labels)
    return df


def aggregate_categorization(df: DataFrame) -> DataFrame:
    counts = df["distance_range"].value_counts().sort_index().reset_index()
    counts.columns = ["km", "Amount"]
    return counts


def compute_monthly_distance(df: DataFrame) -> DataFrame:
    return aggregate_df_named_column(df, "monthly_date", "distance")


def get_current_month_distance_metric(df: DataFrame) -> Metric:
    return get_current_month_metric(df, "distance", ".2f", "km")


def get_distance_before_given_date(df: DataFrame, selected_date: date) -> float:
    current_year_df = filter_dataframe(df, {"year": selected_date.year})
    filtered_df = current_year_df[current_year_df["monthly_date"] <= selected_date]
    return 0 if filtered_df.empty else filtered_df["distance"].sum()


def get_current_year_distance_metric(df: DataFrame) -> Metric:
    df["year"] = df["monthly_date"].apply(lambda x: x.year)
    current_year_km = get_distance_before_given_date(df, get_current_month())
    last_year_km = get_distance_before_given_date(df, get_month_previous_year())
    delta = compute_delta(last_year_km, current_year_km)
    previous_year_month = get_last_day_of_month(get_month_previous_year())
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


def get_date_distance_of_last_run(df: DataFrame) -> tuple[date, float]:
    df = df.copy().sort_values(by="date", ascending=False)
    run_date, distance = df.loc[0, ["date", "distance"]]
    return (run_date, distance)


def render_run_metric(run_date: date, distance: float) -> Metric:
    return Metric(
        label=f"Distance Covered On Last Run ({run_date.strftime('%d.%m.%Y')})",
        value=f"{distance} km",
    )


def render_latest_run_metric(df: DataFrame) -> Metric:
    run_time, distance = get_date_distance_of_last_run(df)
    return render_run_metric(run_time, distance)


def render_monthly_progress(df: DataFrame, column: str, unit: str) -> None:
    monthly_df = compute_monthly_distance(df)
    fig = get_monthly_progression_figure(monthly_df, column, unit)
    event = st.plotly_chart(
        fig,
        width="stretch",
        selection_mode="points",
        on_select="rerun",
        key=get_event_chart_name(ChartEvents.DISTANCE_DIALOG),
    )
    month, _ = validate_streamlit_chart_selection(event)
    if not month:
        st.caption("Click on a month to view the details.")
        return
    selected_month = parse_str_date(month, "%Y-%m-%d").date().replace(day=1)
    previous_selected_month = get_event_state(ChartEvents.DISTANCE_DIALOG)
    if selected_month != previous_selected_month:
        set_event_state(ChartEvents.DISTANCE_DIALOG, selected_month)
        df = filter_dataframe(df, {"monthly_date": selected_month})
        render_run_dialog(selected_month, df, 3)


@track_visit
def main() -> None:
    breadcrumbs(__file__)
    construct_header()
    set_event_state(ChartEvents.DISTANCE_RANGE_DIALOG)
    set_event_state(ChartEvents.DISTANCE_DIALOG)
    df = load_running_df()
    render_distance_metrics(df)
    grid_config = [GridConfig(1, height=550), GridConfig(2)]
    grid = create_grid(grid_config)
    with grid[0][0]:
        render_monthly_progress(df, "distance", "km")
    with grid[1][0]:
        setup_histogram(df)
    with grid[1][1]:
        fig = get_heatmap(df, "Distance", "km")
        st.plotly_chart(fig, width="stretch", height=485)


if __name__ == "__main__":
    main()
