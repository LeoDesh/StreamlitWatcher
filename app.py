import streamlit as st
from garmin.constants import DATA
# MUST BE AT THE TOP - Target the specific navigation list container

st.set_page_config(layout="wide")
home_page = st.Page("views/home.py", title="Home",icon=":material/home:", default=True)
distance_page = st.Page("views/distance.py", title="Distance",icon=":material/route:")
units_page = st.Page("views/units.py", title="Units",icon=":material/table_view:")
speed_page = st.Page("views/speed.py", title="Speed",icon=":material/speed:")
latest_activities_page = st.Page("views/latest_activities.py", title="Latest Activities",icon=":material/search:")

navigation_menu = st.navigation(
    [home_page,units_page,speed_page,distance_page,latest_activities_page],position="top"
)

with st.sidebar:
    st.title("Last Update 26.01.2026")
    min_date = DATA["DATE"].min().strftime("%d.%m.%Y")
    max_date = DATA["DATE"].max().strftime("%d.%m.%Y")
    time_hours = DATA["TIME_IN_MINUTES"].sum() // 60
    distance = round(DATA["DISTANCE"].sum(),2)
    st.write(f"Last Recorded Run: {max_date}")
    st.write(f"Total Distance: {distance} km")
    st.write(f"Total Time: {time_hours} h")
    st.write(f"First Recorded Run: {min_date}")

navigation_menu.run()