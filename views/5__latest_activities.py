import streamlit as st
from garmin.constants import FULL_DATA
from garmin.statistics.pandas_helper import filter_dataframe,get_unique_values_per_column
import pandas as pd
from typing import List,Any


def clean_up_dict(data:dict[str,Any]) -> dict[str,Any]:
    pace = data["AVERAGE_PACE"]
    if pace == "--":
        data["SPEED"] = "--"

def construct_activity_header(date_str:str,activity_type:str,activity_title:str):
    if activity_title.find(activity_type) > -1:
        return f"{date_str} -- {activity_type}"
    return f"{date_str} -- {activity_type} -- {activity_title}"

def show_latest_activities(df: pd.DataFrame,rows:int=20):
    attrs_columns = ["DISTANCE","AVERAGE_PACE", "SPEED", "CALORIES", "TIME","AVG_HEART_RATE"]
    df:pd.DataFrame = df.head(rows)
    df_dict = df.to_dict(orient="records")
    for idx,row_dict in enumerate(df_dict):
        clean_up_dict(row_dict)
        date = row_dict["DATE"].date()
        date_str = date.strftime('%d.%m.%Y')
        activity_title = construct_activity_header(date_str,row_dict["ACTIVITY_TYPE"],row_dict["TITLE"])
        with st.container(border=True,horizontal_alignment="center"):
            st.header(f"{idx+1}: {activity_title}")
            cols = st.columns(len(attrs_columns))
            for col, description in zip(cols, attrs_columns):
                value = row_dict.get(description,"")
                col.metric(description, value)

def get_filters():
    unique_values_dict = get_unique_values_per_column(FULL_DATA,["ACTIVITY_TYPE"])
    filters = {}
    with st.expander("Activity Filter",expanded=False):
        for key,groups in unique_values_dict.items():
            filters[key] = st.multiselect(key,options=groups,default=groups)
    return filters

def main():
    st.header("Latest Activities",text_alignment="center")
    filters = get_filters()
    df = filter_dataframe(FULL_DATA,filters)
    show_latest_activities(df)

if __name__ == '__main__':
    main()