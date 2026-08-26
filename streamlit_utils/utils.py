from dataclasses import asdict, dataclass
from datetime import date
from typing import Any

import streamlit as st
from pandas import DataFrame

from garmin.etl.constants import MIN_YEAR
from garmin.plots.visualization import create_bar_chart_ordinary_axis
from garmin.utils.misc import prettify
from garmin.utils.time_utils import get_current_date, get_first_of_given_year
from streamlit_utils.chart_helpers import place_figure


@dataclass
class Metric:
    label: str
    value: Any
    delta: Any | None = None
    help: str | None = None

    def render_metric(self) -> None:
        return st.metric(**asdict(self))


def stream_metrics(
    metrics: list[Metric], *, num_cols: int = 4, border: bool = False
) -> None:
    with st.container(border=border):
        cols = st.columns(num_cols)
        for idx, metric in enumerate(metrics):
            col_idx = idx % num_cols
            with cols[col_idx]:
                metric.render_metric()


def create_metrics_container(header: str, activites: dict[str, str]) -> None:
    with st.container(border=True, horizontal_alignment="center"):
        st.header(header)
        metrics = [
            Metric(label=prettify(label), value=value)
            for label, value in activites.items()
        ]
        stream_metrics(metrics, num_cols=len(metrics))


def time_options_provider() -> tuple[date, date]:
    pill_col, user_selection_col = st.columns([2, 1])
    current_date = get_current_date()
    config = {
        "Complete Timespan": (get_first_of_given_year(MIN_YEAR), current_date),
        "YTD": (get_first_of_given_year(current_date.year), current_date),
        "Last Year To Date": (
            get_first_of_given_year(current_date.year - 1),
            current_date,
        ),
        "Last 3 Years To Date": (
            get_first_of_given_year(current_date.year - 3),
            current_date,
        ),
    }
    options = [*config.keys(), "Custom Data"]
    selection = pill_col.pills(
        "Select Time Option", options, default="Complete Timespan"
    )
    if selection in config:
        return config[selection]
    else:
        date_range = user_selection_col.date_input(
            "Select Timespan",
            value=(
                get_first_of_given_year(current_date.year),
                current_date,
            ),
            max_value=current_date,
            min_value=get_first_of_given_year(MIN_YEAR),
        )
        if isinstance(date_range, tuple) and len(date_range) == 2:
            return date_range
        else:
            st.stop()


def construct_year_statistics(
    df: DataFrame, config: dict[str, tuple[str, str]], default: str
) -> None:
    category_col, _ = st.columns([1, 2])
    category = category_col.selectbox(
        label="Category",
        index=None,
        options=list(config.keys()),
        placeholder="Choose your Category",
        label_visibility="collapsed",
    )
    category = category if category else default
    header, template = config.get(category)
    hovertemplate = f"{template} in %{{x}} <extra></extra>"
    fig = create_bar_chart_ordinary_axis(
        df, "year", category, y_title=f"{header} per", hovertemplate=hovertemplate
    )
    place_figure(fig)
