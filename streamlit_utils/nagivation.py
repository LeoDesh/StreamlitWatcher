import streamlit as st
from garmin.constants import DATA
from pathlib import Path

#":material/monitoring:"
PAGE_CONFIG = {
    "home":{"icon":":material/home:","default":True},
    "distance":{"icon":":material/route:"},
    "units":{"icon":":material/table_view:"},
    "speed":{"icon":":material/speed:"},
    "latest_activities":{"icon":":material/search:"},
}
    
def get_pages():
    st.set_page_config(layout="wide")
    base_config = {"icon":":material/monitoring:"}
    streamlit_pages = []
    for file in Path("views").iterdir():
        if not file.suffix == ".py":
            continue
        index,file_name = file.stem.split("__")
        index = int(index)
        page_name = " ".join(file.capitalize() for file in file_name.split("_"))
        initial_config = base_config if not PAGE_CONFIG.get(file_name) else PAGE_CONFIG.get(file_name)
        config = initial_config | {"title":page_name,"page":file}
        streamlit_page = st.Page(**config)
        streamlit_pages.append(streamlit_page)
    return st.navigation(streamlit_pages,position="top")
        

def define_sidebar(update_date_str:str) -> None:
    with st.sidebar:
        st.title(f"Last Update {update_date_str}")
        min_date = DATA["DATE"].min().strftime("%d.%m.%Y")
        max_date = DATA["DATE"].max().strftime("%d.%m.%Y")
        time_hours = DATA["TIME_IN_MINUTES"].sum() // 60
        distance = round(DATA["DISTANCE"].sum(),2)
        st.metric(label = "Last Recorded Run",value=max_date)
        st.metric(label="Total Distance",value= f"{distance} km")
        st.metric(label="Total Time",value= f"{time_hours} h")
        st.metric(label = "First Recorded Run",value=min_date)

