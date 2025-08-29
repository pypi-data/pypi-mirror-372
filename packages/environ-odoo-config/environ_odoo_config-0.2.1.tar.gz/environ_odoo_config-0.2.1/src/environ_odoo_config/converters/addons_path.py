import logging
from pathlib import Path

from addons_installer import addons_installer
from typing_extensions import Self, Set

from environ_odoo_config.api import Env
from environ_odoo_config.api_converter import OdooConfigConverter, SimpleCSVKey

_logger = logging.getLogger(__name__)


class ConfigConverterAddonsPath(OdooConfigConverter):
    """
    convert environment variable using `ADDONS_GIT_` or `ADDONS_LOCAL_`
    """

    _opt_group = "Addons Path Configuration"

    addons_path: Set[Path] = SimpleCSVKey(
        cli="--addons-path", info="specify additional addons paths. Use ADDONS_GIT and ADDONS_LOCAL"
    )

    def init(self, curr_env: Env) -> Self:
        super().init(curr_env)
        results = addons_installer.AddonsFinder.parse_env(env_vars=curr_env)
        for result in results:
            path = Path(result.addons_path)
            subs = set(addons_installer.AddonsFinder.parse_submodule([result]))
            self.addons_path.update(map(lambda it: it.addons_path, subs))
            if (path / "EXCLUDE").exists():
                # EXCLUDE not exclude submodule discover
                # Only exclude this module from the addon-path
                _logger.info("Ignore %s with EXCLUDE file", result.addons_path)
                continue
            self.addons_path.add(Path(result.addons_path))
        return self
