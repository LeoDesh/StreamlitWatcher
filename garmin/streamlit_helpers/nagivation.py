from pathlib import Path

import streamlit as st
from streamlit import page_link
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
from garmin.utils.misc import prettify
from garmin.utils.path_utils import (
    extract_order_number_from_page,
    get_page_part,
    get_relative_file_path,
    get_section_folder_mapping,
    look_for_file_in_folder,
    split_page_name,
)


def generate_page_from_file_path(file: Path, parent_folder: str = "") -> StreamlitPage:
    _, file_name = split_page_name(file.stem)
    page_name = " ".join(file.capitalize() for file in file_name.split("_"))
    if parent_folder:
        _, parent_folder = split_page_name(parent_folder)
    page_config = PAGE_CONFIG.get(parent_folder).get(file_name)
    initial_config = {"icon": Icons.MONITORING} if not page_config else page_config
    config = initial_config | {
        "title": page_name,
        "page": file,
        "url_path": str(file).replace("/", "-"),
    }
    return st.Page(**config)


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
    page_layout = get_section_folder_mapping(VIEW_FOLDER)
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


def get_file_references(file_path: Path) -> list[StreamlitPage]:
    """Breaks up the file name in parts and generates pages from it.
    Args:
        file_path (Path): Path for streamlit page

    Returns:
        list[StreamlitPage]: pages associated with the provided path.

    Example:
    ```
    #### 1__running/1__running__distance.py

    Page Name: distance

    Another File Part: 'running', which is also in the same folder.

    Therefore Returns: [StreamlitPage of '1__running.py']
    ```
    """
    page_part = get_page_part(file_path)
    parent_folder = file_path.parent
    file_stem = file_path.stem
    file_parts = [
        part
        for part in file_stem.split("__")
        if not (part.isdigit() or part == page_part)
    ]
    return [
        generate_page_from_file_path(
            look_for_file_in_folder(parent_folder, file_part), parent_folder.stem
        )
        for file_part in file_parts
        if look_for_file_in_folder(parent_folder, file_part)
    ]


def breadcrumbs(file_dunder: str) -> None:
    file_path = get_relative_file_path(file_dunder, VIEW_FOLDER)
    with st.container(horizontal=True, vertical_alignment="center"):
        home_page = get_homepage()
        page_link(home_page, label="Home")
        st.markdown(Icons.ARROW_RIGHT, width="content")
        file_references = get_file_references(file_path)
        for reference_page in file_references:
            page_link(reference_page)
            st.markdown(Icons.ARROW_RIGHT, width="content")
        page_part = get_page_part(file_path)
        current_page_name = " ".join(prettify(part) for part in page_part.split("_"))
        st.markdown(f"**{current_page_name}**")


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
