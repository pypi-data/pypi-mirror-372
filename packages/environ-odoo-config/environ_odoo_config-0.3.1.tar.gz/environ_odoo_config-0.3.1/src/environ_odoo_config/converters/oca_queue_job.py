from typing_extensions import Set

from environ_odoo_config.api import Env, OdooConfig, OdooVersion, OdooVersionRange
from environ_odoo_config.api_converter import (
    NOT_INI_CONFIG,
    OdooConfigConverter,
    RepeatableKey,
    SimpleCSVKey,
    SimpleKey,
)


def if_converter_enable(env: Env) -> bool:
    converter = env.get_converter(ConfigConverterQueueJob)
    return converter.enable


class ConfigConverterQueueJob(OdooConfigConverter):
    """
    convert environment variable related to the OCA queue_job configuration

    CAUTION: If environement variable `ODOO_QUEUE_JOB_XXXX` exist, then `queue_job` take
    it before the configuration in the result config file.
    So use `QUEUE_JOB_XXX` variable or `ODOO_QUEUE_JOB_XXXX` but not both at the same time.

    """

    _opt_group = "OCA: queue_job Configuration"
    _ini_section = "queue_job"

    enable: bool = SimpleKey("QUEUE_JOB_ENABLE", ini_dest=NOT_INI_CONFIG)
    env_channels: Set[str] = SimpleCSVKey("ODOO_QUEUE_JOB_CHANNELS")

    channels: Set[str] = RepeatableKey("QUEUE_JOB_CHANNELS")
    scheme: str = SimpleKey("QUEUE_JOB_SCHEME")
    host: str = SimpleKey("QUEUE_JOB_HOST")
    port: int = SimpleKey("QUEUE_JOB_PORT")
    http_auth_user: str = SimpleKey("QUEUE_JOB_HTTP_AUTH_USER")
    http_auth_password: str = SimpleKey("QUEUE_JOB_HTTP_AUTH_PASSWORD")
    jobrunner_db_host: str = SimpleKey("QUEUE_JOB_JOBRUNNER_DB_HOST")
    jobrunner_db_port: int = SimpleKey("QUEUE_JOB_JOBRUNNER_DB_PORT")
    jobrunner_db_user: str = SimpleKey(
        "QUEUE_JOB_JOBRUNNER_DB_PORT", odoo_version=OdooVersionRange(vmin=OdooVersion.V14)
    )
    jobrunner_db_password: str = SimpleKey(
        "QUEUE_JOB_JOBRUNNER_DB_PORT", odoo_version=OdooVersionRange(vmin=OdooVersion.V14)
    )

    def write_to_config(self, config: OdooConfig):
        if not self.enable:
            return
        self.auto_write_to_config(config)
