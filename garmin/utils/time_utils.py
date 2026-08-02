from datetime import date, datetime
from zoneinfo import ZoneInfo


def parse_date(date_str: str, src_format: str):
    return datetime.strptime(date_str, src_format).replace(tzinfo=ZoneInfo("UTC"))


def get_current_date() -> date:
    return datetime.now(ZoneInfo("UTC")).date()


def get_current_month() -> date:
    today = get_current_date()
    return today.replace(day=1)


def get_current_year() -> int:
    today = get_current_date()
    return today.year


def get_month_previous_year() -> date:
    current_month = get_current_month()
    return current_month.replace(year=current_month.year - 1)
