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

### Before starting the app
- rename .env.example to .env
- create an empty certbot folder
- create a certs folder and create certificates (localhost.pem, localhost-key.pem) with a tool (e.g. mkcert)

### Starting the app
- run: docker compose up -d


