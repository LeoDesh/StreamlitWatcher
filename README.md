### Overall Structure

### Streamlit
- starting point in app
- pages are in views
- organized through navigation

### Handling data
- garmin folder
- loads, translates and operates on the data

### Updating data
- USE to UPDATE: download.py takes the auth tokens to get the data
- ONLY ONCE: workaround.py fakes login to get auth tokens


### Running checks
- uv run pytest
- uv run ruff check .
- uv run ruff format --check .

### Fixing checks
- uv run ruff check --fix 
- uv run ruff format .