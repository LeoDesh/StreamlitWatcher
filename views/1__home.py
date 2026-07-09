from datetime import date

import streamlit as st
from pandas import DataFrame

from garmin.constants import ACTIVITY_ATTR_COLUMNS, DATA
from garmin.plots.visualization import create_bar_chart_ordinary_axis
from garmin.utils.misc import (
    prettify,
    transform_activity_minutes_to_duration_format,
)
from garmin.utils.pace_calculations import (
    transform_hours_minutes_seconds_format_to_hours,
)
from garmin.utils.pandas_helpers import (
    filter_dataframe,
    get_grouped_table,
)
from streamlit_utils.chart_helpers import place_figure
from streamlit_utils.config import Icons
from streamlit_utils.utils import Metric, create_metrics_container, stream_metrics


def get_year_overview_table(df: DataFrame) -> DataFrame:
    df = get_grouped_table(
        df, ["Year"], ["Distance", "Time In Minutes", "Calories", "Average Heart Rate"]
    )
    df["Average Km"] = df.apply(
        lambda row: round(row["Distance"] / row["Count"], 1), axis=1
    )
    df = df.rename(columns={"Time In Minutes": "Time"})
    df["Time"] = df["Time"].apply(
        lambda x: transform_activity_minutes_to_duration_format(x)
    )
    df.columns = [prettify(col) for col in df.columns]
    return df


def construct_column_highlights(df: DataFrame, column: str, amount: int = 3) -> None:
    df = df.sort_values(by=column, ascending=False)
    df = df.head(amount).reset_index()
    df_dict = df.to_dict(orient="records")
    for activity in df_dict:
        date_str = f"{activity['Date'].strftime('%d.%m.%Y')}"
        activity = {
            attr: value
            for attr, value in activity.items()
            if attr in ACTIVITY_ATTR_COLUMNS
        }
        create_metrics_container(date_str, activity)


def construct_year_statistics(df: DataFrame) -> None:
    df = df.copy()
    category_col, _ = st.columns([1, 2])
    mapping = {
        "Count": ("Total Runs", "%{y} Runs"),
        "Distance": ("Distance Covered", "%{y} km covered "),
        "Time": ("Time Spent", "%{y} hours spent "),
        "Average Km": (
            "Average kilometre amount of a run",
            "Average of %{y} km per run",
        ),
    }
    category = category_col.selectbox(
        label="Category",
        index=None,
        options=list(mapping.keys()),
        placeholder="Choose your Category",
        label_visibility="collapsed",
    )
    category = category if category else "Count"
    df = get_year_overview_table(df)
    df["Time"] = df["Time"].apply(transform_hours_minutes_seconds_format_to_hours)
    header, template = mapping.get(category)
    hovertemplate = f"{template} in %{{x}} <extra></extra>"
    fig = create_bar_chart_ordinary_axis(
        df, "Year", category, y_title=f"{header} per", hovertemplate=hovertemplate
    )
    place_figure(fig)


def render_metrics(df: DataFrame) -> None:
    df = get_year_overview_table(df.copy())
    current_year = date.today().year
    st.subheader(f"Current Year: {date.today().year}")
    df = filter_dataframe(df, {"Year": current_year})
    df_dict = df.to_dict(orient="records")[0]
    description_mapping = {
        "Count": "Total Runs",
        "Distance": "Distance Covered",
        "Time": "Time Spent",
    }
    metrics = [
        Metric(label=description, value=df_dict[label])
        for label, description in description_mapping.items()
    ]
    stream_metrics(metrics, num_cols=3)


def main() -> None:
    df = DATA.copy()
    df.columns = [prettify(col) for col in df.columns]
    render_metrics(df)
    home_tab, distance_tab, speed_tab = st.tabs(
        [
            f"{Icons.analytics} Statistics",
            f"{Icons.route} Top Distance Runs",
            f"{Icons.speed} Top Speed Runs",
        ]
    )
    with home_tab:
        construct_year_statistics(df)
    with distance_tab:
        construct_column_highlights(df, "Distance", 5)
    with speed_tab:
        construct_column_highlights(df, "Speed", 5)


if __name__ == "__main__":
    main()
