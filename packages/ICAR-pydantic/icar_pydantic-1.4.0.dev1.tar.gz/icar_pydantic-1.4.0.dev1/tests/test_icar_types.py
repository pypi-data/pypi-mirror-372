import unittest
from datetime import datetime

from icar import types


class TestIcarTypes(unittest.TestCase):

    def test_icar_metadata_type_exists(self):
        self.assertTrue(hasattr(types, "IcarMetaDataType"))
        self.assertTrue(callable(types.IcarMetaDataType))

    def test_icar_metadata_type_instantiation(self):
        metadata = types.IcarMetaDataType(
            source="test.example.com",
            modified=str(datetime(2024, 1, 1, 12, 0, 0)),
        )
        self.assertEqual(metadata.source, "test.example.com")
        self.assertIsNone(metadata.sourceId)
        self.assertIsNone(metadata.isDeleted)
        self.assertEqual(metadata.modified, datetime(2024, 1, 1, 12, 0, 0))

    def test_icar_metadata_type_with_optional_fields(self):
        metadata = types.IcarMetaDataType(
            source="test.example.com",
            sourceId="test-123",
            isDeleted=False,
            modified=str(datetime(2024, 1, 1, 12, 0, 0)),
        )
        self.assertEqual(metadata.source, "test.example.com")
        self.assertEqual(metadata.sourceId, "test-123")
        self.assertEqual(metadata.modified, datetime(2024, 1, 1, 12, 0, 0))
        self.assertFalse(metadata.isDeleted)

    def test_module_imports_dependencies(self):
        import icar.types

        self.assertTrue(hasattr(icar.types, "enums"))
        self.assertTrue(hasattr(icar.types, "geojson"))
        self.assertFalse(hasattr(icar.types, "resources"))
        self.assertFalse(hasattr(icar.types, "collections"))
