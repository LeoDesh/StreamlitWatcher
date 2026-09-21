import streamlit as st

from garmin.streamlit_helpers.nagivation import (
    define_sidebar,
    get_navigation,
    render_logo,
)


def run_app():
    st.set_page_config(layout="wide")
    render_logo()
    define_sidebar()
    nav = get_navigation()
    nav.run()


run_app()
