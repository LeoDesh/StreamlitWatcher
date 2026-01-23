import streamlit as st

# 1. Setup individual pages
# You can rename the entry point (main.py) to "Home" or point to a separate file
home_page = st.Page("views/home.py", title="Home", icon="🏠", default=True)
distance_page = st.Page("views/distance.py", title="Distance",icon="📈")
units_page = st.Page("views/units.py", title="Units",icon="📋")
speed_page = st.Page("views/speed.py", title="Speed",icon="📊")
latest_activities_page = st.Page("views/latest_activities.py", title="Latest Activities",icon="🔢")
# 2. Organize into sidebar sections
# By using a dictionary, you create collapsible headers in the sidebar
navigation_menu = st.navigation(
    [home_page,units_page,speed_page,distance_page,latest_activities_page]
)


# 4. EXECUTE the navigation (Crucial: The app will be blank without this)
navigation_menu.run()