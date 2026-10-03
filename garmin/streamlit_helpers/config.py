from enum import StrEnum
from pathlib import Path


class Icons(StrEnum):
    HOME = ":material/home:"
    ROUTE = ":material/route:"
    TABLE = ":material/table_view:"
    SPEED = ":material/speed:"
    SEARCH = ":material/search:"
    BAR_CHART = ":material/bar_chart:"
    LINE_CHART = ":material/multiline_chart:"
    ANALYTICS = ":material/analytics:"
    TIMELINE = ":material/view_timeline:"
    APPS = ":material/apps:"
    MONITORING = ":material/monitoring:"
    STEPS = ":material/steps:"
    TROPHY = ":material/trophy:"
    VIEW = ":material/grid_view:"
    EXPLORE = ":material/explore:"
    ARROW_RIGHT = ":material/chevron_right:"


PAGE_CONFIG = {
    "": {"home": {"icon": Icons.HOME, "default": True}},
    "Running": {
        "running": {"icon": Icons.VIEW},
        "distance": {"icon": Icons.ROUTE},
        "comparison": {"icon": Icons.ANALYTICS},
        "pace": {"icon": Icons.MONITORING},
        "personal_records": {"icon": Icons.TROPHY},
    },
    "Activities": {
        "activities_over_time": {"icon": Icons.MONITORING},
        "activities": {"icon": Icons.VIEW},
    },
    "Steps": {
        "progress": {"icon": Icons.STEPS},
        "steps": {"icon": Icons.VIEW},
        "personal_records": {"icon": Icons.TROPHY},
    },
}

SECTION_CONFIG = {"Running": "🏃", "Activities": "📊", "Steps": "👟"}
VIEW_FOLDER = Path("garmin/views")
