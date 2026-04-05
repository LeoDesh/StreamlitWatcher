import streamlit as st
from plotly.graph_objects import Figure


def place_figure(fig: Figure, layout_tuple: tuple[int, int, int] = (1, 6, 1)) -> None:
    _, main_col, _ = st.columns(layout_tuple)
    with main_col:
        st.plotly_chart(fig, width="stretch")
