from pathlib import Path

from typing_extensions import Any, Self, Set

from environ_odoo_config import utils
from environ_odoo_config.api import Env, OdooConfig
from environ_odoo_config.api_converter import NOT_INI_CONFIG, OdooConfigConverter, OnlyCli, RepeatableKey, SimpleKey
from environ_odoo_config.utils import csv_set_value


def csv_not_false(value) -> Set[str]:
    return {v for v in csv_set_value(value) if not (utils.is_boolean(v) and not utils.to_bool(value))}


def always_false(x: Any) -> bool:
    return False


class ConfigConverterMisc(OdooConfigConverter):
    _opt_group = "Misc Odoo Options"

    odoo_path: Path = SimpleKey("ODOO_PATH", ini_dest=NOT_INI_CONFIG)
    _config_file: Path = SimpleKey(
        "ODOO_RC", cli=["-c", "--config"], info="specify alternate config file", cli_use_filter=always_false
    )
    import_partial: bool = SimpleKey(
        "IMPORT_PARTIAL",
        cli=["-P", "--import-partial"],
        info="""Use this for big data importation, if it crashes you will be able to continue at the current state.
         Provide a filename to store intermediate importation states.""",
    )
    pidfile: Path = SimpleKey("PIDFILE", cli="--pidfile", info="file where the server pid will be stored")
    _pidfile_auto: bool = SimpleKey("PIDFILE", info="Auto set a pid file in `/tmp/odoo.pid` if the key equal `True`")

    unaccent: bool = SimpleKey(
        "UNACCENT", cli="--unaccent", info="Try to enable the unaccent extension when creating new databases."
    )
    without_demo: Set[str] = RepeatableKey(
        "WITHOUT_DEMO",
        cli="--without-demo",
        info="""disable loading demo data for modules to be installed (comma-separated, use "all" for all modules).
        Requires -d and -i. Default is %default""",
        csv_converter=csv_not_false,
    )
    without_demo_all: bool = SimpleKey(
        "WITHOUT_DEMO",
        # from_environ_value=lambda it: not utils.to_bool(it),
        info="""disable loading demo data for all modules if equal to true""",
        ini_dest=NOT_INI_CONFIG,
    )
    stop_after_init: bool = SimpleKey(
        "STOP_AFTER_INIT",
        cli="--stop-after-init",
        info="stop the server after its initialization",
        ini_dest=NOT_INI_CONFIG,
    )
    save_config_file: bool = SimpleKey(
        "SAVE_CONFIG_FILE", cli=["-s", "--save"], info="Save the generated config. Always True", ini_dest=NOT_INI_CONFIG
    )
    admin_password: str = SimpleKey(
        "ADMIN_PASSWORD", info="The Admin password for database management", ini_dest=NOT_INI_CONFIG
    )
    data_dir: Path = SimpleKey("DATA_DIR", cli=["-D", "--data-dir"], info="Directory where to store Odoo data")

    dev_mode: bool = OnlyCli("--dev", ini_dest=NOT_INI_CONFIG)
    shell_interface: str = OnlyCli("--shell-interface", ini_dest=NOT_INI_CONFIG)

    def init(self, curr_env: Env) -> Self:
        super().init(curr_env)
        if self.without_demo_all:
            # When WITHOUT_DEMO="True", then we set to `all`
            self.without_demo = {"all"}
        # if curr_env.is_boolean("WITHOUT_DEMO") and curr_env.get_bool("WITHOUT_DEMO"):

        # curr_env["WITHOUT_DEMO"] = "all"
        if self.odoo_path:
            self.data_dir = self.odoo_path / self.data_dir
        if self._pidfile_auto and not self.pidfile:
            self.pidfile = Path("/tmp/odoo.pid")
        return self

    def write_to_config(self, config: OdooConfig):
        if self.admin_password:
            config.set_admin_password(self.admin_password)
