import streamlit as st
from pandas import DataFrame

from garmin.constants import ACTIVITY_DF, RUNNING_DF, STEPS_DF
from garmin.utils.pandas_helpers import aggregrate_df_by_dict, filter_dataframe
from garmin.utils.time_utils import get_current_year
from streamlit_utils.nagivation import get_page_mapping, prettify_section
from streamlit_utils.utils import Metric, stream_metrics


def filter_df_for_current_year(df: DataFrame, column: str = "year") -> DataFrame:
    current_year = get_current_year()
    return filter_dataframe(df, {column: current_year})


def render_metrics(dfs: list[DataFrame]) -> None:
    metric_creation_list = [get_running_metric, get_activity_metric, get_step_metric]
    metrics = [
        metric_func(filter_df_for_current_year(df))
        for metric_func, df in zip(metric_creation_list, dfs)
    ]
    stream_metrics(metrics, num_cols=len(metrics))


def get_running_metric(df: DataFrame) -> Metric:
    agg_df = aggregrate_df_by_dict(
        df, "year", {"units": ("year", "count"), "distance": ("distance", "sum")}
    )
    df_dict = agg_df.to_dict(orient="records")[0]
    return Metric(
        label=f"Runs in {df_dict['year']}",
        value=f"{df_dict['distance']} km in {df_dict['units']} Units",
    )


def get_activity_metric(df: DataFrame) -> Metric:
    agg_df = aggregrate_df_by_dict(
        df,
        "year",
        {"units": ("year", "count"), "activities": ("activity_type", "nunique")},
    )
    df_dict = agg_df.to_dict(orient="records")[0]
    return Metric(
        label=f"Activities in {df_dict['year']}",
        value=f"Total of  {df_dict['units']} activities",
    )


def get_step_metric(df: DataFrame) -> Metric:
    agg_df = aggregrate_df_by_dict(
        df,
        "year",
        {"steps": ("Steps", "sum"), "distance": ("Distance", "sum")},
    )
    df_dict = agg_df.to_dict(orient="records")[0]
    return Metric(
        label=f"Steps in {df_dict['year']}",
        value=f"{df_dict['steps']:,.0f} steps taken",
    )


def render_cards():
    section_home_page_mapping = {
        section: pages[0] for section, pages in get_page_mapping().items() if section
    }
    pages = section_home_page_mapping.values()
    sections = section_home_page_mapping.keys()
    descriptions = [
        "Check distance, pace and overall running statistics.",
        "View any activity.",
        "Investigate daily steps.",
    ]
    cols = st.columns(len(descriptions))
    for section, page, col, description in zip(
        sections, pages, cols, descriptions, strict=False
    ):
        with col, st.container(border=True):
            st.subheader(prettify_section(section))
            st.write(description)
            st.page_link(page, label=f"Go to {section}")


def main() -> None:
    st.header("Activity Diary")
    # st.write(RUNNING_DF)
    render_metrics([RUNNING_DF, ACTIVITY_DF, STEPS_DF])
    render_cards()


if __name__ == "__main__":
    main()
