import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
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


def get_empty_figure() -> Figure:
    return plt.figure()


def get_df_distributions(df: pd.DataFrame, column: str, bins: List[int]) -> Figure:
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.hist(df[column], bins=bins, rwidth=0.8)
    ax.set_title(f"Histogram of {column}")
    ax.set_xlabel(f"{column} in km")
    ax.set_ylabel("Count")
    ax.set_xticks(bins)
    ax.tick_params(axis="x", rotation=45)
    return fig


def get_df_count_year_month_histogram(df: pd.DataFrame) -> Figure:
    counts = (
        df.groupby(["YEAR", "MONTH"])
        .size()
        .reset_index(name="count")
        .sort_values(["YEAR", "MONTH"])
    )
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.bar(counts.apply(lambda r: f"{r.YEAR}-{r.MONTH:02d}", axis=1), counts["count"])
    ax.set_xlabel("YEAR-MONTH")
    ax.set_ylabel("Count")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    return fig


def get_df_count_from_column_histogram(df: pd.DataFrame, column: str) -> Figure:
    counts = df.groupby([column]).size().reset_index(name="count").sort_values([column])
    counts[column] = counts[column].astype(str)
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.bar(counts[column], counts["count"])
    ax.set_xlabel(column)
    ax.set_ylabel("Count")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    # ax.xaxis.set_major_locator(MaxNLocator(counts["YEAR"]))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    return fig


def get_df_sum_from_column(
    df: pd.DataFrame, groupby_column: str, value_column: str
) -> pd.DataFrame:
    return df.groupby(groupby_column)[[value_column]].sum()


def get_df_bar_chart(
    df: pd.DataFrame, groupby_column: str, value_column: str
) -> Figure:
    df = get_df_sum_from_column(df, groupby_column, value_column)
    df = df.reset_index()
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.bar(df[groupby_column], df[value_column])
    ax.set_title(f"Barchart of {value_column} per {groupby_column}")
    ax.set_xlabel(groupby_column)
    ax.set_ylabel(value_column)
    ax.set_xticks(df[groupby_column])
    ax.tick_params(axis="x", rotation=45)
    return fig


def get_df_pace_histogram(
    df: pd.DataFrame, pace_float_column: str, number_of_bins: int
) -> Figure:
    fig, ax = plt.subplots(figsize=(4, 3))
    bins, labels = get_pace_bins_labels_for_dataframe(
        df, number_of_bins, pace_float_column
    )
    df = df.copy()
    df.loc[:, "binned"] = pd.cut(df[pace_float_column], bins=bins, labels=labels)
    counts = df["binned"].value_counts().sort_index()
    counts.plot(kind="bar", ax=ax)
    ax.set_xlabel("Pace Ranges (min/km)")
    ax.set_ylabel("Count")
    ax.set_title("Histogram of Paces")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    return fig


def create_plotly_line_chart(df: pd.DataFrame, x_col: str, y_col: str) -> go.Figure:
    fig = go.Figure()
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
) -> go.Figure:
    values = df[y_col].tolist()
    tickvals = calculate_ticker_values(values)
    ticktext = [transform_speed_to_pace(speed) for speed in tickvals]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode="lines+markers",
            # mode="lines",
            name=y_col,
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
            opacity=0.5,
            name=y_col_2,
            line=dict(width=2.5, color="red"),
            hovertemplate="HPM: %{y}",
            yaxis="y2",
        )
    )

    fig.update_layout(
        title={"text": y_col, "font": {"size": 30}},
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
            x=0,
            y=1,
        ),
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig


def create_gantt_chart(
    df: pd.DataFrame, start_date_column: str, end_date_column: str, category_col: str
) -> go.Figure:
    fig = px.timeline(
        df,
        x_start=start_date_column,
        x_end=end_date_column,
        y=category_col,
        color=category_col,
    )
    fig.update_layout(height=400, bargap=0.2,yaxis_title=None)
    return fig


def create_heat_map(df: pd.DataFrame,title:str) -> go.Figure:
    #df.columns = pd.to_datetime(df.columns, format="%Y.%m")
    fig = px.imshow(
        df,
        color_continuous_scale="Viridis",  # modern blue gradient
        text_auto=True,  # show values inside cells
        aspect="auto"
    )

    fig.update_layout(
        
        title=f"Heatmap {title}",xaxis_title="Month",yaxis_title="Year", template="plotly_white",width=1200
    )
    fig.update_xaxes(tickangle=45,  tickformat="%Y.%m", # Zeigt nur Monat und Jahr
    dtick="M1"
    #categoryarray=df.columns
    )
    return fig
