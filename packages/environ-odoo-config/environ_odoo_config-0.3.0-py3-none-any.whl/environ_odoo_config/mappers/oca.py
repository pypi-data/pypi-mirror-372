"""
Contains the mapper specifique for the environment variable provided by CleverCloud addons.
Currently we support :
- S3 addons Cellar
- Postgres Addons of any scaler
"""

from environ_odoo_config.api import Env


def queue_job(curr_env: Env) -> Env:
    def copy(s):
        return [p + s for p in ["QUEUE_JOB_", "ODOO_QUEUE_JOB_", "ODOO_CONNECTOR_"]]

    def copy_connector(s):
        return [p + s for p in ["QUEUE_JOB_", "ODOO_CONNECTOR_"]]

    return curr_env + {
        "QUEUE_JOB_ENABLE": str(curr_env.get_bool(*copy("ENABLE"), default=bool(curr_env.gets(*copy("CHANNELS"))))),
        "QUEUE_JOB_CHANNELS": curr_env.gets(*copy_connector("CHANNELS")),
        "QUEUE_JOB_SCHEME": curr_env.gets(*copy_connector("SCHEME")),
        "QUEUE_JOB_HOST": curr_env.gets(*copy_connector("HOST")),
        "QUEUE_JOB_PORT": curr_env.gets(*copy_connector("PORT")),
        "QUEUE_JOB_HTTP_AUTH_USER": curr_env.gets(*copy_connector("HTTP_AUTH_USER")),
        "QUEUE_JOB_HTTP_AUTH_PASSWORD": curr_env.gets(*copy_connector("HTTP_AUTH_PASSWORD")),
        "QUEUE_JOB_JOBRUNNER_DB_HOST": curr_env.gets(*copy_connector("JOBRUNNER_DB_HOST")),
        "QUEUE_JOB_JOBRUNNER_DB_PORT": curr_env.gets(*copy_connector("JOBRUNNER_DB_PORT")),
    }
