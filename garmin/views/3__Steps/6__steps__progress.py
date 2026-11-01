import streamlit as st
from pandas import DataFrame

from garmin.streamlit_helpers.components import (
    get_current_month_metric,
    get_heatmap,
    get_monthly_progression_figure,
    render_steps_dialog,
    validate_streamlit_chart_selection,
)
from garmin.streamlit_helpers.load import load_steps_df
from garmin.streamlit_helpers.model import (
    GridConfig,
    Metric,
    create_grid,
    stream_metrics,
)
from garmin.streamlit_helpers.nagivation import breadcrumbs
from garmin.streamlit_helpers.session_states import (
    ChartEvents,
    get_event_chart_name,
    get_event_state,
    set_event_state,
)
from garmin.utils.pandas_helpers import aggregate_df_named_column, filter_dataframe
from garmin.utils.time_utils import (
    get_first_of_current_year,
    get_previous_month,
    parse_str_date,
)


def render_metrics(df: DataFrame) -> None:
    metric_funcs = [
        get_average_monthly_steps_metric,
        get_month_with_highest_steps_metric,
        get_current_month_steps_metric,
    ]
    metrics = [func(df) for func in metric_funcs if func(df)]
    stream_metrics(metrics, num_cols=len(metrics))


def compute_monthly_steps(df: DataFrame) -> DataFrame:
    return aggregate_df_named_column(
        df, "monthly_date", "Steps", "steps", sort_asc=False
    )


def get_average_monthly_steps_metric(df: DataFrame) -> Metric | None:
    df = compute_monthly_steps(df)
    previous_month = get_previous_month()
    first_month_of_year = get_first_of_current_year()
    current_year = first_month_of_year.year
    filter_mask = (df["monthly_date"] >= first_month_of_year) & (
        df["monthly_date"] <= previous_month
    )
    filtered_df = df[filter_mask]
    average_steps_per_month = (
        filtered_df["steps"].mean() if not filtered_df.empty else 0
    )
    time_label = f"{first_month_of_year.strftime('%b')}-{previous_month.strftime('%b')}, {current_year}"
    return (
        Metric(
            label=f"Average Steps Per Month {time_label}",
            value=f"{average_steps_per_month:,.0f}",
        )
        if previous_month.year == first_month_of_year.year
        else None
    )


def get_month_with_highest_steps_metric(df: DataFrame) -> Metric:
    df = (
        compute_monthly_steps(df).sort_values(by="steps", ascending=False).reset_index()
    )
    value, date = df.loc[0, ["steps", "monthly_date"]]
    return Metric(
        label=f"Month with most Steps covered: {date.strftime('%b, %Y')}",
        value=f"{value:,.0f}",
    )


def get_current_month_steps_metric(df: DataFrame) -> Metric:
    return get_current_month_metric(df, "Steps", ",.0f", "Steps")


def render_monthly_progress(df: DataFrame, column: str) -> None:
    monthly_df = compute_monthly_steps(df)
    fig = get_monthly_progression_figure(monthly_df, column)
    event = st.plotly_chart(
        fig,
        width="stretch",
        selection_mode="points",
        on_select="rerun",
        height=450,
        key=get_event_chart_name(ChartEvents.STEPS_DIALOG),
    )
    month, _ = validate_streamlit_chart_selection(event)
    if not month:
        st.caption("Click on a month to view the details.")
        return
    selected_month = parse_str_date(month, "%Y-%m-%d").date().replace(day=1)
    previous_selected_month = get_event_state(ChartEvents.STEPS_DIALOG)
    if selected_month != previous_selected_month:
        set_event_state(ChartEvents.STEPS_DIALOG, selected_month)
        df = filter_dataframe(df, {"monthly_date": selected_month})
        render_steps_dialog(selected_month, df, 3)


def main() -> None:
    breadcrumbs(__file__)
    st.header("Monthly Steps Progress")
    set_event_state(ChartEvents.STEPS_DIALOG)
    df = load_steps_df()
    render_metrics(df)
    grid = create_grid([GridConfig(columns=2)])
    with grid[0][0]:
        render_monthly_progress(df, "steps")
    with grid[0][1]:
        fig = get_heatmap(df, "Steps", "Steps", ",.0f")
        st.plotly_chart(fig, width="stretch", height=490)


main()
