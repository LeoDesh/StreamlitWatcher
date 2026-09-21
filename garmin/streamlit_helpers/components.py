from datetime import date, timedelta

import streamlit as st
from pandas import DataFrame

from garmin.charts.tools import create_bar_chart, create_heat_map_monthly_axis
from garmin.etl import MIN_YEAR
from garmin.streamlit_helpers.model import Metric
from garmin.utils.misc import compute_delta, prettify
from garmin.utils.pandas_helpers import generate_dates_df
from garmin.utils.time_utils import (
    get_current_date,
    get_current_month,
    get_first_of_given_year,
    get_last_day_of_date,
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
