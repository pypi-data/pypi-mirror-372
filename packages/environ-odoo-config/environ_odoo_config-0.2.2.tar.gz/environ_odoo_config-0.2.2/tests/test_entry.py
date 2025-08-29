# -*- coding: utf8 -*-
import unittest
from ._decorators import SkipIf
from src.environ_odoo_config.api_converter import OdooConfigConverter
from src.environ_odoo_config import api, entry
from src.environ_odoo_config.converters.database import ConfigConverterDatabase


class TestOdooConfig(unittest.TestCase):

    @SkipIf.env_odoo
    def test_no_config(self):
        config = entry.env_to_odoo_args()
        self.assertIn(config, [['--load=web,base'], ['--load=base,web']])

    def test_args_database(self):
        db_host = "my-host.com"
        db_name = "my-db"
        db_port = str(5253)
        db_user = "my-user"
        db_password = "py-password"
        extra_env = {
            "POSTGRESQL_ADDON_DB": db_name,
            "POSTGRESQL_ADDON_HOST": db_host,
            "POSTGRESQL_ADDON_PORT": db_port,
            "POSTGRESQL_ADDON_USER": db_user,
            "POSTGRESQL_ADDON_PASSWORD": db_password,
        }
        args = entry.env_to_odoo_args(extra_env)
        wanted = {
                "--db_host=" + db_host,
                "--db_port=" + db_port,
                "--db_user=" + db_user,
                "--db_password=" + db_password,
                "--database=" + db_name,
            }
        self.assertSetEqual(set(args),wanted | set(args))

    def test_args_direct_database(self):
        """
        Assert Mapper for direct acces postgres provide by clevercloud
        """
        db_host = "my-host.com"
        db_name = "my-db"
        db_port = str(5253)
        db_user = "my-user"
        db_password = "py-password"
        extra_env = {
            "POSTGRESQL_ADDON_DB": db_name,
            "POSTGRESQL_ADDON_DIRECT_HOST": db_host,
            "POSTGRESQL_ADDON_DIRECT_PORT": db_port,
            "POSTGRESQL_ADDON_USER": db_user,
            "POSTGRESQL_ADDON_PASSWORD": db_password,
        }
        args = entry.env_to_odoo_args(extra_env)
        wanted = {
                "--db_host=" + db_host,
                "--db_port=" + db_port,
                "--db_user=" + db_user,
                "--db_password=" + db_password,
                "--database=" + db_name,
            }
        self.assertEqual(set(args),wanted | set(args))

    @SkipIf.env_odoo
    def test_env_to_dict_no_config(self):
        config = entry.env_to_dict()
        self.assertEqual({'--load': {'web', 'base'}}, config)

    def test_env_to_dict_db_config(self):
        db_host = "my-host.com"
        db_name = "my-db"
        db_port = 5253
        db_user = "my-user"
        db_password = "py-password"
        extra_env = {
            "POSTGRESQL_ADDON_DB": db_name,
            "POSTGRESQL_ADDON_HOST": db_host,
            "POSTGRESQL_ADDON_PORT": db_port,
            "POSTGRESQL_ADDON_USER": db_user,
            "POSTGRESQL_ADDON_PASSWORD": db_password,
        }
        dict_args = entry.env_to_dict(extra_env)
        self.assertEqual(
            dict_args,
            {
                **dict_args, **{
                "--db_host": db_host,
                "--db_port": db_port,
                "--db_user": db_user,
                "--db_password": db_password,
                "--database": db_name,
            }
             }
        )

    def test_env_to_section(self):
        db_host = "my-host.com"
        db_name = "my-db"
        db_port = 5253
        db_user = "my-user"
        db_password = "py-password"
        extra_env = {
            "POSTGRESQL_ADDON_DB": db_name,
            "POSTGRESQL_ADDON_HOST": db_host,
            "POSTGRESQL_ADDON_PORT": db_port,
            "POSTGRESQL_ADDON_USER": db_user,
            "POSTGRESQL_ADDON_PASSWORD": db_password,
            "LONGPOLLING_PORT": 8072,
        }
        result_section = ConfigConverterDatabase.new(extra_env)
        self.assertEqual(db_host, result_section.host)
        self.assertEqual(db_name, result_section.name)
        self.assertEqual(db_port, result_section.port)
        self.assertEqual(db_user, result_section.user)
        self.assertEqual(db_password, result_section.password)
        with self.assertRaises(AttributeError):
            result_section.longpolling_port

    def test_empty_env(self):
        result_section = ConfigConverterDatabase.new()
        self.assertIsNone(result_section.host)
        self.assertIsNone(result_section.name)
        self.assertFalse(result_section.port)
        self.assertIsNone(result_section.user)
        self.assertIsNone(result_section.password)
        dict_args = entry.env_to_dict()
        self.assertFalse(result_section.to_values())
