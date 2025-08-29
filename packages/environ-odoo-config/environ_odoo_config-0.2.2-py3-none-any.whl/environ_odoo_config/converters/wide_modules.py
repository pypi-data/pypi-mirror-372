import importlib_metadata as md
from typing_extensions import Callable, Dict, Self, Set

from environ_odoo_config.api import Env
from environ_odoo_config.api_converter import NOT_INI_CONFIG, OdooConfigConverter, RepeatableKey, SimpleCSVKey

EP_GROUP_NAME = "environ_odoo_config.server_wide_module"


def _auto_load_entry_point() -> Dict[str, Callable[[Env], bool]]:
    result: Dict[str, Callable[[Env], bool]] = {}
    for entry_point in md.entry_points().select(group="environ_odoo_config.server_wide_module"):
        result[entry_point.name] = entry_point.load()
    return result


def always_true(env: Env) -> bool:
    return True


class ConfigConverterServerWideModule(OdooConfigConverter):
    """
    convert environment variable related to the server_wide_module configuration
    """

    _opt_group = "Server wide module Configuration"
    __auto_load: Dict[set, Callable[[Env], bool]] = set()

    _legacy_load: Set[str] = SimpleCSVKey(
        "SERVER_WIDE_MODULES", info="old version of the list of the server-wide modules"
    )
    loads: Set[str] = RepeatableKey(
        "LOAD", cli=["--load"], ini_dest="server_wide_modules", info="list of server-wide modules."
    )
    exclude_auto_load: Set[str] = SimpleCSVKey(
        "ODOO_ENV2CONFIG_EXCLUDE_EP_LOAD",
        info="Allow to exclude auto loading server wide module",
        ini_dest=NOT_INI_CONFIG,
    )

    def init(self, env: Env) -> Self:
        super().init(env)
        for name, auto_load_callback in self.__auto_load.items():
            if name not in self.exclude_auto_load and auto_load_callback(env):
                self.loads.add(name)
        return self

    @property
    def server_wide_modules(self) -> Set[str]:
        return self._legacy_load | self.loads

    @classmethod
    def _post_load(cls):
        cls.__auto_load = _auto_load_entry_point()

    @staticmethod
    def __adoc__() -> str:
        return """
        """
