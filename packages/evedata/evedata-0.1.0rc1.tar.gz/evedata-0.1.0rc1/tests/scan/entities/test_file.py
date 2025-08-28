import unittest

from evedata.scan.entities import file


class TestFile(unittest.TestCase):
    def setUp(self):
        self.file = file.File()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "location",
            "scan",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.file, attribute))
