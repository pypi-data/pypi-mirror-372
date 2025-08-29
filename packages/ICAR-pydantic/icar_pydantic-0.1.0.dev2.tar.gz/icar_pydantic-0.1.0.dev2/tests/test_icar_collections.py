import unittest

from icar import collections, resources


class TestIcarCollections(unittest.TestCase):
    def test_icar_error_collection_exists(self):
        self.assertTrue(hasattr(collections, "IcarErrorCollection"))
        self.assertTrue(callable(collections.IcarErrorCollection))

    def test_icar_error_collection_instantiation(self):
        error_collection = collections.IcarErrorCollection()
        self.assertIsNone(error_collection.errors)

    def test_icar_error_collection_with_errors(self):
        error_msg = resources.IcarResponseMessageResource(
            title="Test Error", detail="Test error detail"
        )
        error_collection = collections.IcarErrorCollection(errors=[error_msg])
        self.assertIsNotNone(error_collection.errors)
        self.assertEqual(len(error_collection.errors), 1)
        self.assertEqual(error_collection.errors[0].title, "Test Error")

    def test_view_class_exists(self):
        self.assertTrue(hasattr(collections, "View"))
        self.assertTrue(callable(collections.View))

    def test_view_instantiation(self):
        view = collections.View()
        self.assertIsNone(view.totalItems)
        self.assertIsNone(view.totalPages)
        self.assertIsNone(view.pageSize)
        self.assertIsNone(view.currentPage)

    def test_view_with_pagination_data(self):
        view = collections.View(
            totalItems=100, totalPages=10, pageSize=10, currentPage=1
        )
        self.assertEqual(view.totalItems, 100)
        self.assertEqual(view.totalPages, 10)
        self.assertEqual(view.pageSize, 10)
        self.assertEqual(view.currentPage, 1)

    def test_module_imports_dependencies(self):
        import icar.collections

        self.assertTrue(hasattr(icar.collections, "resources"))
        self.assertFalse(hasattr(icar.collections, "types"))
        self.assertFalse(hasattr(icar.collections, "enums"))
