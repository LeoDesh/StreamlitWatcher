from pathlib import Path

import streamlit as st
from streamlit.navigation.page import StreamlitPage

from garmin.constants import (
    APP_VERSION,
    IMAGE_ICON_PATH,
    IMAGE_LOGO_PATH,
    IMAGE_TRANSPARENT_PATH,
    RUNNING_DF,
)
from streamlit_utils.config import PAGE_CONFIG, Icons

VIEW_FOLDER = Path("views")


def split_page_name(file_name: str) -> tuple[int, str]:
    idx, page_name = file_name.split("__")
    return (int(idx), page_name)


def get_folders(path: Path) -> list[Path]:
    return [folder for folder in path.iterdir() if folder.is_dir()]


def get_section_folder_mapping() -> dict[str, Path]:
    folder_dict = {}
    for folder_path in get_folders(VIEW_FOLDER):
        idx, section_name = split_page_name(folder_path.name)
        folder_dict[idx] = (section_name, folder_path)
    sorted_folder_dict = dict(sorted(folder_dict.items()))
    return {
        section_name: folder for (section_name, folder) in sorted_folder_dict.values()
    }


def generate_page_from_file_path(file: Path, parent_folder: str = "") -> StreamlitPage:
    _, file_name = file.stem.split("__")
    page_name = " ".join(file.capitalize() for file in file_name.split("_"))
    if parent_folder:
        _, parent_folder = split_page_name(parent_folder)
    page_config = PAGE_CONFIG.get(parent_folder).get(file_name)
    initial_config = {"icon": Icons.monitoring} if not page_config else page_config
    config = initial_config | {"title": page_name, "page": file}
    return st.Page(**config)


def extract_order_number_from_page(file: Path) -> int:
    index, _ = file.stem.split("__")
    return int(index)


def get_pages(path: Path) -> list[StreamlitPage]:
    streamlit_pages = {
        extract_order_number_from_page(file): generate_page_from_file_path(
            file, path.name
        )
        for file in path.iterdir()
        if file.suffix == ".py"
    }
    sorted_pages = dict(sorted(streamlit_pages.items()))
    return list(sorted_pages.values())


def render_page_layout() -> dict[str, list[StreamlitPage]]:
    page_layout = get_section_folder_mapping()
    return {"": [generate_page_from_file_path(VIEW_FOLDER / "0__home.py")]} | {
        section: get_pages(folder_path) for section, folder_path in page_layout.items()
    }


def get_navigation() -> StreamlitPage:
    st.set_page_config(layout="wide")
    streamlit_pages = render_page_layout()
    return st.navigation(streamlit_pages, position="top")


def render_logo() -> None:
    st.set_page_config(
        page_title="Activity Diary",
        page_icon=IMAGE_ICON_PATH,
        layout="wide",
    )
    st.logo(IMAGE_TRANSPARENT_PATH, size="small", icon_image=IMAGE_ICON_PATH)


def define_sidebar() -> None:
    with st.sidebar:
        st.image(IMAGE_LOGO_PATH)
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
