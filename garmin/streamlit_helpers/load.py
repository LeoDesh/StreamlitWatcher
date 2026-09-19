import streamlit as st
from pandas import DataFrame

from garmin.etl.config import ACTIVITY_FILE_PATH, RECORDS_DATA_FILE, STEPS_DATA_FILE
from garmin.etl.load import (
    load_activity_file,
    load_records_file,
    load_running_data,
    load_steps_file,
)

CACHE_KWARGS = {"ttl": 3600}


@st.cache_data(**CACHE_KWARGS)
def load_running_df() -> DataFrame:
    return load_running_data(ACTIVITY_FILE_PATH)


@st.cache_data(**CACHE_KWARGS)
def load_activity_df() -> DataFrame:
    return load_activity_file(ACTIVITY_FILE_PATH)


@st.cache_data(**CACHE_KWARGS)
def load_records_df() -> DataFrame:
    return load_records_file(RECORDS_DATA_FILE, load_activity_df())


@st.cache_data(**CACHE_KWARGS)
def load_steps_df() -> DataFrame:
    return load_steps_file(STEPS_DATA_FILE)
