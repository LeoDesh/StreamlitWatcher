import streamlit as st
from pandas import DataFrame

from garmin.constants import ACTIVITY_ATTR_COLUMNS, RUNNING_DF
from garmin.plots.visualization import create_bar_chart_ordinary_axis
from garmin.utils.pandas_helpers import aggregrate_df_by_dict, filter_dataframe
from garmin.utils.time_utils import get_current_year
from streamlit_utils.chart_helpers import place_figure
from streamlit_utils.config import Icons
from streamlit_utils.utils import Metric, create_metrics_container, stream_metrics


def get_year_overview_table(df: DataFrame) -> DataFrame:
    agg_dict = {
        "Distance": ("distance", "sum"),
        "Time": ("time_in_minutes", "sum"),
        "Count": ("distance", "count"),
        "Average Time": ("time_in_minutes", "mean"),
        "Average Distance": ("distance", "mean"),
    }
    df = aggregrate_df_by_dict(df, "year", agg_dict)
    df["Time"] = df["Time"].apply(lambda x: round(x / 60, 2))
    return df


def construct_column_highlights(df: DataFrame, column: str, amount: int = 3) -> None:
    df = df.sort_values(by=column, ascending=False)
    df = df.head(amount).reset_index()
    df_dict = df.to_dict(orient="records")
    for activity in df_dict:
        date_str = f"{activity['date'].strftime('%d.%m.%Y')}"
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
        "Average Time": (
            "Average Time in minutes spent on a run",
            "Average of %{y:.2f} minutes per run",
        ),
        "Average Distance": (
            "Average kilometre amount of a run",
            "Average of %{y:.2f} km per run",
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
    header, template = mapping.get(category)
    hovertemplate = f"{template} in %{{x}} <extra></extra>"
    fig = create_bar_chart_ordinary_axis(
        df, "year", category, y_title=f"{header} per", hovertemplate=hovertemplate
    )
    place_figure(fig)


def render_metrics(df: DataFrame) -> None:
    df = get_year_overview_table(df.copy())
    current_year = get_current_year()
    st.header("Overview")
    df = filter_dataframe(df, {"year": current_year})
    df_dict = df.to_dict(orient="records")[0]
    description_mapping = {
        "Count": ("Total Runs", "Units"),
        "Distance": ("Distance Covered by Runs", "km"),
        "Time": ("Time Spent Running", "hours"),
    }
    metrics = [
        Metric(
            label=f"{description} in {current_year}", value=f"{df_dict[attr]} {suffix}"
        )
        for attr, (description, suffix) in description_mapping.items()
    ]
    stream_metrics(metrics, num_cols=3)


def main() -> None:
    df = RUNNING_DF.copy()

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
        construct_column_highlights(df, "distance", 5)
    with speed_tab:
        construct_column_highlights(df, "speed", 5)


if __name__ == "__main__":
    main()
