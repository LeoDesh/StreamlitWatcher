### Overall Structure

### Streamlit
- starting point in app.py
- pages are in garmin/view folder
- organized through garmin/streamlit_helpers/navigation.py

### Handling data
- garmin/etl/data folder
- loads, translates and operates on the data

### Running checks
```
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

### Fixing checks
```
- uv run ruff check --fix 
- uv run ruff format .
```

### Start the App

#### Setup data
- in case you do not have your own data
- use ```uv run app.py setup``` to move data from "example" directory to "data" directory in ETL

#### Streamlit
```
uv run streamlit run app.py
```
#### Full App (Docker)
- starts streamlit, nginx, redis

##### Requirements
- rename .env.example to .env
- rename .garminconnect_example to .garminconnect
- create an empty certbot folder
- create a certs folder and create certificates (localhost.pem, localhost-key.pem) with a tool (e.g. mkcert)

##### Starting the app
- run: 
```
docker compose up -d
```

