import tomllib  # Use 'import tomli as tomllib' on Python < 3.11
from pathlib import Path

from garmin.etl.data_load import (
    get_running_data,
    load_activity_file,
    load_records_file,
    load_steps_file,
)


def get_app_version() -> str:
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
        return data.get("project", {}).get("version", "unknown")


IMAGE_PATH = Path("garmin/assets/ActivityDiary.png")
DATA_PATH = Path("garmin/etl/data/")
ARCHIVE_PATH = Path("garmin/etl/data/archive")
ACTIVITY_FILE_PATH = DATA_PATH / "Activities.csv"
STEPS_DATA_FILE = DATA_PATH / "Steps.csv"
RECORDS_DATA_FILE = DATA_PATH / "PersonalRecords.csv"

RUNNING_DF = get_running_data(ACTIVITY_FILE_PATH)
COMPLETE_ACTIVITY_DF = load_activity_file(ACTIVITY_FILE_PATH)
STEPS_DF = load_steps_file(STEPS_DATA_FILE)
RECORDS_DF = load_records_file(RECORDS_DATA_FILE, COMPLETE_ACTIVITY_DF)
ACTIVITY_ATTR_COLUMNS = [
    "distance",
    "average_pace",
    "speed",
    "calories",
    "time",
    "average_heart_rate",
]
APP_VERSION = get_app_version()
