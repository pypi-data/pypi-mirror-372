"""
Contains the mapper specifique for the environment variable provided by CleverCloud addons.
Currently we support :
- S3 addons Cellar
- Postgres Addons of any scaler
"""

from environ_odoo_config.api import Env


def redis_session(curr_env: Env) -> Env:
    """ """
    return curr_env + {
        "REDIS_SESSION_ENABLE": str(
            curr_env.get_bool("REDIS_SESSION_ENABLE", default=bool(curr_env.gets("REDIS_SESSION_HOST", "REDIS_HOST")))
        ),
        "REDIS_SESSION_URL": curr_env.gets("REDIS_SESSION_URL", "REDIS_URL"),
        "REDIS_SESSION_HOST": curr_env.gets("REDIS_SESSION_HOST", "REDIS_HOST"),
        "REDIS_SESSION_PORT": curr_env.gets("REDIS_SESSION_PORT", "REDIS_PORT"),
        "REDIS_SESSION_DB_INDEX": curr_env.gets("REDIS_SESSION_DB_INDEX", "REDIS_DB_INDEX"),
        "REDIS_SESSION_PASSWORD": curr_env.gets("REDIS_SESSION_PASSWORD", "REDIS_PASSWORD"),
    }
