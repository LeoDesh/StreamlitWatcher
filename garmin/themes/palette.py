from enum import StrEnum


class Palette(StrEnum):
    # ==========================================
    # NEUTRALS (White to Black Scale)
    # ==========================================
    WHITE = "#FFFFFF"  # Main canvas light mode / text dark mode
    NEUTRAL_50 = "#F8F9FA"  # Light mode background / card background
    NEUTRAL_100 = "#E9ECEF"  # Light mode borders / dividers
    NEUTRAL_200 = "#DEE2E6"  # Subtle borders / disabled elements
    NEUTRAL_400 = "#6C757D"  # Secondary text / captions
    NEUTRAL_700 = "#343A40"  # Dark mode card surface / body text
    NEUTRAL_800 = "#212529"  # Dark mode app background
    BLACK = "#000000"  # Pure contrast anchors

    # ==========================================
    # BLUE THEME (Information / Primary Actions)
    # ==========================================
    BLUE_100 = "#E3F2FD"  # Very subtle blue (Alert banners, light card tint)
    BLUE_300 = "#90CAF9"  # Soft blue (Hover states / light charts)
    BLUE_500 = "#0D6EFD"  # Primary brand blue (Buttons, links, selection)
    BLUE_700 = "#0A58CA"  # Deep blue (Hover dark states / primary text)
    BLUE_900 = "#052C65"  # Navy blue (Dark mode headers / text contrast)

    # ==========================================
    # GREEN THEME (Success / Positive Metrics)
    # ==========================================
    GREEN_100 = "#E8F5E9"  # Light green tint (Positive trends, success banners)
    GREEN_300 = "#81C784"  # Soft green (Chart fills / toggle active)
    GREEN_500 = "#198754"  # Success green (Positive indicators, badges)
    GREEN_700 = "#146C43"  # Dark green (Accessible green text on light background)
    GREEN_900 = "#0A3622"  # Deep forest green (Dark mode status surfaces)

    # ==========================================
    # RED THEME (Danger / Errors / Critical Alerts)
    # ==========================================
    RED_100 = "#FFEBEE"  # Light red tint (Error banners, destructive backdrops)
    RED_300 = "#E57373"  # Soft red (Critical chart indicators)
    RED_500 = "#DC3545"  # Danger red (Error messages, delete buttons)
    RED_700 = "#B02A37"  # Dark red (Accessible error text)
    RED_900 = "#58151C"  # Deep maroon (Dark mode critical panel backgrounds)

    PURPLE_100 = "#F3E5F5"  # Very soft lavender (Plot zone backing)
    PURPLE_300 = "#CE93D8"  # Light orchid (Subtle line or bar shade)
    PURPLE_500 = "#9C27B0"  # Pure purple (Primary anomaly marker)
    PURPLE_700 = "#7B1FA2"  # Deep violet (High contrast plot marker)
    PURPLE_900 = "#4A148C"  # Dark plum (Accessible chart labels)

    # ==========================================
    # AMBER / ORANGE (Warnings / Pending States)
    # ==========================================
    AMBER_100 = "#FFF3E0"  # Pale peach (In-progress process container)
    AMBER_300 = "#FFB74D"  # Light orange (Secondary forecast lines)
    AMBER_500 = "#FF9800"  # Deep amber (Active data pipeline warnings)
    AMBER_700 = "#F57C00"  # Burnt orange (Visible data point rings)
    AMBER_900 = "#E65100"  # Dark rust (Warning typography)

    # ==========================================
    # MAGENTA / FUCHSIA (Statistical Outliers)
    # ==========================================
    MAGENTA_100 = "#FCE4EC"  # Minimal pink sheen (Extreme threshold zoning)
    MAGENTA_300 = "#F06292"  # Pastel fuchsia (Secondary cluster group)
    MAGENTA_500 = "#E91E63"  # Shocking fuchsia (Hard critical outlier dots)
    MAGENTA_700 = "#C2185B"  # Dark magenta (Dense scatterplot overlaps)
    MAGENTA_900 = "#880E4F"  # Deep wine (Outlier text tags)

    # ==========================================
    # TEAL / CYAN (Forecasts / ML Projections)
    # ==========================================
    TEAL_100 = "#E0F2F1"  # Light mist (Expected confidence intervals)
    TEAL_300 = "#4DB6AC"  # Soft seafoam (Trend filling shadows)
    TEAL_500 = "#009688"  # Sharp teal (Machine learning model baseline)
    TEAL_700 = "#00796B"  # Dark teal (High-density plot lines)
    TEAL_900 = "#004D40"  # Deep spruce (Chart axis titles)

    # ==========================================
    # BROWN / TOPO (Historical / Legacy Baselines)
    # ==========================================
    BROWN_100 = "#EFEBE9"  # Warm parchment (Archive data card backing)
    BROWN_300 = "#A1887F"  # Soft tan (Dormant system data lines)
    BROWN_500 = "#795548"  # Cocoa brown (Comparative historical baseline)
    BROWN_700 = "#5D4037"  # Dark chocolate (Static threshold lines)
    BROWN_900 = "#3E2723"  # Espresso (Legacy node labels)

    # ==========================================
    # CORAL (Stale Data / Missing Telemetry)
    # ==========================================
    CORAL_100 = "#FFEBEB"  # Light salmon wash (Dropped packet zones)
    CORAL_300 = "#FF8A80"  # Pastel coral (Temporary timeout bars)
    CORAL_500 = "#FF6F61"  # Living coral (Delayed sensor reporting point)
    CORAL_700 = "#E65545"  # Dark coral (High contrast stale markers)
    CORAL_900 = "#7A1F1D"  # Dark brick (Telemetry error details text)
