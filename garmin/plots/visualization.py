from itertools import pairwise
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objects import Figure

from garmin.plots.config import X_AXIS_BASE_CONFIG, X_AXIS_MONTH_CONFIG
from garmin.utils.misc import calculate_ticker_values, categorize_df_column, prettify
from garmin.utils.pace_calculations import (
    transform_speed_to_pace,
)
from garmin.utils.pandas_helpers import get_pace_bins_labels_for_dataframe


def get_df_pace_histogram(
    df: pd.DataFrame, pace_float_column: str, number_of_bins: int
) -> Figure:
    df = categorize_df_column(
        df, pace_float_column, number_of_bins, get_pace_bins_labels_for_dataframe
    )
    counts = df[pace_float_column].value_counts().sort_index().reset_index()
    counts.columns = ["Minute per km", "Amount"]
    return create_histogram(counts, "Pace Distribution")


def get_df_km_histogram(df: pd.DataFrame, trg_col: str, bins: list[int]) -> Figure:
    labels = [f"{current_km}-{next_km} km" for current_km, next_km in pairwise(bins)]
    df = df.copy()
    df.loc[:, "binned"] = pd.cut(df[trg_col], bins=bins, labels=labels)
    counts = df["binned"].value_counts().sort_index().reset_index()
    counts.columns = ["km", "Amount"]
    return create_histogram(counts, "km Distribution")


def create_histogram(df: pd.DataFrame, title: str):
    x_col, y_col = df.columns
    fig = Figure()
    fig.add_bar(x=df[x_col], y=df[y_col])
    fig.update_layout(
        xaxis=X_AXIS_BASE_CONFIG | {"title": x_col},
        yaxis_title=y_col,
        title={"text": title, "font": {"size": 20}},
    )
    return fig


def get_empty_figure() -> Figure:
    return Figure()


def create_bar_chart(
    df: pd.DataFrame, x_col: str, y_col: str, *, x_axis_config: dict[str, Any]
) -> Figure:
    fig = Figure()
    fig.add_bar(
        x=df[x_col],
        y=df[y_col],
    )
    fig.update_layout(
        xaxis=x_axis_config | {"title": x_col},
        yaxis_title="Amount",
        title={"text": f"km run per {x_col}", "font": {"size": 20}},
    )
    return fig


def create_bar_chart_month_axis(df: pd.DataFrame, x_col: str, y_col: str):
    return create_bar_chart(df, x_col, y_col, x_axis_config=X_AXIS_MONTH_CONFIG)


def create_bar_chart_ordinary_axis(df: pd.DataFrame, x_col: str, y_col: str):
    return create_bar_chart(df, x_col, y_col, x_axis_config=X_AXIS_BASE_CONFIG)


def create_plotly_pace_chart(
    df: pd.DataFrame, x_col: str, y_col: str, y_text_col: str, y_col_2: str
) -> Figure:
    values = df[y_col].tolist()
    tickvals = calculate_ticker_values(values)
    ticktext = [transform_speed_to_pace(speed) for speed in tickvals]
    fig = Figure()
    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode="lines+markers",
            # mode="lines",
            name=y_col,
            connectgaps=False,
            line=dict(width=2.5, color="blue"),
            customdata=df[y_text_col],
            hovertemplate="Speed: %{y} km/h<br>" + "Pace: %{customdata}<extra></extra>",
            yaxis="y1",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=df[y_col_2],
            mode="lines+markers",
            opacity=0.25,
            name=y_col_2,
            connectgaps=False,
            line=dict(width=2.5, color="red"),
            hovertemplate="HPM: %{y}",
            yaxis="y2",
        )
    )

    fig.update_layout(
        title={"text": "Pace and Heartbeat Per Minute", "font": {"size": 20}},
        xaxis_title="Date",
        yaxis1=dict(
            title="Pace min/km",
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            # autorange="reversed"
        ),
        yaxis2=dict(
            title="Heartbeats per Minute",
            # tickvals = tickvals_hpm,
            overlaying="y",
            showgrid=False,
            side="right",
        ),
        template="plotly_white",
        hovermode="x unified",
        legend=dict(
            title="Columns",
            bgcolor="rgba(240,240,240,0.6)",
            bordercolor="lightgray",
            borderwidth=1,
            x=0.5,
            y=1.2,
        ),
        margin=dict(l=10, r=20, t=60, b=10),
    )
    return fig


def create_gantt_chart(
    df: pd.DataFrame, start_date_column: str, end_date_column: str, category_col: str
) -> Figure:
    fig = px.timeline(
        df,
        x_start=start_date_column,
        x_end=end_date_column,
        y=category_col,
        color=category_col,
    )
    fig.update_layout(height=400, bargap=0.2, yaxis_title=None)
    return fig


def create_heat_map(df: pd.DataFrame, title: str) -> Figure:
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
        xaxis=X_AXIS_MONTH_CONFIG | {"title": columns_name},
        yaxis_title=index_name,
        template="plotly_white",
        width=1200,
    )
    return fig
