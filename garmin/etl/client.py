import os
from typing import Any, Protocol

from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv()
GARMIN_FOLDER = os.getenv("GARMIN_TOKEN_DIR")


class DataClient(Protocol):
    def get_daily_steps(start: str, end: str) -> list[dict[str, str | float]]: ...
    def connectapi(request_str: str) -> list[dict[str, Any]]: ...
    def get_activities(start: int, limit: int) -> list[dict[str, Any]]: ...
    def get_personal_record() -> dict[str, Any]: ...


def get_garmin_client() -> Garmin:
    user = os.getenv("GARMIN_USER")
    password = os.getenv("GARMIN_PASSWORD")
    client = Garmin(user, password)
    client.login(tokenstore=GARMIN_FOLDER)
    return client
