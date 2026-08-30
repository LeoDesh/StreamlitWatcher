from dataclasses import asdict, dataclass
from datetime import date
from typing import Any

import streamlit as st
from pandas import DataFrame
from streamlit.delta_generator import DeltaGenerator

from garmin.etl.constants import MIN_YEAR
from garmin.plots.visualization import (
    create_bar_chart_ordinary_axis,
    create_heat_map_monthly_axis,
)
from garmin.utils.misc import prettify
from garmin.utils.pandas_helpers import generate_dates_df
from garmin.utils.time_utils import (
    get_current_date,
    get_first_of_given_year,
    get_last_day_of_date,
)
from streamlit_utils.chart_helpers import place_figure
from streamlit_utils.model import GridConfig


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


def render_monthly_progression(
    df: DataFrame, target_column: str, unit: str = ""
) -> None:
    unit = unit if unit else target_column
    date_df = generate_dates_df(
        df["monthly_date"].min(),
        df["monthly_date"].max(),
        freq="MS",
        date_column="monthly_date",
    )
    df = date_df.merge(df, how="left", on="monthly_date").fillna(0)
    df[target_column] = df[target_column].cumsum()
    df["month"] = df["monthly_date"].apply(get_last_day_of_date)
    fig = create_bar_chart_ordinary_axis(
        df,
        "month",
        target_column,
        f"Total {target_column} covered per",
        hovertemplate=f"%{{y:,.0f}} {unit} covered up to %{{x}} <extra></extra>",
        show_x_title=False,
    )
    place_figure(fig, layout_tuple=(1, 22, 1))


def setup_heatmap(df: DataFrame, target_column: str, unit: str = "") -> None:
    df = df.copy()
    df.columns = [prettify(col) for col in df.columns]
    pivot_df = df.pivot_table(
        values=target_column, index="Year", columns="Month", aggfunc="sum"
    ).fillna(0)
    column_details = f"in {unit}" if unit else ""
    template_details = unit if unit else ""
    fig = create_heat_map_monthly_axis(
        pivot_df,
        f"{target_column} {column_details} per month over years",
        hovertemplate=f"%{{y}}, %{{x}}: %{{z:.2f}} {template_details} <extra></extra>",
    )
    place_figure(fig, layout_tuple=(1, 22, 1))


def create_grid(grid_config: list[GridConfig]) -> list[list[DeltaGenerator]]:
    grid_layout = []
    for config in grid_config:
        cols_config = st.columns(config.columns, gap=config.gap)
        containers = [
            col.container(border=config.has_border, height=config.height)
            for col in cols_config
        ]
        grid_layout.append(containers)
    return grid_layout
