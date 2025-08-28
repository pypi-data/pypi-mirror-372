import unittest

from evedata.measurement.entities import metadata


class TestMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.Metadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "filename",
            "eveh5_version",
            "eve_version",
            "xml_version",
            "measurement_station",
            "start",
            "end",
            "description",
            "simulation",
            "preferred_axis",
            "preferred_channel",
            "preferred_normalisation_channel",
            "sample",
            "machine",
            "beamline",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestSample(unittest.TestCase):
    def setUp(self):
        self.sample = metadata.Sample()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "id",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.sample, attribute))
