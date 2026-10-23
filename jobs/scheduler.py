from datetime import datetime

from rq.cron import CronScheduler

from jobs.config import get_redis_conn


def exec_job() -> None:
    print(f"done. {datetime.now()}")


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
