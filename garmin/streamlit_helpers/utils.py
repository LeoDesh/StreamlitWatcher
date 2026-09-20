from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import streamlit as st
from pandas import DataFrame
from streamlit import page_link
from streamlit.delta_generator import DeltaGenerator
from streamlit.navigation.page import StreamlitPage

from garmin.charts.tools import (
    create_bar_chart,
    create_heat_map_monthly_axis,
)
from garmin.etl import MIN_YEAR
from garmin.streamlit_helpers.config import VIEW_FOLDER, Icons
from garmin.streamlit_helpers.model import GridConfig
from garmin.streamlit_helpers.nagivation import (
    generate_page_from_file_path,
    get_homepage,
    get_page_part,
    look_for_file_in_folder,
)
from garmin.utils.misc import compute_delta, prettify
from garmin.utils.pandas_helpers import generate_dates_df
from garmin.utils.time_utils import (
    get_current_date,
    get_current_month,
    get_first_of_given_year,
    get_last_day_of_date,
    get_month_previous_year,
)


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


def create_metrics_container(header: str, data: dict[str, str]) -> None:
    with st.container(border=True, horizontal_alignment="center"):
        st.header(header)
        metrics = [
            Metric(label=prettify(label), value=value) for label, value in data.items()
        ]
        stream_metrics(metrics, num_cols=len(metrics))


def time_options_provider() -> tuple[date, date]:
    pill_col, user_selection_col = st.columns([2, 1])
    current_date = get_current_date()
    current_year = current_date.year
    latest_date = current_date + timedelta(days=1)
    config = {
        "Complete Timespan": (get_first_of_given_year(MIN_YEAR), latest_date),
        "YTD": (get_first_of_given_year(current_year), latest_date),
        "Last Year To Date": (
            get_first_of_given_year(current_year - 1),
            latest_date,
        ),
        "Last 3 Years To Date": (
            get_first_of_given_year(current_year - 3),
            latest_date,
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
    fig = create_bar_chart(
        df, "year", category, y_title=f"{header} per", hovertemplate=hovertemplate
    )
    st.plotly_chart(fig, width="stretch")


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
    fig = create_bar_chart(
        df,
        "month",
        target_column,
        y_title=f"Total {target_column} covered per",
        hovertemplate=f"%{{y:,.0f}} {unit} covered up to %{{x}} <extra></extra>",
        show_x_title=False,
    )
    st.plotly_chart(fig, width="stretch")


def setup_heatmap(df: DataFrame, target_column: str, unit: str = "") -> None:
    df = df.copy()
    df.columns = [prettify(col) for col in df.columns]
    pivot_df = df.pivot_table(
        values=target_column, index="Year", columns="Month", aggfunc="sum"
    ).fillna(0)
    column_details = f" in {unit}" if unit else ""
    template_details = unit if unit else ""
    fig = create_heat_map_monthly_axis(
        pivot_df,
        f"{target_column}{column_details} per month over years",
        hovertemplate=f"%{{y}}, %{{x}}: %{{z:.2f}} {template_details} <extra></extra>",
    )
    st.plotly_chart(fig, width="stretch")


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


def get_current_month_metric(
    df: DataFrame, column: str, format: str, unit: str
) -> Metric:
    current_month = get_current_month()
    previous_year_month = get_month_previous_year()
    date_km_dict = dict(zip(df["monthly_date"], df[column]))
    current_km, previous_km = (
        date_km_dict.get(current_month, 0),
        date_km_dict.get(previous_year_month, 0),
    )
    delta = compute_delta(previous_km, current_km)
    return Metric(
        label="Distance Covered Current Month",
        value=f"{current_km:{format}} {unit}",
        delta=f"{delta} %",
        help=f"Comparison with {previous_year_month.strftime('%b, %Y')}",
    )


def get_file_references(file_path: Path) -> list[StreamlitPage]:
    page_part = get_page_part(file_path)
    parent_folder = file_path.parent
    file_stem = file_path.stem
    file_parts = [
        part
        for part in file_stem.split("__")
        if not (part.isdigit() or part == page_part)
    ]
    return [
        generate_page_from_file_path(
            look_for_file_in_folder(parent_folder, file_part), parent_folder.stem
        )
        for file_part in file_parts
        if look_for_file_in_folder(parent_folder, file_part)
    ]


def get_file_path(file_dunder: str) -> Path:
    path = Path(file_dunder).resolve()
    parts = path.parts
    view_folder_name = VIEW_FOLDER.name
    parent_folder_name = VIEW_FOLDER.parent.name
    if view_folder_name in parts and parent_folder_name in parts:
        idx = parts.index(parent_folder_name)
        return Path(*parts[idx:])
    return path


def breadcrumbs(file_dunder: str) -> None:
    file_path = get_file_path(file_dunder)
    with st.container(horizontal=True, vertical_alignment="center"):
        home_page = get_homepage()
        page_link(home_page, label="Home")
        st.markdown(Icons.ARROW_RIGHT, width="content")
        file_references = get_file_references(file_path)
        for reference_page in file_references:
            page_link(reference_page)
            st.markdown(Icons.ARROW_RIGHT, width="content")
        page_part = get_page_part(file_path)
        current_page_name = " ".join(prettify(part) for part in page_part.split("_"))
        st.markdown(f"**{current_page_name}**")
