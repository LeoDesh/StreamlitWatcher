from matplotlib.figure import Figure
import streamlit as st

def place_figure(fig:Figure,layout_tuple:tuple[int,int,int]=(1,6,1)):
    _,main_col,_ = st.columns(layout_tuple)
    with main_col:
        st.pyplot(fig,width="content")