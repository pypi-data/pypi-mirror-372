import enum

from environ_odoo_config.api import Env, OdooVersion
from environ_odoo_config.api_converter import OdooConfigConverter, OnlyCli, SimpleKey

from .workers import ConfigConverterWorkers


class MaxConnMode(enum.Enum):
    """
    Mode to compute the max_conn attribute
    Attributes:
        AUTO: the max_conn is compute from the number of worker defined
        in [`WorkerConfig`][odoo_env_config.section.worker_section]
        FIXED: the value is taken from `"DB_MAX_CONN"` is [][os.environ]
    """

    AUTO = "AUTO"
    FIXED = "FIXED"


class DbSslMode(enum.Enum):
    DISABLE = "disable"
    ALLOW = "allow"
    PREFER = "prefer"
    REQUIRE = "require"
    VERIFY_CA = "verify-ca"
    VERIFY_FULL = "verify-full"


def compute_auto_maxconn(curr_env: Env) -> int:
    """
    Compute the current maxconn based on the number of worker
    Odoo recomendation is ~= Number of worker * 1.5.
    Args:
        curr_env: The current Env

    Returns:
        The number of worker * 1.5
    """
    nb_workers = ConfigConverterWorkers(curr_env).workers
    return nb_workers + int(nb_workers // 2)


class ConfigConverterGevent(OdooConfigConverter):
    """
    convert environment variable related to the PostgreSQL database
    """

    _opt_group = "Database Configuration"
    # DB Section
    maxconn: int = SimpleKey(
        "DB_MAXCONN_GEVENT",
        info="specify the maximum number of physical connections to PostgreSQL by the gevent process",
        cli="--db_maxconn_gevent",
        odoo_version=OdooVersion.V17.min(),
        ini_dest="db_maxconn_gevent",
    )
    port: int = SimpleKey(
        "GEVENT_PORT",
        cli="--gevent-port",
        ini_dest="gevent_port",
        odoo_version=OdooVersion.V16.min(),
        other_version=[
            OnlyCli(
                "--longpolling-port",
                odoo_version=OdooVersion.V15.max(),
                ini_dest="longpolling_port",
            )
        ],
        info="Listen port for the gevent (longpolling) worker.",
    )
    limit_memory_soft: int = SimpleKey(
        "LIMIT_MEMORY_SOFT_GEVENT",
        cli="--limit-memory-soft-gevent",
        ini_dest="limit_memory_soft_gevent",
        odoo_version=OdooVersion.V18.min(),
        info="""Maximum allowed virtual memory per gevent worker (in bytes),
        when reached the worker will be reset after the current request. Defaults to `--limit-memory-soft`.""",
    )
    limit_memory_hard: int = SimpleKey(
        "LIMIT_MEMORY_HARD_GEVENT",
        cli="--limit-memory-hard-gevent",
        ini_dest="limit_memory_hard_gevent",
        odoo_version=OdooVersion.V18.min(),
        info="""Maximum allowed virtual memory per gevent worker (in bytes), when reached,
                any memory allocation will fail. Defaults to `--limit-memory-hard`.""",
    )

    @property
    def longpolling_port(self):
        return self.port
