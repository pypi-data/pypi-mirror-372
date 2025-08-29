# -*- coding: utf8 -*-
import unittest

from src.environ_odoo_config import entry, mappers, converters


class TestOdooConfig(unittest.TestCase):
    def test_all_mappers_are_register(self):
        number_of_mapper = 3
        self.assertEqual(number_of_mapper, len(mappers.load_mappers()))

    def test_all_section_are_register(self):
        number_of_section = 15
        self.assertEqual(number_of_section, len(converters.load_converter()))
