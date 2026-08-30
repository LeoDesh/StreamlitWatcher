from pathlib import Path

import streamlit as st
from streamlit.navigation.page import StreamlitPage

from garmin.constants import APP_VERSION, IMAGE_PATH, RUNNING_DF
from streamlit_utils.config import PAGE_CONFIG, Icons


def get_pages() -> StreamlitPage:
    st.set_page_config(layout="wide")
    base_config = {"icon": Icons.monitoring}
    page_order_dict = {}
    for file in Path("views").iterdir():
        if file.suffix != ".py":
            continue
        index, file_name = file.stem.split("__")
        index = int(index)
        page_name = " ".join(file.capitalize() for file in file_name.split("_"))
        initial_config = (
            base_config
            if not PAGE_CONFIG.get(file_name)
            else PAGE_CONFIG.get(file_name)
        )
        config = initial_config | {"title": page_name, "page": file}
        streamlit_page = st.Page(**config)
        page_order_dict[index] = streamlit_page
    streamlit_pages = [page_order_dict[idx] for idx in sorted(page_order_dict)]
    return st.navigation(streamlit_pages, position="top")


def render_logo() -> None:
    st.set_page_config(
        page_title="Activity Diary",
        page_icon=IMAGE_PATH,
        layout="wide",
    )
    st.logo(IMAGE_PATH, size="small", icon_image=IMAGE_PATH)


def define_sidebar() -> None:
    with st.sidebar:
        st.subheader(f"Version {APP_VERSION}")
        min_date = RUNNING_DF["date"].min().strftime("%d.%m.%Y")
        max_date = RUNNING_DF["date"].max().strftime("%d.%m.%Y")
        time_hours = RUNNING_DF["time_in_minutes"].sum() // 60
        total_runs = len(RUNNING_DF)
        distance = round(RUNNING_DF["distance"].sum(), 2)
        st.metric(label="Last Recorded Run", value=max_date)
        st.metric(label="Total Distance", value=f"{distance} km")
        st.metric(label="Total Time", value=f"{time_hours} h")
        st.metric(label="Total Runs", value=f"{total_runs} units")
        st.metric(label="First Recorded Run", value=min_date)
