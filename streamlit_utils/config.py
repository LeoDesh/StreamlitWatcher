from enum import StrEnum
from pathlib import Path


class Icons(StrEnum):
    home = ":material/home:"
    route = ":material/route:"
    table = ":material/table_view:"
    speed = ":material/speed:"
    search = ":material/search:"
    bar_chart = ":material/bar_chart:"
    line_chart = ":material/multiline_chart:"
    analytics = ":material/analytics:"
    timeline = ":material/view_timeline:"
    apps = ":material/apps:"
    monitoring = ":material/monitoring:"
    steps = ":material/steps:"
    trophy = ":material/trophy:"
    view = ":material/grid_view:"
    explore = ":material/explore:"
    arrow_right = ":material/chevron_right:"


PAGE_CONFIG = {
    "": {"home": {"icon": Icons.home, "default": True}},
    "Running": {
        "running": {"icon": Icons.view},
        "distance": {"icon": Icons.route},
        "comparison": {"icon": Icons.analytics},
        "pace": {"icon": Icons.monitoring},
        "personal_records": {"icon": Icons.trophy},
    },
    "Activities": {
        "activities_over_time": {"icon": Icons.monitoring},
        "activities": {"icon": Icons.view},
    },
    "Steps": {
        "progress": {"icon": Icons.steps},
        "steps": {"icon": Icons.view},
        "personal_records": {"icon": Icons.trophy},
    },
}

SECTION_CONFIG = {"Running": "🏃", "Activities": "📊", "Steps": "👟"}
VIEW_FOLDER = Path("views")
