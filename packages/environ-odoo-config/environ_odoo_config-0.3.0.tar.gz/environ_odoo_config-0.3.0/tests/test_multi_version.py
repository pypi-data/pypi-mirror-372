import unittest


from typing_extensions import Union
from environ_odoo_config.api import Env
from environ_odoo_config.api_converter import OnlyCli
from src.environ_odoo_config.api import OdooCliFlag, OdooVersion, OdooVersionRange
from src.environ_odoo_config.api_converter import OdooConfigConverter, SimpleKey


class _ConfigConverterForTest(OdooConfigConverter):
    var_to_assert: str = SimpleKey(
        "ENV_VAR_DEFAULT",
        cli="--cli-default",
        odoo_version=OdooVersionRange(vmin=OdooVersion.V18),
        other_version=[
            SimpleKey(
                "ENV_VAR_V12",
                cli="--cli-v12",
                odoo_version=OdooVersionRange(vmin=OdooVersion.V12),
                ini_dest="var_v12",
            ),
            SimpleKey(
                "ENV_VAR_V13",
                cli="--cli-v13",
                odoo_version=OdooVersionRange(vmin=OdooVersion.V13),
                ini_dest="var_v13",
            ),
            SimpleKey(
                "ENV_VAR_V14",
                cli="--cli-v14",
                odoo_version=OdooVersionRange(vmin=OdooVersion.V14),
                ini_dest="var_v14",
            ),
            SimpleKey(
                "ENV_VAR_V15",
                cli="--cli-v15",
                odoo_version=OdooVersionRange(vmin=OdooVersion.V15),
                ini_dest="var_v15",
            ),
            SimpleKey(
                "ENV_VAR_V16",
                odoo_version=OdooVersionRange(vmin=OdooVersion.V16),
                ini_dest="var_v16",
            ),
            OnlyCli("--cli-v17",
                odoo_version=OdooVersionRange(vmin=OdooVersion.V17),
            ),
        ],
        info="Listen port for the gevent (longpolling) worker.",
    )


class TestMultiVersionKey(unittest.TestCase):

    def test_default(self):
        self.skipTest("Not yet implemented")
        for odoo_version in [17, 18]:
            with self.subTest(odoo_version=odoo_version):
                env = Env({
                    "ODOO_VERSION": odoo_version,
                    "ENV_VAR_DEFAULT": "DEFAULT"
                })
                converter = _ConfigConverterForTest(env)
                self.assertEqual("DEFAULT", converter.var_to_assert)
