import streamlit as st
from pandas import DataFrame

from garmin.constants import RUNNING_DF
from garmin.plots.visualization import create_box_plot_chart
from garmin.utils.misc import prettify
from garmin.utils.pace_calculations import (
    transform_seconds_to_hour_minutes_seconds_format,
    transform_speed_to_pace_prettified,
)
from garmin.utils.pandas_helpers import filter_dataframe
from garmin.utils.time_utils import get_current_year
from streamlit_utils.chart_helpers import place_figure
from streamlit_utils.utils import Metric, stream_metrics


def render_comparison_metrics(df: DataFrame) -> None:
    current_year = get_current_year()
    df = filter_dataframe(df, {"year": current_year})
    distance, speed, time = (
        df["distance"].mean(),
        df["speed"].mean(),
        df["time_in_minutes"].mean(),
    )
    metrics_dict = {
        "Current Year Average Distance": f"{distance:.02f} km",
        "Current Year Average Speed": transform_speed_to_pace_prettified(speed),
        "Current Year Average Time": transform_seconds_to_hour_minutes_seconds_format(
            time * 60
        ),
    }
    metrics = [
        Metric(label=label, value=value) for label, value in metrics_dict.items()
    ]
    stream_metrics(metrics)


def render_comparison_dashboard(df: DataFrame) -> None:
    select_box_col, _ = st.columns([1, 5])
    category = select_box_col.selectbox(
        "Category",
        options=["distance", "time_in_minutes", "speed"],
        index=0,
        format_func=prettify,
    )
    fig = create_box_plot_chart(df, category)
    place_figure(fig)


def main() -> None:
    st.header("Comparison")
    df = RUNNING_DF.copy()
    render_comparison_metrics(df)
    render_comparison_dashboard(df)


if __name__ == "__main__":
    main()
