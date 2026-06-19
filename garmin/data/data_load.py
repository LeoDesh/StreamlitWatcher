from functools import cache
from pathlib import Path

import pandas as pd

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
def import_file(file: Path) -> pd.DataFrame:
    validate_csv_file(file)
    df = read_file(file)
    df = rename_df_columns(df)
    return transform_dataframe(df)


def get_running_data(file: Path) -> pd.DataFrame:
    df = import_file(file)
    return filter_garmin_df(df)


def read_file(file: Path) -> pd.DataFrame:
    return pd.read_csv(str(file))


def rename_df_columns(df: pd.DataFrame) -> pd.DataFrame:
    selected_columns = [col for col in GARMIN_COLUMNS.keys()]
    df = df[selected_columns].copy()
    df.columns = [str(GARMIN_COLUMNS[col]) for col in df.columns]
    return df


def filter_garmin_df(df: pd.DataFrame):
    df = df[df["AVERAGE_PACE"] != "--"]
    df = df[df["ACTIVITY_TYPE"] == "Laufen"]
    df = df[df["DISTANCE"] >= MIN_DISTANCE]
    df = df.reset_index()
    return df


def transform_activity(activity: str, title: str):
    if activity != "Cardio":
        return activity
    if "FB" in title:
        return "Fußball"
    elif "Schwimmen" in title:
        return "Schwimmen"
    return activity


def add_pace(activity: str, title: str, pace: str):
    if activity == "Indoor Cycling" and "KM" in title.upper():
        value = parse_indoor_cycling_title(title)
        return transform_speed_to_pace(value) if value else pace
    return pace


def add_distance(
    activity: str, title: str, speed: float, time_in_minutes: float, distance: float
):
    if activity == "Indoor Cycling" and "KM" in title.upper():
        return round(speed * time_in_minutes / 60, 2) if speed > 1 else distance
    return distance


def transform_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df["ACTIVITY_TYPE"] = df.apply(
        lambda row: transform_activity(row["ACTIVITY_TYPE"], row["TITLE"]), axis=1
    )
    df["AVERAGE_PACE"] = df.apply(
        lambda row: add_pace(row["ACTIVITY_TYPE"], row["TITLE"], row["AVERAGE_PACE"]),
        axis=1,
    )
    df["DATE"] = df["DATE"].apply(transform_str_to_date)
    df["HOUR"] = df["DATE"].apply(lambda x: x.hour)
    df["MONTH"] = df["DATE"].apply(lambda x: x.month)
    df["YEAR"] = df["DATE"].apply(lambda x: x.year)
    df["STEPS"] = df["STEPS"].apply(parse_str_to_int)
    df["SPEED"] = df["AVERAGE_PACE"].apply(transform_pace_to_speed)
    df["PACE_FLOAT"] = df["AVERAGE_PACE"].apply(
        lambda x: round(transform_pace_to_pace_float(x), 2)
    )
    df["TIME_IN_MINUTES"] = df["TIME"].apply(parse_activity_duration_to_minutes)
    df["TIME_IN_HOURS"] = df["TIME"].apply(parse_activity_duration_to_hours)
    df["DISTANCE"] = df.apply(
        lambda row: add_distance(
            row["ACTIVITY_TYPE"],
            row["TITLE"],
            row["SPEED"],
            row["TIME_IN_MINUTES"],
            row["DISTANCE"],
        ),
        axis=1,
    )
    return df[df["YEAR"] >= MIN_YEAR]
