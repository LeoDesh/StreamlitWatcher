from pathlib import Path

from garmin.data.data_load import get_running_data, import_file

DATA_PATH = Path("garmin/data/")
ARCHIVE_PATH = Path("garmin/data/archive")
ACTIVITY_FILE_PATH = DATA_PATH / "Activities.csv"
RUNNING_DF = get_running_data(ACTIVITY_FILE_PATH)
COMPLETE_ACTIVITY_DF = import_file(ACTIVITY_FILE_PATH)

ACTIVITY_ATTR_COLUMNS = [
    "distance",
    "average_pace",
    "speed",
    "calories",
    "time",
    "average_heart_rate",
]
