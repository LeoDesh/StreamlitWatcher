import streamlit as st
from garmin.constants import DATA
import pandas as pd
from typing import List

def get_highlights_data(df: pd.DataFrame, columns: List[str], idx: int):
    return df.loc[idx, columns].values


def show_latest_activities(df: pd.DataFrame,rows:int=20):
    attrs_columns = ["DISTANCE", "SPEED", "CALORIES", "TIME","AVG_HEART_RATE"]
    df:pd.DataFrame = df.head(rows)
    df_dict = df.to_dict(orient="records")
    for idx,row_dict in enumerate(df_dict):
        date = row_dict["DATE"].date()
        date_str = f"{date.strftime('%d.%m.%Y')}"
        with st.container(border=True,horizontal_alignment="center"):
            st.header(f"{idx+1}: {date_str}")
            cols = st.columns(len(attrs_columns))
            for col, description in zip(cols, attrs_columns):
                col.metric(description, row_dict[description])


def main():
    st.header("Latest Activities",text_alignment="center")
    show_latest_activities(DATA)

if __name__ == '__main__':
    main()