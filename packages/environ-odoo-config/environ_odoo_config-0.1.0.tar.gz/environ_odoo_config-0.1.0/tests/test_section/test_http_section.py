import unittest

from src.environ_odoo_config.api import Env, OdooCliFlag
from src.environ_odoo_config.converters.http import ConfigConverterHttp


class TestHttpOdooConfigSection(unittest.TestCase):
    def test_default(self):
        conf = ConfigConverterHttp()
        self.assertEqual(OdooCliFlag({"--no-http": True}), conf.to_values())
        self.assertIsNone(conf.interface)
        self.assertEqual(0, conf.port)
        self.assertFalse(conf.enable)
        self.assertEqual(0, conf.longpolling_port)

    def test_disable(self):
        conf = ConfigConverterHttp()
        conf.enable = True
        self.assertEqual(OdooCliFlag(), conf.to_values())
        self.assertIsNone(conf.interface)
        self.assertEqual(0, conf.port)
        self.assertTrue(conf.enable)
        self.assertEqual(0, conf.longpolling_port)

    def test_global_http_key(self):
        conf = ConfigConverterHttp().init(
            Env(
                {
                    "GEVENT_PORT": "4040",
                    "HTTP_INTERFACE": "0.1.2.3",
                    "HTTP_PORT": "8080",
                    "HTTP_ENABLE": "True",
                }
            )
        )
        self.assertEqual("0.1.2.3", conf.interface)
        self.assertEqual(8080, conf.port)
        self.assertTrue(conf.enable)
        self.assertEqual(4040, conf.longpolling_port)
        self.assertDictEqual(
            OdooCliFlag(
                {
                    "--gevent-port": 4040,
                    "--http-port": 8080,
                    "--http-interface": "0.1.2.3",
                }
            ),
            conf.to_values(),
        )

    def test_enable(self):
        conf = ConfigConverterHttp().init(
            Env(
                {
                    "HTTP_ENABLE": "True",
                }
            )
        )
        self.assertEqual(OdooCliFlag(), conf.to_values())
        self.assertIsNone(conf.interface)
        self.assertEqual(0, conf.port)
        self.assertTrue(conf.enable)
        self.assertEqual(0, conf.longpolling_port)
        conf = ConfigConverterHttp().init(
            Env(
                {
                    "HTTP_ENABLE": "False",
                }
            )
        )
        self.assertEqual(OdooCliFlag({"--no-http": True}), conf.to_values())
        self.assertIsNone(conf.interface)
        self.assertEqual(0, conf.port)
        self.assertFalse(conf.enable)
        self.assertEqual(0, conf.longpolling_port)

    def test_longpolling_port_before_v16(self):
        for odoo_version in range(11, 16):
            with self.subTest(odoo_version):
                conf = ConfigConverterHttp().init(
                    Env(
                        {
                            "ODOO_VERSION": odoo_version,
                            "GEVENT_PORT": "4040",
                            "HTTP_INTERFACE": "0.1.2.3",
                            "HTTP_PORT": "8080",
                            "HTTP_ENABLE": "True",
                        }
                    )
                )
                self.assertEqual("0.1.2.3", conf.interface)
                self.assertEqual(8080, conf.port)
                self.assertTrue(conf.enable)
                self.assertEqual(4040, conf.longpolling_port)
                self.assertDictEqual(
                    OdooCliFlag(
                        {
                            "--longpolling-port": 4040,
                            "--http-port": 8080,
                            "--http-interface": "0.1.2.3",
                        }
                    ),
                    conf.to_values(),
                )

    def test_gevent_key_v18(self):
        for odoo_version in range(16, 30):
            with self.subTest(odoo_version):
                conf = ConfigConverterHttp().init(
                    Env(
                        {
                            "ODOO_VERSION": odoo_version,
                            "GEVENT_PORT": "4040",
                            "HTTP_INTERFACE": "0.1.2.3",
                            "HTTP_PORT": "8080",
                            "HTTP_ENABLE": "True",
                        }
                    )
                )
                self.assertEqual("0.1.2.3", conf.interface)
                self.assertEqual(8080, conf.port)
                self.assertTrue(conf.enable)
                self.assertEqual(4040, conf.longpolling_port)
                self.assertDictEqual(
                    OdooCliFlag(
                        {
                            "--gevent-port": 4040,
                            "--http-port": 8080,
                            "--http-interface": "0.1.2.3",
                        }
                    ),
                    conf.to_values(),
                )
