from datetime import date, datetime
from zoneinfo import ZoneInfo

from garmin.etl.constants import MIN_YEAR


def parse_date(date_str: str, src_format: str):
    return datetime.strptime(date_str, src_format).replace(tzinfo=ZoneInfo("UTC"))


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


def get_min_date() -> date:
    return get_first_of_given_year(MIN_YEAR)
