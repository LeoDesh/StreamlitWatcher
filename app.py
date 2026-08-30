from streamlit_utils.nagivation import define_sidebar, get_pages, render_logo

render_logo()
define_sidebar()
nav = get_pages()
nav.run()
