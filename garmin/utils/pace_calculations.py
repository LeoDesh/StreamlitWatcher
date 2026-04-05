from garmin.utils.misc import (
    get_all_regex_matches,
)
import math


def transform_speed_to_pace(speed: float) -> str:
    pace_float = float(60) / speed if speed > 0 else 0
    return transform_pace_float_to_pace(pace_float)


def transform_pace_to_speed(pace_str: str) -> float:
    pace_float = transform_pace_to_pace_float(pace_str)
    return round(float(60) / pace_float, 2)


def transform_pace_to_pace_float(pace_str: str) -> float:
    mins, secs = transform_pace_to_minutes_seconds(pace_str)
    return mins + float(secs) / 60


def transform_pace_float_to_pace(pace_float: float) -> str:
    mins = math.floor(pace_float)
    secs = math.floor((pace_float - mins) * 60)
    return f"{mins}:{secs:02d}"


def transform_pace_to_minutes_seconds(pace_str: str) -> tuple[int, int]:
    if not verify_pace_format(pace_str):
        return (59, 59)
    mins = get_all_regex_matches(r"\d?\d", pace_str)[0]
    secs = get_all_regex_matches(r":([0-5]\d)", pace_str)[0].replace(":", "")
    return (int(mins), int(secs))


def verify_pace_format(pace_str: str) -> bool:
    pattern = r"^([0-5]?\d:[0-5]\d)$"
    if get_all_regex_matches(pattern, pace_str):
        return True
    return False


def transform_seconds_to_hour_minutes_seconds_format(seconds: int):
    hours = int(seconds // 3600)
    seconds -= hours * 3600
    minutes = int(seconds // 60)
    seconds -= minutes * 60
    seconds = int(round(seconds, 0))
    return f"{hours:02}:{minutes:02}:{seconds:02}"
