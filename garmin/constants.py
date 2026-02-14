from pathlib import Path
from garmin.data.data_load import import_file,get_running_data


FILE_PATH = Path("garmin/data/Activities.csv")
DATA = get_running_data(FILE_PATH)
FULL_DATA = import_file(FILE_PATH)
