from pathlib import Path

from typing_extensions import Set

from environ_odoo_config.api import OdooVersion
from environ_odoo_config.api_converter import NOT_INI_CONFIG, OdooConfigConverter, RepeatableKey


class ConfigConverterUpdateInit(OdooConfigConverter):
    """
    convert environment variable used to update or init modules
    """

    _opt_group = "Update or Install Configuration"
    install: Set[str] = RepeatableKey(
        "INSTALL", cli=["-i", "--init"], info="Install odoo modules.", ini_dest=NOT_INI_CONFIG
    )
    update: Set[str] = RepeatableKey(
        "UPDATE", cli=["-u", "--update"], info="Update odoo modules.", ini_dest=NOT_INI_CONFIG
    )
    upgrade_path: Set[Path] = RepeatableKey(
        "UPGRADE_PATH",
        cli="--upgrade-path",
        info="specify an additional upgrade path.",
        odoo_version=OdooVersion.V13.min(),
    )
    pre_upgrade_scripts: Set[Path] = RepeatableKey(
        "PRE_UPGRADE_SCRIPTS",
        cli="--pre-upgrade-scripts",
        odoo_version=OdooVersion.V16.min(),
        info="Run specific upgrade scripts before loading any module when -u is provided.",
    )
