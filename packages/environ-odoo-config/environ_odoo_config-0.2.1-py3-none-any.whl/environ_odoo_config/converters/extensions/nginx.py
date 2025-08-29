from __future__ import annotations

from environ_odoo_config.api import Env
from environ_odoo_config.converters.extensions import ConfigConverterItems, OdooConfigConverterExtension
from environ_odoo_config.converters.gevent import ConfigConverterGevent
from environ_odoo_config.converters.http import ConfigConverterHttp


class NginxHttpExtension(OdooConfigConverterExtension):
    def apply(self, env: Env, full_config: ConfigConverterItems) -> None:
        if env.get_bool("ACTIVATE_NGINX"):
            full_config[ConfigConverterHttp].http_port = 8069
            full_config[ConfigConverterHttp].proxy_mode = True
            full_config[ConfigConverterHttp].http_interface = "127.0.0.1"
            full_config[ConfigConverterGevent].port = 8072
