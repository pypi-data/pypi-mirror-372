# -*- coding: utf8 -*-
import unittest

from src.environ_odoo_config import api
from src.environ_odoo_config.mappers import oenv2config_compatibility as compatibility

NB_KEY_MAPPED = 12
class TestOdooCompatibilityMapper(unittest.TestCase):
    def test_empty(self):
        result = compatibility(api.Env())
        self.assertEqual(NB_KEY_MAPPED, len(result.keys()))
        for key_result, value in result.items():
            self.assertIsNone(value, "Value of key [%s] is not None" % key_result)

    def test_not_change(self):
        to_map = {
            "WORKER_HTTP": "2",
            "WORKERS": "3",
        }
        result = compatibility(api.Env(to_map))
        self.assertEqual(NB_KEY_MAPPED + 1, len(result.keys()))
        self.assertEqual("2", result["WORKER_HTTP"])
        self.assertIsNone(result["WORKER_CRON"])
        self.assertIsNone(result["HTTP_INTERFACE"])
        self.assertIsNone(result["HTTP_PORT"])
        self.assertIsNone(result["HTTP_ENABLE"])
        self.assertIsNone(result["SERVER_WIDE_MODULES"])

    def test_workers_in_worker_http(self):
        value = "2"
        to_map = {
            "WORKER_HTTP": value,
            # "WORKERS": value,
        }
        result = compatibility(api.Env(to_map))
        self.assertEqual(NB_KEY_MAPPED, len(result.keys()))
        self.assertEqual(value, result["WORKER_HTTP"])
        self.assertIsNone(result["WORKER_CRON"])
        self.assertIsNone(result["HTTP_INTERFACE"])
        self.assertIsNone(result["HTTP_PORT"])
        self.assertIsNone(result["HTTP_ENABLE"])
        self.assertIsNone(result["SERVER_WIDE_MODULES"])

    def test_worker_http_in_workers(self):
        value = "3"
        to_map = {
            # "WORKER_HTTP": value,
            "WORKERS": value,
        }
        result = compatibility(api.Env(to_map))
        self.assertEqual(NB_KEY_MAPPED + 1, len(result.keys()))
        self.assertEqual(value, result["WORKER_HTTP"])
        self.assertIsNone(result["WORKER_CRON"])
        self.assertIsNone(result["HTTP_INTERFACE"])
        self.assertIsNone(result["HTTP_PORT"])
        self.assertIsNone(result["HTTP_ENABLE"])
        self.assertIsNone(result["SERVER_WIDE_MODULES"])

    def test_gevent_port(self):
        result = compatibility(api.Env({
            "GEVENT_PORT": "7894",
            "LONGPOLLING_PORT": "1234",
        }))
        self.assertEqual(result["LONGPOLLING_PORT"], "1234")
        result = compatibility(api.Env({
            "LONGPOLLING_PORT": "1234",
        }))
        self.assertEqual(result["LONGPOLLING_PORT"], "1234")
        self.assertEqual(result["GEVENT_PORT"], "1234")
        result = compatibility(api.Env({
            "GEVENT_PORT": "1234",
        }))
        self.assertEqual(result["GEVENT_PORT"], "1234")
        self.assertTrue("LONGPOLLING_PORT" not in result)

    def test_server_wide_modules(self):
        value = "module"
        to_map = {
            # "WORKER_HTTP": value,
            "SERVER_WIDE_MODULES": value,
        }
        result = compatibility(api.Env(to_map))
        self.assertEqual(NB_KEY_MAPPED, len(result.keys()))
        self.assertEqual(value, result["SERVER_WIDE_MODULES"])
        self.assertIsNone(result["WORKER_HTTP"])
        self.assertIsNone(result["WORKER_CRON"])
        self.assertIsNone(result["HTTP_INTERFACE"])
        self.assertIsNone(result["HTTP_PORT"])
        self.assertIsNone(result["HTTP_ENABLE"])

        value = "module"
        to_map = {
            # "WORKER_HTTP": value,
            "LOAD": value,
        }
        result = compatibility(api.Env(to_map))
        self.assertEqual(NB_KEY_MAPPED+1, len(result.keys()))
        self.assertEqual(value, result["SERVER_WIDE_MODULES"])
        self.assertIsNone(result["WORKER_HTTP"])
        self.assertIsNone(result["WORKER_CRON"])
        self.assertIsNone(result["HTTP_INTERFACE"])
        self.assertIsNone(result["HTTP_PORT"])
        self.assertIsNone(result["HTTP_ENABLE"])

    def test_http_config_xmlrpc(self):
        HTTP_INTERFACE = "127.0.0.1"
        HTTP_PORT = "8080"
        HTTP_ENABLE = "True"
        LONGPOLLING_PORT = "4040"
        to_map = {
            "XMLRPC_INTERFACE": HTTP_INTERFACE,
            "XMLRPC_PORT": HTTP_PORT,
            "XMLRPC_ENABLE": HTTP_ENABLE,
            "LONGPOLLING_PORT": LONGPOLLING_PORT,
        }

        result = compatibility(api.Env(to_map))
        self.assertIsNone(result["WORKER_HTTP"])
        self.assertIsNone(result["WORKER_CRON"])
        self.assertEqual(HTTP_INTERFACE, result["HTTP_INTERFACE"])
        self.assertEqual(HTTP_PORT, result["HTTP_PORT"])
        self.assertEqual(HTTP_ENABLE, result["HTTP_ENABLE"])
        self.assertEqual(LONGPOLLING_PORT, result["LONGPOLLING_PORT"])
        self.assertIsNone(result["SERVER_WIDE_MODULES"])

    def test_http_config_http(self):
        HTTP_INTERFACE = "127.0.0.1"
        HTTP_PORT = "8080"
        HTTP_ENABLE = "True"
        LONGPOLLING_PORT = "4040"
        to_map = {
            "HTTP_INTERFACE": HTTP_INTERFACE,
            "HTTP_PORT": HTTP_PORT,
            "HTTP_ENABLE": HTTP_ENABLE,
            "LONGPOLLING_PORT": LONGPOLLING_PORT,
        }
        result = compatibility(api.Env(to_map))
        self.assertEqual(HTTP_INTERFACE, result["HTTP_INTERFACE"])
        self.assertEqual(HTTP_PORT, result["HTTP_PORT"])
        self.assertEqual(HTTP_ENABLE, result["HTTP_ENABLE"])
        self.assertEqual(LONGPOLLING_PORT, result["LONGPOLLING_PORT"])
        self.assertIsNone(result["SERVER_WIDE_MODULES"])

    def test_priority(self):
        HTTP_INTERFACE = "127.0.0.1"
        HTTP_PORT = "8080"
        HTTP_ENABLE = "True"
        to_map = {
            "WORKER_HTTP": "1",
            "WORKER_CRON": "2",
            "WORKER_JOB": "3",
            "WORKERS": "4",
            "HTTP_INTERFACE": HTTP_INTERFACE,
            "XMLRPC_INTERFACE": HTTP_INTERFACE + "_fake",
            "HTTP_PORT": HTTP_PORT,
            "XMLRPC_PORT": HTTP_PORT + "_fake",
            "HTTP_ENABLE": HTTP_ENABLE,
            "XMLRPC_ENABLE": HTTP_ENABLE + "_fake",
            "SERVER_WIDE_MODULES": "module",
            "LOAD": "module_fake",
        }
        result = compatibility(api.Env(to_map))
        self.assertEqual(HTTP_INTERFACE, result["HTTP_INTERFACE"])
        self.assertEqual(HTTP_PORT, result["HTTP_PORT"])
        self.assertEqual(HTTP_ENABLE, result["HTTP_ENABLE"])
        self.assertEqual("module", result["SERVER_WIDE_MODULES"])
        self.assertEqual("1", result["WORKER_HTTP"])
        self.assertEqual("2", result["WORKER_CRON"])
        self.assertEqual(
            "3", result["WORKER_JOB"], "WORKER_JOB prioritaire sur WORKERS"
        )
