import os

import garth
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv()
GARTH_FOLDER = ".garth"
GARMIN_FOLDER = ".garminconnect"


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
