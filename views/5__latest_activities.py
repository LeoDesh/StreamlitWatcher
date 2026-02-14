import streamlit as st
from garmin.constants import FULL_DATA
import pandas as pd
from typing import List,Any

def get_highlights_data(df: pd.DataFrame, columns: List[str], idx: int):
    return df.loc[idx, columns].values


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


def main():
    st.header("Latest Activities",text_alignment="center")
    show_latest_activities(FULL_DATA)

if __name__ == '__main__':
    main()