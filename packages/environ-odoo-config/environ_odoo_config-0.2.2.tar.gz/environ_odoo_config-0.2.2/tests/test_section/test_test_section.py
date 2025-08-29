from pathlib import Path

import unittest

from src.environ_odoo_config.api import Env
from src.environ_odoo_config.converters.test import ConfigConverterTest
from tests._decorators import MultiOdooVersion


class TestTestSection(unittest.TestCase):
    @MultiOdooVersion.without_args
    def test_default(self):
        conf = ConfigConverterTest()
        self.assertFalse(conf.test_enable)
        self.assertFalse(conf.test_enable_filled)
        self.assertFalse(conf.test_tags)
        self.assertIsNone(conf.test_file)

        flags = conf.to_values()
        self.assertFalse(flags)

    @MultiOdooVersion.with_args
    def test_version_disable(self, version: int):
        conf = ConfigConverterTest().init(
            Env(
                {
                    "ODOO_VERSION": str(version),
                    "TEST_ENABLE": str(True),
                    "TEST_TAGS": "test_tags_value",
                    "TEST_FILE": "test_file_value",
                }
            )
        )
        self.assertTrue(conf.test_enable)
        self.assertTrue(conf.test_enable_filled)
        self.assertEqual({"test_tags_value"}, conf.test_tags)
        self.assertEqual(Path("test_file_value"), conf.test_file)

    @MultiOdooVersion.with_args
    def test_odoo_test_tags(self, version: int):
        conf = ConfigConverterTest().init(
            Env(
                {
                    "ODOO_VERSION": str(version),
                    "TEST_ENABLE": str(True),
                    "TEST_TAGS": "test_tags_value0,test_tags_value2",
                    "TEST_TAGS_1": "test_tags_value1",
                    "TEST_TAGS_2": "test_tags_value2",
                    "TEST_FILE": "test_file_value",
                }
            )
        )
        flags = conf.to_values()

        self.assertTrue(conf.test_enable)
        self.assertTrue(conf.test_enable_filled)
        self.assertIn("--test-enable", flags)
        self.assertTrue(flags["--test-enable"])

        # test-tags not supported in Odoo 11 or less
        if version > 11:
            self.assertIn("--test-tags", flags)
            self.assertEqual({"test_tags_value0", "test_tags_value1", "test_tags_value2"}, flags["--test-tags"])
        else:
            self.assertNotIn("test-tags", flags)

        self.assertEqual(Path("test_file_value"), conf.test_file)
        self.assertIn("--test-file", flags)
        self.assertEqual(Path("test_file_value"), flags["--test-file"])
