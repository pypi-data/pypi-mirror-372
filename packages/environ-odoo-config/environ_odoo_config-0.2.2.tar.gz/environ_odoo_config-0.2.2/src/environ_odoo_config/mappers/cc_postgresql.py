"""
Contains the mapper specifique for the environment variable provided by CleverCloud addons.
Currently we support :
- S3 addons Cellar
- Postgres Addons of any scaler
"""

from environ_odoo_config.api import Env


def clevercloud_postgresql(curr_env: Env) -> Env:
    """ """
    return curr_env + {
        "DB_NAME": curr_env.gets("DB_NAME", "DATABASE", "POSTGRESQL_ADDON_DB", "POSTGRES_DB"),
        "DB_HOST": curr_env.gets(
            "DB_HOST",
            "POSTGRESQL_ADDON_DIRECT_HOST",
            "POSTGRESQL_ADDON_HOST",
        ),
        "DB_PORT": curr_env.gets(
            "DB_PORT",
            "POSTGRESQL_ADDON_DIRECT_PORT",
            "POSTGRESQL_ADDON_PORT",
        ),
        "DB_USER": curr_env.gets("DB_USER", "POSTGRESQL_ADDON_USER", "POSTGRES_USER"),
        "DB_PASSWORD": curr_env.gets(
            "DB_PASSWORD",
            "POSTGRESQL_ADDON_PASSWORD",
            "POSTGRES_PASSWORD",
        ),
    }
