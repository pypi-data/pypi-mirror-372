import unittest

from src.environ_odoo_config import api
from src.environ_odoo_config.mappers.session_redis import redis_session


class TestOdooQueueJobMapper(unittest.TestCase):
    def test_empty(self):
        result = redis_session(api.Env())
        self.assertEqual(6, len(result.keys()))
        for key_result, value in result.items():
            if key_result == "REDIS_SESSION_ENABLE":
                self.assertEqual("False", value)
                continue
            self.assertIsNone(value, "Value of key [%s] is not None" % key_result)

    def test_not_change(self):
        value1 = "1"
        value2 = "2"
        value3 = "3"
        value4 = "4"
        value5 = "5"
        to_map = {
            "REDIS_SESSION_ENABLE": str(True),
            "REDIS_SESSION_URL": value1,
            "REDIS_SESSION_HOST": value2,
            "REDIS_SESSION_PORT": value3,
            "REDIS_SESSION_DB_INDEX": value4,
            "REDIS_SESSION_PASSWORD": value5,
        }
        result = redis_session(api.Env(to_map))
        self.assertEqual(6, len(result.keys()))
        self.assertEqual("True", result["REDIS_SESSION_ENABLE"])
        self.assertEqual(value1, result["REDIS_SESSION_URL"])
        self.assertEqual(value2, result["REDIS_SESSION_HOST"])
        self.assertEqual(value3, result["REDIS_SESSION_PORT"])
        self.assertEqual(value4, result["REDIS_SESSION_DB_INDEX"])
        self.assertEqual(value5, result["REDIS_SESSION_PASSWORD"])

    def test_priority(self):
        value1 = "1"
        value2 = "2"
        value3 = "3"
        value4 = "4"
        value5 = "5"
        to_map = {
            "REDIS_SESSION_ENABLE": "True",
            "REDIS_URL": value1 + "_fake",
            "REDIS_HOST": value2 + "_fake",
            "REDIS_PORT": value3 + "_fake",
            "REDIS_DB_INDEX": value4 + "_fake",
            "REDIS_PASSWORD": value5 + "_fake",
            "REDIS_SESSION_URL": value1,
            "REDIS_SESSION_HOST": value2,
            "REDIS_SESSION_PORT": value3,
            "REDIS_SESSION_DB_INDEX": value4,
            "REDIS_SESSION_PASSWORD": value5,
        }
        result = redis_session(api.Env(to_map))
        self.assertEqual(11, len(result.keys()))
        self.assertEqual("True", result["REDIS_SESSION_ENABLE"])
        self.assertEqual(value1, result["REDIS_SESSION_URL"])
        self.assertEqual(value2, result["REDIS_SESSION_HOST"])
        self.assertEqual(value3, result["REDIS_SESSION_PORT"])
        self.assertEqual(value4, result["REDIS_SESSION_DB_INDEX"])
        self.assertEqual(value5, result["REDIS_SESSION_PASSWORD"])

    def test_second_value(self):
        value1 = "1"
        value2 = "2"
        value3 = "3"
        value4 = "4"
        value5 = "5"
        to_map = {
            "REDIS_SESSION_ENABLE": "True",
            "REDIS_URL": value1,
            "REDIS_HOST": value2,
            "REDIS_PORT": value3,
            "REDIS_DB_INDEX": value4,
            "REDIS_PASSWORD": value5,
        }
        result = redis_session(api.Env(to_map))
        self.assertEqual(11, len(result.keys()))
        self.assertEqual("True", result["REDIS_SESSION_ENABLE"])
        self.assertEqual(value1, result["REDIS_SESSION_URL"])
        self.assertEqual(value2, result["REDIS_SESSION_HOST"])
        self.assertEqual(value3, result["REDIS_SESSION_PORT"])
        self.assertEqual(value4, result["REDIS_SESSION_DB_INDEX"])
        self.assertEqual(value5, result["REDIS_SESSION_PASSWORD"])

    def test_not_enable(self):
        value1 = "1"
        value3 = "3"
        value4 = "4"
        value5 = "5"
        to_map = {
            "REDIS_URL": value1,
            "REDIS_SESSION_PORT": value3,
            "REDIS_SESSION_DB_INDEX": value4,
            "REDIS_SESSION_PASSWORD": value5,
        }
        result = redis_session(api.Env(to_map))
        self.assertEqual(7, len(result.keys()))
        self.assertEqual("False", result["REDIS_SESSION_ENABLE"])
