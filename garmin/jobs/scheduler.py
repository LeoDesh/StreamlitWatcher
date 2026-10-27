from datetime import datetime

from rq.cron import CronScheduler

from garmin.jobs.config import get_redis_conn
from garmin.logger import JOBS_LOGGER


def exec_job() -> None:
    JOBS_LOGGER.info(f"DONE. {datetime.now()}")


def run_scheduler():

    connection = get_redis_conn()

    scheduler = CronScheduler(
        connection=connection,
        logging_level="INFO",
    )

    scheduler.register(
        exec_job,
        queue_name="daily",
        # cron="0 3 * * *",
        cron="* * * * *",
    )

    scheduler.start()
