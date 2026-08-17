from dataclasses import dataclass

from garmin.themes.palette import Palette


@dataclass
class Theme:
    name: str = "Base"
    primary_green: str = Palette.GREEN_500
    bright_green: str = Palette.GREEN_300
    primary_red: str = Palette.RED_500
    bright_red: str = Palette.RED_300
    primary_blue: str = Palette.BLUE_500
    bright_blue: str = Palette.BLUE_300
    purple: str = Palette.PURPLE_500
    amber: str = Palette.AMBER_500
    magenta: str = Palette.MAGENTA_500
    teal: str = Palette.TEAL_500
    coral: str = Palette.CORAL_500
    white: str = Palette.WHITE
    bright_grey: str = Palette.NEUTRAL_100
    primary_grey: str = Palette.NEUTRAL_400
    dark_grey: str = Palette.NEUTRAL_800
    black: str = Palette.BLACK


@dataclass
class LightTheme(Theme):
    name: str = "Light"
    purple: str = Palette.PURPLE_300
    amber: str = Palette.AMBER_300
    teal: str = Palette.TEAL_300
    coral: str = Palette.CORAL_300
