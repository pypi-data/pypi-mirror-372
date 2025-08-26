from typing import Any, Set

from environ_odoo_config.api_converter import OdooConfigConverter, OnlyCli, RepeatableKey, SimpleKey


class ConfigConverterI18n(OdooConfigConverter):
    """
    convert environment variable related to the I18n configuration
    """

    _opt_group = "I18n Configuration"
    load_language: Set[str] = RepeatableKey()
    overwrite_existing_translations: bool = SimpleKey(
        "I18N_OVERRIDE",
        cli=["--i18n-overwrite"],
        info="overwrites existing translation terms on updating a module or importing a CSV or a PO file.",
    )
    _cli_i18n: Any = OnlyCli("--load-language", "-l", "--language", "--i18n-export", "--i18n-import", "--modules")
