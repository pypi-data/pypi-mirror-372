import os
import unittest
from typing import TYPE_CHECKING
from unittest.mock import patch

from environ_odoo_config.converters.http import ConfigConverterHttp
from environ_odoo_config.entry import AllOdooConfigConverter
from environ_odoo_config.api import Env
from environ_odoo_config.converters.extensions import OdooConfigConverterExtension, ConfigConverterItems



class HttpConverterForce(OdooConfigConverterExtension):

    def apply(self, env:Env, full_config: ConfigConverterItems) -> None:
        full_config[ConfigConverterHttp].http_enable = False
        full_config[ConfigConverterHttp].http_port = 8080
        full_config[ConfigConverterHttp].http_interface = "127.0.0.1"


class TestExtensionConverter(unittest.TestCase):

    def test_without_extension(self):
        converter = ConfigConverterHttp.new({
            "HTTP_ENABLE": "True",
            "HTTP_INTERFACE": "0.0.0.0",
            "HTTP_PORT": "8080",
        })
        self.assertEqual(8080, converter.http_port)
        self.assertEqual("0.0.0.0", converter.http_interface)
        self.assertEqual(True, converter.http_enable)

    def test_true(self):
        converter = AllOdooConfigConverter({
            "HTTP_ENABLE": "False",
        })
        HttpConverterForce().apply(converter.env, converter)
        self.assertEqual(8080, converter[ConfigConverterHttp].http_port)
        self.assertEqual("127.0.0.1", converter[ConfigConverterHttp].http_interface)
        self.assertEqual(False, converter[ConfigConverterHttp].http_enable)

    def test_false2(self):
        converter = AllOdooConfigConverter({
            "HTTP_ENABLE": "False",
            "FORCE_ENABLE_HTTP": "False"
        })
        HttpConverterForce().apply(converter.env, converter)
        self.assertEqual(8080, converter[ConfigConverterHttp].http_port)
        self.assertEqual("127.0.0.1", converter[ConfigConverterHttp].http_interface)
        self.assertEqual(False, converter[ConfigConverterHttp].http_enable)

class TestNginxExtension(unittest.TestCase):

    def setUp(self):
        self.config = {
            "HTTP_ENABLE": "True",
            "HTTP_INTERFACE": "0.0.0.0",
            "HTTP_PORT": "8080",
            "PROXY_MODE": "False"
        }

    def test_no_activate_nginx(self):
        converter = AllOdooConfigConverter(self.config)
        self.assertEqual(8080, converter[ConfigConverterHttp].http_port)
        self.assertEqual("0.0.0.0", converter[ConfigConverterHttp].http_interface)
        self.assertEqual(True, converter[ConfigConverterHttp].http_enable)
        self.assertEqual(False, converter[ConfigConverterHttp].proxy_mode)

    def test_activate_nginx(self):
        converter = AllOdooConfigConverter({**self.config, **{"ACTIVATE_NGINX": "True"}})
        self.assertEqual(8069, converter[ConfigConverterHttp].http_port)
        self.assertEqual("127.0.0.1", converter[ConfigConverterHttp].http_interface)
        self.assertEqual(True, converter[ConfigConverterHttp].http_enable)
        self.assertEqual(True, converter[ConfigConverterHttp].proxy_mode)

    @patch.dict(os.environ, {"ODOO_ENV2CONFIG_EXCLUDE_CONVERTER_EXTENSIONS": "nginx_ext"})
    def test_activate_nginx_exclude(self):
        converter = AllOdooConfigConverter({**self.config, **{"ACTIVATE_NGINX": "True"}})
        self.assertEqual(8080, converter[ConfigConverterHttp].http_port)
        self.assertEqual("0.0.0.0", converter[ConfigConverterHttp].http_interface)
        self.assertEqual(True, converter[ConfigConverterHttp].http_enable)
        self.assertEqual(False, converter[ConfigConverterHttp].proxy_mode)
