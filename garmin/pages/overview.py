import streamlit as st
from garmin.constants import DATA
from garmin.statistics.pandas_helper import get_overview_table,get_grouped_table
from garmin.utils.pace_calculations import transform_pace_float_to_pace
from garmin.utils.misc import transform_activity_minutes_to_duration_format
import pandas as pd
from typing import List




def get_overview_page_df(df: pd.DataFrame):
    pace = get_overview_table(df, "PACE_FLOAT")
    distance = get_overview_table(df, "DISTANCE")
    speed = get_overview_table(df, "SPEED")
    calories = get_overview_table(df, "CALORIES")
    final_df = pd.concat([pace, distance, speed, calories], axis=1)
    final_df["PACE_FLOAT"] = final_df["PACE_FLOAT"].apply(transform_pace_float_to_pace)
    final_df = final_df.rename(columns={'PACE_FLOAT': 'PACE'})
    final_df = final_df.round(2)
    return final_df

def get_year_overview_table(df:pd.DataFrame):
    df = get_grouped_table(df,["YEAR"],["DISTANCE","TIME_IN_MINUTES","CALORIES"])
    df = df.rename(columns={'TIME_IN_MINUTES': 'TIME'})
    df["TIME"] = df["TIME"].apply(lambda x: transform_activity_minutes_to_duration_format(x))
    return df



def get_highlights_data(df: pd.DataFrame, columns: List[str], idx: int):
    return df.loc[idx, columns].values


def construct_highlights(df: pd.DataFrame):
    attrs_columns = ["DISTANCE", "SPEED", "CALORIES", "TIME","AVG_HEART_RATE"]
    columns = ["DISTANCE", "SPEED"]
    headers = ["Largest Distance Stats", "Largest Speed Stats"]
    for col, header in zip(columns, headers):
        idx = df[col].values.argmax()
        date = df.loc[idx,["DATE"]].values[0].date()
        date_str = f"{date.strftime('%d.%m.%Y')}"
        st.header(f"{header}: {date_str}")
        cols = st.columns(len(attrs_columns))
        data = get_highlights_data(df, attrs_columns, idx)
        for col, value, description in zip(cols, data, attrs_columns):
            col.metric(description, value)



def construct_header():
    st.title("Overview")


def construct_overall_statistics(df: pd.DataFrame):
    st.header("Statistics of an individual run")
    final_df = get_overview_page_df(df)
    #st.dataframe(final_df)
    st.markdown(final_df.to_html(), unsafe_allow_html=True)

def construct_year_statistics(df:pd.DataFrame):
    st.header("Metrics Overview per Year")
    df = get_year_overview_table(df)
    #st.dataframe(df.reset_index(drop=True))
    st.markdown(df.to_html(index=False), unsafe_allow_html=True)


def main():
    construct_header()
    df = DATA
    construct_highlights(df)
    construct_year_statistics(df)
    construct_overall_statistics(df)


if __name__ == "__main__":
    main()
