import re
import tomllib
from itertools import pairwise
from typing import Any


def parse_steps_number(value: str | int) -> int:
    if isinstance(value, int):
        return value
    if value.find("--") > -1:
        return 0
    return int(value.replace(",", ""))


def get_all_regex_matches(regex_pattern: str, target_str: str) -> list[str]:
    regex = re.compile(regex_pattern)
    return regex.findall(target_str)


def find_regex_match(regex_pattern: str, target_str: str, idx: int = 0) -> str:
    match = re.search(regex_pattern, target_str)
    if match:
        group = match.group(idx)
        return group
    return ""


def check_prettified(text: str) -> bool:
    text_parts = text.split(" ")
    return all(part == part.capitalize() for part in text_parts)


def prettify(text: str) -> str:
    return text if check_prettified(text) else prettify_by_sep(text)


def prettify_by_sep(text: str, sep: str = "_") -> str:
    return " ".join(part.capitalize() for part in text.split(sep))


def calculate_minutes(hours: float, minutes: float, seconds: float) -> float:
    return round(hours * 60 + minutes + seconds / 60, 5)


def calculate_hours(hours: float, minutes: float, seconds: float) -> float:
    return round(hours + minutes / 60 + seconds / 3600, 5)


def replace_comma_in_number(line: str) -> str:
    pattern = r"\d+,\d{3}"
    matches = get_all_regex_matches(pattern, line)
    for match in matches:
        replacement_match = match.replace(",", "")
        line = line.replace(match, replacement_match)
    return line


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


def filter_mapping(data: dict[str, Any], filter_columns: list[str]) -> dict[str, Any]:
    return {key: value for key, value in data.items() if key in filter_columns}


def create_label_pairs_from_values(
    data: list[float | str | int], *, delimiter: str = "-", suffix: str = ""
) -> list[str]:
    suffix = f" {suffix}" if suffix else ""
    return [
        f"{current_value}{delimiter}{next_value}{suffix}"
        for current_value, next_value in pairwise(data)
    ]


def get_app_version() -> str:
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
        return data.get("project", {}).get("version", "unknown")
