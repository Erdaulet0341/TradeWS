import os
from dotenv import load_dotenv

load_dotenv()


def get_env_variable(var_name: str):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = 'Set the %s environment variable' % var_name
        raise Exception(error_msg)

