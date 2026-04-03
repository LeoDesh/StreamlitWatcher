import pandas as pd
import plotly.graph_objects as go
from plotly.graph_objects import Figure
import plotly.express as px
from itertools import pairwise
from plotly.subplots import make_subplots
from garmin.utils.pace_calculations import (
    get_pace_bins_labels_for_dataframe,
    transform_speed_to_pace,
)
from typing import List


def calculate_ticker_values(values: List[float]) -> List[float]:
    sample_number = len(values)
    y_numbers = 7
    if sample_number <= y_numbers:
        return values
    min_val = min(values) - 1
    max_val = max(values) + 1
    return sorted(
        list(
            set(
                [
                    min_val + (max_val - min_val) / y_numbers * k
                    for k in range(y_numbers + 1)
                ]
            )
        )
    )



def get_df_sum_from_column(
    df: pd.DataFrame, groupby_column: str, value_column: str
) -> pd.DataFrame:
    return df.groupby(groupby_column)[[value_column]].sum()



def get_df_pace_histogram(
    df: pd.DataFrame, pace_float_column: str, number_of_bins: int
) -> Figure:
    bins, labels = get_pace_bins_labels_for_dataframe(
        df, number_of_bins, pace_float_column
    )
    df = df.copy()
    df.loc[:, "binned"] = pd.cut(df[pace_float_column], bins=bins, labels=labels)
    fig = Figure()
    counts = df["binned"].value_counts().sort_index().reset_index()
    counts.columns = ["Timeframe", "Amount"]
    fig.add_bar(
        x=counts["Timeframe"], y=counts["Amount"], name="Runs distributed by pace"
    )
    fig.update_layout(
        xaxis_title="(min/km)",
        yaxis_title="Amount",
        title={"text": "Pace Distribution", "font": {"size": 20}},
    )
    fig.update_xaxes(tickangle=45)

    return fig

def get_df_km_histogram(
    df: pd.DataFrame, trg_col: str, bins:list[int]
) -> Figure:
    labels = [f"{current_km}-{next_km} km" for current_km,next_km in pairwise(bins)]
    df = df.copy()
    df.loc[:, "binned"] = pd.cut(df[trg_col], bins=bins,labels=labels)
    fig = Figure()
    counts = df["binned"].value_counts().sort_index().reset_index()

    counts.columns = [trg_col, "Amount"]
    fig.add_bar(
        x=counts[trg_col], y=counts["Amount"], name="Runs distributed by km"
    )
    fig.update_layout(
        xaxis_title="km",
        yaxis_title="Amount",
        title={"text": "km Distribution", "font": {"size": 20}},
    )
    fig.update_xaxes(tickangle=45)
    return fig

def get_empty_figure() -> Figure:
    return Figure()

def create_bar_chart(df,x_col:str,y_col:str,month:bool) -> Figure:
    fig = Figure()
    fig.add_bar(
        x=df[x_col], y=df[y_col],
    )
    fig.update_layout(
        xaxis_title=x_col,
        yaxis_title="Amount",
        title={"text": f"km run per {x_col}", "font": {"size": 20}},
    )
    if month:
        fig.update_xaxes(
            tickmode = 'array',
            tickvals = list(range(1, 13)), 
            ticktext = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 
                        'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'], 
            tickangle = 45 
        )
    else: 
        fig.update_xaxes(
            tickmode = 'array',
            tickangle = 45 
        )
    return fig

def create_plotly_line_chart(df: pd.DataFrame, x_col: str, y_col: str) -> Figure:
    fig = Figure()
    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=df[y_col],
            # mode="lines+markers",
            mode="lines",
            name=y_col,
            line=dict(width=2.5),
            # marker=dict(size=6),
        )
    )
    fig.update_layout(
        title={"text": y_col, "font": {"size": 30}},
        xaxis_title="Date",
        yaxis_title=y_col,
        template="plotly_white",
        hovermode="x unified",
        legend=dict(
            title="Columns",
            bgcolor="rgba(240,240,240,0.6)",
            bordercolor="lightgray",
            borderwidth=1,
        ),
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig


def create_plotly_pace_chart(
    df: pd.DataFrame, x_col: str, y_col: str, y_text_col: str, y_col_2: str
) -> Figure:
    values = df[y_col].tolist()
    tickvals = calculate_ticker_values(values)
    ticktext = [transform_speed_to_pace(speed) for speed in tickvals]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
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
        ),
        secondary_y=False,
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
        ),
        secondary_y=True,
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
    # df.columns = pd.to_datetime(df.columns, format="%Y.%m")
    fig = px.imshow(
        df,
        color_continuous_scale="Viridis",  # modern blue gradient
        text_auto=True,  # show values inside cells
        aspect="auto",
    )

    fig.update_layout(
        title=f"Heatmap {title}",
        xaxis_title="Month",
        yaxis_title="Year",
        template="plotly_white",
        width=1200,
    )
    fig.update_xaxes(
        tickangle=45,
        tickformat="%Y.%m",  # Zeigt nur Monat und Jahr
        dtick="M1",
        # categoryarray=df.columns
    )
    return fig
