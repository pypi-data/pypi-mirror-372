import doctest
import unittest

from src.environ_odoo_config import utils


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(doctest.DocTestSuite(utils))
    return test_suite


if __name__ in ["__main__", "tests.test_doctests"]:
    runner = unittest.TextTestRunner()
    runner.run(suite())
