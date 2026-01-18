from pathlib import Path
from garmin.data.data_load import import_file


FILE_PATH = Path("garmin/data/Activities.csv")
DATA = import_file(FILE_PATH)
