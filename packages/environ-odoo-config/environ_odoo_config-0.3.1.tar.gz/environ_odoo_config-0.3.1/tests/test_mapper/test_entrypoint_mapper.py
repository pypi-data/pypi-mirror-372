from unittest import TestCase
from src.environ_odoo_config.mappers import load_mappers

class TestEntrypointMapper(TestCase):

    def test_load(self):
        self.assertTrue(load_mappers())
