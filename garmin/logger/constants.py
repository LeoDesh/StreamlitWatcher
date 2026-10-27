import logging.config
from pathlib import Path

from garmin.etl.load import load_json
from garmin.utils.path_utils import create_folder_if_not_exists

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
create_folder_if_not_exists(LOG_DIR)
logging_config = load_json(BASE_DIR / "config.json")
logging.config.dictConfig(config=logging_config)
LOGGER = logging.getLogger("app")
