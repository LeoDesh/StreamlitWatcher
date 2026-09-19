from typing import Any

import plotly.express as px
from pandas import DataFrame
from plotly.graph_objects import Box, Figure, Scatter

from garmin.charts.config import X_AXIS_BASE_CONFIG, X_AXIS_MONTH_CONFIG
from garmin.themes import THEME
from garmin.utils.bucketing import create_bins_by_series
from garmin.utils.misc import prettify
from garmin.utils.pace_calculations import transform_speed_to_pace


def create_histogram(df: DataFrame, title: str, hovertemplate: str) -> Figure:
    x_col, y_col = df.columns
    fig = Figure()
    fig.add_bar(x=df[x_col], y=df[y_col], marker_color=THEME.primary_blue)
    fig.update_layout(
        xaxis=X_AXIS_BASE_CONFIG | {"title": x_col},
        yaxis_title=y_col,
        title={"text": title, "font": {"size": 20}},
    )
    fig.update_traces(hovertemplate=hovertemplate)
    return fig


def get_empty_figure() -> Figure:
    return Figure()


def create_bar_chart(
    df: DataFrame,
    x_col: str,
    y_col: str,
    *,
    x_axis_config: dict[str, Any] = X_AXIS_BASE_CONFIG,
    show_x_title: bool = True,
    y_title: str = "km run per",
    hovertemplate: str = "",
) -> Figure:
    fig = Figure()
    fig.add_bar(x=df[x_col], y=df[y_col], marker_color=THEME.primary_blue)
    fig.update_layout(
        xaxis=x_axis_config | {"title": prettify(x_col)} if show_x_title else {},
        yaxis_title="Amount",
        title={"text": f"{y_title} {x_col}", "font": {"size": 20}},
    )
    if hovertemplate:
        fig.update_traces(hovertemplate=hovertemplate)
    return fig


def create_pace_chart(df: DataFrame) -> Figure:
    date_col, speed_col, pace_col, hpm_col = (
        "date",
        "speed",
        "average_pace",
        "average_heart_rate",
    )
    values = df[speed_col].tolist()
    tickvals = create_bins_by_series(values, number_of_bins=7, enhancer=0.05)
    ticktext = [transform_speed_to_pace(speed) for speed in tickvals]
    fig = Figure()
    fig.add_trace(
        Scatter(
            x=df[date_col],
            y=df[speed_col],
            mode="lines+markers",
            name=prettify(speed_col),
            connectgaps=False,
            line={"width": 2.5, "color": THEME.primary_blue},
            customdata=df[pace_col],
            hovertemplate="Speed: %{y} km/h<br>" + "Pace: %{customdata}<extra></extra>",
            yaxis="y1",
        )
    )
    fig.add_trace(
        Scatter(
            x=df[date_col],
            y=df[hpm_col],
            mode="lines+markers",
            opacity=0.25,
            name=prettify(hpm_col),
            connectgaps=False,
            line={"width": 2.5, "color": THEME.primary_red},
            hovertemplate="HPM: %{y}",
            yaxis="y2",
        )
    )

    fig.update_layout(
        title={"text": "Pace and Heartbeat Per Minute", "font": {"size": 20}},
        xaxis_title="Date",
        yaxis1={
            "title": "Pace min/km",
            "tickmode": "array",
            "tickvals": tickvals,
            "ticktext": ticktext,
        },
        yaxis2={
            "title": "Heartbeats per Minute",
            "overlaying": "y",
            "showgrid": False,
            "side": "right",
        },
        template="plotly_white",
        hovermode="x unified",
        legend={
            "bgcolor": THEME.bright_grey,
            "bordercolor": THEME.primary_grey,
            "borderwidth": 1,
            "x": 0.5,
            "y": 1.2,
        },
        margin={"l": 10, "r": 20, "t": 60, "b": 10},
    )
    return fig


def create_gantt_chart(
    df: DataFrame, start_date_column: str, end_date_column: str, category_col: str
) -> Figure:
    fig = px.timeline(
        df,
        x_start=start_date_column,
        x_end=end_date_column,
        y=category_col,
        color=category_col,
    )
    fig.update_layout(
        height=400,
        bargap=0.2,
        yaxis_title=None,
        legend_title_text=prettify(category_col),
    )
    return fig


def create_heat_map(
    df: DataFrame, title: str, *, x_axis_kwargs: dict[str, Any], hovertemplate: str
) -> Figure:
    index_name = prettify(df.index.name)
    columns_name = prettify(df.columns.name)
    fig = px.imshow(
        df,
        color_continuous_scale="Viridis",
        text_auto=True,
        aspect="auto",
    )
    fig.update_layout(
        title=title,
        xaxis=x_axis_kwargs | {"title": columns_name},
        yaxis_title=index_name,
        template="plotly_white",
        width=1200,
    )
    fig.update_traces(hovertemplate=hovertemplate)
    return fig


def create_hpm_heatmap(df: DataFrame, title: str) -> Figure:
    hovertemplate = "With Avg. Heart Rate %{y}: %{z:.2f} % chance of a run with Pace %{x}<extra></extra>"
    return create_heat_map(
        df, title, x_axis_kwargs=X_AXIS_BASE_CONFIG, hovertemplate=hovertemplate
    )


def create_heat_map_monthly_axis(
    df: DataFrame, title: str, hovertemplate: str
) -> Figure:
    return create_heat_map(
        df, title, x_axis_kwargs=X_AXIS_MONTH_CONFIG, hovertemplate=hovertemplate
    )


def create_box_plot_chart(df: DataFrame, column: str) -> Figure:
    fig = Figure()
    fig.add_trace(
        Box(
            x=df["year"].astype(
                str
            ),  # Convert to string so years are distinct categories
            y=df[column],
            name=prettify(column),  # Label for the legend
            marker_color=THEME.primary_blue,  # Customize box color
            boxpoints="all",  # Optional: shows all data points next to the boxes
        )
    )

    fig.update_layout(
        title=f"Annual Distribution of {prettify(column)}",
        xaxis_title="Year of Run",
        yaxis_title=prettify(column),
    )
    return fig
