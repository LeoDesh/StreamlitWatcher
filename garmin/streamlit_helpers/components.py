import inspect
from collections.abc import Callable
from datetime import date, timedelta
from functools import wraps
from math import ceil
from pathlib import Path
from typing import Any

import streamlit as st
from pandas import DataFrame
from plotly.graph_objects import Figure
from streamlit.typing import PlotlyState

from garmin.charts.tools import (
    create_bar_chart,
    create_heat_map_monthly_axis,
    create_steps_bar_chart,
)
from garmin.etl import MIN_YEAR
from garmin.logger.constants import APP_LOGGER
from garmin.streamlit_helpers.model import Metric, create_metrics_container
from garmin.streamlit_helpers.session_states import ChartEvents, reset_event_state
from garmin.utils.misc import compute_delta, filter_mapping, prettify
from garmin.utils.pandas_helpers import generate_daily_dates_df, generate_dates_df
from garmin.utils.path_utils import get_page_name
from garmin.utils.time_utils import (
    get_current_date,
    get_current_month,
    get_first_of_given_year,
    get_last_day_of_month,
    get_month_previous_year,
)


def extract_ip_address() -> str:
    return st.context.headers.get("X-Forwarded-For", st.context.ip_address) or ""


def extract_covered_ip_address() -> str:
    ip = extract_ip_address()

    if not ip and "." not in ip and ":" not in ip:
        return "0.0.0.0"

    if "." in ip:
        parts = ip.split(".")
        parts[-1] = "XXX"
        return ".".join(parts)

    if ":" in ip:
        parts = ip.split(":")
        parts[-1] = "XXXX"
        return ":".join(parts)


def log_page_visit(page_name: str):
    masked_ip = extract_covered_ip_address()
    user_agent = st.context.headers.get("User-Agent", "Unknown-Agent")
    delimiter = "||"
    APP_LOGGER.info(
        f"LOGGED VISIT {delimiter} Page: {page_name} {delimiter} IP: {masked_ip} {delimiter} Agent: {user_agent}"
    )


