import unittest

from icar import resources


class TestIcarResources(unittest.TestCase):

    def test_icar_response_message_resource_exists(self):
        self.assertTrue(hasattr(resources, "IcarResponseMessageResource"))
        self.assertTrue(callable(resources.IcarResponseMessageResource))

    def test_icar_response_message_resource_instantiation(self):
        response = resources.IcarResponseMessageResource()
        self.assertIsNone(response.type)
        self.assertIsNone(response.severity)
        self.assertIsNone(response.status)
        self.assertIsNone(response.title)
        self.assertIsNone(response.detail)

    def test_module_imports_dependencies(self):
        import icar.resources

        self.assertTrue(hasattr(icar.resources, "enums"))
        self.assertTrue(hasattr(icar.resources, "types"))
        self.assertFalse(hasattr(icar.resources, "collections"))
