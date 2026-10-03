from datetime import date

import pytest

from garmin.etl.load import load_json
from garmin.etl.retrieval import (
    RECORD_CONFIG_FILE,
    transform_daily_steps,
    translate_activity_line,
    translate_raw_record_data,
)


@pytest.mark.etl
def test_steps_conversion(get_steps_data: list[dict[str, str | float]]):
    df = transform_daily_steps(get_steps_data)
    assert list(df.columns) == ["Date", "Steps", "Distance", "Goal"]
    assert list(df.dtypes) == ["object", "int64", "int64", "int64"]


@pytest.mark.etl
def test_record_translation_1km(get_records_data: list[dict[str, str | float]]):
    record_mapping = load_json(RECORD_CONFIG_FILE)
    record = get_records_data[0]
    assert translate_raw_record_data(record, record_mapping) == {
        "Record": "1k Run",
        "ActivityID": 23260542824,
        "Date": date(2026, 6, 15),
        "Unit": "min",
        "Value": 3.6706166585286457,
    }


@pytest.mark.etl
def test_record_translation_monthly_steps(
    get_records_data: list[dict[str, str | float]],
):
    record_mapping = load_json(RECORD_CONFIG_FILE)
    record = get_records_data[1]
    assert translate_raw_record_data(record, record_mapping) == {
        "Record": "Steps Best Month",
        "Date": None,
        "Value": 354729.0,
        "Unit": "steps",
        "ActivityID": 0,
    }


@pytest.mark.etl
def test_translate_activity_line_running(
    get_activity_data: list[dict[str, str | float]],
):
    record = get_activity_data[0]
    assert translate_activity_line(record) == {
        "ID": 24503212106,
        "Aktivitätstyp": "Laufen",
        "Datum": "2026-09-26 11:37:43",
        "Titel": "Deutschlandsberg Laufen",
        "Distanz": 8.78,
        "Kalorien": 565.0,
        "Ø Geschwindigkeit": "5:57",
        "Maximale Geschwindigkeit": "4:40",
        "Ø Herzfrequenz": 145.0,
        "Maximale Herzfrequenz": 156.0,
        "Schritte": 8432,
        "Gesamtzeit": "00:52:15",
    }


@pytest.mark.etl
def test_translate_activity_line_tennis(
    get_activity_data: list[dict[str, str | float]],
):
    record = get_activity_data[1]
    assert translate_activity_line(record) == {
        "ID": 24483538443,
        "Aktivitätstyp": "Cardio",
        "Datum": "2026-09-24 17:03:20",
        "Titel": "Tennis",
        "Distanz": 0.0,
        "Kalorien": 620.0,
        "Ø Geschwindigkeit": "--",
        "Maximale Geschwindigkeit": "--",
        "Ø Herzfrequenz": 147.0,
        "Maximale Herzfrequenz": 170.0,
        "Schritte": 0,
        "Gesamtzeit": "00:57:16",
    }
