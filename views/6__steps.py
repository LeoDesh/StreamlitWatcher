import streamlit as st
from pandas import DataFrame

from garmin.constants import STEPS_DF
from garmin.utils.pandas_helpers import (
    aggregrate_df_by_dict,
    filter_dataframe,
)
from garmin.utils.time_utils import get_current_year
from streamlit_utils.config import Icons
from streamlit_utils.utils import (
    Metric,
    construct_year_statistics,
    render_monthly_progression,
    setup_heatmap,
    stream_metrics,
)


def get_year_overview_table(df: DataFrame) -> DataFrame:
    agg_dict = {
        "Distance": ("Distance", "sum"),
        "Steps": ("Steps", "sum"),
        "Daily Steps": ("Steps", "mean"),
        "Total": ("Distance", "count"),
        "Goal Reached": ("goal_reached", "sum"),
        "Daily Goal": ("Goal", "mean"),
    }
    df = aggregrate_df_by_dict(df, "year", agg_dict)
    df["Distance"] = df["Distance"] / 1000
    df["Goal Conversion"] = df["Goal Reached"] / df["Total"]
    df["Goal Conversion"] = df["Goal Conversion"].apply(lambda x: round(x * 100, 2))
    return df


def render_metrics(df: DataFrame) -> None:
    current_year = get_current_year()
    st.header("Overview")
    df = filter_dataframe(df, {"year": current_year})
    df_dict = df.to_dict(orient="records")[0]
    description_mapping = {
        "Steps": ("Total Steps", "Steps", ",.0f"),
        "Distance": ("Distance Covered by Steps", "km", ".1f"),
        "Goal Conversion": ("Step Goal Conversion Rate", "%", ".2f"),
    }
    metrics = [
        Metric(
            label=f"{description} in {current_year}",
            value=f"{df_dict[attr]:{formatter}} {suffix}",
        )
        for attr, (description, suffix, formatter) in description_mapping.items()
    ]
    stream_metrics(metrics, num_cols=3)


def render_year_statistics(df: DataFrame) -> None:
    mapping = {
        "Steps": ("Total Steps", "%{y:,.0f} Steps"),
        "Distance": ("Distance Covered", "%{y:.2f} km covered"),
        "Daily Steps": (
            "Average Daily Steps",
            "%{y:.0f} Steps per day on average",
        ),
        "Goal Conversion": (
            "Daily Step Goal Reached",
            "%{y:.2f} % of daily Step Goal reached",
        ),
        "Daily Goal": (
            "Average Daily Step Goal",
            "%{y:.0f} Steps on average required to fulfill the daily goal",
        ),
    }
    construct_year_statistics(df, mapping, "Steps")


def compute_monthly_steps(df: DataFrame) -> DataFrame:
    df = df.copy()
    return (
        df.groupby(by="monthly_date")
        .agg(steps=("Steps", "sum"))
        .sort_values(by="monthly_date")
        .reset_index()
    )


# uv run ruff check --fix
def main() -> None:
    st.title("Steps Statistics")
    df = STEPS_DF.copy()
    overview_df = get_year_overview_table(df.copy())
    render_metrics(overview_df)
    progress_tab, histogram_tab, heatmap_tab = st.tabs(
        [
            f"{Icons.bar_chart} Statistics",
            f"{Icons.monitoring} Progress per Month",
            f"{Icons.analytics} Month Year Distribution",
        ]
    )
    with progress_tab:
        render_year_statistics(overview_df)
    with histogram_tab:
        monthly_df = compute_monthly_steps(df)
        render_monthly_progression(monthly_df, "steps")
    with heatmap_tab:
        setup_heatmap(df, "Steps")


main()
