import os
from typing import Any, Protocol

import garth
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv()
GARTH_FOLDER = ".garth"
GARMIN_FOLDER = ".garminconnect"


class DataClient(Protocol):
    def get_daily_steps(start: str, end: str) -> list[dict[str, str | float]]: ...
    def connectapi(request_str: str) -> list[dict[str, Any]]: ...
    def get_activities(start: int, limit: int) -> list[dict[str, Any]]: ...
    def get_personal_record() -> dict[str, Any]: ...


def get_garth_client() -> Garmin:
    client = Garmin()
    garth.resume(GARTH_FOLDER)
    client.garth = garth.client
    client.display_name = garth.client.profile["displayName"]
    return client


def get_garmin_client() -> Garmin:
    user = os.getenv("GARMIN_USER")
    password = os.getenv("GARMIN_PASSWORD")
    client = Garmin(user, password)
    client.login(tokenstore=GARMIN_FOLDER)
    return client
