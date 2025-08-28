import logging
import unittest

import numpy
import numpy as np

from evedata.evefile.entities import metadata


class TestMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.Metadata()
        self.logger = logging.getLogger(name="evedata")
        self.logger.setLevel(logging.WARNING)

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))

    def test_copy_attributes_from_copies_attributes(self):
        new_metadata = metadata.Metadata()
        self.metadata.options = {"foo": "bar", "bla": "blub"}
        new_metadata.copy_attributes_from(self.metadata)
        self.assertDictEqual(self.metadata.options, new_metadata.options)

    def test_copy_attributes_from_copies_only_attr_existing_in_target(self):
        new_metadata = metadata.Metadata()
        self.metadata.non_existing_attribute = None
        new_metadata.copy_attributes_from(self.metadata)
        self.assertFalse(hasattr(new_metadata, "non_existing_attribute"))

    def test_copy_attributes_from_copies_only_attr_existing_in_source(self):
        new_metadata = metadata.Metadata()
        new_metadata.non_existing_attribute = None
        self.logger.setLevel(logging.DEBUG)
        with self.assertLogs(level=logging.DEBUG) as captured:
            new_metadata.copy_attributes_from(self.metadata)
        self.assertEqual(len(captured.records), 1)
        self.assertIn(
            "Cannot set non-existing attribute",
            captured.records[0].getMessage(),
        )

    def test_copied_attribute_is_copy(self):
        new_metadata = metadata.Metadata()
        self.metadata.options = {"foo": "bar", "bla": "blub"}
        new_metadata.copy_attributes_from(self.metadata)
        self.metadata.options.update({"baz": "foobar"})
        self.assertNotIn("baz", new_metadata.options)

    def test_copy_attributes_from_without_source_raises(self):
        with self.assertRaisesRegex(
            ValueError, "No source provided to copy attributes from."
        ):
            self.metadata.copy_attributes_from()


class TestAbstractDeviceMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.AbstractDeviceMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "id",
            "pv",
            "access_mode",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestMeasureMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.MeasureMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestMonitorMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.MonitorMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "id",
            "pv",
            "access_mode",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestDeviceMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.DeviceMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestAxisMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.AxisMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "deadband",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.ChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestTimestampMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.TimestampMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestNonnumericChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.NonnumericChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestSinglePointChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.SinglePointChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestAverageChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.AverageChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "n_averages",
            "low_limit",
            "max_attempts",
            "max_deviation",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestIntervalChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.IntervalChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "trigger_interval",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestArrayChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.ArrayChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestAreaChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.AreaChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "file_type",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestNormalizedChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.NormalizedChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "normalize_id",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestSinglePointNormalizedChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.SinglePointNormalizedChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "normalize_id",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestAverageNormalizedChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.AverageNormalizedChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "normalize_id",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestIntervalNormalizedChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.IntervalNormalizedChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "normalize_id",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestScopeChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.ScopeChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestMCAChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.MCAChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "calibration",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestMCAChannelCalibration(unittest.TestCase):
    def setUp(self):
        self.calibration = metadata.MCAChannelCalibration()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "offset",
            "slope",
            "quadratic",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.calibration, attribute))

    def test_calibrate_returns_array(self):
        calibrated_values = self.calibration.calibrate(n_channels=4096)
        self.assertIsInstance(calibrated_values, numpy.ndarray)

    def test_calibrate_returns_correct_calibration(self):
        n_channels = 4096
        self.calibration.offset = 12.0
        self.calibration.slope = 2.0
        self.calibration.quadratic = 1.2
        channels = np.arange(n_channels)
        expected_values = (
            self.calibration.offset
            + channels * self.calibration.slope
            + channels**2 * self.calibration.quadratic
        )
        calibrated_values = self.calibration.calibrate(n_channels=n_channels)
        np.testing.assert_array_equal(expected_values, calibrated_values)


class TestScientificCameraMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.ScientificCameraMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "gain",
            "reverse_x",
            "reverse_y",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestSampleCameraMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.SampleCameraMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "beam_x",
            "beam_y",
            "fractional_x_position",
            "fractional_y_position",
            "skip_frames",
            "average_frames",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestNonencodedAxisMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.NonencodedAxisMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "deadband",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestSkipMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.SkipMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "n_averages",
            "low_limit",
            "max_attempts",
            "max_deviation",
            "channel",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))
