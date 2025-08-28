import os
import unittest

from src.environ_odoo_config.api import OdooConfig, Env

try:
    ODOO_VERSION = int(float(os.getenv("ODOO_VERSION", "0")))
except ValueError:
    ODOO_VERSION = None





class MultiOdooVersion:
    """
    Contains decorator run function for each Odoo version supported
    See the doc to use it.


    """

    @staticmethod
    def with_args(function):
        def _wrapper(case):
            for version in range(12, 19):
                with case.subTest(odoo_version=version):
                    function(case, version)

        return _wrapper

    @staticmethod
    def with_env(function):
        """

        Args:
            function:

        Returns:

        """

        def _wrapper(case):
            for version in range(0, 30 + 1):
                with case.subTest(odoo_version=version):
                    function(case, Env(ODOO_VERSION=version))

        return _wrapper

    @staticmethod
    def without_args(function):
        def _wrapper(case):
            for version in range(0, 30 + 1):
                with case.subTest(odoo_version=version):
                    function(case)

        return _wrapper


class SkipUnless:
    env_odoo = unittest.skipUnless(
        ODOO_VERSION,
        f"Not in Odoo Env, ODOO_VERSION is {ODOO_VERSION or 'not'} supplied",
    )
    env_odoo11 = unittest.skipUnless(
        ODOO_VERSION == 11,
        f"Not in Odoo 11 Env, ODOO_VERSION is {ODOO_VERSION or 'not'} supplied",
    )
    env_odoo12 = unittest.skipUnless(
        ODOO_VERSION == 12,
        f"Not in Odoo 12 Env, ODOO_VERSION is {ODOO_VERSION or 'not'} supplied",
    )
    odoo_more11 = unittest.skipUnless(
        ODOO_VERSION >= 12,
        f"Not in Odoo version more than 12, ODOO_VERSION is {ODOO_VERSION or 'not'} supplied",
    )
    env_odoo13 = unittest.skipUnless(
        ODOO_VERSION == 13,
        f"Not in Odoo 13 Env, ODOO_VERSION is {ODOO_VERSION or 'not'} supplied",
    )
    env_odoo14 = unittest.skipUnless(
        ODOO_VERSION == 14,
        f"Not in Odoo 14 Env, ODOO_VERSION is {ODOO_VERSION or 'not'} supplied",
    )
    env_odoo15 = unittest.skipUnless(
        ODOO_VERSION == 15,
        f"Not in Odoo 15 Env, ODOO_VERSION is {ODOO_VERSION or 'not'} supplied",
    )
    env_odoo16 = unittest.skipUnless(
        ODOO_VERSION == 16,
        f"Not in Odoo 16 Env, ODOO_VERSION is {ODOO_VERSION or 'not'} supplied",
    )
class SkipIf:
    env_odoo = unittest.skipIf(
        ODOO_VERSION,
        f"Not in Odoo Env, ODOO_VERSION is {ODOO_VERSION or 'not'} supplied",
    )
