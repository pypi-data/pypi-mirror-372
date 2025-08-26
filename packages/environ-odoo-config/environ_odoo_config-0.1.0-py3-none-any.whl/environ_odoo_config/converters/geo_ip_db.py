from pathlib import Path

from environ_odoo_config.api_converter import OdooConfigConverter, SimpleKey


class ConfigConverterGeoIPDb(OdooConfigConverter):
    """
    convert environment variable related to the Odoo Geo IP configuration
    """

    _opt_group = "Geo IP Database Configuration"
    geoip_city_db: Path = SimpleKey(
        "GEOIP_CITY_DB", cli="--geoip-db", info="Absolute path to the GeoIP City database file."
    )
    geoip_country_db: Path = SimpleKey(
        "GEOIP_COUNTRY_DB", cli="--geoip-country-db", info="Absolute path to the GeoIP Country database file."
    )
