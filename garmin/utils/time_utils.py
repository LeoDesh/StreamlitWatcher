import calendar
from datetime import date, datetime, time
from zoneinfo import ZoneInfo


def parse_str_date(date_str: str, date_format: str) -> datetime:
    return datetime.strptime(date_str, date_format).replace(tzinfo=ZoneInfo("UTC"))


def get_current_date() -> date:
    return datetime.now(ZoneInfo("UTC")).date()


def convert_iso_format_to_date(date_iso_format: str | None) -> date | None:
    return datetime.fromisoformat(date_iso_format).date() if date_iso_format else None


def get_current_date_str(format: str = "%Y%m%d") -> str:
    current_date = get_current_date()
    return current_date.strftime(format)


def get_current_month() -> date:
    today = get_current_date()
    return today.replace(day=1)


def get_current_year() -> int:
    today = get_current_date()
    return today.year


def get_month_previous_year() -> date:
    current_month = get_current_month()
    return current_month.replace(year=current_month.year - 1)


def get_first_of_given_year(yr: int) -> date:
    return date(yr, 1, 1)


def get_last_day_of_date(given_date: date) -> date:
    _, last_day = calendar.monthrange(given_date.year, given_date.month)
    return given_date.replace(day=last_day)


def transform_date_to_datetime(date_value: date) -> datetime:
    return datetime.combine(date_value, time.min)


def parse_value_to_datetime(
    date_value: str | date | datetime, date_format: str = "%Y-%m-%d %H:%M:%S"
) -> datetime:
    if isinstance(date_value, datetime):
        return date_value
    elif isinstance(date_value, date):
        return transform_date_to_datetime(date_value)
    return parse_str_date(date_value, date_format)
