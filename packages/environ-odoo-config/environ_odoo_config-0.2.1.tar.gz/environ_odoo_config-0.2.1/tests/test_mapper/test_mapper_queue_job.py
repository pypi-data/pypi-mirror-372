import unittest

from src.environ_odoo_config import api
from src.environ_odoo_config.mappers.oca import queue_job


class TestOdooQueueJobMapper(unittest.TestCase):
    def test_empty(self):
        result = queue_job(api.Env())
        self.assertEqual(9, len(result.keys()))
        for key_result, value in result.items():
            if key_result == "QUEUE_JOB_ENABLE":
                self.assertEqual("False", value)
                continue
            self.assertIsNone(value, "Value of key [%s] is not None" % key_result)

    def test_not_change(self):
        value1 = "1"
        value2 = "2"
        value3 = "3"
        value4 = "4"
        value5 = "5"
        value6 = "6"
        value7 = "7"
        value8 = "8"
        to_map = {
            "ODOO_QUEUE_JOB_ENABLE": "True",
            "ODOO_QUEUE_JOB_CHANNELS": value1,
            "ODOO_QUEUE_JOB_SCHEME": value2,
            "ODOO_QUEUE_JOB_HOST": value3,
            "ODOO_QUEUE_JOB_PORT": value4,
            "ODOO_QUEUE_JOB_HTTP_AUTH_USER": value5,
            "ODOO_QUEUE_JOB_HTTP_AUTH_PASSWORD": value6,
            "ODOO_QUEUE_JOB_JOBRUNNER_DB_HOST": value7,
            "ODOO_QUEUE_JOB_JOBRUNNER_DB_PORT": value8,
        }
        result = queue_job(api.Env(to_map))
        self.assertEqual(18, len(result.keys()))
        self.assertEqual(value1, result["ODOO_QUEUE_JOB_CHANNELS"])
        self.assertEqual(value2, result["ODOO_QUEUE_JOB_SCHEME"])
        self.assertEqual(value3, result["ODOO_QUEUE_JOB_HOST"])
        self.assertEqual(value4, result["ODOO_QUEUE_JOB_PORT"])
        self.assertEqual(value5, result["ODOO_QUEUE_JOB_HTTP_AUTH_USER"])
        self.assertEqual(value6, result["ODOO_QUEUE_JOB_HTTP_AUTH_PASSWORD"])
        self.assertEqual(value7, result["ODOO_QUEUE_JOB_JOBRUNNER_DB_HOST"])
        self.assertEqual(value8, result["ODOO_QUEUE_JOB_JOBRUNNER_DB_PORT"])

    def test_second_value(self):
        value1 = "1"
        value2 = "2"
        value3 = "3"
        value4 = "4"
        value5 = "5"
        value6 = "6"
        value7 = "7"
        value8 = "8"
        to_map = {
            "ODOO_QUEUE_JOB_ENABLE": "True",
            "ODOO_CONNECTOR_CHANNELS": value1 + "_fake",
            "ODOO_CONNECTOR_SCHEME": value2 + "_fake",
            "ODOO_CONNECTOR_HOST": value3 + "_fake",
            "ODOO_CONNECTOR_PORT": value4 + "_fake",
            "ODOO_CONNECTOR_HTTP_AUTH_USER": value5 + "_fake",
            "ODOO_CONNECTOR_HTTP_AUTH_PASSWORD": value6 + "_fake",
            "ODOO_CONNECTOR_JOBRUNNER_DB_HOST": value7 + "_fake",
            "ODOO_CONNECTOR_JOBRUNNER_DB_PORT": value8 + "_fake",
            "ODOO_QUEUE_JOB_CHANNELS": value1,
            "ODOO_QUEUE_JOB_SCHEME": value2,
            "ODOO_QUEUE_JOB_HOST": value3,
            "ODOO_QUEUE_JOB_PORT": value4,
            "ODOO_QUEUE_JOB_HTTP_AUTH_USER": value5,
            "ODOO_QUEUE_JOB_HTTP_AUTH_PASSWORD": value6,
            "ODOO_QUEUE_JOB_JOBRUNNER_DB_HOST": value7,
            "ODOO_QUEUE_JOB_JOBRUNNER_DB_PORT": value8,
        }
        result = queue_job(api.Env(to_map))
        self.assertEqual(26, len(result.keys()))
        self.assertEqual(value1, result["ODOO_QUEUE_JOB_CHANNELS"])
        self.assertEqual(value2, result["ODOO_QUEUE_JOB_SCHEME"])
        self.assertEqual(value3, result["ODOO_QUEUE_JOB_HOST"])
        self.assertEqual(value4, result["ODOO_QUEUE_JOB_PORT"])
        self.assertEqual(value5, result["ODOO_QUEUE_JOB_HTTP_AUTH_USER"])
        self.assertEqual(value6, result["ODOO_QUEUE_JOB_HTTP_AUTH_PASSWORD"])
        self.assertEqual(value7, result["ODOO_QUEUE_JOB_JOBRUNNER_DB_HOST"])
        self.assertEqual(value8, result["ODOO_QUEUE_JOB_JOBRUNNER_DB_PORT"])

    def test_priority(self):
        value1 = "1"
        value2 = "2"
        value3 = "3"
        value4 = "4"
        value5 = "5"
        value6 = "6"
        value7 = "7"
        value8 = "8"
        to_map = {
            "ODOO_QUEUE_JOB_ENABLE": "True",
            "ODOO_CONNECTOR_CHANNELS": value1,
            "ODOO_CONNECTOR_SCHEME": value2,
            "ODOO_CONNECTOR_HOST": value3,
            "ODOO_CONNECTOR_PORT": value4,
            "ODOO_CONNECTOR_HTTP_AUTH_USER": value5,
            "ODOO_CONNECTOR_HTTP_AUTH_PASSWORD": value6,
            "ODOO_CONNECTOR_JOBRUNNER_DB_HOST": value7,
            "ODOO_CONNECTOR_JOBRUNNER_DB_PORT": value8,
        }
        result = queue_job(api.Env(to_map))
        self.assertEqual(18, len(result.keys()))
        self.assertEqual(value1, result["QUEUE_JOB_CHANNELS"])
        self.assertEqual(value2, result["QUEUE_JOB_SCHEME"])
        self.assertEqual(value3, result["QUEUE_JOB_HOST"])
        self.assertEqual(value4, result["QUEUE_JOB_PORT"])
        self.assertEqual(value5, result["QUEUE_JOB_HTTP_AUTH_USER"])
        self.assertEqual(value6, result["QUEUE_JOB_HTTP_AUTH_PASSWORD"])
        self.assertEqual(value7, result["QUEUE_JOB_JOBRUNNER_DB_HOST"])
        self.assertEqual(value8, result["QUEUE_JOB_JOBRUNNER_DB_PORT"])
