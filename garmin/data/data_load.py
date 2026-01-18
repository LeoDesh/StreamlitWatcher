from pathlib import Path
import pandas as pd
from garmin.data.column_mapping import GARMIN_COLUMNS
from garmin.utils.misc import transform_str_to_date,parse_str_int
from garmin.data.file_verification import validate_csv_file
from garmin.utils.pace_calculations import transform_pace_to_speed,transform_pace_to_pace_float
from garmin.utils.misc import parse_activity_duration_to_minutes

def import_file(file: Path) -> pd.DataFrame:
    validate_csv_file(file)
    df = read_file(file)
    df = rename_df_columns(df)
    df = filter_garmin_df(df)
    return transform_dataframe(df)


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
    df = df.reset_index()
    return df

def transform_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df["DATE"] = df["DATE"].apply(transform_str_to_date)
    df["HOUR"] = df["DATE"].apply(lambda x: x.hour)
    df["MONTH"] = df["DATE"].apply(lambda x: x.month)
    df["YEAR"] = df["DATE"].apply(lambda x: x.year)
    df["STEPS"] = df["STEPS"].apply(lambda x: parse_str_int(x))
    df["CALORIES"] = df["CALORIES"].apply(lambda x: parse_str_int(x))
    df["SPEED"] = df["AVERAGE_PACE"].apply(lambda x:transform_pace_to_speed(x))
    df["PACE_FLOAT"] = df["AVERAGE_PACE"].apply(lambda x:round(transform_pace_to_pace_float(x),2))
    df["TIME_IN_MINUTES"] = df["TIME"].apply(lambda x:parse_activity_duration_to_minutes(x))
    return df
