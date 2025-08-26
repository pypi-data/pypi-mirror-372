import unittest
from pathlib import Path

from src.environ_odoo_config.api import Env
from src.environ_odoo_config.converters.addons_path import ConfigConverterAddonsPath
from tests._decorators import MultiOdooVersion


class TestDatabaseOdooConfigSection(unittest.TestCase):
    @MultiOdooVersion.without_args
    def test_default(self):
        conf = ConfigConverterAddonsPath()
        self.assertFalse(conf.addons_path)
        flags = conf.to_values()
        self.assertFalse(flags)

    @MultiOdooVersion.with_args
    def test_global(self, version):
        conf = ConfigConverterAddonsPath().init(
            Env(
                {
                    "ODOO_VERSION": str(version),
                    "ADDONS_GIT_DEFAULT_SERVER": "github.com",
                    "ADDONS_GIT_MODULE_1": "my_module",
                    "ADDONS_LOCAL_RELATIVE_MODULE_2": "path/to/module",
                    "ADDONS_LOCAL_RELATIVE_MODULE_2_BASE_PATH": "/base/relative",
                    "ADDONS_LOCAL_ABS_PATH_MODULE_3": "/path/to/module3",
                }
            )
        )
        flags = conf.to_values()
        self.assertIn("--addons-path", flags)
        self.assertEqual(3, len(conf.addons_path))
        self.assertIn(Path("/odoo/addons/my_module"), flags["--addons-path"])
        self.assertIn(Path("/base/relative/path/to/module"), flags["--addons-path"])
        self.assertIn(Path("/path/to/module3"), flags["--addons-path"])
