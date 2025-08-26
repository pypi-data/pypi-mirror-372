from environ_odoo_config.api_converter import OdooConfigConverter, SimpleKey


class ConfigConverterWorkers(OdooConfigConverter):
    _opt_group = "POSIX Worker Configuration"
    workers: int = SimpleKey("WORKER_HTTP", cli="--workers")
    cron: int = SimpleKey("WORKER_CRON", cli="--max-cron-thread")

    @property
    def total(self):
        return self.workers + self.cron
