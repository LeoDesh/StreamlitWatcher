from typing import Any

import streamlit as st
from pandas import DataFrame

from garmin.constants import ACTIVITY_ATTR_COLUMNS, RECORDS_DF
from streamlit_utils.utils import create_metrics_container


def construct_activity_header(activity: dict[str, Any]) -> str:
    date_str = activity["date"].date().strftime("%d.%m.%Y")
    value = activity["formatted_value"]
    return f"{date_str}, {value}"


def show_records(df: DataFrame) -> None:
    df_dict = df.to_dict(orient="records")
    for activity in df_dict:
        activity_title = construct_activity_header(activity)
        activity = {
            attr: value
            for attr, value in activity.items()
            if attr in ACTIVITY_ATTR_COLUMNS
        }
        create_metrics_container(activity_title, activity)


def main() -> None:
    st.title("Personal Records")
    df = RECORDS_DF.copy()
    show_records(df)


main()
