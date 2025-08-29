import unittest

from src.environ_odoo_config.api import Env, OdooCliFlag
from src.environ_odoo_config.converters.workers import ConfigConverterWorkers


class TestConfigConverterWorkers(unittest.TestCase):
    def test_default(self):
        conf = ConfigConverterWorkers()
        self.assertEqual(0, conf.workers)
        self.assertEqual(0, conf.cron)
        self.assertEqual(0, conf.total)
        conf.init(Env())
        self.assertEqual(0, conf.workers)
        self.assertEqual(0, conf.cron)
        self.assertEqual(0, conf.total)
        self.assertFalse(conf.to_values())

    def test_WORKER_HTTP(self):
        conf = ConfigConverterWorkers()
        self.assertEqual(0, conf.workers)
        self.assertEqual(0, conf.cron)
        self.assertEqual(0, conf.total)
        conf.init(Env({"WORKER_HTTP": str(10)}))
        self.assertEqual(10, conf.workers)
        self.assertEqual(0, conf.cron)
        self.assertEqual(10, conf.total)
        self.assertEqual(OdooCliFlag({"--workers": 10}), conf.to_values())

    def test_priority(self):
        conf = ConfigConverterWorkers().init(
            Env(
                {
                    "WORKER_HTTP": str(2),
                    "WORKER_JOB": str(3),
                }
            )
        )
        self.assertEqual(2, conf.workers)
        self.assertEqual(0, conf.cron)  # default value
        self.assertEqual(2, conf.total)

    def test_usecase_worker(self):
        conf = ConfigConverterWorkers().init(
            Env(
                {
                    "WORKER_HTTP": str(2),
                    "WORKER_JOB": str(3),
                    "WORKER_CRON": str(1),
                }
            )
        )
        self.assertEqual(2, conf.workers)
        self.assertEqual(1, conf.cron)
        self.assertEqual(3, conf.total)
        self.assertEqual(
            OdooCliFlag({"--workers": 2, "--max-cron-threads": 1}), conf.to_values()
        )
