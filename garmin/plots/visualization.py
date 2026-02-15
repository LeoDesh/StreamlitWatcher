import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from matplotlib import figure
from matplotlib.ticker import MaxNLocator
from garmin.utils.pace_calculations import get_pace_bins_labels_for_dataframe,transform_speed_to_pace
from typing import List

def calculate_ticker_values(values:list[float]):
    sample_number = len(values)
    y_numbers = 7
    if sample_number <= y_numbers:
        return values
    min_val = min(values) - 1
    max_val = max(values) + 1
    return sorted(list(set([min_val + (max_val-min_val)/y_numbers*k for k in range(y_numbers+1)])))

def get_empty_figure() -> figure:
    return plt.figure()

def get_df_distributions(df: pd.DataFrame, column: str,bins:List[int]) -> figure:
    fig, ax = plt.subplots(figsize=(4,3))
    ax.hist(
        df[column],
        bins=bins,
        edgecolor="black",
    )
    ax.set_title(f"Histogram of {column}")
    ax.set_xlabel(f"{column} in km")
    ax.set_ylabel("Count")
    ax.set_xticks(bins)
    ax.tick_params(axis="x", rotation=45)
    return fig


def get_df_count_year_month_histogram(df: pd.DataFrame):
    counts = (
        df.groupby(["YEAR", "MONTH"])
        .size()
        .reset_index(name="count")
        .sort_values(["YEAR", "MONTH"])
    )
    fig,ax = plt.subplots(figsize=(8,3))
    ax.bar(counts.apply(lambda r: f"{r.YEAR}-{r.MONTH:02d}", axis=1), counts["count"])
    ax.set_xlabel("YEAR-MONTH")
    ax.set_ylabel("Count")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    return fig

def get_df_count_from_column_histogram(df: pd.DataFrame,column:str):
    counts = (
        df.groupby([column])
        .size()
        .reset_index(name="count")
        .sort_values([column])
    )
    counts[column] = counts[column].astype(str)
    fig,ax = plt.subplots(figsize=(4,3))
    ax.bar(counts[column], counts["count"])
    ax.set_xlabel(column)
    ax.set_ylabel("Count")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    #ax.xaxis.set_major_locator(MaxNLocator(counts["YEAR"]))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    return fig

def get_df_sum_from_column(df:pd.DataFrame,groupby_column:str,value_column:str):
    return df.groupby(groupby_column)[[value_column]].sum() 

def get_df_bar_chart(df:pd.DataFrame,groupby_column:str,value_column:str):
    df = get_df_sum_from_column(df,groupby_column,value_column)
    df = df.reset_index()
    fig, ax = plt.subplots(figsize=(4,3))
    ax.bar(
        df[groupby_column],
        df[value_column]
    )
    ax.set_title(f"Barchart of {value_column} per {groupby_column}")
    ax.set_xlabel(groupby_column)
    ax.set_ylabel(value_column)
    ax.set_xticks(df[groupby_column])
    ax.tick_params(axis="x", rotation=45)
    return fig

def get_df_pace_histogram(
    df: pd.DataFrame, pace_float_column: str, number_of_bins: int
) -> figure:
    fig, ax = plt.subplots(figsize=(4,3))
    bins,labels = get_pace_bins_labels_for_dataframe(df,number_of_bins,pace_float_column)
    df = df.copy()
    df.loc[:,"binned"] = pd.cut(df[pace_float_column], bins=bins, labels=labels)
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

def create_plotly_pace_chart(df: pd.DataFrame, x_col: str, y_col: str,y_text_col:str,y_col_2:str) -> go.Figure:
    values = df[y_col].tolist()
    tickvals = calculate_ticker_values(values)
    ticktext = [transform_speed_to_pace(speed) for speed in tickvals] 
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode="lines+markers",
            #mode="lines",
            name=y_col,
            line=dict(width=2.5,color="blue"),
            customdata=df[y_text_col],
            hovertemplate= "Speed: %{y} km/h<br>" + "Pace: %{customdata}<extra></extra>",
            yaxis="y1"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=df[y_col_2],
            mode="lines+markers",
            opacity=0.5,
            name=y_col_2,
            line=dict(width=2.5,color="red"),
            hovertemplate= "HPM: %{y}",
            yaxis="y2"
        )
    )

    fig.update_layout(
        title={"text": y_col, "font": {"size": 30}},
        xaxis_title="Date",
        yaxis1 = dict(
        title="Pace min/km",
        tickmode="array",
        tickvals=tickvals,
        ticktext=ticktext,
        #autorange="reversed"
    ),
     yaxis2=dict(
        title="Heartbeats per Minute",
        #tickvals = tickvals_hpm,
        overlaying="y",   
        showgrid=False,
        side="right"      
    ),
        template="plotly_white",
        hovermode="x unified",
        legend=dict(
            title="Columns",
            bgcolor="rgba(240,240,240,0.6)",
            bordercolor="lightgray",
            borderwidth=1,
            x=0,
            y=1
        ),
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig