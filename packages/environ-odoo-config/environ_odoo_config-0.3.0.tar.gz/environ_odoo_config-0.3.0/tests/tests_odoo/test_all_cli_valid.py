from __future__ import annotations

import logging
import optparse
import os
import unittest

from tests import _decorators
from environ_odoo_config.api import Env, OdooVersionRange, OdooVersion
from environ_odoo_config.api_converter import OnlyCli, NOT_INI_CONFIG
from environ_odoo_config.entry import AllOdooConfigConverter
try:
    from odoo.tools import config
except ImportError:
    config = None

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

@_decorators.SkipUnless.env_odoo
class TestAllCliValid(unittest.TestCase):
    def setUp(self):
        self.possible_keys = {}
        self.possible_dest = {}
        for group in config.parser.option_groups:
            for option in group.option_list:
                if option.help == optparse.SUPPRESS_HELP:
                    continue

                self.possible_keys[option.get_opt_string()] = option
                if option.dest not in config.blacklist_for_save:
                    self.possible_dest[option.dest] = option


    def test_all_cli_valid(self):
        current_version = Env(os.environ).odoo_version_type
        allconfig = AllOdooConfigConverter()
        not_exist = []
        _logger.info("======================================")
        for converter_type, converter_inst in allconfig.converters().items():
            for field_name, key in converter_type._private_fields().items():
                version_key = key.get_by_version(current_version)
                if not version_key:
                    _logger.info("%s : '%s#%s' not valid", current_version, converter_type, field_name)
                    continue
                cli_used = version_key.cli_used()
                if cli_used:
                    valid = self.possible_keys.pop(cli_used, False)
                    _logger.info("%s : Key '%s#%s' process -> %s", current_version, converter_type, field_name, cli_used)
                    if not valid:
                        not_exist.append(f"L'option cli '{cli_used}' n'existe pas dans la version {current_version}. {converter_type}#{field_name}")
                else:
                    _logger.info("%s : Key '%s#%s' no cli", current_version, converter_type, field_name)

                if version_key.ini_section == "options":
                    ini_dest = version_key.ini_dest
                    if ini_dest and ini_dest != NOT_INI_CONFIG:
                        valid = self.possible_dest.pop(ini_dest, False)
                        if not valid:
                            not_exist.append(f"L'option ini '{ini_dest}' n'existe pas dans la version {current_version}. {converter_type}#{field_name}")
                    else:
                        _logger.info("%s : Key '%s#%s' no ini_dest", current_version, converter_type, field_name)

        _logger.info("======================================")
        if OdooVersionRange(vmin=OdooVersion.V14, vmax=OdooVersion.V16).is_valid(current_version):
            # This options is a deprecated option, and odoo copy it to transient_age_limit
            self.possible_dest.pop("osv_memory_age_limit")
            self.possible_keys.pop("--osv-memory-age-limit")
        if OdooVersionRange(vmin=OdooVersion.V16, vmax=OdooVersion.V17).is_valid(current_version):
            # This options is a deprecated option, and odoo copy it to transient_age_limit
            self.possible_dest.pop("longpolling_port", None)
            self.possible_keys.pop("--longpolling-port")

        self.assertTrue(len(not_exist) == 0, msg="\n".join(not_exist))

        self.assertTrue(len(self.possible_dest) == 0, msg="\n".join(self.possible_dest.keys()))
        self.assertTrue(len(self.possible_keys) == 0, msg="\n".join(self.possible_keys.keys()))
