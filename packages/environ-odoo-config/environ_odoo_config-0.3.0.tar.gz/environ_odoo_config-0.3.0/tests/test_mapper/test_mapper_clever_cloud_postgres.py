import unittest

from src.environ_odoo_config import api
from src.environ_odoo_config.mappers.cc_postgresql import clevercloud_postgresql


class TestCleverCloudMapperPostgres(unittest.TestCase):
    def _test_priority(self, key, to_map, expected, nb_key=6):
        result = clevercloud_postgresql(api.Env(to_map))
        self.assertEqual(nb_key, len(result.keys()))
        self.assertEqual(
            expected,
            result[key],
            "Value of key [%s] is not '%s' result : '%s'"
            % (key, expected, result[key]),
        )

    def test_no_value(self):
        result = clevercloud_postgresql(api.Env({}))
        self.assertEqual(5, len(result.keys()))
        self.assertIsNone(result["DB_NAME"])
        self.assertIsNone(result["DB_HOST"])
        self.assertIsNone(result["DB_PORT"])
        self.assertIsNone(result["DB_USER"])
        self.assertIsNone(result["DB_PASSWORD"])

    def test_postgres_addon(self):
        db_host = "my-host.com"
        db_name = "my-db"
        db_port = "my-port"
        db_user = "my-user"
        db_password = "py-password"

        result = clevercloud_postgresql(
            api.Env(
                {
                    "POSTGRESQL_ADDON_DB": db_name,
                    "POSTGRESQL_ADDON_HOST": db_host,
                    "POSTGRESQL_ADDON_PORT": db_port,
                    "POSTGRESQL_ADDON_USER": db_user,
                    "POSTGRESQL_ADDON_PASSWORD": db_password,
                }
            )
        )
        self.assertEqual(10, len(result.keys()))
        self.assertEqual(db_name, result["DB_NAME"])
        self.assertEqual(db_host, result["DB_HOST"])
        self.assertEqual(db_port, result["DB_PORT"])
        self.assertEqual(db_user, result["DB_USER"])
        self.assertEqual(db_password, result["DB_PASSWORD"])

    def test_postgres_addon_direct(self):
        """
        Chez Clever cloud les connections sont géré via un proxy,
        il reste possible via une option chez eux d'avoir un acces direct
        Dans ce cas les variables <POSTGRESQL_ADDON_DIRECT_PORT> et <POSTGRESQL_ADDON_DIRECT_HOST> sont disponibles.
        Les variables <POSTGRESQL_ADDON_DIRECT_DB>, <POSTGRESQL_ADDON_DIRECT_USER> et
         <POSTGRESQL_ADDON_DIRECT_PASSWORD> n'existent pas
        """

        db_host = "my-host.com"
        db_name = "my-db"
        db_port = "my-port"
        db_user = "my-user"
        db_password = "py-password"

        result = clevercloud_postgresql(
            api.Env(
                {
                    "POSTGRESQL_ADDON_DIRECT_DB": db_name,
                    "POSTGRESQL_ADDON_DIRECT_HOST": db_host,
                    "POSTGRESQL_ADDON_DIRECT_PORT": db_port,
                    "POSTGRESQL_ADDON_DIRECT_USER": db_user,
                    "POSTGRESQL_ADDON_DIRECT_PASSWORD": db_password,
                }
            )
        )
        self.assertEqual(10, len(result.keys()))
        self.assertIsNone(
            result["DB_NAME"],
            "POSTGRESQL_ADDON_DIRECT_DB n'est pas prise en compte par le mapper",
        )
        self.assertEqual(db_host, result["DB_HOST"])
        self.assertEqual(db_port, result["DB_PORT"])
        self.assertIsNone(
            result["DB_USER"],
            "POSTGRESQL_ADDON_DIRECT_USER n'est pas prise en compte par le mapper",
        )
        self.assertIsNone(
            result["DB_PASSWORD"],
            "POSTGRESQL_ADDON_DIRECT_PASSWORD n'est pas prise en compte par le mapper",
        )

    def test_postgres_addon_direct_priority(self):
        """
        Chez Clever cloud les connections sont géré via un proxy,
        il reste possible via une option chez eux d'avoir un acces direct
        Dans ce cas les variables <POSTGRESQL_ADDON_DIRECT_PORT> et <POSTGRESQL_ADDON_DIRECT_HOST> sont disponibles.
        Dans ce cas, elles doivent être prises en priorité par rapport
         à <POSTGRESQL_ADDON_PORT> et <POSTGRESQL_ADDON_HOST>
        """

        db_host = "my-host.com"
        db_port = "my-port"
        suffix = "_no_take"
        result = clevercloud_postgresql(
            api.Env(
                {
                    "POSTGRESQL_ADDON_DIRECT_HOST": db_host,
                    "POSTGRESQL_ADDON_HOST": db_host + suffix,
                    "POSTGRESQL_ADDON_DIRECT_PORT": db_port,
                    "POSTGRESQL_ADDON_PORT": db_port + suffix,
                }
            )
        )
        self.assertEqual(9, len(result.keys()))
        self.assertIsNone(result["DB_NAME"])
        self.assertEqual(db_host, result["DB_HOST"])
        self.assertEqual(db_port, result["DB_PORT"])
        self.assertIsNone(result["DB_USER"])
        self.assertIsNone(result["DB_PASSWORD"])

    def test_postgres_priority_global(self):
        db_host = "my-host.com"
        db_name = "my-db"
        db_port = "my-port"
        db_user = "my-user"
        db_password = "py-password"
        origin = "_no_take"
        result = clevercloud_postgresql(
            api.Env(
                {
                    "DB_NAME": db_name,
                    "POSTGRESQL_ADDON_DB": db_name + origin,
                    "DB_HOST": db_host,
                    "POSTGRESQL_ADDON_HOST": db_host + origin,
                    "DB_PORT": db_port,
                    "POSTGRESQL_ADDON_PORT": db_port + origin,
                    "DB_USER": db_user,
                    "POSTGRESQL_ADDON_USER": db_user + origin,
                    "DB_PASSWORD": db_password,
                    "POSTGRESQL_ADDON_PASSWORD": db_password + origin,
                }
            )
        )
        self.assertEqual(10, len(result.keys()))
        self.assertEqual(
            db_name,
            result["DB_NAME"],
            "DB_NAME est prioritaire sur POSTGRESQL_ADDON_DB",
        )
        self.assertEqual(
            db_host,
            result["DB_HOST"],
            "DB_HOST est prioritaire sur POSTGRESQL_ADDON_HOST",
        )
        self.assertEqual(
            db_port,
            result["DB_PORT"],
            "DB_PORT est prioritaire sur POSTGRESQL_ADDON_PORT",
        )
        self.assertEqual(
            db_user,
            result["DB_USER"],
            "DB_USER est prioritaire sur POSTGRESQL_ADDON_USER",
        )
        self.assertEqual(
            db_password,
            result["DB_PASSWORD"],
            "DB_PASSWORD est prioritaire sur POSTGRESQL_ADDON_PASSWORD",
        )

    def test_postgres_priority_db_name(self):
        """
        Test de la prise en compte des variables permettant de préciser le nom de la DB
        DB_NAME > POSTGRESQL_ADDON_DB > DATABASE
        """

        db_name = "my-db"
        db_name1 = "my-db1"
        db_name2 = "my-db2"
        self._test_priority(
            "DB_NAME",
            {
                "DATABASE": db_name,
                "DB_NAME": db_name1,
                "POSTGRESQL_ADDON_DB": db_name2,
            },
            db_name1,
            nb_key=7,
        )
        db_name2 = "my-db2"
        self._test_priority(
            "DB_NAME",
            {
                "DATABASE": db_name,
                # "DB_NAME": db_name1,
                "POSTGRESQL_ADDON_DB": db_name2,
            },
            db_name,
            nb_key=7,
        )
        self._test_priority(
            "DB_NAME",
            {
                # "DATABASE": db_name,
                # "DB_NAME": db_name1,
                "POSTGRESQL_ADDON_DB": db_name2,
            },
            db_name2,
        )

    def test_postgres_priority_db_host(self):
        """
        Test de la prise en compte des variables permetant de préciser l'url de la DB
        DB_HOST > POSTGRESQL_ADDON_DIRECT_HOST > POSTGRESQL_ADDON_HOST
        """

        db_value = "value"
        db_value1 = "value1"
        db_value2 = "value2"
        self._test_priority(
            "DB_HOST",
            {
                "DB_HOST": db_value,
                "POSTGRESQL_ADDON_DIRECT_HOST": db_value1,
                "POSTGRESQL_ADDON_HOST": db_value2,
            },
            db_value,
            nb_key=7,
        )
        self._test_priority(
            "DB_HOST",
            {
                # "DB_HOST": db_value,
                "POSTGRESQL_ADDON_DIRECT_HOST": db_value1,
                "POSTGRESQL_ADDON_HOST": db_value2,
            },
            db_value1,
            nb_key=7,
        )
        self._test_priority(
            "DB_HOST",
            {
                # "DB_HOST": db_value,
                # "POSTGRESQL_ADDON_DIRECT_HOST": db_value1,
                "POSTGRESQL_ADDON_HOST": db_value2,
            },
            db_value2,
        )

    def test_postgres_priority_db_port(self):
        """
        Test de la prise en compte des variables permettant de préciser le port de la DB
        DB_PORT > POSTGRESQL_ADDON_DIRECT_PORT > POSTGRESQL_ADDON_PORT
        """

        db_value = "value"
        db_value1 = "value1"
        db_value2 = "value2"
        self._test_priority(
            "DB_PORT",
            {
                "DB_PORT": db_value,
                "POSTGRESQL_ADDON_DIRECT_PORT": db_value1,
                "POSTGRESQL_ADDON_PORT": db_value2,
            },
            db_value,
            nb_key=7,
        )
        self._test_priority(
            "DB_PORT",
            {
                # "DB_PORT": db_value,
                "POSTGRESQL_ADDON_DIRECT_PORT": db_value1,
                "POSTGRESQL_ADDON_PORT": db_value2,
            },
            db_value1,
            nb_key=7,
        )
        self._test_priority(
            "DB_PORT",
            {
                # "DB_PORT": db_value,
                # "POSTGRESQL_ADDON_DIRECT_PORT": db_value1,
                "POSTGRESQL_ADDON_PORT": db_value2,
            },
            db_value2,
        )

    def test_postgres_priority_db_user(self):
        """
        Test de la prise en compte des variables permettant de préciser le nom de l'utilisateur postgres
        DB_USER > POSTGRESQL_ADDON_USER
        """

        db_value = "value"
        db_value1 = "value1"
        self._test_priority(
            "DB_USER",
            {
                "DB_USER": db_value,
                "POSTGRESQL_ADDON_USER": db_value1,
            },
            db_value,
        )
        self._test_priority(
            "DB_USER",
            {
                # "DB_USER": db_value,
                "POSTGRESQL_ADDON_USER": db_value1,
            },
            db_value1,
        )

    def test_postgres_priority_db_password(self):
        """
        Test de la prise en compte des variables permettant de préciser le nom de l'utilisateur postgres
        DB_PASSWORD > POSTGRESQL_ADDON_PASSWORD
        """

        db_value = "value"
        db_value1 = "value1"
        self._test_priority(
            "DB_PASSWORD",
            {
                "DB_PASSWORD": db_value,
                "POSTGRESQL_ADDON_PASSWORD": db_value1,
            },
            db_value,
        )
        self._test_priority(
            "DB_PASSWORD",
            {
                # "DB_PASSWORD": db_value,
                "POSTGRESQL_ADDON_PASSWORD": db_value1,
            },
            db_value1,
        )
