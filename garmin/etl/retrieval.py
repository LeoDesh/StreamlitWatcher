from typing import Any

from garminconnect import Garmin
from pandas import DataFrame, to_datetime

from garmin.constants import ACTIVITY_FILE_PATH, ARCHIVE_PATH, DATA_PATH
from garmin.etl.data_load import load_json, save_dict_to_json
from garmin.etl.transformation import (
    scale_distance,
    scale_hour,
    scale_metre,
    scale_minute,
    scale_steps,
    scale_streak,
)
from garmin.utils.misc import prettify_by_sep
from garmin.utils.pace_calculations import (
    transform_seconds_to_hour_minutes_seconds_format,
    transform_speed_to_pace,
)
from garmin.utils.pandas_helpers import read_file, save_df_to_csv, update_data
from garmin.utils.time_utils import (
    convert_iso_format_to_date,
    get_current_date_str,
)

ACTIVITY_MAPPING = {
    "other": "Sontige",
    "treadmill_running": "Laufbandtraining",
    "indoor_cardio": "Cardio",
    "indoor_cycling": "Indoor Cycling",
    "walking": "Gehen",
    "running": "Laufen",
    "cycling": "Radfahren",
}
CONFIG = {
    1: scale_minute,
    2: scale_minute,
    3: scale_minute,
    4: scale_minute,
    5: scale_hour,
    6: scale_hour,
    7: scale_distance,
    8: scale_distance,
    9: scale_metre,
    12: scale_steps,
    13: scale_steps,
    14: scale_steps,
    15: scale_streak,
    16: scale_streak,
}
ACTIVITY_COUNT_THRESHOLD = 50
RECORD_CONFIG_FILE = DATA_PATH / "PersonalRecordsConfig.json"
RECORD_DATA_FILE = DATA_PATH / "PersonalRecords.csv"
STEPS_DATA_FILE = DATA_PATH / "Steps.csv"


def extract_data_from_entry(activity_entry: dict[str, Any]) -> dict[str, Any]:
    activity_id = activity_entry["activityId"]
    name = activity_entry["activityName"]
    activity_time = activity_entry["startTimeLocal"]
    activity_type = ACTIVITY_MAPPING[activity_entry["activityType"]["typeKey"]]
    avg_speed = activity_entry["averageSpeed"]
    averageHR = activity_entry.get("averageHR", 0)
    maxSpeed = activity_entry.get("maxSpeed", 0)
    maxHR = activity_entry["maxHR"]
    calories = activity_entry["calories"]
    distance = activity_entry.get("distance", 0)
    duration = activity_entry["duration"]
    steps = activity_entry.get("steps", 0)
    return {
        "ID": activity_id,
        "Aktivitätstyp": activity_type,
        "Datum": activity_time,
        "Titel": name.replace(",", "."),
        "Distanz": round(distance / 1000, 2),
        "Kalorien": calories,
        "Ø Geschwindigkeit": transform_speed_to_pace(round(avg_speed * 3.6, 2))
        if avg_speed > 0
        else "--",
        "Maximale Geschwindigkeit": transform_speed_to_pace(round(maxSpeed * 3.6, 2))
        if maxSpeed > 0
        else "--",
        "Ø Herzfrequenz": averageHR,
        "Maximale Herzfrequenz": maxHR,
        "Schritte": steps,
        "Gesamtzeit": transform_seconds_to_hour_minutes_seconds_format(duration),
    }


def prepare_data(data: dict[str, Any]) -> DataFrame:
    df_data = [extract_data_from_entry(line) for line in data]
    return DataFrame(df_data)


def archive_data(df: DataFrame) -> None:
    date_stamp = get_current_date_str()
    filename = ARCHIVE_PATH / f"{date_stamp}_activities.csv"
    save_df_to_csv(df, filename)


def download_garmin_activities(client: Garmin) -> None:
    activities = client.get_activities(0, ACTIVITY_COUNT_THRESHOLD)
    personal_records = client.get_personal_record()
    convert_personal_records_to_csv(personal_records)
    update_activities(activities)


def convert_personal_records_to_csv(personal_records: dict[str, Any]) -> None:
    mapping = load_json(RECORD_CONFIG_FILE)
    converted_records = []
    for record in personal_records:
        record_id = record["typeId"]
        record_type = mapping[str(record_id)]
        value_converter = CONFIG[record_id]
        value, unit = value_converter(record["value"])
        converted_record = {
            "Record": prettify_by_sep(record_type, "."),
            "Date": convert_iso_format_to_date(
                record["actStartDateTimeInGMTFormatted"]
            ),
            "Value": value,
            "Unit": unit,
            "ActivityID": record["activityId"],
        }
        converted_records.append(converted_record)
    df = DataFrame(converted_records)
    save_df_to_csv(df, RECORD_DATA_FILE)


def update_personal_records(client: Garmin) -> None:
    personal_records = client.get_personal_record()
    convert_personal_records_to_csv(personal_records)


def update_activities(activities: dict[str, Any]) -> None:
    df = prepare_data(activities)
    archive_data(df)
    current_activities_df = read_file(ACTIVITY_FILE_PATH)
    updated_activities_df = update_data(current_activities_df, df)
    save_df_to_csv(updated_activities_df, ACTIVITY_FILE_PATH)


def refine_personal_record_mapping(
    mapping: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return {item["id"]: item["key"].replace("pr.label.", "") for item in mapping}


def refresh_personal_record_ids_mapping(client: Garmin) -> list[dict[str, Any]]:
    initial_mapping = client.connectapi(
        f"/personalrecord-service/personalrecordtype/prtypes/{client.display_name}"
    )
    refined_mapping = refine_personal_record_mapping(initial_mapping)
    save_dict_to_json(RECORD_CONFIG_FILE, refined_mapping)


def get_daily_steps(
    client: Garmin,
    start: str = "2020-01-01",
    end: str = get_current_date_str("%Y-%m-%d"),
) -> list[dict[str, str | float]]:
    return client.get_daily_steps(start, end)


def transform_daily_steps(data: list[dict[str, str | float]]) -> DataFrame:
    df = DataFrame(data)
    df.columns = ["Date", "Steps", "Distance", "Goal"]
    df["Date"] = to_datetime(df["Date"]).dt.date
    return df


def update_garmin_steps(garmin: Garmin) -> None:
    steps_df = read_file(STEPS_DATA_FILE)
    steps_df["Date"] = to_datetime(steps_df["Date"]).dt.date
    start = (
        "2022-01-01" if steps_df.empty else steps_df["Date"].max().strftime("%Y-%m-%d")
    )
    steps_data = get_daily_steps(garmin, start=start)
    new_steps_df = transform_daily_steps(steps_data)
    df = update_data(new_steps_df, steps_df)
    save_df_to_csv(df, STEPS_DATA_FILE)
