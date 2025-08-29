from typing_extensions import Union

from environ_odoo_config.api import OdooCliFlag, OdooVersion, OdooVersionRange
from environ_odoo_config.api_converter import OdooConfigConverter, SimpleKey


class ConfigConverterHttp(OdooConfigConverter):
    """
    convert environment variable related to the Odoo Http configuration
    """

    _opt_group = "Http Configuration"

    http_enable: bool = SimpleKey(
        "HTTP_ENABLE",
        cli="--no-http",
        # cli_use_filter=negate_bool,
        info="Disable the HTTP and Longpolling services entirely",
        py_default=False,
        ini_default=True,
    )

    _http_enable_exist: bool = SimpleKey("HTTP_ENABLE")
    http_interface: str = SimpleKey(
        "HTTP_INTERFACE",
        cli="--http-interface",
        info="Listen interface address for HTTP services. Keep empty to listen on all interfaces (0.0.0.0)",
    )
    http_port: int = SimpleKey(
        "HTTP_PORT",
        cli="--http-port",
        info="Listen port for the main HTTP service. Keep empty to listen on all interfaces (0.0.0.0)",
    )
    proxy_mode: bool = SimpleKey(
        "PROXY_MODE",
        cli="--proxy-mode",
        info="""Activate reverse proxy WSGI wrappers (headers rewriting).
        Only enable this when running behind a trusted web proxy!""",
    )
    x_sendfile: bool = SimpleKey(
        "X_SENDFILE",
        cli="--x-sendfile",
        info="""Activate X-Sendfile (apache) and X-Accel-Redirect (nginx)
        HTTP response header to delegate the delivery of large
        files (assets/attachments) to the web server.""",
        odoo_version=OdooVersionRange(vmin=OdooVersion.V16),
    )

    @property
    def enable(self):
        return self.http_enable

    @enable.setter
    def enable(self, value):
        self.http_enable = value

    @property
    def interface(self) -> Union[str, None]:
        return self.http_interface or None

    @property
    def port(self):
        return self.http_port

    def to_values(self) -> OdooCliFlag:
        if not self.http_enable:
            return OdooCliFlag({"--no-http": True})
        return super().to_values()
