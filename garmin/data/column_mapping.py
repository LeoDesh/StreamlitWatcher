from enum import auto
from typing import Dict

from strenum import StrEnum


class Activity(StrEnum):
    ACTIVITY_TYPE = auto()
    DATE = auto()
    TITLE = auto()
    DISTANCE = auto()
    CALORIES = auto()
    TIME = auto()
    AVG_HEART_RATE = auto()
    MAX_HEART_RATE = auto()
    AVERAGE_PACE = auto()
    MAX_PACE = auto()
    STEPS = auto()


TRANSLATION_DICT: Dict[Activity, str] = {
    Activity.ACTIVITY_TYPE: "Aktivitätstyp",
    Activity.DATE: "Datum",
    Activity.TITLE: "Titel",
    Activity.DISTANCE: "Distanz",
    Activity.CALORIES: "Kalorien",
    Activity.TIME: "Zeit",
    Activity.AVG_HEART_RATE: "Durchschnittliche Herzfrequenz",
    Activity.MAX_HEART_RATE: "Maximale Herzfrequenz",
    Activity.AVERAGE_PACE: "Durchschnittliche Pace",
    Activity.MAX_PACE: "Maximale Pace",
    Activity.STEPS: "Gesamtschritte",
}

GARMIN_COLUMNS = {
    "Aktivitätstyp": Activity.ACTIVITY_TYPE,
    "Datum": Activity.DATE,
    "Titel": Activity.TITLE,
    "Distanz": Activity.DISTANCE,
    "Kalorien": Activity.CALORIES,
    "Gesamtzeit": Activity.TIME,
    "Ø Herzfrequenz": Activity.AVG_HEART_RATE,
    "Maximale Herzfrequenz": Activity.MAX_HEART_RATE,
    "Ø Geschwindigkeit": Activity.AVERAGE_PACE,
    "Maximale Geschwindigkeit": Activity.MAX_PACE,
    "Schritte": Activity.STEPS,
}
