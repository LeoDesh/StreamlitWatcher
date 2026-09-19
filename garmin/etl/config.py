from enum import StrEnum, auto
from pathlib import Path

DATA_PATH = Path("garmin/etl/data/")
ARCHIVE_PATH = Path("garmin/etl/data/archive")
ACTIVITY_FILE_PATH = DATA_PATH / "Activities.csv"
RECORDS_DATA_FILE = DATA_PATH / "PersonalRecords.csv"
STEPS_DATA_FILE = DATA_PATH / "Steps.csv"

MIN_YEAR = 2022
MIN_DISTANCE = 2.5
ACTIVITY_TYPE_MAPPING = {
    "Laufen": "Running",
    "Cardio": "Cardio",
    "Gehen": "Walking",
    "Laufbandtraining": "Treadmill",
    "Radfahren": "Cycling",
    "Indoor Cycling": "Indoor Cycling",
    "Sontige": "Cardio",
}

ACTIVITY_TRANSLATION_MAPPING = {
    "FB": "Football",
    "Padel": "Padel Tennis",
    "Schwimmen": "Swimming",
    "Tennis": "Tennis",
    "Indoor Cycling": "Indoor Cycling",
    "Wandern": "Hiking",
}


class Activity(StrEnum):
    ID = auto()
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
    "ID": Activity.ID,
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
