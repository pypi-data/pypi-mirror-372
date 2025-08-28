import unittest

from environ_odoo_config.converters.gevent import ConfigConverterGevent
from src.environ_odoo_config.api import Env, OdooCliFlag
from src.environ_odoo_config.converters.http import ConfigConverterHttp


class TestHttpOdooConfigSection(unittest.TestCase):
    def test_default(self):
        conf = ConfigConverterHttp()
        self.assertEqual(OdooCliFlag({"--no-http": True}), conf.to_values())
        self.assertIsNone(conf.interface)
        self.assertEqual(0, conf.port)
        self.assertFalse(conf.enable)
        conf = ConfigConverterGevent()
        self.assertEqual(0, conf.port)

    def test_disable(self):
        conf = ConfigConverterHttp()
        conf.enable = True
        self.assertEqual(OdooCliFlag(), conf.to_values())
        self.assertIsNone(conf.interface)
        self.assertEqual(0, conf.port)
        self.assertTrue(conf.enable)
        conf = ConfigConverterGevent()
        self.assertEqual(0, conf.longpolling_port)

    def test_global_http_key(self):
        env = Env(
            {
                "GEVENT_PORT": "4040",
                "HTTP_INTERFACE": "0.1.2.3",
                "HTTP_PORT": "8080",
                "HTTP_ENABLE": "True",
            }
        )
        gevent = env.get_converter(ConfigConverterGevent)
        http = env.get_converter(ConfigConverterHttp)
        self.assertEqual("0.1.2.3", http.interface)
        self.assertEqual(8080, http.port)
        self.assertTrue(http.enable)

        self.assertDictEqual(
            OdooCliFlag(
                {
                    "--http-port": 8080,
                    "--http-interface": "0.1.2.3",
                }
            ),
            http.to_values(),
        )

        self.assertEqual(4040, gevent.longpolling_port)
        self.assertDictEqual(
            OdooCliFlag(
                {
                    "--gevent-port": 4040,
                }
            ),
            gevent.to_values(),
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

    def test_longpolling_port_before_v16(self):
        for odoo_version in range(12, 16):
            with self.subTest(odoo_version):
                env = Env(
                    {
                        "ODOO_VERSION": odoo_version,
                        "GEVENT_PORT": "4040",
                        "HTTP_INTERFACE": "0.1.2.3",
                        "HTTP_PORT": "8080",
                        "HTTP_ENABLE": "True",
                    }
                ).apply_mapper()
                http = env.get_converter(ConfigConverterHttp)
                gevent = env.get_converter(ConfigConverterGevent)
                self.assertEqual("0.1.2.3", http.interface)
                self.assertEqual(8080, http.port)
                self.assertTrue(http.enable)
                self.assertEqual(4040, gevent.longpolling_port)
                self.assertDictEqual(
                    OdooCliFlag(
                        {
                            "--http-port": 8080,
                            "--http-interface": "0.1.2.3",
                        }
                    ),
                    http.to_values(),
                )
                self.assertDictEqual(
                    OdooCliFlag(
                        {
                            "--longpolling-port": 4040,
                        }
                    ),
                    gevent.to_values(),
                )

    def test_gevent_key_v18(self):
        for odoo_version in range(16, 30):
            with self.subTest(odoo_version):
                env = Env(
                    {
                        "ODOO_VERSION": odoo_version,
                        "GEVENT_PORT": "4040",
                        "HTTP_INTERFACE": "0.1.2.3",
                        "HTTP_PORT": "8080",
                        "HTTP_ENABLE": "True",
                    }
                )
                http = env.get_converter(ConfigConverterHttp)
                gevent = env.get_converter(ConfigConverterGevent)
                self.assertEqual("0.1.2.3", http.http_interface)
                self.assertEqual(4040, gevent.port)
                self.assertDictEqual(
                    OdooCliFlag(
                        {
                            "--http-port": 8080,
                            "--http-interface": "0.1.2.3",
                        }
                    ),
                    http.to_values(),
                )
                self.assertDictEqual(
                    OdooCliFlag(
                        {
                            "--gevent-port": 4040,
                        }
                    ),
                    gevent.to_values(),
                )
