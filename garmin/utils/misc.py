from datetime import datetime
import re
import pandas as pd
import math
from itertools import pairwise
from typing import Callable


def parse_str_int(value: str | int) -> int:
    if isinstance(value, int):
        return value
    if value.find("--") > -1:
        return 0
    return int(value.replace(",", ""))


def get_all_regex_matches(regex_pattern: str, target_str: str) -> str:
    regex = re.compile(regex_pattern)
    return regex.findall(target_str)


def get_regex_match(regex_pattern: str, target_str: str, idx: int) -> str:
    regex = re.compile(regex_pattern)
    return regex.findall(target_str)[idx]


def search_with_regex(regex_pattern: str, target_str, idx: int = 0) -> str:
    match = re.search(regex_pattern, target_str)
    if match:
        group = match.group(idx)
        return group
    return ""


def get_df_sum_from_column(
    df: pd.DataFrame, groupby_column: str, value_column: str
) -> pd.DataFrame:
    return df.groupby(groupby_column)[[value_column]].sum()


def calculate_ticker_values(values: list[float], max_numb: int = 7) -> list[float]:
    sample_number = len(values)
    if sample_number <= max_numb:
        return values
    min_val = min(values) - 1
    max_val = max(values) + 1
    return sorted(
        list(
            set(
                [
                    (min_val + (max_val - min_val) / max_numb * k)
                    for k in range(max_numb + 1)
                ]
            )
        )
    )


def bin_label_heartbeat(df: pd.DataFrame, number_of_bins: int, trg_column: str):
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
):
    bins, labels = bins_labels_func(df, number_of_bins, trg_column)
    df = df.copy()
    df.loc[:, f"new_{trg_column}"] = pd.cut(df[trg_column], bins=bins, labels=labels)
    df[trg_column] = df[f"new_{trg_column}"]
    return df


def verify_activity_duration(duration_str: str) -> bool:
    regex_pattern = r"\d{2}:[0-5]\d:[0-5]\d(\.\d+)?"
    if get_all_regex_matches(regex_pattern, duration_str):
        return True
    return False
    # 00:02:56.8


def prettify(text: str) -> str:
    return " ".join(part.capitalize() for part in text.split("_"))


def parse_activity_duration_to_minutes(duration_str: str) -> float:
    if not verify_activity_duration(duration_str):
        return 0.0
    hours = parse_hours_from_activity_duration(duration_str)
    minutes = parse_minutes_from_activity_duration(duration_str)
    seconds = parse_seconds_from_activity_duration(duration_str)
    return calculate_minutes(hours, minutes, seconds)


def parse_hours_from_activity_duration(duration_str: str) -> float:
    regex_pattern = r"(\d{2}):[0-5]\d:[0-5]\d(\.\d+)?"
    hours = search_with_regex(regex_pattern, duration_str, 1)
    return int(hours)


def parse_minutes_from_activity_duration(duration_str: str) -> float:
    regex_pattern = r"\d{2}:([0-5]\d):[0-5]\d(\.\d+)?"
    minutes = search_with_regex(regex_pattern, duration_str, 1)
    return int(minutes)


def parse_seconds_from_activity_duration(duration_str: str) -> float:
    regex_pattern = r"\d{2}:[0-5]\d:([0-5]\d)(\.\d+)?"
    seconds = search_with_regex(regex_pattern, duration_str, 1)
    return int(seconds)


def calculate_minutes(hours: float, minutes: float, seconds: float) -> float:
    return round(hours * 60 + minutes + seconds / 60, 5)


def transform_activity_minutes_to_duration_format(duration_in_minutes: float) -> str:
    hours = int(duration_in_minutes // 60)
    minutes = int(math.floor(duration_in_minutes - hours * 60))
    seconds = int(round((duration_in_minutes - hours * 60 - minutes) * 60, 0))
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def transform_str_to_date(date_str: str) -> datetime:
    if isinstance(date_str, datetime):
        return date_str
    src_format = "%Y-%m-%d %H:%M:%S"  # 2026-01-02 13:50:51
    return datetime.strptime(date_str, src_format)


def calculate_bins_values_dataframe(
    df: pd.DataFrame, number_of_bins: int, column: str
) -> list[float]:
    min_value, max_value = df[column].min(), df[column].max()
    return calculate_bins_from_min_max_value(min_value, max_value, number_of_bins)


def calculate_bins_from_min_max_value(
    min_value: float | int, max_value: float | int, number_of_bins: int
) -> list[float]:
    step = (max_value - min_value) / number_of_bins
    return [min_value + step * idx for idx in range(number_of_bins + 1)]


def split_lines_with_comma(line: str, sep: str = ",") -> list[str]:
    line = replace_comma_in_number(line)
    return line.split(sep)


def replace_comma_in_number(line: str) -> str:
    pattern = r"\d+,\d{3}"
    matches = get_all_regex_matches(pattern, line)
    for match in matches:
        replacement_match = match.replace(",", "")
        line = line.replace(match, replacement_match)
    return line
