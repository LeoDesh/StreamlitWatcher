import calendar
import math
import re
from collections.abc import Callable
from datetime import date, datetime
from itertools import pairwise

import pandas as pd

from garmin.utils.time_utils import parse_date

TIME_PATTERN = r"(\d{2}):([0-5]\d|60):([0-5]\d|60)(\.\d+)?"


def parse_str_to_int(value: str | int) -> int:
    if isinstance(value, int):
        return value
    if value.find("--") > -1:
        return 0
    return int(value.replace(",", ""))


def get_all_regex_matches(regex_pattern: str, target_str: str) -> str:
    regex = re.compile(regex_pattern)
    return regex.findall(target_str)


"""Keep it. May still be used"""


def get_regex_match(regex_pattern: str, target_str: str, idx: int) -> str:
    regex = re.compile(regex_pattern)
    return regex.findall(target_str)[idx]


def search_with_regex(regex_pattern: str, target_str: str, idx: int = 0) -> str:
    match = re.search(regex_pattern, target_str)
    if match:
        group = match.group(idx)
        return group
    return ""


def calculate_bins_from_min_max_value(
    min_value: float, max_value: float, number_of_bins: int
) -> list[float]:
    step = (max_value - min_value) / number_of_bins
    return sorted({min_value + step * idx for idx in range(number_of_bins + 1)})


def calculate_int_bins(min_value: int, max_value: int, factor: int) -> list[float]:
    steps = int(float(max_value - min_value) // factor)
    return [min_value + factor * idx for idx in range(steps + 2)]


def calculate_ticker_values(values: list[float], max_numb: int = 7) -> list[float]:
    sample_number = len(set(values))
    number_of_bins = min(sample_number, max_numb)
    min_val = min(values) * 0.98
    max_val = max(values) * 1.02
    return calculate_bins_from_min_max_value(min_val, max_val, number_of_bins)


def bin_label_heartbeat(
    df: pd.DataFrame, number_of_bins: int, trg_column: str
) -> tuple[list[int], list[str]]:
    values = df[trg_column].tolist()
    bin_values = [
        int(value) for value in calculate_ticker_values(values, number_of_bins)
    ]
    labels = [
        f"{current_value}-{next_value}"
        for current_value, next_value in pairwise(bin_values)
    ]
    return (bin_values, labels)


def categorize_df_column(
    df: pd.DataFrame,
    trg_column: str,
    number_of_bins: int,
    bins_labels_func: Callable[[pd.DataFrame, int, str], tuple[list, list]],
) -> pd.DataFrame:
    bins, labels = bins_labels_func(df, number_of_bins, trg_column)
    df = df.copy()
    df.loc[:, f"new_{trg_column}"] = pd.cut(df[trg_column], bins=bins, labels=labels)
    df[trg_column] = df[f"new_{trg_column}"]
    return df


def verify_activity_duration(duration_str: str) -> bool:
    if not get_all_regex_matches(TIME_PATTERN, duration_str):
        return False
    minutes = parse_minutes_from_activity_duration(duration_str)
    seconds = parse_seconds_from_activity_duration(duration_str)
    hundreth = search_with_regex(r"\.(\d+)", duration_str, 1)
    hundreth = int(hundreth) if hundreth else 0
    if minutes == 60 and seconds > 0:
        return False
    return not (seconds == 60 and hundreth > 0)
    # 00:02:56.8


def check_prettified(text: str) -> bool:
    text_parts = text.split(" ")
    return all(part == part.capitalize() for part in text_parts)


def prettify(text: str) -> str:
    return text if check_prettified(text) else prettify_by_sep(text)


def prettify_by_sep(text: str, sep: str = "_") -> str:
    return " ".join(part.capitalize() for part in text.split(sep))


def parse_activity_duration_to_minutes(duration_str: str) -> float:
    if not verify_activity_duration(duration_str):
        return 0.0
    hours = parse_hours_from_activity_duration(duration_str)
    minutes = parse_minutes_from_activity_duration(duration_str)
    seconds = parse_seconds_from_activity_duration(duration_str)
    return calculate_minutes(hours, minutes, seconds)


def parse_activity_duration_to_hours(duration_str: str) -> float:
    if not verify_activity_duration(duration_str):
        return 0.0
    hours = parse_hours_from_activity_duration(duration_str)
    minutes = parse_minutes_from_activity_duration(duration_str)
    seconds = parse_seconds_from_activity_duration(duration_str)
    return calculate_hours(hours, minutes, seconds)


def _parse_time_components_from_activity_duration(
    duration_str: str, component_part: int
) -> int:
    regex_pattern = TIME_PATTERN
    return int(search_with_regex(regex_pattern, duration_str, component_part))


def parse_hours_from_activity_duration(duration_str: str) -> int:
    return _parse_time_components_from_activity_duration(duration_str, 1)


def parse_minutes_from_activity_duration(duration_str: str) -> int:
    return _parse_time_components_from_activity_duration(duration_str, 2)


def parse_seconds_from_activity_duration(duration_str: str) -> int:
    return _parse_time_components_from_activity_duration(duration_str, 3)


def calculate_minutes(hours: float, minutes: float, seconds: float) -> float:
    return round(hours * 60 + minutes + seconds / 60, 5)


def calculate_hours(hours: float, minutes: float, seconds: float) -> float:
    return round(hours + minutes / 60 + seconds / 3600, 5)


def transform_activity_minutes_to_duration_format(duration_in_minutes: float) -> str:
    hours = int(duration_in_minutes // 60)
    minutes = math.floor(duration_in_minutes - hours * 60)
    seconds = int(round((duration_in_minutes - hours * 60 - minutes) * 60, 0))
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def transform_str_to_datetime(
    date_str: str, src_format: str = "%Y-%m-%d %H:%M:%S"
) -> datetime:
    if isinstance(date_str, datetime):
        return date_str
    return parse_date(date_str, src_format)


def transform_str_to_datetime_date_str(date_str: str) -> datetime:
    return transform_str_to_datetime(date_str, "%Y-%m-%d")


def replace_comma_in_number(line: str) -> str:
    pattern = r"\d+,\d{3}"
    matches = get_all_regex_matches(pattern, line)
    for match in matches:
        replacement_match = match.replace(",", "")
        line = line.replace(match, replacement_match)
    return line


def parse_indoor_cycling_title(line: str) -> float | str:
    pattern = r"(\d+([\.,]\s*\d+)?)\s*KM"
    value = search_with_regex(pattern, line.upper(), 1)
    return transform_str_to_float(value)


def transform_str_to_float(value: str) -> float | str:
    value = value.replace(" ", "")
    value = value.replace(",", ".")
    try:
        return float(value)
    except (TypeError, ValueError):
        return value


def compute_delta(src: float, trg: float) -> float:
    if src and trg:
        return round((trg - src) / src * 100, 2)
    if src:
        return -100
    if trg:
        return 100
    return 0


def get_last_day_of_date(given_date: date) -> date:
    _, last_day = calendar.monthrange(given_date.year, given_date.month)
    return given_date.replace(day=last_day)
