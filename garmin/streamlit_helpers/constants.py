from pathlib import Path

from garmin.utils.misc import get_app_version

### Sidebar
IMAGE_ICON_PATH = Path("garmin/assets/ActivityDiaryIcon.png")
IMAGE_LOGO_PATH = Path("garmin/assets/ActivityDiaryLogo.png")
IMAGE_TRANSPARENT_PATH = Path("garmin/assets/Transparent.png")
APP_VERSION = get_app_version()


ACTIVITY_ATTR_COLUMNS = [
    "distance",
    "average_pace",
    "speed",
    "calories",
    "time",
    "average_heart_rate",
]
