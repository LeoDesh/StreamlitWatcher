from pathlib import Path

import streamlit as st
from streamlit.navigation.page import StreamlitPage

from garmin.streamlit_helpers.config import (
    PAGE_CONFIG,
    SECTION_CONFIG,
    VIEW_FOLDER,
    Icons,
)
from garmin.streamlit_helpers.constants import (
    APP_VERSION,
    IMAGE_ICON_PATH,
    IMAGE_LOGO_PATH,
    IMAGE_TRANSPARENT_PATH,
)
from garmin.streamlit_helpers.load import load_activity_df, load_running_df


def split_page_name(file_name: str) -> tuple[int, str]:
    idx, *_, page_name = file_name.split("__")
    return (int(idx), page_name)


def look_for_file_in_folder(folder: Path, file_stem: str) -> Path | None:
    for file in folder.iterdir():
        file_name_suffix = file.stem.split("__")[-1]
        if file_name_suffix == file_stem and file.suffix == ".py":
            return file
    return None


def get_page_part(file_path: Path) -> str:
    return file_path.stem.split("__")[-1]


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
    _, file_name = split_page_name(file.stem)
    page_name = " ".join(file.capitalize() for file in file_name.split("_"))
    if parent_folder:
        _, parent_folder = split_page_name(parent_folder)
    page_config = PAGE_CONFIG.get(parent_folder).get(file_name)
    initial_config = {"icon": Icons.monitoring} if not page_config else page_config
    config = initial_config | {
        "title": page_name,
        "page": file,
        "url_path": str(file).replace("/", "-"),
    }
    return st.Page(**config)


def extract_order_number_from_page(file: Path) -> int:
    index, *_ = file.stem.split("__")
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


def prettify_section(section: str) -> str:
    icon = SECTION_CONFIG.get(section, "")
    return f"{icon} {section}" if icon else section


def get_homepage() -> StreamlitPage:
    return generate_page_from_file_path(VIEW_FOLDER / "0__home.py")


def get_page_mapping() -> dict[str, list[StreamlitPage]]:
    page_layout = get_section_folder_mapping()
    return {"": [get_homepage()]} | {
        section: get_pages(folder_path) for section, folder_path in page_layout.items()
    }


def prettify_page_mapping(
    mapping: dict[str, list[StreamlitPage]],
) -> dict[str, list[StreamlitPage]]:
    return {prettify_section(section): pages for section, pages in mapping.items()}


def get_navigation() -> StreamlitPage:
    st.set_page_config(layout="wide")
    page_mapping = get_page_mapping()
    streamlit_pages = prettify_page_mapping(page_mapping)
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
        activity_df = load_activity_df()
        running_df = load_running_df()
        activity_min_date = activity_df["date"].min().strftime("%d.%m.%Y")
        activity_max_date = activity_df["date"].max().strftime("%d.%m.%Y")
        running_max_date = running_df["date"].max().strftime("%d.%m.%Y")
        total_runs = len(running_df)
        total_activities = len(activity_df)
        st.metric(label="Last Recorded Activity", value=activity_max_date)
        st.metric(label="Total Activities", value=f"{total_activities} units")
        st.metric(label="Last Recorded Run", value=running_max_date)
        st.metric(label="Total Runs", value=f"{total_runs} units")
        st.metric(label="First Recorded Activity", value=activity_min_date)
