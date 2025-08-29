import unittest

from src.environ_odoo_config.api import Env, OdooCliFlag
from src.environ_odoo_config.converters.database import (
    ConfigConverterDatabase,
    MaxConnMode,
)


class TestDatabaseOdooConfigSection(unittest.TestCase):
    def test_default(self):
        conf = ConfigConverterDatabase()
        self.assertIsNone(conf.name)
        self.assertIsNone(conf.host)
        self.assertEqual(0, conf.max_conn)
        self.assertIsNone(conf.filter)
        self.assertIsNone(conf.user)
        self.assertEqual(0, conf.port)
        self.assertIsNone(conf.password)
        self.assertTrue(conf.show)

    def test_global(self):
        conf = ConfigConverterDatabase().init(
            Env(
                {
                    "DB_FILTER": "db_filter.*",
                    "DB_NAME": "db_name",
                    "DB_HOST": "db_host",
                    "DB_MAX_CONN": "20",
                    "DB_PORT": "1234",
                    "DB_USER": "db_user",
                    "DB_PASSWORD": "db_password",
                    "LIST_DB": "True",
                }
            )
        )
        self.assertEqual("db_filter.*", conf.filter)
        self.assertEqual("db_host", conf.host)
        self.assertEqual(20, conf.max_conn)
        self.assertEqual("db_name", conf.name)
        self.assertEqual("db_user", conf.user)
        self.assertEqual(1234, conf.port)
        self.assertEqual("db_password", conf.password)
        self.assertTrue(conf.show)

    def test_db_name(self):
        """
        If a <DB_NAME> is filled and no  <DB_FILTER> then <DB_FILTER> is set to <DB_NAME>
        and DatabaseOdooConfigSection#show is set to false
        """
        conf = ConfigConverterDatabase().init(
            Env(
                {
                    "DB_NAME": "db_name",
                }
            )
        )
        self.assertEqual("db_name", conf.name)
        self.assertIsNone(conf.filter)
        self.assertTrue(conf.show)

        self.assertIsNone(conf.host)
        self.assertIsNone(conf.user)
        self.assertEqual(0, conf.port)
        self.assertIsNone(conf.password)
        self.assertEqual(0, conf.max_conn)

    def test_db_filter(self):
        """
        If <DB_FILTER> is set but no <DB_NAME> then :
        - DatabaseOdooConfigSection#name is None
        - DatabaseOdooConfigSection#show is True
        """
        conf = ConfigConverterDatabase().init(
            Env(
                {
                    "DB_FILTER": "db_filter.*",
                }
            )
        )
        self.assertEqual("db_filter.*", conf.filter)
        self.assertTrue(conf.show)
        self.assertIsNone(conf.name)

        self.assertIsNone(conf.host)
        self.assertIsNone(conf.user)
        self.assertEqual(0, conf.port)
        self.assertIsNone(conf.password)
        self.assertEqual(0, conf.max_conn)

    def test_db_name_with_show(self):
        """
        If <DB_NAME> is set but no <DB_FILTER> and <SHOW_DB> then:
        - DatabaseOdooConfigSection#name eq <DB_NAME>
        - DatabaseOdooConfigSection#filter eq <DB_NAME> + '.*'
        - DatabaseOdooConfigSection#show is True
        """
        conf = ConfigConverterDatabase().init(
            Env(
                {
                    "DB_NAME": "db_name",
                    "LIST_DB": "True",
                }
            )
        )
        self.assertEqual("db_name", conf.name)
        self.assertIsNone(conf.filter)
        self.assertTrue(conf.show)

        self.assertIsNone(conf.host)
        self.assertIsNone(conf.user)
        self.assertEqual(0, conf.port)
        self.assertIsNone(conf.password)
        self.assertEqual(0, conf.max_conn)

    def test_max_con_auto(self):
        """
        By default there 3 workers
        If <DB_MAX_CONN_MODE> is set to "AUTO" and a <DB_MAX_CONN> is provided then:
        if <DB_MAX_CONN> superior to AUTO computed value
        - DatabaseOdooConfigSection#max_conn eq <DB_MAX_CONN>
        """
        conf = ConfigConverterDatabase().init(
            Env(
                {
                    "DB_MAX_CONN_MODE": MaxConnMode.AUTO.value,
                    "DB_MAX_CONN": 100,
                }
            )
        )
        self.assertEqual(100, conf.max_conn)

        self.assertIsNone(conf.filter)
        self.assertIsNone(conf.name)
        self.assertIsNone(conf.host)
        self.assertIsNone(conf.user)
        self.assertEqual(0, conf.port)
        self.assertIsNone(conf.password)
        self.assertTrue(conf.show)

    def test_max_con_auto_workers(self):
        """
        If <DB_MAX_CONN_MODE> is set to "AUTO" then:
        - DatabaseOdooConfigSection#max_conn eq (nb workers total) + (nb workers total) // 2

        We don't care of <DB_MAX_CONN>
        """
        conf = ConfigConverterDatabase().init(
            Env(
                {
                    "DB_MAX_CONN_MODE": MaxConnMode.AUTO.value,
                    "WORKER_HTTP": str(100),
                    "DB_MAX_CONN": str(20),
                }
            )
        )
        # 100 + 2 (cron) + 102 // 2 => 150
        self.assertEqual(150, conf.max_conn)

        self.assertIsNone(conf.filter)
        self.assertIsNone(conf.name)
        self.assertIsNone(conf.host)
        self.assertIsNone(conf.user)
        self.assertEqual(0, conf.port)
        self.assertIsNone(conf.password)
        self.assertTrue(conf.show)

    def test_max_con_fixed_with_vaue(self):
        """
         By default there 3 workers
         If <DB_MAX_CONN_MODE> is set to "AUTO" then:
         - DatabaseOdooConfigSection#max_conn eq (nb workers total) + (nb workers total) divide by 2

        We ensure the value of <DB_MAX_CONN> is taken
        """
        conf = ConfigConverterDatabase().init(
            Env(
                {
                    "DB_MAX_CONN_MODE": MaxConnMode.FIXED.value,
                    "DB_MAX_CONN": 100,
                }
            )
        )
        self.assertEqual(100, conf.max_conn)

        self.assertIsNone(conf.filter)
        self.assertIsNone(conf.name)
        self.assertIsNone(conf.host)
        self.assertIsNone(conf.user)
        self.assertEqual(0, conf.port)
        self.assertIsNone(conf.password)
        self.assertTrue(conf.show)

    def test_max_con_fixed_with_less_than_required(self):
        conf = ConfigConverterDatabase().init(
            Env(
                {
                    "DB_MAX_CONN_MODE": MaxConnMode.FIXED.value,
                    "DB_MAX_CONN": 20,
                    "WORKER_HTTP": 15,
                }
            )
        )
        self.assertEqual(20, conf.max_conn)

        self.assertIsNone(conf.filter)
        self.assertIsNone(conf.name)
        self.assertIsNone(conf.host)
        self.assertIsNone(conf.user)
        self.assertEqual(0, conf.port)
        self.assertIsNone(conf.password)
        self.assertTrue(conf.show)

    def test_max_con_fixed_no_value(self):
        """
        By default there 3 workers
        If <DB_MAX_CONN_MODE> is set to "FIXED" then:
        - DatabaseOdooConfigSection#max_conn eq <DB_MAX_CONN>>

        In this test we don't have <DB_MAX_CONN> so we ensure the system switch back to auto
        """
        conf = ConfigConverterDatabase().init(
            Env(
                {
                    "DB_MAX_CONN_MODE": MaxConnMode.FIXED.value,
                }
            )
        )
        self.assertEqual(0, conf.max_conn)

        self.assertIsNone(conf.filter)
        self.assertIsNone(conf.name)
        self.assertIsNone(conf.host)
        self.assertIsNone(conf.user)
        self.assertEqual(0, conf.port)
        self.assertIsNone(conf.password)
        self.assertTrue(conf.show)
