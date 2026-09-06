import streamlit as st
from pandas import DataFrame

from garmin.constants import STEPS_DF
from garmin.utils.misc import compute_delta
from garmin.utils.pandas_helpers import aggregate_df_named_column, filter_dataframe
from garmin.utils.time_utils import (
    get_current_month,
    get_current_year,
    get_month_previous_year,
)
from streamlit_utils.utils import (
    GridConfig,
    Metric,
    create_grid,
    render_monthly_progression,
    setup_heatmap,
    stream_metrics,
)


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
        label=f"Month with highest Steps count: {date.strftime('%b, %Y')}",
        value=f"{value:,.0f}",
    )


def get_current_month_steps_metric(df: DataFrame) -> Metric:
    current_month = get_current_month()
    previous_year_month = get_month_previous_year()
    steps_dict = dict(zip(df["monthly_date"], df["steps"]))
    current_steps, previous_steps = (
        steps_dict.get(current_month, 0),
        steps_dict.get(previous_year_month, 0),
    )
    delta = compute_delta(previous_steps, current_steps)
    return Metric(
        label="Steps Covered Current Month",
        value=f"{current_steps:,.0f}",
        delta=f"{delta} %",
        help=f"Comparison with {previous_year_month.strftime('%b, %Y')}",
    )


# Monthly statistics as metrics for Progress/Month Distribution
def main() -> None:
    st.header("Monthly Steps Progress")
    df = STEPS_DF.copy()
    monthly_df = compute_monthly_steps(df)
    render_metrics(monthly_df)
    grid = create_grid([GridConfig(columns=2)])
    with grid[0][0]:
        render_monthly_progression(monthly_df, "steps")
    with grid[0][1]:
        setup_heatmap(df, "Steps")


main()
