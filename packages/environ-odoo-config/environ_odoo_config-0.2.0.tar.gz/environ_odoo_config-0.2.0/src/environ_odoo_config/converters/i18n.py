from pathlib import Path

from environ_odoo_config.api_converter import NOT_INI_CONFIG, OdooConfigConverter, OnlyCli, SimpleKey


class ConfigConverterI18n(OdooConfigConverter):
    """
    convert environment variable related to the I18n configuration
    """

    _opt_group = "I18n Configuration"
    overwrite_existing_translations: bool = SimpleKey(
        "I18N_OVERRIDE",
        cli=["--i18n-overwrite"],
        info="overwrites existing translation terms on updating a module or importing a CSV or a PO file.",
    )
    load_language: str = OnlyCli(
        "--load-language",
        info="specifies the languages for the translations you want to be loaded",
        ini_dest=NOT_INI_CONFIG,
    )
    language: str = OnlyCli(
        "-l",
        "--language",
        info="specify the language of the translation file. Use it with --i18n-export or --i18n-import",
    )
    translate_out: Path = OnlyCli(
        "--i18n-export",
        info="export all sentences to be translated to a CSV file, a PO file or a TGZ archive and exit",
    )
    translate_in: Path = OnlyCli(
        "--i18n-import", info="import a CSV or a PO file with translations and exit. The '-l' option is required."
    )
    translate_modules: str = OnlyCli(
        "--modules", info="specify modules to export. Use in combination with --i18n-export"
    )
