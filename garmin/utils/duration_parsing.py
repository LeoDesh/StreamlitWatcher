from math import floor

from garmin.utils.misc import (
    calculate_hours,
    calculate_minutes,
    find_regex_match,
    get_all_regex_matches,
    transform_str_to_float,
)

TIME_PATTERN = r"(\d{2}):([0-5]\d|60):([0-5]\d|60)(\.\d+)?"


def parse_indoor_cycling_title(line: str) -> float | str:
    pattern = r"(\d+([\.,]\s*\d+)?)\s*KM"
    value = find_regex_match(pattern, line.upper(), 1)
    return transform_str_to_float(value)


def transform_activity_minutes_to_duration_format(duration_in_minutes: float) -> str:
    hours = int(duration_in_minutes // 60)
    minutes = floor(duration_in_minutes - hours * 60)
    seconds = int(round((duration_in_minutes - hours * 60 - minutes) * 60, 0))
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def transform_activity_minutes_to_duration_minute_format(
    duration_in_minutes: float,
) -> str:
    minutes = floor(duration_in_minutes)
    seconds = floor((duration_in_minutes - minutes) * 60)
    return f"{minutes:02d}:{seconds:02d}"


def parse_activity_duration(duration_str: str) -> tuple[int, int, int]:
    if not verify_activity_duration(duration_str):
        return (0, 0, 0)
    hours = parse_hours_from_activity_duration(duration_str)
    minutes = parse_minutes_from_activity_duration(duration_str)
    seconds = parse_seconds_from_activity_duration(duration_str)
    return (hours, minutes, seconds)


def parse_activity_duration_to_minutes(duration_str: str) -> float:
    hours, minutes, seconds = parse_activity_duration(duration_str)
    return calculate_minutes(hours, minutes, seconds)


def parse_activity_duration_to_hours(duration_str: str) -> float:
    hours, minutes, seconds = parse_activity_duration(duration_str)
    return calculate_hours(hours, minutes, seconds)


def _parse_time_components_from_activity_duration(
    duration_str: str, component_part: int
) -> int:
    regex_pattern = TIME_PATTERN
    return int(find_regex_match(regex_pattern, duration_str, component_part))


def parse_hours_from_activity_duration(duration_str: str) -> int:
    return _parse_time_components_from_activity_duration(duration_str, 1)


def parse_minutes_from_activity_duration(duration_str: str) -> int:
    return _parse_time_components_from_activity_duration(duration_str, 2)


def parse_seconds_from_activity_duration(duration_str: str) -> int:
    return _parse_time_components_from_activity_duration(duration_str, 3)


def verify_activity_duration(duration_str: str) -> bool:
    if not get_all_regex_matches(TIME_PATTERN, duration_str):
        return False
    minutes = parse_minutes_from_activity_duration(duration_str)
    seconds = parse_seconds_from_activity_duration(duration_str)
    hundreth = find_regex_match(r"\.(\d+)", duration_str, 1)
    hundreth = int(hundreth) if hundreth else 0
    if minutes == 60 and seconds > 0:
        return False
    return not (seconds == 60 and hundreth > 0)
