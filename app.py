import streamlit as st

# 1. Setup individual pages
# You can rename the entry point (main.py) to "Home" or point to a separate file
home_page = st.Page("views/home.py", title="Home",  default=True)
dash_page = st.Page("views/distance.py", title="Analytics")
settings_page = st.Page("views/units.py", title="App Settings")

# 2. Organize into sidebar sections
# By using a dictionary, you create collapsible headers in the sidebar
navigation_menu = st.navigation(
    [home_page,dash_page,settings_page]
)


# 4. EXECUTE the navigation (Crucial: The app will be blank without this)
navigation_menu.run()