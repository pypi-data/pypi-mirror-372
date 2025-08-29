import unittest

from src.environ_odoo_config.api import Env
from src.environ_odoo_config.converters.process_limit import ConfigConverterLimit


class TestLimitOdooConfigSection(unittest.TestCase):
    def test_no_value(self):
        conf = ConfigConverterLimit()
        self.assertEqual(0, conf.limit_request)
        self.assertEqual(0, conf.limit_time_cpu)
        self.assertEqual(0, conf.limit_time_real)
        self.assertEqual(0, conf.transient_age_limit)
        self.assertEqual(0, conf.limit_memory_hard)
        self.assertEqual(0, conf.limit_memory_soft)

    def test_value(self):
        conf = Env(
                {
                    "LIMIT_REQUEST": str(1),
                    "LIMIT_TIME_CPU": str(2),
                    "LIMIT_TIME_REAL": str(3),
                    "TRANSIENT_COUNT_LIMIT": str(4),
                    "TRANSIENT_AGE_LIMIT": str(7),
                    "LIMIT_MEMORY_HARD": str(5),
                    "LIMIT_MEMORY_SOFT": str(6),
                }
            ).get_converter(ConfigConverterLimit)
        self.assertEqual(1, conf.limit_request)
        self.assertEqual(2, conf.limit_time_cpu)
        self.assertEqual(3, conf.limit_time_real)
        self.assertEqual(4, conf.transient_count_limit)
        self.assertEqual(5, conf.limit_memory_hard)
        self.assertEqual(6, conf.limit_memory_soft)
        self.assertEqual(7, conf.transient_age_limit)

    def test_global_hard_default_worker(self):
        conf = ConfigConverterLimit().init(
            Env(
                {
                    "GLOBAL_LIMIT_MEMORY_HARD": str(1000),
                }
            )
        )
        self.assertEqual(1000, conf.limit_memory_hard)
        self.assertEqual(0, conf.limit_request)
        self.assertEqual(0, conf.limit_time_cpu)
        self.assertEqual(0, conf.limit_time_real)
        self.assertEqual(0, conf.transient_age_limit)
        self.assertEqual(0, conf.limit_memory_soft)

    def test_global_hard_no_worker(self):
        """
        by default 2 worker cron and 1 worker http so we force to 0 worker http and worker cron
        so <GLOBAL_LIMIT_MEMORY_HARD> is divide by 3 (integer way with '//')
        """
        conf = ConfigConverterLimit().init(
            Env(
                {
                    "WORKER_HTTP": str(0),
                    "WORKER_CRON": str(0),
                    "GLOBAL_LIMIT_MEMORY_HARD": str(1000),
                }
            )
        )
        self.assertEqual(1000, conf.limit_memory_hard)
        self.assertEqual(0, conf.limit_request)
        self.assertEqual(0, conf.limit_time_cpu)
        self.assertEqual(0, conf.limit_time_real)
        self.assertEqual(0, conf.transient_age_limit)
        self.assertEqual(0, conf.limit_memory_soft)

    def test_global_soft_default_worker(self):
        """
        by default 2 worker cron and 1 worker http
        so <GLOBAL_LIMIT_MEMORY_SOFT> is divide by 3 (integer way with '//')
        """
        conf = ConfigConverterLimit().init(
            Env(
                {
                    "GLOBAL_LIMIT_MEMORY_SOFT": str(1000),
                }
            )
        )
        self.assertEqual(1000, conf.limit_memory_soft)
        self.assertEqual(0, conf.limit_request)
        self.assertEqual(0, conf.limit_time_cpu)
        self.assertEqual(0, conf.limit_time_real)
        self.assertEqual(0, conf.transient_age_limit)
        self.assertEqual(0, conf.limit_memory_hard)

    def test_global_soft_priority(self):
        """
        check priority between <GLOBAL_LIMIT_MEMORY_SOFT> and <LIMIT_MEMORY_SOFT>
        LIMIT_MEMORY_SOFT > GLOBAL_LIMIT_MEMORY_SOFT
        """
        conf = ConfigConverterLimit().init(
            Env(
                {
                    "LIMIT_MEMORY_SOFT": str(100),
                    "GLOBAL_LIMIT_MEMORY_SOFT": str(1000),
                }
            )
        )
        self.assertEqual(100, conf.limit_memory_soft)
        self.assertEqual(0, conf.limit_request)
        self.assertEqual(0, conf.limit_time_cpu)
        self.assertEqual(0, conf.limit_time_real)
        self.assertEqual(0, conf.transient_age_limit)
        self.assertEqual(0, conf.limit_memory_hard)

    def test_global_hard_priority(self):
        """
        check priority between <GLOBAL_LIMIT_MEMORY_HARD> and <LIMIT_MEMORY_HARD>
        LIMIT_MEMORY_HARD > GLOBAL_LIMIT_MEMORY_HARD
        """
        conf = ConfigConverterLimit().init(
            Env(
                {
                    "LIMIT_MEMORY_HARD": str(100),
                    "GLOBAL_LIMIT_MEMORY_HARD": str(1000),
                }
            )
        )
        self.assertEqual(100, conf.limit_memory_hard)
        self.assertEqual(0, conf.limit_request)
        self.assertEqual(0, conf.limit_time_cpu)
        self.assertEqual(0, conf.limit_time_real)
        self.assertEqual(0, conf.transient_age_limit)

    def test_global_soft_no_worker(self):
        """
        `GLOBAL_LIMIT_MEMORY_SOFT` is divide by 3 (integer way with '//')
        """
        conf = ConfigConverterLimit().init(
            Env(
                {
                    "WORKER_HTTP": str(2),
                    "WORKER_CRON": str(1),
                    "GLOBAL_LIMIT_MEMORY_SOFT": str(1000),
                    "LIMIT_MEMORY_HARD": str(200),
                }
            )
        )
        self.assertEqual(333, conf.limit_memory_soft)
        self.assertEqual(0, conf.limit_request)
        self.assertEqual(0, conf.limit_time_cpu)
        self.assertEqual(0, conf.limit_time_real)
        self.assertEqual(0, conf.transient_age_limit)
        self.assertEqual(200, conf.limit_memory_hard)
