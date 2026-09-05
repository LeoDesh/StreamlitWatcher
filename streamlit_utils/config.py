from enum import StrEnum


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
    view = ":material/grid_view"
    explore = ":material/explore"


PAGE_CONFIG = {
    "": {"home": {"icon": Icons.home, "default": True}},
    "Running": {
        "distance": {"icon": Icons.route},
        "comparison": {"icon": Icons.analytics},
        "pace": {"icon": Icons.monitoring},
        "personal_records": {"icon": Icons.trophy},
    },
    "Activities": {"latest_activities": {"icon": Icons.search}},
    "Steps": {"steps": {"icon": Icons.steps}},
}

SECTION_CONFIG = {"Running": "🏃", "Activities": "📊", "Steps": "👟"}
