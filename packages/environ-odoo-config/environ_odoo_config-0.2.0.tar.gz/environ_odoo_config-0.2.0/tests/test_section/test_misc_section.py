import unittest
from pathlib import Path

from src.environ_odoo_config.api import Env
from src.environ_odoo_config.converters.misc import ConfigConverterMisc


class TestConfigConverterMisc(unittest.TestCase):
    def test_default(self):
        conf = ConfigConverterMisc()
        self.assertFalse(conf.unaccent)
        self.assertFalse(conf.without_demo)
        self.assertFalse(conf.stop_after_init)
        self.assertFalse(conf.save_config_file)

        flags = conf.to_values()
        self.assertFalse(flags)

    def test_global(self):
        conf = ConfigConverterMisc().init(
            Env(
                {
                    "UNACCENT": str(True),
                    "WITHOUT_DEMO": "all,account",
                    "STOP_AFTER_INIT": str(True),
                    "SAVE_CONFIG_FILE": str(True),
                    "DATA_DIR": "data",
                }
            )
        )
        self.assertTrue(conf.unaccent)
        self.assertEqual({"all", "account"}, conf.without_demo)
        self.assertTrue(conf.stop_after_init)
        self.assertTrue(conf.save_config_file)

        flags = conf.to_values()
        self.assertIn("--unaccent", flags)
        self.assertTrue(flags["--unaccent"])

        self.assertIn("--without-demo", flags)
        self.assertEqual({"all", "account"}, flags["--without-demo"])

        self.assertIn("--save", flags)
        self.assertTrue(flags["--save"])

        self.assertIn("--stop-after-init", flags)
        self.assertTrue(flags["--stop-after-init"])

        self.assertIn("--data-dir", flags)
        self.assertEqual(flags["--data-dir"], Path("data"))

    def test_datadir_sub_ODOO_PATH(self):
        conf = ConfigConverterMisc().init(
            Env(
                {
                    "ODOO_PATH": "/odoo",
                    "DATA_DIR": "data",
                }
            )
        )
        self.assertEqual(conf.data_dir, Path("/odoo/data"))
        flags = conf.to_values()
        self.assertIn("--data-dir", flags)
        self.assertEqual(flags["--data-dir"], Path("/odoo/data"))

    def test_without_demo_FALSE(self):
        conf = ConfigConverterMisc().init(
            Env(
                {
                    "WITHOUT_DEMO": "False",
                }
            )
        )
        self.assertFalse(conf.without_demo)
        flags = conf.to_values()
        self.assertNotIn("--without-demo", flags)

    def test_without_demo_True(self):
        """
        Env WITHOUT_DEMO=True handle as --without-demo=all
        Returns:

        """
        conf = ConfigConverterMisc().init(
            Env(
                {
                    "WITHOUT_DEMO": "True",
                }
            )
        )
        self.assertSetEqual({"all"}, conf.without_demo)
        flags = conf.to_values()
        self.assertIn("--without-demo", flags)
        self.assertSetEqual({"all"}, flags["--without-demo"])
