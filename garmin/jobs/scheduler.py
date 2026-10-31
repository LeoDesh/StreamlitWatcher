import time
from collections.abc import Callable

from rq.cron import CronScheduler

from garmin.etl.client import DataClient, get_garmin_client
from garmin.etl.retrieval import (
    update_garmin_activities,
    update_garmin_steps,
    update_personal_records,
)
from garmin.jobs.config import get_redis_conn
from garmin.logger import JOBS_LOGGER

CRON_SCHEDULE = "0 7,11,15,19,23 * * *"


def track_func(func: Callable[[DataClient], None], *args):
    start = time.perf_counter()
    try:
        result = func(*args)
        JOBS_LOGGER.info(f"[{func.__name__}] succeded.")
    except Exception as exc:  # noqa: BLE001
        JOBS_LOGGER.info(f"[{func.__name__}] failed. {exc!s}")
        result = None
    end = time.perf_counter()
    JOBS_LOGGER.info(f"[{func.__name__}] finished in {end - start:.6f} seconds")
    return result


def refresh_data():
    client = track_func(get_garmin_client)
    refresh_funcs = [
        update_garmin_activities,
        update_garmin_steps,
        update_personal_records,
    ]
    for func in refresh_funcs:
        track_func(func, client)


def run_scheduler():

    connection = get_redis_conn()

    scheduler = CronScheduler(
        connection=connection,
        logging_level="INFO",
    )

    scheduler.register(
        refresh_data,
        queue_name="daily",
        cron=CRON_SCHEDULE,
    )
    scheduler.start()
