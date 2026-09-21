import streamlit as st
from pandas import DataFrame

from garmin.streamlit_helpers.components import (
    get_current_month_metric,
    render_monthly_progression,
    setup_heatmap,
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
from garmin.utils.time_utils import get_current_year


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


# Monthly statistics as metrics for Progress/Month Distribution
def main() -> None:
    breadcrumbs(__file__)
    st.header("Monthly Steps Progress")
    df = load_steps_df()
    monthly_df = compute_monthly_steps(df)
    render_metrics(monthly_df)
    grid = create_grid([GridConfig(columns=2)])
    with grid[0][0]:
        render_monthly_progression(monthly_df, "steps")
    with grid[0][1]:
        setup_heatmap(df, "Steps")


main()
