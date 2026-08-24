from pathlib import Path

from garmin.etl.data_load import get_running_data, load_activity_file, load_steps_file

DATA_PATH = Path("garmin/etl/data/")
ARCHIVE_PATH = Path("garmin/etl/data/archive")
ACTIVITY_FILE_PATH = DATA_PATH / "Activities.csv"
STEPS_DATA_FILE = DATA_PATH / "Steps.csv"
RUNNING_DF = get_running_data(ACTIVITY_FILE_PATH)
COMPLETE_ACTIVITY_DF = load_activity_file(ACTIVITY_FILE_PATH)
STEPS_DF = load_steps_file(STEPS_DATA_FILE)
ACTIVITY_ATTR_COLUMNS = [
    "distance",
    "average_pace",
    "speed",
    "calories",
    "time",
    "average_heart_rate",
]
