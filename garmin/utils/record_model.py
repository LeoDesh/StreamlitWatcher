from garmin.utils.misc import (
    transform_activity_minutes_to_duration_format,
    transform_activity_minutes_to_duration_minute_format,
)

PACE_SUFFIX = "min/km"


def record_name_changer(name: str) -> str:
    match name:
        case "1k Run":
            return "Fastest 1 km pace"
        case "1mile Run":
            return "Fastest 1 mile pace"
        case "5k Run":
            return "Fastest 5 km pace"
        case "10k Run":
            return "Fastest 10 km pace"
        case "Half Marathon":
            return "Fastest half marathon pace"
        case "Marathon":
            return "Fastest marathon pace"
        case _:
            return name


def distance_mapping(name: str) -> float:
    match name:
        case "1k Run":
            return 1
        case "1mile Run":
            return 1.61
        case "5k Run":
            return 5
        case "10k Run":
            return 10
        case "Half Marathon":
            return 21.1
        case "Marathon":
            return 42.2
        case _:
            return 0


def is_1k_run(record: str) -> bool:
    return record == "1k Run"


def transform_1_km_record(record: str, value: float, *args) -> str:
    name = record_name_changer(record)
    pace = transform_activity_minutes_to_duration_minute_format(value)
    return f"{name}: {pace}"


def transform_running_record(record: str, value: float, unit: str) -> str:
    name = record_name_changer(record)
    distance = distance_mapping(record)
    value = value if unit == "min" else 60 * value
    value_per_km = value / distance
    formatter_func = (
        transform_activity_minutes_to_duration_minute_format
        if unit == "min"
        else transform_activity_minutes_to_duration_format
    )
    formatted_time = formatter_func(value)
    pace = transform_activity_minutes_to_duration_minute_format(value_per_km)
    return f"{name}: {formatted_time} ({pace} {PACE_SUFFIX})"


def transform_distance_record(record: str, value: float, unit: str) -> str:
    match unit:
        case "km":
            return f"{record} {value:.2f} {unit}"
        case "metre":
            return f"{record} {value:.0f} m"


def create_formatted_record_value(record: str, value: float, unit: str) -> str:
    if "1k" in record:
        return transform_1_km_record(record, value, unit)
    elif "Farthest" in record:
        return transform_distance_record(record, value, unit)
    else:
        return transform_running_record(record, value, unit)
