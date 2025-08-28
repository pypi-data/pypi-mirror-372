import enum
from pathlib import Path

from typing_extensions import Self

from environ_odoo_config.api import Env, OdooVersion, OdooVersionRange
from environ_odoo_config.api_converter import EnumKey, OdooConfigConverter, OnlyCli, SimpleKey

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


class ConfigConverterDatabase(OdooConfigConverter):
    """
    convert environment variable related to the PostgreSQL database
    """

    _opt_group = "Database Configuration"
    pg_path: Path = OnlyCli("--pg_path", info="specify the pg executable path")
    # DB Section
    name: str = SimpleKey("DB_NAME", cli=["-d", "--database"], info="specify the database name", ini_dest="db_name")
    host: str = SimpleKey("DB_HOST", cli="--db_host", info="specify the database host", ini_dest="db_host")
    port: int = SimpleKey("DB_PORT", cli=["--db_port"], info="specify the database port", ini_dest="db_port")
    user: str = SimpleKey("DB_USER", cli=["-r", "--db_user"], info="specify the database user name", ini_dest="db_user")
    password: str = SimpleKey(
        "DB_PASSWORD", cli=["-w", "--db_password"], info="specify the database password", ini_dest="db_password"
    )
    max_conn: int = SimpleKey(
        "DB_MAX_CONN",
        cli="--db_maxconn",
        info="specify the maximum number of physical connections to PostgreSQL",
        ini_dest="db_maxconn",
    )
    _max_connections_mode: MaxConnMode = EnumKey(MaxConnMode, "DB_MAX_CONN_MODE", py_default=MaxConnMode.FIXED)
    replica_host: str = SimpleKey(
        "DB_REPLICA_HOST",
        cli="--db_replica_host",
        info="specify the replica host. Specify an empty db_replica_host to use the default unix socket.",
        odoo_version=OdooVersionRange(vmin=OdooVersion.V18),
        ini_dest="db_replica_host",
    )
    replica_port: int = SimpleKey(
        "DB_REPLICA_PORT",
        cli="--db_replica_port",
        info="specify the replica port",
        odoo_version=OdooVersionRange(vmin=OdooVersion.V18),
        ini_dest="db_replica_port",
    )
    template: str = SimpleKey(
        "DB_TEMPLATE",
        cli="--db-template",
        info="specify a custom database template to create a new database",
        ini_dest="db_template",
    )
    sslmode: DbSslMode = EnumKey(
        DbSslMode,
        "DB_SSL_MODE",
        cli="--db_sslmode",
        info="specify the database ssl connection mode (see PostgreSQL documentation)",
        ini_dest="db_sslmode",
    )
    # Security-related options
    list_db: bool = SimpleKey(
        "LIST_DB",
        cli=["--no-database-list"],
        info="""Disable the ability to obtain or view the list of databases.
        Also disable access to the database manager and selector,
        so be sure to set a proper --database parameter first""",
        py_default=True,
    )
    filter: str = SimpleKey(
        "DB_FILTER",
        cli="--db-filter",
        info="""Regular expressions for filtering available databases for Web UI.
        The expression can use %d (domain) and %h (host) placeholders.""",
        ini_dest="dbfilter",
    )

    @property
    def maxconn_mode(self) -> MaxConnMode:
        return self._max_connections_mode

    @property
    def show(self) -> bool:
        return self.list_db

    def init(self, curr_env: Env) -> Self:
        super().init(curr_env)
        if self._max_connections_mode == MaxConnMode.AUTO:
            self.max_conn = max(self.max_conn, compute_auto_maxconn(curr_env))
        if not self.filter and not self.list_db:
            self.filter = self.name
        return self