def track_visit(func: Callable[[], None]):
    """
    Decorator to automatically log unique page views based on the filename.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        if not st.runtime.exists() or st.session_state.get("is_automated_test", False):
            return func(*args, **kwargs)
        file_path = Path(inspect.getfile(func))
        page_name = get_page_name(file_path)
        state_key = f"logged_{page_name}"
        if state_key not in st.session_state:
            log_page_visit(page_name)
            st.session_state[state_key] = True

        return func(*args, **kwargs)

    return wrapper


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


def get_selection_params(categories: list[str], default: str) -> tuple[str, bool]:
    category_col, to_date_toggle_col, _ = st.columns([1, 1, 1])
    category = category_col.selectbox(
        label="Category",
        index=None,
        options=categories,
        placeholder="Choose your Category",
        label_visibility="collapsed",
    )
    category = category if category else default
    filter_to_current_month = to_date_toggle_col.toggle(
        label="Filter To Current Month",
        value=False,
        help="Excludes runs of previous years in months, which are yet to come",
    )
    return (category, filter_to_current_month)


def filter_prior_months(
    df: DataFrame, month: int, month_col: str = "month"
) -> DataFrame:
    return df[df[month_col] <= month]


def construct_year_statistics(
    df: DataFrame,
    config: dict[str, tuple[str, str]],
    default: str,
    aggregation_func: Callable[[DataFrame], DataFrame],
) -> None:
    category, filter_to_current_month = get_selection_params(
        list(config.keys()), default
    )
    month = get_current_month().month
    df = filter_prior_months(df, month) if filter_to_current_month else df
    df = aggregation_func(df)
    header, template = config.get(category)
    render_year_bar_chart(df, category, header, template)


def render_year_bar_chart(
    df: DataFrame, category: str, header: str, template: str
) -> None:
    hovertemplate = f"{template} in %{{x}} <extra></extra>"
    fig = create_bar_chart(
        df, "year", category, y_title=f"{header} per", hovertemplate=hovertemplate
    )
    st.plotly_chart(fig, width="stretch")


def get_monthly_progression_figure(
    df: DataFrame, target_column: str, unit: str = ""
) -> Figure:
    unit = unit if unit else target_column
    date_df = generate_dates_df(
        df["monthly_date"].min(),
        df["monthly_date"].max(),
        freq="MS",
        date_column="monthly_date",
    )
    df = date_df.merge(df, how="left", on="monthly_date").fillna(0)
    df[target_column] = df[target_column].cumsum()
    df["month"] = df["monthly_date"].apply(get_last_day_of_month)
    return create_bar_chart(
        df,
        "month",
        target_column,
        y_title=f"Total {target_column} covered per",
        hovertemplate=f"%{{y:,.0f}} {unit} covered up to %{{x}} <extra></extra>",
        show_x_title=False,
    )


def render_monthly_progression(df: DataFrame, target_column: str, unit: str) -> None:
    fig = get_monthly_progression_figure(df, target_column, unit)
    st.plotly_chart(fig, width="stretch")


def get_heatmap(
    df: DataFrame, target_column: str, unit: str = "", formatting: str = ".02f"
) -> Figure:
    df = df.copy()
    df.columns = [prettify(col) for col in df.columns]
    pivot_df = df.pivot_table(
        values=target_column, index="Year", columns="Month", aggfunc="sum"
    ).fillna(0)
    column_details = f" in {unit}" if unit else ""
    template_details = unit if unit else ""
    return create_heat_map_monthly_axis(
        pivot_df,
        f"{target_column}{column_details} per month over years",
        hovertemplate=f"%{{y}}, %{{x}}: %{{z:{formatting}}} {template_details} <extra></extra>",
    )


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


def validate_streamlit_chart_selection(state: PlotlyState) -> tuple[Any, Any]:
    if not (state and "selection" in state and "points" in state["selection"]):
        return None
    points = state.selection.points
    if not points:
        return (None, None)
    clicked_point = points[0]
    return (clicked_point.get("x"), clicked_point.get("y"))


def enrich_steps_df(df: DataFrame) -> DataFrame:
    def color_by_steps_and_goal(steps: int, goal: int) -> str:
        if goal <= 0:
            return "bright_red"
        ratio = float(steps) / goal
        if ratio < 0.7:
            return "bright_red"
        elif ratio < 1.0:
            return "bright_amber"
        return "bright_green"

    df["color"] = df.apply(
        lambda row: color_by_steps_and_goal(row["Steps"], row["Goal"]), axis=1
    )
    return df


@st.dialog(
    title="Monthly Steps Breakdown",
    width="large",
    on_dismiss=lambda: reset_event_state(event=ChartEvents.STEPS_DIALOG),
)
def render_steps_dialog(
    selected_month: date, df: DataFrame, page_size: int = 3
) -> None:
    header = f"Steps Insights for {selected_month.strftime('%b %Y')}"
    st.subheader(header)
    if df.empty:
        st.info("In the selected timeframe there is no data available.")
    else:
        top_days_column, chart_column = st.columns([1, 1])
        with top_days_column:
            attributes = ["day", "Steps", "Goal", "Distance"]
            render_runs_in_dialog(
                df,
                page_size,
                "monthly_steps_pagination",
                attribute_list=attributes,
                sort_selection=attributes,
                sort_index=1,
            )
        with chart_column:
            if selected_month != get_current_month():
                daily_df = generate_daily_dates_df(selected_month)
                chart_df = daily_df.merge(df, how="left").fillna(0)
            else:
                chart_df = df
            chart_df = enrich_steps_df(chart_df)
            fig = create_steps_bar_chart(chart_df)
            st.plotly_chart(fig)


@st.dialog(
    title="Monthly Runs Breakdown",
    width="large",
    on_dismiss=lambda: reset_event_state(event=ChartEvents.DISTANCE_DIALOG),
)
def render_run_dialog(selected_month: date, df: DataFrame, page_size: int = 3) -> None:
    header = f"Run Insights for {selected_month.strftime('%B %Y')}"
    st.subheader(header)
    if df.empty:
        st.info("In the selected timeframe there is no data available.")
    else:
        top_days_column, chart_column = st.columns([1, 1])
        with top_days_column:
            sort_selection = {
                "day": "day",
                "distance": "distance",
                "average_pace": "speed",
                "time": "time_in_minutes",
            }
            render_runs_in_dialog(
                df,
                page_size,
                "monthly_run_pagination",
                attribute_list=list(sort_selection.keys()),
                sort_selection=sort_selection,
                sort_index=1,
            )
        with chart_column:
            daily_df = generate_daily_dates_df(selected_month, date_column="date")
            chart_df = daily_df.merge(df, how="left").fillna(0)
            fig = create_bar_chart(chart_df, "date", "distance", y_title="Distance per")
            st.plotly_chart(fig)


@st.dialog(
    title="Runs within selected range",
    width="large",
    on_dismiss=lambda: reset_event_state(event=ChartEvents.PACE_RANGE_DIALOG),
)
def render_pace_range_dialog(header: str, df: DataFrame, page_size: int = 10) -> None:
    render_default_runs(header, df, page_size, "pace_pagination")


@st.dialog(
    title="Runs within selected range",
    width="large",
    on_dismiss=lambda: reset_event_state(event=ChartEvents.DISTANCE_RANGE_DIALOG),
)
def render_distance_range_dialog(
    header: str, df: DataFrame, page_size: int = 10
) -> None:
    render_default_runs(header, df, page_size, "distance_pagination")


def render_default_runs(
    header: str, df: DataFrame, page_size: int, pagination_name: str
) -> None:
    st.subheader(header)
    if df.empty:
        st.info("In the selected timeframe there is no data available.")
    else:
        attribute_list = [
            "date",
            "distance",
            "average_pace",
            "speed",
            "time",
            "average_heart_rate",
        ]
        sort_list = ["date", "distance", "speed"]
        render_runs_in_dialog(df, page_size, pagination_name, attribute_list, sort_list)


def render_runs_in_dialog(
    df: DataFrame,
    page_size: int,
    pagination_key: str,
    attribute_list: list[str],
    sort_selection: dict[str, str] | list[str],
    sort_index: int = 0,
    order_ascending: bool = False,
) -> None:
    sort_mapping = (
        sort_selection
        if isinstance(sort_selection, dict)
        else {item: item for item in sort_selection}
    )
    sort_list = list(sort_mapping.keys())
    pagination_col, sort_col, order_col = st.columns([2, 1, 1])
    sort_key = sort_col.selectbox(
        label="Sort By",
        options=sort_list,
        index=None,
        placeholder="Sort By",
        label_visibility="collapsed",
        format_func=prettify,
    )
    sort_key = sort_key if sort_key else sort_list[sort_index]
    sort_item = sort_mapping[sort_key]
    sort_order = order_col.toggle(label="Order Ascending", value=order_ascending)
    sorted_df = df.copy().sort_values(by=sort_item, ascending=sort_order)
    with pagination_col:
        records = sorted_df.to_dict(orient="records")
        chosen_records = get_pagination(records, page_size, pagination_key)
    for record in chosen_records:
        record = filter_mapping(record, attribute_list)
        create_metrics_container(header="", data=record, gap="xxsmall")


def get_pagination(records: list[Any], page_size: int, key: str) -> list:
    num_pages = ceil(len(records) / page_size)
    current_page = st.pagination(num_pages=num_pages, key=key)
    return records[(current_page - 1) * page_size : current_page * page_size]
