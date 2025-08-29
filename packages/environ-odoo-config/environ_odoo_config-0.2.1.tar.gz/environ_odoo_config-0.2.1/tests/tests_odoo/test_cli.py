import unittest
from unittest.mock import patch

from tests import _decorators
try:
    from odoo.cli.command import commands
    from odoo.tools import config
    from odoo.addons import environ_odoo_config
except ImportError:
    commands = {}
    print("Odoo not installed")

@_decorators.SkipUnless.env_odoo
class TestOdooCommand(unittest.TestCase):
    def test_create(self):
        """
        Assert the class [cli.OdooCommand][cli.OdooCommand] is correct to make a new odoo command

        1. The name is env2config`
        2. Have 1 function names 'run'
        3. Is subclass of odoo.cli.Command in the test case `_FakeOdooCommand`

        """

        self.assertIn("oenv2config", commands)
        inst_clazz = commands["oenv2config"]
        self.assertTrue(hasattr(inst_clazz, "run"))

        self.assertIn("envconfig", commands)
        inst_clazz = commands["envconfig"]
        self.assertTrue(hasattr(inst_clazz, "run"))

        self.assertIn("generate-config", commands)
        inst_clazz = commands["generate-config"]
        self.assertTrue(hasattr(inst_clazz, "run"))

        self.assertIn("config_show", commands)
        inst_clazz = commands["config_show"]
        self.assertTrue(hasattr(inst_clazz, "run"))

    def test_runcommand1(self):
        """
        Assert the `run` function of the dynamic odoo.cli.Command call
        1. the save function of the config
        2. split the env parse in 2 step (env args then odoo args)
        """
        self.assertIn("envconfig", commands)
        inst_clazz = commands["envconfig"]()
        parser_args = [
            "--dest=/tmp/dest.ini",
        ]

        with patch.object(config, "save") as save_mock, patch.object(config, "_parse_config") as parse_args_mock:
            odoo_args = ["-d", "my_database"]
            inst_clazz.run(parser_args + odoo_args)

            self.assertEqual(1, save_mock.call_count)
            self.assertEqual(3, parse_args_mock.call_count, msg="1 for reset config, 1 for env to args, 1 for cli additional args")
            args, kwargs = parse_args_mock.call_args_list[0]
            self.assertEqual( tuple(), args)
            self.assertFalse(kwargs)
            # The first call depends of the current env, we can't assert it
            args, kwargs = parse_args_mock.call_args_list[2]
            self.assertEqual( (["-d", "my_database"],), args)
            self.assertFalse(kwargs)
