from pathlib import Path

from typing_extensions import Set

from environ_odoo_config.api_converter import OdooConfigConverter, RepeatableKey


class ConfigConverterUpdateInit(OdooConfigConverter):
    """
    convert environment variable used to update or init modules
    """

    _opt_group = "Update or Install Configuration"
    install: Set[str] = RepeatableKey("INSTALL", cli=["-i", "--init"], info="Install odoo modules.")
    update: Set[str] = RepeatableKey("UPDATE", cli=["-u", "--update"], info="Update odoo modules.")
    upgrade_path: Set[Path] = RepeatableKey(
        "UPGRADE_PATH", cli="--upgrade-path", info="specify an additional upgrade path."
    )
    pre_upgrade_scripts: Set[Path] = RepeatableKey(
        "PRE_UPGRADE_SCRIPTS", info="Run specific upgrade scripts before loading any module when -u is provided."
    )
