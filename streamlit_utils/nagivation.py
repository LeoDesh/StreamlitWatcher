from pathlib import Path

import streamlit as st
from streamlit.navigation.page import StreamlitPage

from garmin.constants import DATA
from streamlit_utils.config import PAGE_CONFIG, Icons


def get_pages() -> StreamlitPage:
    st.set_page_config(layout="wide")
    base_config = {"icon": Icons.monitoring}
    page_order_dict = {}
    for file in Path("views").iterdir():
        if not file.suffix == ".py":
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


def define_sidebar(update_date_str: str) -> None:
    with st.sidebar:
        st.title(f"Last Update {update_date_str}")
        min_date = DATA["date"].min().strftime("%d.%m.%Y")
        max_date = DATA["date"].max().strftime("%d.%m.%Y")
        time_hours = DATA["time_in_minutes"].sum() // 60
        distance = round(DATA["distance"].sum(), 2)
        st.metric(label="Last Recorded Run", value=max_date)
        st.metric(label="Total Distance", value=f"{distance} km")
        st.metric(label="Total Time", value=f"{time_hours} h")
        st.metric(label="First Recorded Run", value=min_date)
