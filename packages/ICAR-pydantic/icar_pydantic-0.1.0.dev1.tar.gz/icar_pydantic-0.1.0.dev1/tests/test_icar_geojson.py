import unittest
from enum import Enum

from icar import geojson


class TestIcarGeojson(unittest.TestCase):

    def test_type_enum_exists(self):
        self.assertTrue(hasattr(geojson, "Type"))
        self.assertTrue(issubclass(geojson.Type, Enum))

    def test_type_enum_point_value(self):
        self.assertEqual(geojson.Type.Point.value, "Point")

    def test_module_imports_dependencies(self):
        import icar.geojson

        self.assertFalse(hasattr(icar.geojson, "resources"))
        self.assertFalse(hasattr(icar.geojson, "types"))
        self.assertFalse(hasattr(icar.geojson, "enums"))
        self.assertFalse(hasattr(icar.geojson, "collections"))
