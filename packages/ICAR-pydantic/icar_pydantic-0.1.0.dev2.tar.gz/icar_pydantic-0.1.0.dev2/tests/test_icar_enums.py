"""Test module for icar.enums module."""

import unittest
from enum import Enum

from icar import enums


class TestIcarEnums(unittest.TestCase):

    def test_icar_batch_result_severity_type_exists(self):
        self.assertTrue(hasattr(enums, "IcarBatchResultSeverityType"))
        self.assertTrue(issubclass(enums.IcarBatchResultSeverityType, Enum))

    def test_icar_batch_result_severity_type_values(self):
        severity_enum = enums.IcarBatchResultSeverityType
        expected_values = {"Information", "Warning", "Error"}
        actual_values = {item.value for item in severity_enum}
        self.assertEqual(actual_values, expected_values)

    def test_module_imports_dependencies(self):
        import icar.enums

        self.assertFalse(hasattr(icar.enums, "resources"))
        self.assertFalse(hasattr(icar.enums, "types"))
        self.assertFalse(hasattr(icar.enums, "collections"))
