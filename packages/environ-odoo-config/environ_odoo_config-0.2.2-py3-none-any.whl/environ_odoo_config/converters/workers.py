from environ_odoo_config.api_converter import OdooConfigConverter, SimpleKey


class ConfigConverterWorkers(OdooConfigConverter):
    _opt_group = "POSIX Worker Configuration"
    workers: int = SimpleKey("WORKER_HTTP", cli="--workers")
    max_cron_threads: int = SimpleKey(
        "WORKER_CRON",
        cli="--max-cron-threads",
        info="Maximum number of threads processing concurrently cron jobs (default 2).",
    )

    @property
    def cron(self) -> int:
        return self.max_cron_threads

    @property
    def total(self) -> int:
        return self.workers + self.max_cron_threads
