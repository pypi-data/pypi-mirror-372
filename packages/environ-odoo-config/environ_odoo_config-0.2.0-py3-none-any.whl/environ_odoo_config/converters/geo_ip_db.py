from pathlib import Path

from environ_odoo_config.api import OdooVersion, OdooVersionRange
from environ_odoo_config.api_converter import OdooConfigConverter, OnlyCli, SimpleKey


class ConfigConverterGeoIPDb(OdooConfigConverter):
    """
    convert environment variable related to the Odoo Geo IP configuration
    """

    _opt_group = "Geo IP Database Configuration"
    geoip_city_db: Path = SimpleKey(
        "GEOIP_CITY_DB",
        cli=["--geoip-city-db", "--geoip-db"],
        info="Absolute path to the GeoIP City database file.",
        odoo_version=OdooVersionRange(vmin=OdooVersion.V17),
        other_version=[OnlyCli("--geoip-db", ini_dest="geoip_database", odoo_version=OdooVersion.V16.max())],
    )
    geoip_country_db: Path = SimpleKey(
        "GEOIP_COUNTRY_DB",
        cli="--geoip-country-db",
        odoo_version=OdooVersionRange(vmin=OdooVersion.V17),
        info="Absolute path to the GeoIP Country database file.",
    )
