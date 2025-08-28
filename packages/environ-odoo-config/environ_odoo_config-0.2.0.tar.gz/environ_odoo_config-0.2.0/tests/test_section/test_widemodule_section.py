import unittest

from src.environ_odoo_config.api import Env, OdooCliFlag
from src.environ_odoo_config.converters.wide_modules import ConfigConverterServerWideModule

_base_web = {"base", "web"}

class TestHttpOdooConfigSection(unittest.TestCase):
    def test_default(self):
        conf = ConfigConverterServerWideModule()
        self.assertEqual(OdooCliFlag(), conf.to_values())
        self.assertSetEqual(set(), conf.server_wide_modules)

    def test_serer_wide_modules_key(self):
        conf = ConfigConverterServerWideModule().init(
            Env({"SERVER_WIDE_MODULES": "module1,module2"})
        )
        self.assertEqual({"module1", "module2"} | _base_web, conf.server_wide_modules)
        conf = ConfigConverterServerWideModule().init(
            Env({"SERVER_WIDE_MODULES": "module1,module2,module1,base"})
        )
        # Assert no duplicate module and order is keeped
        self.assertEqual({"module1", "module2", "base"} | _base_web, conf.server_wide_modules)

    def test_module_name(self):
        conf = ConfigConverterServerWideModule().init(
            Env(
                {
                    "LOAD_MODULE_A": str(True),
                    "LOAD_MODULE_0": str(1),
                    "LOAD_MODULE_1": str(False),
                    "LOAD_MODULE_2": str(0),
                }
            )
        )
        # Assert "True" or "1" is valid activate value, and the sort is alpha
        self.assertSetEqual({"module_a", "module_0"} | _base_web, conf.server_wide_modules)
        conf = ConfigConverterServerWideModule().init(
            Env(
                {
                    "LOAD_QUEUE_JOB": "my_custom_module",
                }
            )
        )
        self.assertSetEqual({"my_custom_module"} | _base_web, conf.server_wide_modules)
        conf = ConfigConverterServerWideModule().init(
            Env(
                {
                    "LOAD_aslkaskalds": "queue_job",
                }
            )
        )
        self.assertSetEqual({"queue_job"} | _base_web, conf.server_wide_modules)


    def test_serer_wide_modules_mix(self):
        conf = ConfigConverterServerWideModule().init(
            Env({
                "SERVER_WIDE_MODULES": "module1,module2",
                "LOAD_QUEUE_JOB": "my_custom_module",
                "LOAD_MODULE1": "True",
            })
        )
        self.assertEqual({"my_custom_module", "module1", "module2"} | _base_web, conf.server_wide_modules)
