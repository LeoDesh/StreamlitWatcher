from streamlit_utils.nagivation import setup_pages,define_sidebar,get_pages

define_sidebar()
nav = get_pages()
nav.run()