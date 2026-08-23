from enum import StrEnum, auto


class Activity(StrEnum):
    ACTIVITY_TYPE = auto()
    DATE = auto()
    TITLE = auto()
    DISTANCE = auto()
    CALORIES = auto()
    TIME = auto()
    AVERAGE_HEART_RATE = auto()
    MAX_HEART_RATE = auto()
    AVERAGE_PACE = auto()
    MAX_PACE = auto()
    STEPS = auto()


GARMIN_COLUMNS = {
    "Aktivitätstyp": Activity.ACTIVITY_TYPE,
    "Datum": Activity.DATE,
    "Titel": Activity.TITLE,
    "Distanz": Activity.DISTANCE,
    "Kalorien": Activity.CALORIES,
    "Gesamtzeit": Activity.TIME,
    "Ø Herzfrequenz": Activity.AVERAGE_HEART_RATE,
    "Maximale Herzfrequenz": Activity.MAX_HEART_RATE,
    "Ø Geschwindigkeit": Activity.AVERAGE_PACE,
    "Maximale Geschwindigkeit": Activity.MAX_PACE,
    "Schritte": Activity.STEPS,
}
