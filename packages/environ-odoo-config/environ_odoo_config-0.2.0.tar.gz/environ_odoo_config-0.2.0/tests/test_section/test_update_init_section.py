import unittest

from src.environ_odoo_config.api import Env
from src.environ_odoo_config.converters.update_init import ConfigConverterUpdateInit
from tests._decorators import MultiOdooVersion


class TestUpdateInitSection(unittest.TestCase):
    @MultiOdooVersion.without_args
    def test_default(self):
        conf = ConfigConverterUpdateInit()
        self.assertEqual(set(), conf.install)
        self.assertEqual(set(), conf.update)
        flags = conf.to_values()
        self.assertFalse(flags)

    @MultiOdooVersion.with_args
    def test_value(self, version: int):
        conf = ConfigConverterUpdateInit().init(
            Env(
                {
                    "ODOO_VERSION": str(version),
                    "INSTALL": " module1 , module2, module3 , module1 ",
                    "UPDATE": " module_a , module_b , module_c, module_b ",
                }
            )
        )
        flags = conf.to_values()

        self.assertSetEqual({"module1", "module2", "module3"}, conf.install)
        self.assertIn("--init", flags)
        self.assertSetEqual({"module1", "module2","module3"}, flags["--init"])

        self.assertSetEqual({"module_a", "module_b", "module_c"}, conf.update)
        self.assertIn("--update", flags)
        self.assertSetEqual({"module_a","module_b","module_c"}, flags["--update"])

    @MultiOdooVersion.with_args
    def test_value_repeat(self, version: int):
        conf = ConfigConverterUpdateInit().init(
            Env(
                {
                    "ODOO_VERSION": str(version),
                    "INSTALL": "module0, module3",
                    "INSTALL_MODULE1": "True",
                    "INSTALL_MODULE2": "module2",
                    "UPDATE": " module_a , module_b ,  ",
                    "UPDATE_MODULE_C": "module_c, module_b"
                }
            )
        )
        flags = conf.to_values()

        self.assertSetEqual({"module0", "module1", "module2", "module3"}, conf.install)
        self.assertIn("--init", flags)
        self.assertEqual({"module0", "module1", "module2", "module3"}, flags["--init"])

        self.assertSetEqual({"module_a", "module_b", "module_c"}, conf.update)
        self.assertIn("--update", flags)
        self.assertEqual({"module_a", "module_b", "module_c"}, flags["--update"])
