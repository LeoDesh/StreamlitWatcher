from functools import cache
from pathlib import Path

from pandas import DataFrame, read_csv

from garmin.data.column_mapping import GARMIN_COLUMNS
from garmin.data.file_verification import validate_csv_file
from garmin.utils.misc import (
    parse_activity_duration_to_hours,
    parse_activity_duration_to_minutes,
    parse_indoor_cycling_title,
    parse_str_to_int,
    transform_str_to_date,
)
from garmin.utils.pace_calculations import (
    transform_pace_to_pace_float,
    transform_pace_to_speed,
    transform_speed_to_pace,
)

MIN_YEAR = 2022
MIN_DISTANCE = 2.5


@cache
def import_file(file: Path) -> DataFrame:
    validate_csv_file(file)
    df = read_file(file)
    df = rename_df_columns(df)
    return transform_dataframe(df)


def get_running_data(file: Path) -> DataFrame:
    df = import_file(file)
    return filter_garmin_df(df)


def read_file(file: Path) -> DataFrame:
    return read_csv(str(file))


def rename_df_columns(df: DataFrame) -> DataFrame:
    selected_columns = [col for col in GARMIN_COLUMNS.keys()]
    df = df[selected_columns].copy()
    df.columns = [str(GARMIN_COLUMNS[col]) for col in df.columns]
    return df


def filter_garmin_df(df: DataFrame) -> DataFrame:
    df = df[df["average_pace"] != "--"]
    df = df[df["activity_type"] == "Laufen"]
    df = df[df["distance"] >= MIN_DISTANCE]
    df = df.reset_index()
    return df


def transform_activity(initial_activity: str, title: str) -> str:
    if initial_activity != "Cardio":
        return initial_activity
    activity_mapping = {
        "FB": "Fußball",
        "Schwimmen": "Schwimmen",
        "Tennis": "Tennis",
    }
    for title_part, activity in activity_mapping.items():
        if title_part in title:
            return activity
    return initial_activity


def add_pace(activity: str, title: str, pace: str) -> str:
    if activity == "Indoor Cycling" and "KM" in title.upper():
        value = parse_indoor_cycling_title(title)
        return transform_speed_to_pace(value) if value else pace
    return pace


def add_distance(
    activity: str, title: str, speed: float, time_in_minutes: float, distance: float
) -> float:
    if activity == "Indoor Cycling" and "KM" in title.upper():
        return round(speed * time_in_minutes / 60, 2) if speed > 1 else distance
    return distance


def transform_dataframe(df: DataFrame) -> DataFrame:
    df["activity_type"] = df.apply(
        lambda row: transform_activity(row["activity_type"], row["title"]), axis=1
    )
    df["average_pace"] = df.apply(
        lambda row: add_pace(row["activity_type"], row["title"], row["average_pace"]),
        axis=1,
    )
    df["date"] = df["date"].apply(transform_str_to_date)
    df["hour"] = df["date"].apply(lambda x: x.hour)
    df["month"] = df["date"].apply(lambda x: x.month)
    df["year"] = df["date"].apply(lambda x: x.year)
    df["steps"] = df["steps"].apply(parse_str_to_int)
    df["speed"] = df["average_pace"].apply(transform_pace_to_speed)
    df["pace_float"] = df["average_pace"].apply(
        lambda x: round(transform_pace_to_pace_float(x), 2)
    )
    df["time_in_minutes"] = df["time"].apply(parse_activity_duration_to_minutes)
    df["time_in_hours"] = df["time"].apply(parse_activity_duration_to_hours)
    df["distance"] = df.apply(
        lambda row: add_distance(
            row["activity_type"],
            row["title"],
            row["speed"],
            row["time_in_minutes"],
            row["distance"],
        ),
        axis=1,
    )
    return df[df["year"] >= MIN_YEAR]
