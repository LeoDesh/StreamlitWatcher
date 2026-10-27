import os

from redis import Redis

REDIS_URL = os.getenv("REDIS_URL")


def get_redis_conn():
    return Redis.from_url(REDIS_URL)
