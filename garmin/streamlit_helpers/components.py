from datetime import date, timedelta
from math import ceil
from typing import Any

import streamlit as st
from pandas import DataFrame
from plotly.graph_objects import Figure
from streamlit.typing import PlotlyState

from garmin.charts.tools import create_bar_chart, create_heat_map_monthly_axis
from garmin.etl import MIN_YEAR
from garmin.streamlit_helpers.model import Metric, create_metrics_container
from garmin.utils.misc import compute_delta, filter_mapping, prettify
from garmin.utils.pandas_helpers import generate_daily_dates_df, generate_dates_df
from garmin.utils.time_utils import (
    get_current_date,
    get_current_month,
    get_first_of_given_year,
    get_last_day_of_month,
    get_month_previous_year,
)


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


@st.dialog(title="Monthly Steps Breakdown", width="large")
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
            sorted_df = df.copy().sort_values(by="Steps", ascending=False)
            records = sorted_df.to_dict(orient="records")
            for record in get_pagination(records, page_size, "steps_pagination"):
                record = filter_mapping(record, ["Date", "Steps"])
                record["Steps"] = int(record["Steps"])
                record["Date"] = record["Date"].strftime("%d.%m.%Y")
                create_metrics_container(header="", data=record)
        with chart_column:
            daily_df = generate_daily_dates_df(selected_month)
            chart_df = daily_df.merge(df, how="left").fillna(0)
            fig = create_bar_chart(chart_df, "Date", "Steps", y_title="Steps per")
            st.plotly_chart(fig)


@st.dialog(title="Monthly Runs Breakdown", width="large")
def render_run_dialog(selected_month: date, df: DataFrame, page_size: int = 3) -> None:
    header = f"Run Insights for {selected_month.strftime('%b %Y')}"
    st.subheader(header)
    if df.empty:
        st.info("In the selected timeframe there is no data available.")
    else:
        top_days_column, chart_column = st.columns([1, 1])
        with top_days_column:
            sorted_df = df.copy().sort_values(by="distance", ascending=False)
            sorted_df["day"] = sorted_df["date"].apply(lambda x: x.day)
            records = sorted_df.to_dict(orient="records")
            for record in get_pagination(records, page_size, "run_pagination"):
                record = filter_mapping(
                    record, ["day", "distance", "average_pace", "time"]
                )
                create_metrics_container(header="", data=record, gap="xxsmall")
        with chart_column:
            daily_df = generate_daily_dates_df(selected_month, date_column="date")
            chart_df = daily_df.merge(df, how="left").fillna(0)
            fig = create_bar_chart(chart_df, "date", "distance", y_title="Distance per")
            st.plotly_chart(fig)


def get_pagination(records: list[Any], page_size: int, key: str) -> list:
    num_pages = ceil(len(records) / page_size)
    current_page = st.pagination(num_pages=num_pages, key=key)
    return records[(current_page - 1) * page_size : current_page * page_size]
