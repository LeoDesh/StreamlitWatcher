import streamlit as st
from pathlib import Path
""" st.set_page_config(
    layout="wide"
) """
# 📊,📈,📋,🔢,📋
PATH = Path(__file__).resolve().parent


def setup_pages():
    st.set_page_config(page_title="Overview")  # Sets the browser tab title

    home_page = st.Page(PATH / "pages/overview.py", title="Home", icon="🏠")
    unit_page = st.Page(PATH /"pages/unit.py", title="Units", icon="📋")
    speed_page = st.Page(PATH / "pages/speed_page.py", title="Speed Data", icon="📊")
    distance_page = st.Page(PATH / "pages/distance_page.py", title="Distance Data", icon="📈")
    runs_page = st.Page(PATH / "pages/latest_activities.py", title="Last Activities", icon="🔢")
    pg = st.navigation([home_page, unit_page, speed_page, distance_page,runs_page])
    # pg = st.navigation([import_page])
    pg.run()


if __name__ == "__main__":
    setup_pages()
    