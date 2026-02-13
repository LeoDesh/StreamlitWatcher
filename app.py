import streamlit as st
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


navigation_menu.run()