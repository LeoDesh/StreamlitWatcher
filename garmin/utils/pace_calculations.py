from garmin.utils.misc import get_all_regex_matches,calculate_bins_values_dataframe
import pandas as pd
import math

def transform_speed_to_pace(speed:float) -> str:
    pace_float = float(60) / speed
    return transform_pace_float_to_pace(pace_float)

def transform_pace_to_speed(pace_str: str) -> float:
    pace_float = transform_pace_to_pace_float(pace_str)
    return round(float(60) / pace_float, 2)


def transform_pace_to_pace_float(pace_str: str) -> float:
    mins, secs = transform_pace_to_minutes_seconds(pace_str)
    return mins + float(secs) / 60


def transform_pace_float_to_pace(pace_float: float) -> str:
    mins = math.floor(pace_float)
    secs = math.floor((pace_float - mins)*60)
    return f"{mins}:{secs:02d}"


def transform_pace_to_minutes_seconds(pace_str: str) -> tuple[int, int]:
    if not verify_pace_format(pace_str):
        return (59, 59)
    mins = get_all_regex_matches(r"\d?\d", pace_str)[0]
    secs = get_all_regex_matches(r":([0-5]\d)", pace_str)[0].replace(":","")
    return (int(mins), int(secs))


def verify_pace_format(pace_str: str) -> bool:
    pattern = r"^([0-5]?\d:[0-5]\d)$"
    if get_all_regex_matches(pattern, pace_str):
        return True
    return False

def get_pace_bins_labels_for_dataframe(df:pd.DataFrame,number_of_bins:int,pace_float_column:str) -> tuple[list[float],list[str]]:
    bins = calculate_bins_values_dataframe(df, number_of_bins, pace_float_column)
    pace_str_bins = [transform_pace_float_to_pace(bin) for bin in bins]
    pins_set = set()
    chosen_nums = []
    for idx,pace_bin in enumerate(pace_str_bins):
        if pace_bin not in pins_set:
            chosen_nums.append(idx)
        pins_set.add(pace_bin)
    calc_bins = [bins[idx] for idx in chosen_nums]
    labels = [
        f"{transform_pace_float_to_pace(calc_bins[idx])}-{transform_pace_float_to_pace(calc_bins[idx + 1])}"
        for idx in range(len(calc_bins)-1)
    ]
    return (calc_bins,labels)