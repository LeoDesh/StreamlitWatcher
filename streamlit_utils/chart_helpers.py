from matplotlib.figure import Figure
import plotly.graph_objects as go
import streamlit as st

def place_figure(fig:Figure,layout_tuple:tuple[int,int,int]=(1,6,1)) -> None:
    _,main_col,_ = st.columns(layout_tuple)
    with main_col:
        if isinstance(fig,Figure):
            st.pyplot(fig,width="stretch")
        elif isinstance(fig,go.Figure):
            st.plotly_chart(fig,width="stretch")


