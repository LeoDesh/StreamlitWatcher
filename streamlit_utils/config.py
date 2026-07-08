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


PAGE_CONFIG = {
    "home": {"icon": Icons.home, "default": True},
    "distance": {"icon": Icons.route},
    "comparison": {"icon": Icons.analytics},
    "pace": {"icon": Icons.monitoring},
    "latest_activities": {"icon": Icons.search},
}
