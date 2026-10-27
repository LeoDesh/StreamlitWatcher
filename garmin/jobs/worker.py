from rq import Queue, Worker

from garmin.jobs.config import get_redis_conn


def run_worker():
    redis_conn = get_redis_conn()

    queue = Queue(
        "daily",
        connection=redis_conn,
    )

    worker = Worker(
        [queue],
        connection=redis_conn,
    )

    worker.work()
