import streamlit as st
from pandas import DataFrame

from garmin.constants import STEPS_DF
from garmin.utils.pandas_helpers import aggregrate_df_by_dict, filter_dataframe
from garmin.utils.time_utils import get_current_year
from streamlit_utils.config import Icons
from streamlit_utils.utils import Metric, stream_metrics


def get_year_overview_table(df: DataFrame) -> DataFrame:
    agg_dict = {
        "Distance": ("Distance", "sum"),
        "Steps": ("Steps", "sum"),
        "Total": ("Distance", "count"),
        "Goal Reached": ("goal_reached", "sum"),
    }
    df = aggregrate_df_by_dict(df, "year", agg_dict)
    df["Distance"] = df["Distance"] / 1000
    df["Goal"] = df["Goal Reached"] / df["Total"]
    df["Goal"] = df["Goal"].apply(lambda x: round(x * 100, 2))
    return df


def render_metrics(df: DataFrame) -> None:
    df = get_year_overview_table(df.copy())
    current_year = get_current_year()
    st.header("Overview")
    df = filter_dataframe(df, {"year": current_year})
    df_dict = df.to_dict(orient="records")[0]
    description_mapping = {
        "Steps": ("Total Steps", "Steps", ",.0f"),
        "Distance": ("Distance Covered by Steps", "km", ".1f"),
        "Goal": ("Step Goal Conversion Rate", "%", ".2f"),
    }
    metrics = [
        Metric(
            label=f"{description} in {current_year}",
            value=f"{df_dict[attr]:{formatter}} {suffix}",
        )
        for attr, (description, suffix, formatter) in description_mapping.items()
    ]
    stream_metrics(metrics, num_cols=3)


def main() -> None:
    st.title("Steps Statistics")
    df = STEPS_DF.copy()
    render_metrics(df)
    progress_tab, histogram_tab, heatmap_tab = st.tabs(
        [
            f"{Icons.bar_chart} Statistics",
            f"{Icons.monitoring} Progress per Month",
            f"{Icons.analytics} Month Year Distribution",
        ]
    )


main()
