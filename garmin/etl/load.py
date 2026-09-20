import json
from datetime import date
from pathlib import Path
from typing import Any

from pandas import DataFrame

from garmin.etl.config import (
    ACTIVITY_TRANSLATION_MAPPING,
    ACTIVITY_TYPE_MAPPING,
    GARMIN_COLUMNS,
    MIN_DISTANCE,
    MIN_YEAR,
)
from garmin.etl.verification import validate_activities_file
from garmin.utils.duration_parsing import (
    parse_activity_duration_to_hours,
    parse_activity_duration_to_minutes,
    parse_indoor_cycling_title,
)
from garmin.utils.misc import parse_steps_number
from garmin.utils.pace_calculations import (
    transform_pace_to_pace_float,
    transform_pace_to_speed,
    transform_speed_to_pace,
)
from garmin.utils.pandas_helpers import filter_dataframe, read_file
from garmin.utils.record_model import create_formatted_record_value
from garmin.utils.time_utils import parse_value_to_datetime


def load_activity_file(file: Path) -> DataFrame:
    validate_activities_file(file)
    df = read_file(file)
    df = rename_activity_df_columns(df)
    return transform_dataframe(df)


def load_running_data(file: Path) -> DataFrame:
    df = load_activity_file(file)
    return filter_valid_running_activities(df)


def load_records_file(file: Path, activity_df: DataFrame) -> DataFrame:
    record_df = read_file(file)
    df = record_df.merge(activity_df, left_on="ActivityID", right_on="id", how="inner")
    df = filter_dataframe(df, {"activity_type": "Running"})
    df["formatted_value"] = df.apply(
        lambda row: create_formatted_record_value(
            row["Record"], row["Value"], row["Unit"]
        ),
        axis=1,
    )
    return df


def load_steps_file(file: Path) -> DataFrame:
    df = read_file(file)
    df = apply_date_transformation(df, "Date", "%Y-%m-%d")
    df["week"] = df["Date"].apply(
        lambda x: f"{x.isocalendar()[0]}_{x.isocalendar()[1]}"
    )
    df = df[df["year"] >= MIN_YEAR]
    df["goal_reached"] = df["Steps"] >= df["Goal"]
    return df


def rename_activity_df_columns(df: DataFrame) -> DataFrame:
    selected_columns = [col for col in GARMIN_COLUMNS]
    df = df[selected_columns].copy()
    df.columns = [str(GARMIN_COLUMNS[col]) for col in df.columns]
    return df


def filter_valid_running_activities(df: DataFrame) -> DataFrame:
    df = df.copy()
    filter_mask = (
        (df["average_pace"] != "--")
        & (df["activity_type"] == "Running")
        & (df["distance"] >= MIN_DISTANCE)
    )
    return df[filter_mask].reset_index(drop=True)


def transform_activity(initial_activity: str, title: str) -> str:
    if initial_activity not in ("Cardio", "Walking"):
        return initial_activity
    for title_part, activity in ACTIVITY_TRANSLATION_MAPPING.items():
        if title_part in title:
            return activity
    return initial_activity


def validate_valid_indoor_cycling(activity: str, title: str) -> bool:
    return activity == "Indoor Cycling" and "KM" in title.upper()


def add_pace_to_indoor_cycling(
    activity: str, pace: str, distance: float, time_in_hours: float
) -> str:
    if activity == "Indoor Cycling" and distance > 0:
        return transform_speed_to_pace(distance / time_in_hours) if distance else pace
    return pace


def add_distance_to_indoor_cycling(activity: str, title: str, distance: float) -> float:
    if validate_valid_indoor_cycling(activity, title):
        value = parse_indoor_cycling_title(title)
        return value if value else distance
    return distance


def apply_date_transformation(
    df: DataFrame, date_column: str, format: str
) -> DataFrame:
    df[date_column] = df[date_column].apply(
        lambda x: parse_value_to_datetime(x, format)
    )
    df["hour"] = df[date_column].apply(lambda x: x.hour)
    df["month"] = df[date_column].apply(lambda x: x.month)
    df["year"] = df[date_column].apply(lambda x: x.year)
    df["monthly_date"] = df[date_column].apply(lambda x: date(x.year, x.month, 1))
    return df


def transform_date_columns(df: DataFrame) -> DataFrame:
    df = apply_date_transformation(df, "date", "%Y-%m-%d %H:%M:%S")
    df["time_in_minutes"] = df["time"].apply(parse_activity_duration_to_minutes)
    df["time_in_hours"] = df["time"].apply(parse_activity_duration_to_hours)
    return df


def transform_activity_columns(df: DataFrame) -> DataFrame:
    df["activity_type"] = df["activity_type"].map(ACTIVITY_TYPE_MAPPING)
    df["activity_type"] = df.apply(
        lambda row: transform_activity(row["activity_type"], row["title"]), axis=1
    )
    return df


def transform_distance_pace_columns(df: DataFrame) -> DataFrame:
    df["distance"] = df.apply(
        lambda row: add_distance_to_indoor_cycling(
            row["activity_type"],
            row["title"],
            row["distance"],
        ),
        axis=1,
    )
    df["average_pace"] = df.apply(
        lambda row: add_pace_to_indoor_cycling(
            row["activity_type"],
            row["average_pace"],
            row["distance"],
            row["time_in_hours"],
        ),
        axis=1,
    )
    df["steps"] = df["steps"].apply(parse_steps_number)
    df["speed"] = df["average_pace"].apply(transform_pace_to_speed)
    df["pace_float"] = df["average_pace"].apply(
        lambda x: round(transform_pace_to_pace_float(x), 2)
    )
    return df


def transform_dataframe(df: DataFrame) -> DataFrame:
    df = transform_date_columns(df)
    df = transform_activity_columns(df)
    df = transform_distance_pace_columns(df)
    return df[df["year"] >= MIN_YEAR]


def save_dict_to_json(filename: Path, data: dict[str, Any]) -> None:
    with open(filename, "w") as f:
        json.dump(data, f)


def load_json(filename: Path) -> dict[str, Any]:
    with open(filename) as f:
        return json.load(f)
