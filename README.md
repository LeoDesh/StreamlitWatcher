### Overall Structure

### Streamlit
- starting point in app
- pages are in views
- organized through navigation

### Handling data
- garmin folder
- loads, translates and operates on the data

### Running checks
- uv run pytest
- uv run ruff check .
- uv run ruff format --check .

### Fixing checks
- uv run ruff check --fix 
- uv run ruff format .


### Docker
- build image: docker build -t activity-diary .
- run container DEV: docker run -d -v "$(PWD):/app" -v /app/.venv -p 8501:8501 --name activity-diary activity-diary 
- run container PROD: docker run -d -p 8501:8501 --name activity-diary activity-diary 

### Starting the app
- uv run streamlit run app.py

