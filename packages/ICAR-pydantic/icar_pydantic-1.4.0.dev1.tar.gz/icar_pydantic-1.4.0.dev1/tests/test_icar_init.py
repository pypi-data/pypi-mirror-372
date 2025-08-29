import unittest

import icar


class TestIcarInit(unittest.TestCase):

    def test_package_version_exists(self):
        self.assertTrue(hasattr(icar, "__version__"))
        self.assertIsInstance(icar.__version__, str)

    def test_package_name_exists(self):
        self.assertTrue(hasattr(icar, "name"))
        self.assertEqual(icar.name, "icar")

    def test_version_tuple_exists(self):
        self.assertTrue(hasattr(icar, "VERSION"))
        self.assertIsInstance(icar.VERSION, tuple)
        self.assertGreaterEqual(len(icar.VERSION), 3)

    def test_version_format(self):
        version_parts = icar.__version__.split(".")
        self.assertGreaterEqual(len(version_parts), 3)
        for part in version_parts[:3]:  # Check only major, minor, patch
            self.assertTrue(part.isdigit())
