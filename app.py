from streamlit_utils.nagivation import define_sidebar, get_navigation, render_logo

render_logo()
define_sidebar()
nav = get_navigation()
nav.run()
