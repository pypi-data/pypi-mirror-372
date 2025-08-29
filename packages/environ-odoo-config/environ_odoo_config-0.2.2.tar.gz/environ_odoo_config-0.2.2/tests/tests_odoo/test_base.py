import unittest

from tests import _decorators

from ._helpers import assertParser, create_config


class BaseCase:
    class OdooVersionTest(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.template_name = "template0"

        def test_db(self):
            parser = create_config()
            self.assertFalse(parser.getboolean("options", "db_host"))
            self.assertEqual(64, parser.getint("options", "db_maxconn"))
            self.assertFalse(parser.getboolean("options", "db_name"))
            self.assertFalse(parser.getboolean("options", "db_password"))
            self.assertFalse(parser.getboolean("options", "db_port"))
            self.assertEqual("prefer", parser.get("options", "db_sslmode"))
            self.assertEqual(self.template_name, parser.get("options", "db_template"))
            self.assertFalse(parser.getboolean("options", "db_user"))
            self.assertEqual("", parser.get("options", "dbfilter"))

        def test_db_default(self):
            parser = create_config()
            assertParser(
                self,
                parser,
                {
                    "db_host": False,
                    "db_maxconn": 64,
                    "db_name": False,
                    "db_password": False,
                    "db_port": False,
                    "db_sslmode": "prefer",
                    "db_template": self.template_name,
                    "db_user": False,
                    "dbfilter": "",
                },
            )

        def test_db_default15(self):
            parser = create_config()
            assertParser(
                self,
                parser,
                {
                    "db_host": False,
                    "db_maxconn": 64,
                    "db_name": False,
                    "db_password": False,
                    "db_port": False,
                    "db_sslmode": "prefer",
                    "db_template": self.template_name,
                    "db_user": False,
                    "dbfilter": "",
                },
            )

        def test_db_profile_clever(self):
            parser = create_config(["test_db_clever"])
            assertParser(
                self,
                parser,
                {
                    "db_host": "my_db_host",
                    "db_maxconn": 64,
                    "db_name": "my_db_name",
                    "db_password": "my_db_password",
                    "db_port": 1234,
                    "db_sslmode": "prefer",
                    "db_template": self.template_name,
                    "db_user": "my_db_user",
                    "dbfilter": "",
                },
            )

        def test_db_profile_clever_direct(self):
            parser = create_config(["test_db_clever_direct"])
            assertParser(
                self,
                parser,
                {
                    "db_host": "my_db_host_direct",
                    "db_maxconn": 64,
                    "db_name": "my_db_name_direct",
                    "db_password": "my_db_password_direct",
                    "db_port": 4567,
                    "db_sslmode": "prefer",
                    "db_template": self.template_name,
                    "db_user": "my_db_user_direct",
                    "dbfilter": "",
                },
            )

        def test_db_profile_clever_full_both(self):
            parser = create_config(["test_db_clever", "test_db_clever_direct"])
            assertParser(
                self,
                parser,
                {
                    "db_host": "my_db_host_direct",
                    "db_maxconn": 64,
                    "db_name": "my_db_name_direct",
                    "db_password": "my_db_password_direct",
                    "db_port": 4567,
                    "db_sslmode": "prefer",
                    "db_template": self.template_name,
                    "db_user": "my_db_user_direct",
                    "dbfilter": "",
                },
            )

        def test_runbot_classic_config(self):
            parser = create_config(["runbot_classic_before"])
            assertParser(
                self,
                parser,
                {
                    "db_host": "database",
                    "db_maxconn": 64,
                    "db_name": "databasehbkw",
                    "db_password": "ltniqmdrwo",
                    "db_port": 5432,
                    "db_sslmode": "prefer",
                    "db_template": self.template_name,
                    "db_user": "ddjwl",
                    "log_level": "debug",
                    "without_demo": "False",
                    "test_enable": "False",
                },
            )
            self.assertNotEqual("admin", parser.get("options", "admin_passwd"))
            self.assertTrue(
                parser.get("options", "admin_passwd").startswith("$pbkdf2-sha512$"),
                parser.get("options", "admin_passwd"),
            )


@_decorators.SkipUnless.env_odoo11
class BaseOdooVersionTest11(BaseCase.OdooVersionTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template_name = "template1"


@_decorators.SkipUnless.odoo_more11
class BaseOdooVersionTest12AndMore(BaseCase.OdooVersionTest): ...
