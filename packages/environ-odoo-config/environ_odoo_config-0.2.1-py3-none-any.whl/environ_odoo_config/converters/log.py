from pathlib import Path
from typing import Set

from environ_odoo_config.api import OdooVersion, OdooVersionRange, odoo_log_levels
from environ_odoo_config.api_converter import NOT_INI_CONFIG, OdooConfigConverter, OnlyCli, RepeatableKey, SimpleKey


class ConfigConverterLogging(OdooConfigConverter):
    """
    convert environment variable related to the logging configuration
    """

    _opt_group = "Logging Configuration"
    logrotate: bool = OnlyCli("--logrotate", odoo_version=OdooVersion.V12.max())
    logfile: Path = SimpleKey("LOGFILE", cli="--logfile", info="file where the server log will be stored")
    use_syslog: bool = SimpleKey(
        "USE_SYSLOG", cli="--syslog", info="Send the log to the syslog server", ini_dest="syslog"
    )
    log_handler: Set[str] = RepeatableKey(
        "LOG_HANDLER",
        cli="--log-handler",
        info="""setup a handler at LEVEL for a given PREFIX. An empty PREFIX indicates the root logger.
        This option can be repeated. Example: "odoo.orm:DEBUG" or "werkzeug:CRITICAL" (default: ":INFO")""",
    )
    log_web: bool = SimpleKey(
        "LOG_WEB", cli="--log-web", info="shortcut for --log-handler=odoo.http:DEBUG", ini_dest=NOT_INI_CONFIG
    )
    log_sql: bool = SimpleKey("LOG_SQL", cli="--log-sql", info="enable web logging", ini_dest=NOT_INI_CONFIG)
    log_request: bool = SimpleKey(
        "LOG_REQUEST",
        cli="--log-request",
        odoo_version=OdooVersionRange(vmax=OdooVersion.V15),
        info="shortcut for --log-handler=odoo.http.rpc.request:DEBUG",
        ini_dest=NOT_INI_CONFIG,
    )
    log_response: bool = SimpleKey(
        "LOG_RESPONSE",
        cli="--log-response",
        odoo_version=OdooVersionRange(vmax=OdooVersion.V15),
        info="shortcut for --log-handler=odoo.http.rpc.response:DEBUG",
        ini_dest=NOT_INI_CONFIG,
    )
    log_db: bool = SimpleKey("LOG_DB", cli="--log-db", info="Logging database")
    log_db_level: str = SimpleKey("LOG_DB_LEVEL", cli="--log-db-level", info="Logging database level")
    log_level: str = SimpleKey(
        "LOG_LEVEL",
        cli="--log-level",
        info="specify the level of the logging. Accepted values: %s." % (odoo_log_levels,),
    )
