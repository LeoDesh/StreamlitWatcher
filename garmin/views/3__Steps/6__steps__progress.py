from datetime import date

import streamlit as st
from pandas import DataFrame

from garmin.streamlit_helpers.components import (
    get_current_month_metric,
    get_monthly_progression_figure,
    render_steps_dialog,
    setup_heatmap,
    validate_streamlit_chart_selection,
)
from garmin.streamlit_helpers.load import load_steps_df
from garmin.streamlit_helpers.model import (
    GridConfig,
    Metric,
    create_grid,
    stream_metrics,
)
from garmin.streamlit_helpers.nagivation import breadcrumbs
from garmin.utils.pandas_helpers import aggregate_df_named_column, filter_dataframe
from garmin.utils.time_utils import get_current_year, parse_str_date


def set_progress_state(value: date | None = None) -> None:
    st.session_state["steps_progress"] = value


def get_progress_state() -> date:
    return st.session_state["steps_progress"]


def render_metrics(df: DataFrame) -> None:
    metric_funcs = [
        get_average_monthly_steps_metric,
        get_month_with_highest_steps_metric,
        get_current_month_steps_metric,
    ]
    metrics = [func(df) for func in metric_funcs]
    stream_metrics(metrics, num_cols=3)


def compute_monthly_steps(df: DataFrame) -> DataFrame:
    return aggregate_df_named_column(
        df, "monthly_date", "Steps", "steps", sort_asc=False
    )


def get_average_monthly_steps_metric(df: DataFrame) -> Metric:
    df = df.copy()
    current_year = get_current_year()
    df["year"] = df["monthly_date"].apply(lambda x: x.year)
    current_year_df = filter_dataframe(df, {"year": current_year})
    average_steps_per_month = current_year_df["steps"].mean()
    return Metric(
        label=f"Average Steps per month in {current_year}",
        value=f"{average_steps_per_month:,.0f}",
    )


def get_month_with_highest_steps_metric(df: DataFrame) -> Metric:
    df = df.copy().sort_values(by="steps", ascending=False).reset_index()
    value, date = df.loc[0, ["steps", "monthly_date"]]
    return Metric(
        label=f"Month with most Steps covered: {date.strftime('%b, %Y')}",
        value=f"{value:,.0f}",
    )


def get_current_month_steps_metric(df: DataFrame) -> Metric:
    return get_current_month_metric(df, "steps", ",.0f", "Steps")


def render_monthly_progress(df: DataFrame, column: str) -> None:
    monthly_df = compute_monthly_steps(df)
    fig = get_monthly_progression_figure(monthly_df, column)
    event = st.plotly_chart(
        fig, width="stretch", selection_mode="points", on_select="rerun"
    )
    month, _ = validate_streamlit_chart_selection(event)
    if not month:
        return
    selected_month = parse_str_date(month, "%Y-%m-%d").date().replace(day=1)
    current_selected_month = get_progress_state()
    if selected_month != current_selected_month:
        set_progress_state(selected_month)
        df = filter_dataframe(df, {"monthly_date": selected_month})
        header = f"Steps Insights for {selected_month.strftime('%b %Y')}"
        render_steps_dialog(header, df, 3)


def main() -> None:
    breadcrumbs(__file__)
    st.header("Monthly Steps Progress")
    set_progress_state()
    df = load_steps_df()
    monthly_df = compute_monthly_steps(df)
    render_metrics(monthly_df)
    grid = create_grid([GridConfig(columns=2)])
    with grid[0][0]:
        render_monthly_progress(df, "steps")
    with grid[0][1]:
        setup_heatmap(df, "Steps", "Steps", ",.0f")


main()
