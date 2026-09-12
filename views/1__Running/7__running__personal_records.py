from typing import Any

import streamlit as st
from pandas import DataFrame

from garmin.constants import ACTIVITY_ATTR_COLUMNS, RECORDS_DF
from streamlit_utils.utils import breadcrumbs, create_metrics_container


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


@st.dialog("Description")
def show_description() -> None:
    st.markdown(
        """  
        In the following individuel personal running records on different *timeframes* and the corresponding activity will be shown.  
        In each container the date, the record type and the achieved time can be seen.  
        Further in the brackets the pace for the corresponding distance is computed in min/km.
        """
    )


def main() -> None:
    breadcrumbs(__file__)
    title_col, _, info_col = st.columns([10, 1, 1])
    title_col.header("Personal Records")
    btn = info_col.button(label="Info", icon=":material/info:", type="secondary")
    if btn:
        show_description()
    df = RECORDS_DF.copy()
    show_records(df)


main()
