from typing_extensions import Self

from environ_odoo_config.api import Env, OdooVersion, OdooVersionRange
from environ_odoo_config.api_converter import OdooConfigConverter, OnlyCli, SimpleKey

from .workers import ConfigConverterWorkers


class ConfigConverterLimit(OdooConfigConverter):
    """
    convert environment variable related to limit Worker or Threaded server
    """

    _opt_group = "Worker or Threaded server POSIX Limit Configuration"
    limit_request: int = SimpleKey(
        "LIMIT_REQUEST",
        cli="--limit-request",
        info="Maximum number of request to be processed per worker (default 65536).",
    )
    limit_time_cpu: int = SimpleKey(
        "LIMIT_TIME_CPU",
        cli="--limit-time-cpu",
        info="Maximum allowed CPU time per request (default 60).",
    )
    limit_time_real: int = SimpleKey(
        "LIMIT_TIME_REAL",
        cli="--limit-time-real",
        info="Maximum allowed Real time per request in seconds (default 120).",
    )
    limit_time_real_cron: int = SimpleKey(
        "LIMIT_TIME_REAL_CRON",
        cli="--limit-time-real-cron",
        info="Maximum allowed Real time per cron job. (default: --limit-time-real). Set to 0 for no limit. ",
    )
    transient_count_limit: int = SimpleKey(
        "TRANSIENT_COUNT_LIMIT",
        cli="--osv-memory-count-limit",
        ini_dest="osv_memory_count_limit",
        info="""Force a limit on the maximum number of records kept in the virtual osv_memory tables.
         By default there is no limit.""",
    )
    transient_age_limit: float = SimpleKey(
        "TRANSIENT_AGE_LIMIT",
        cli="--transient-age-limit",
        odoo_version=OdooVersion.V14.min(),
        other_version=[
            OnlyCli("--osv-memory-age-limit", ini_dest="osv_memory_age_limit", odoo_version=OdooVersion.V13.max())
        ],
        info="""Time limit (decimal value in hours) records created with a TransientModel (mostly wizard)
        are kept in the database. Default to 1 hour.""",
    )
    limit_memory_hard: int = SimpleKey(
        "LIMIT_MEMORY_HARD",
        cli="--limit-memory-hard",
        info="""Maximum allowed virtual memory per worker (in bytes), when reached,
         any memory allocation will fail (default 2560MiB).""",
    )
    limit_memory_soft: int = SimpleKey(
        "LIMIT_MEMORY_SOFT",
        cli="--limit-memory-soft",
        info="""Maximum allowed virtual memory per worker (in bytes),
         when reached the worker be reset after the current request (default 2048MiB).""",
    )
    limit_time_worker_cron: int = SimpleKey(
        "LIMIT_TIME_WORKER_CRON",
        cli="--limit-time-worker-cron",
        odoo_version=OdooVersionRange(vmin=OdooVersion.V16),
        info="Maximum time a cron thread/worker stays alive before it is restarted. Set to 0 to disable. (default: 0)",
    )

    def init(self, env: Env) -> Self:
        super().init(env)
        if not self.limit_memory_hard or not self.limit_memory_soft:
            global_limit_memory_hard = env.get_int("GLOBAL_LIMIT_MEMORY_HARD")
            global_limit_memory_soft = env.get_int("GLOBAL_LIMIT_MEMORY_SOFT")
            nb_workers = ConfigConverterWorkers().init(env).total or 1
            if not self.limit_memory_soft and global_limit_memory_soft:
                self.limit_memory_soft = global_limit_memory_soft // nb_workers
            if not self.limit_memory_hard and global_limit_memory_hard:
                self.limit_memory_hard = global_limit_memory_hard // nb_workers
        return self
