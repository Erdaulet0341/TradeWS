import os
from dotenv import load_dotenv

load_dotenv()


def get_env_variable(var_name: str):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = 'Set the %s environment variable' % var_name
        raise Exception(error_msg)


BINANCE_WS_URL = get_env_variable("BINANCE_WS_URL")
REDIS_HOST = get_env_variable("REDIS_HOST")
REDIS_PORT = int(get_env_variable("REDIS_PORT"))

CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'

TIME_INTERVAL = get_env_variable("TIME_INTERVAL")  # for how long to keep trades in Redis (in seconds)
SYMBOLS = ["btcusdt", "ethusdt"]  # list of symbols to listen to
