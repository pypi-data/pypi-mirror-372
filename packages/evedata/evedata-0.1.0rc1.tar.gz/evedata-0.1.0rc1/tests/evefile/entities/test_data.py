import logging
import os
import unittest

import h5py
import numpy as np

from evedata.evefile.entities import data, metadata


class DummyHDF5File:
    def __init__(self, filename=""):
        self.filename = filename
        self.shape = 10

    def create(self, random=False, double=False, gaps=False):
        with h5py.File(self.filename, "w") as file:
            c1 = file.create_group("c1")
            c1.create_group("main")
            c1.create_group("snapshot")
            meta = c1.create_group("meta")
            data_ = np.ndarray(
                [self.shape],
                dtype=np.dtype(
                    [("PosCounter", "<i4"), ("PosCountTimer", "<i4")]
                ),
            )
            if random:
                data_["PosCounter"] = np.random.randint(
                    low=1, high=self.shape, size=self.shape
                )
                data_["PosCountTimer"] = np.linspace(start=2, stop=20, num=10)
            elif double:
                data_["PosCounter"] = np.asarray(
                    [1, 1, 2, 3, 4, 4, 4, 5, 6, 6]
                )
                self.shape = len(np.unique(data_["PosCounter"]))
                data_["PosCountTimer"] = np.asarray(
                    [2, 3, 4, 6, 8, 9, 9, 10, 12, 13]
                )
            elif gaps:
                data_["PosCounter"] = np.asarray(
                    [1, 2, 4, 5, 6, 8, 9, 10, 12, 13]
                )
                self.shape = len(np.unique(data_["PosCounter"]))
                data_["PosCountTimer"] = np.asarray(
                    [2, 3, 4, 6, 8, 9, 9, 10, 12, 13]
                )
            else:
                data_["PosCounter"] = np.linspace(
                    start=1, stop=self.shape, num=self.shape
                )
                data_["PosCountTimer"] = np.linspace(
                    start=2, stop=self.shape * 2, num=self.shape
                )
            poscounttimer = meta.create_dataset("PosCountTimer", data=data_)
            poscounttimer.attrs["Unit"] = np.bytes_(["msecs"])

    def add_array_data(self):
        with h5py.File(self.filename, "r+") as file:
            file["c1"]["main"].create_group("array")
            for position in range(5, 20):
                data_ = np.ndarray([4096], dtype=np.dtype([("0", "<i4")]))
                data_["0"] = np.random.randint(low=0, high=1024, size=4096)
                file["c1"]["main"]["array"].create_dataset(
                    str(position), data=data_
                )


class TestData(unittest.TestCase):
    def setUp(self):
        self.data = data.Data()
        self.logger = logging.getLogger(name="evedata")
        self.logger.setLevel(logging.WARNING)

        class MockData(data.Data):

            def __init__(self):
                super().__init__()
                self.get_data_called = False

            def get_data(self):
                super().get_data()
                self.get_data_called = True

        self.mock_data = MockData()
        self.filename = "test.h5"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "importer",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_setting_data_sets_data(self):
        self.data.data = np.random.random(5)
        self.assertTrue(self.data)

    def test_accessing_data_calls_get_data_if_data_not_loaded(self):
        _ = self.mock_data.data
        self.assertTrue(self.mock_data.get_data_called)

    def test_accessing_data_with_data_does_not_call_get_data(self):
        self.mock_data.data = np.random.random(5)
        _ = self.mock_data.data
        self.assertFalse(self.mock_data.get_data_called)

    def test_get_data_loads_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        importer = data.HDF5DataImporter(source=self.filename)
        importer.item = "/c1/meta/PosCountTimer"
        importer.mapping = {
            "PosCounter": "position_counts",
            "PosCountTimer": "data",
        }
        self.data.importer.append(importer)
        self.data.get_data()
        self.assertTrue(self.data.data.any())

    def test_copy_attributes_from_copies_attributes(self):
        new_data = data.Data()
        self.data.options = {"foo": "bar", "bla": "blub"}
        new_data.copy_attributes_from(self.data)
        self.assertDictEqual(self.data.options, new_data.options)

    def test_copy_attributes_from_copies_only_existing_attributes(self):
        new_data = data.Data()
        self.data.non_existing_attribute = None
        new_data.copy_attributes_from(self.data)
        self.assertFalse(hasattr(new_data, "non_existing_attribute"))

    def test_copy_attributes_from_copies_only_attr_existing_in_source(self):
        new_data = data.Data()
        new_data.non_existing_attribute = None
        self.logger.setLevel(logging.DEBUG)
        with self.assertLogs(level=logging.DEBUG) as captured:
            new_data.copy_attributes_from(self.data)
        self.assertEqual(len(captured.records), 1)
        self.assertIn(
            "Cannot set non-existing attribute",
            captured.records[0].getMessage(),
        )

    def test_copied_attribute_is_copy(self):
        new_data = data.Data()
        self.data.options = {"foo": "bar", "bla": "blub"}
        new_data.copy_attributes_from(self.data)
        self.data.options.update({"baz": "foobar"})
        self.assertNotIn("baz", new_data.options)

    def test_copy_attributes_from_copies_metadata(self):
        new_data = data.Data()
        self.data.metadata.name = "foo"
        new_data.copy_attributes_from(self.data)
        self.assertEqual(self.data.metadata.name, new_data.metadata.name)

    def test_copy_attributes_from_copies_only_existing_metadata(self):
        new_data = data.Data()
        self.data.metadata.nonexisting_attribute = "foo"
        new_data.copy_attributes_from(self.data)
        self.assertFalse(hasattr(new_data.metadata, "nonexisting_attribute"))

    def test_copy_attributes_from_without_source_raises(self):
        with self.assertRaisesRegex(
            ValueError, "No source provided to copy attributes from."
        ):
            self.data.copy_attributes_from()


class TestMonitorData(unittest.TestCase):
    def setUp(self):
        self.data = data.MonitorData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "milliseconds",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(self.data.metadata, metadata.MonitorMetadata)


class TestMeasureData(unittest.TestCase):
    def setUp(self):
        self.data = data.MeasureData()
        self.filename = "test.h5"

        class MockData(data.MeasureData):

            def __init__(self):
                super().__init__()
                self.get_data_called = False

            def get_data(self):
                super().get_data()
                self.get_data_called = True

        self.mock_data = MockData()

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(self.data.metadata, metadata.MeasureMetadata)

    def test_get_data_sorts_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(random=True)
        importer = data.HDF5DataImporter(source=self.filename)
        importer.item = "/c1/meta/PosCountTimer"
        importer.mapping = {
            "PosCounter": "position_counts",
            "PosCountTimer": "data",
        }
        self.data.importer.append(importer)
        self.data.get_data()
        self.assertTrue(np.all(np.diff(self.data.position_counts) >= 0))
        self.assertFalse(np.all(np.diff(self.data.data) >= 0))

    def test_setting_positions_sets_positions(self):
        self.data.position_counts = np.random.random(5)
        self.assertGreater(len(self.data.position_counts), 0)

    def test_accessing_positions_calls_get_data_if_not_loaded(self):
        _ = self.mock_data.position_counts
        self.assertTrue(self.mock_data.get_data_called)

    def test_accessing_positions_with_positions_does_not_call_get_data(self):
        self.mock_data.position_counts = np.random.random(5)
        _ = self.mock_data.position_counts
        self.assertFalse(self.mock_data.get_data_called)


class TestDeviceData(unittest.TestCase):
    def setUp(self):
        self.data = data.DeviceData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(self.data.metadata, metadata.DeviceMetadata)


class TestAxisData(unittest.TestCase):
    def setUp(self):
        self.data = data.AxisData()
        self.filename = "test.h5"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
            "set_values",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(self.data.metadata, metadata.AxisMetadata)

    def test_get_data_takes_last_from_duplicate_pos_counts(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(double=True)
        importer = data.HDF5DataImporter(source=self.filename)
        importer.item = "/c1/meta/PosCountTimer"
        importer.mapping = {
            "PosCounter": "position_counts",
            "PosCountTimer": "data",
        }
        self.data.importer.append(importer)
        self.data.get_data()
        self.assertTrue(np.all(np.diff(self.data.position_counts) > 0))
        self.assertTrue(np.any(self.data.data % 2))
        self.assertEqual(h5file.shape, len(self.data.data))

    def test_get_data_preserves_length_of_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(double=False)
        importer = data.HDF5DataImporter(source=self.filename)
        importer.item = "/c1/meta/PosCountTimer"
        importer.mapping = {
            "PosCounter": "position_counts",
            "PosCountTimer": "data",
        }
        self.data.importer.append(importer)
        self.data.get_data()
        self.assertEqual(h5file.shape, len(self.data.data))

    def test_get_data_with_gaps_in_position_counts_returns_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(gaps=True)
        importer = data.HDF5DataImporter(source=self.filename)
        importer.item = "/c1/meta/PosCountTimer"
        importer.mapping = {
            "PosCounter": "position_counts",
            "PosCountTimer": "data",
        }
        self.data.importer.append(importer)
        self.data.get_data()
        self.assertEqual(h5file.shape, len(self.data.data))


class TestChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.ChannelData()
        self.filename = "test.h5"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(self.data.metadata, metadata.ChannelMetadata)

    def test_get_data_takes_first_from_duplicate_pos_counts(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(double=True)
        importer = data.HDF5DataImporter(source=self.filename)
        importer.item = "/c1/meta/PosCountTimer"
        importer.mapping = {
            "PosCounter": "position_counts",
            "PosCountTimer": "data",
        }
        self.data.importer.append(importer)
        self.data.get_data()
        self.assertTrue(np.all(np.diff(self.data.position_counts) > 0))
        self.assertFalse(np.any(self.data.data % 2))

    def test_get_data_with_gaps_in_position_counts_returns_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(gaps=True)
        importer = data.HDF5DataImporter(source=self.filename)
        importer.item = "/c1/meta/PosCountTimer"
        importer.mapping = {
            "PosCounter": "position_counts",
            "PosCountTimer": "data",
        }
        self.data.importer.append(importer)
        self.data.get_data()
        self.assertEqual(h5file.shape, len(self.data.data))


class TestTimestampData(unittest.TestCase):
    def setUp(self):
        self.data = data.TimestampData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(self.data.metadata, metadata.TimestampMetadata)

    def test_get_position_returns_position(self):
        self.data.position_counts = np.linspace(start=4, stop=23, num=20)
        self.data.data = np.linspace(start=0, stop=19, num=20)
        self.assertEqual(
            self.data.position_counts[3], self.data.get_position(3.2)
        )

    def test_get_position_with_array_returns_position_array(self):
        self.data.position_counts = np.linspace(start=4, stop=23, num=20)
        self.data.data = np.linspace(start=0, stop=19, num=20)
        np.testing.assert_array_equal(
            self.data.position_counts[[3, 5, 6]],
            self.data.get_position([3.2, 5.5, 6.8]),
        )

    def test_get_position_for_minus_one_returns_first_position(self):
        self.data.position_counts = np.linspace(start=4, stop=23, num=20)
        self.data.data = np.linspace(start=0, stop=19, num=20)
        self.assertEqual(
            self.data.position_counts[0], self.data.get_position(-1)
        )

    def test_get_position_with_minus_one_in_array(self):
        self.data.position_counts = np.linspace(start=4, stop=23, num=20)
        self.data.data = np.linspace(start=0, stop=19, num=20)
        np.testing.assert_array_equal(
            self.data.position_counts[[0, 3, 5, 6]],
            self.data.get_position([-1, 3.2, 5.5, 6.8]),
        )


class TestNonnumericChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.NonnumericChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.NonnumericChannelMetadata
        )


class TestSinglePointChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.SinglePointChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.SinglePointChannelMetadata
        )


class TestAverageChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.AverageChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
            "raw_data",
            "attempts",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.AverageChannelMetadata
        )

    def test_mean_returns_mean_values(self):
        self.data.raw_data = np.asarray([[1, 2, 3], [1, 2, 3], [1, 2, 3]])
        np.testing.assert_array_equal(
            self.data.raw_data.mean(axis=1), self.data.mean
        )

    def test_std_returns_std_values(self):
        self.data.raw_data = np.asarray([[1, 2, 3], [1, 2, 3], [1, 2, 3]])
        np.testing.assert_array_equal(
            self.data.raw_data.std(axis=1), self.data.std
        )

    def test_set_std_values(self):
        self.data.std = np.asarray([[1, 2, 3], [1, 2, 3], [1, 2, 3]]).std(
            axis=1
        )


class TestIntervalChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.IntervalChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
            "raw_data",
            "counts",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.IntervalChannelMetadata
        )

    def test_mean_returns_mean_values(self):
        self.data.raw_data = np.asarray([[1, 2, 3], [1, 2, 3], [1, 2, 3]])
        np.testing.assert_array_equal(
            self.data.raw_data.mean(axis=1), self.data.mean
        )

    def test_std_returns_std_values(self):
        self.data.raw_data = np.asarray([[1, 2, 3], [1, 2, 3], [1, 2, 3]])
        np.testing.assert_array_equal(
            self.data.raw_data.std(axis=1), self.data.std
        )

    def test_set_std_values(self):
        self.data.std = np.asarray([[1, 2, 3], [1, 2, 3], [1, 2, 3]]).std(
            axis=1
        )


class TestArrayChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.ArrayChannelData()
        self.filename = "test.h5"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.ArrayChannelMetadata
        )

    def test_get_data_loads_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        h5file.add_array_data()
        for position in range(5, 20):
            importer = data.HDF5DataImporter(source=self.filename)
            importer.item = f"/c1/main/array/{position}"
            importer.mapping = {
                "0": "data",
            }
            self.data.importer.append(importer)
        self.data.get_data()
        self.assertEqual(2, self.data.data.ndim)


class TestAreaChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.AreaChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.AreaChannelMetadata
        )


class TestNormalizedChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.NormalizedChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "normalized_data",
            "normalizing_data",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.NormalizedChannelMetadata
        )


class TestSinglePointNormalizedChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.SinglePointNormalizedChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
            "normalized_data",
            "normalizing_data",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.SinglePointNormalizedChannelMetadata
        )


class TestAverageNormalizedChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.AverageNormalizedChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
            "raw_data",
            "attempts",
            "normalized_data",
            "normalizing_data",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.AverageNormalizedChannelMetadata
        )


class TestIntervalNormalizedChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.IntervalNormalizedChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
            "raw_data",
            "counts",
            "normalized_data",
            "normalizing_data",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.IntervalNormalizedChannelMetadata
        )


class TestScopeChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.ScopeChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.ScopeChannelMetadata
        )


class TestMCAChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.MCAChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
            "roi",
            "life_time",
            "real_time",
            "preset_life_time",
            "preset_real_time",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(self.data.metadata, metadata.MCAChannelMetadata)


class TestMCAChannelROIData(unittest.TestCase):
    def setUp(self):
        self.data = data.MCAChannelROIData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
            "label",
            "marker",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))


class TestScientificCameraData(unittest.TestCase):
    def setUp(self):
        self.data = data.ScientificCameraData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
            "roi",
            "statistics",
            "acquire_time",
            "temperature",
            "humidity",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.ScientificCameraMetadata
        )


class TestScientificCameraROIData(unittest.TestCase):
    def setUp(self):
        self.data = data.ScientificCameraROIData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
            "label",
            "marker",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))


class TestScientificCameraStatisticsData(unittest.TestCase):
    def setUp(self):
        self.data = data.ScientificCameraStatisticsData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
            "background_width",
            "min_value",
            "min_x",
            "min_y",
            "max_value",
            "max_x",
            "max_y",
            "mean",
            "total",
            "net",
            "sigma",
            "centroid_x",
            "centroid_y",
            "centroid_sigma_x",
            "centroid_sigma_y",
            "centroid_sigma_xy",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))


class TestSampleCameraData(unittest.TestCase):
    def setUp(self):
        self.data = data.SampleCameraData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.SampleCameraMetadata
        )


class TestNonencodedAxisData(unittest.TestCase):
    def setUp(self):
        self.data = data.NonencodedAxisData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
            "set_values",
            "filled_data",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.NonencodedAxisMetadata
        )


class TestDataImporter(unittest.TestCase):
    def setUp(self):
        self.importer = data.DataImporter()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "source",
            "preprocessing",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.importer, attribute))

    def test_load_without_source_raises(self):
        self.importer.source = ""
        with self.assertRaises(ValueError):
            self.importer.load()

    def test_load_with_source_as_parameter(self):
        self.importer.source = ""
        self.importer.load(source="foo")

    def test_load_returns_data(self):

        class MockDataImporter(data.DataImporter):
            def _load(self):
                return "foo"

        importer = MockDataImporter()
        importer.source = "baz"
        self.assertTrue(importer.load())

    def test_instantiate_with_source_sets_source(self):
        source = "baz"
        importer = data.DataImporter(source=source)
        self.assertEqual(source, importer.source)

    def test_load_performs_preprocessing_data(self):

        class MockDataImporter(data.DataImporter):
            def _load(self):
                return self.source

        class MockImporterPreprocessingStep(data.ImporterPreprocessingStep):
            def _process(self, data=None):
                return data * 2

        importer = MockDataImporter()
        importer.preprocessing = [MockImporterPreprocessingStep()]
        importer.source = "baz"
        self.assertEqual(importer.source * 2, importer.load())


class TestHDF5DataImporter(unittest.TestCase):
    def setUp(self):
        self.importer = data.HDF5DataImporter()
        self.filename = "test.h5"
        self.item = "/c1/main/test"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def create_hdf5_file(self):
        with h5py.File(self.filename, "w") as file:
            c1 = file.create_group("c1")
            main = c1.create_group("main")
            main.create_dataset("test", data=np.ones([5, 2]))

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "source",
            "item",
            "mapping",
            "data",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.importer, attribute))

    def test_load_without_item_raises(self):
        self.importer.source = "foo"
        with self.assertRaises(ValueError):
            self.importer.load()

    def test_load_with_item_as_parameter(self):
        self.create_hdf5_file()
        self.importer.source = self.filename
        self.importer.load(item=self.item)

    def test_load_returns_HDF5_dataset_data(self):
        self.create_hdf5_file()
        self.importer.source = self.filename
        self.importer.item = self.item
        np.testing.assert_array_equal(np.ones([5, 2]), self.importer.load())

    def test_load_sets_data_attribute(self):
        self.create_hdf5_file()
        self.importer.source = self.filename
        self.importer.item = self.item
        self.importer.load()
        np.testing.assert_array_equal(np.ones([5, 2]), self.importer.data)

    def test_load_performs_preprocessing_data(self):
        self.create_hdf5_file()

        class MockImporterPreprocessingStep(data.ImporterPreprocessingStep):
            def _process(self, data=None):
                return data * 2

        self.importer.preprocessing = [MockImporterPreprocessingStep()]
        self.importer.source = self.filename
        self.importer.item = self.item
        self.importer.load()
        np.testing.assert_array_equal(self.importer.data, np.ones([5, 2]) * 2)


class TestSkipData(unittest.TestCase):
    def setUp(self):
        self.data = data.SkipData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(self.data.metadata, metadata.SkipMetadata)

    def test_get_parent_positions(self):
        self.data.position_counts = np.asarray(
            [2, 3, 4, 6, 7, 8, 9, 11, 12, 14, 15, 16], dtype=int
        )
        parent_positions = np.asarray([1, 5, 10, 13], dtype=int)
        np.testing.assert_array_equal(
            parent_positions, self.data.get_parent_positions()
        )

    def test_get_scan_module_positions(self):
        self.data.position_counts = np.asarray(
            [2, 3, 4, 6, 7, 8, 11, 12, 13, 15, 16, 17], dtype=int
        )
        scan_module_positions = np.asarray(
            [[2, 3, 4, 6, 7, 8], [11, 12, 13, 15, 16, 17]], dtype=int
        )
        np.testing.assert_array_equal(
            scan_module_positions, self.data.get_scan_module_positions()
        )

    def test_get_parent_positions_with_multiple_scan_modules(self):
        self.data.position_counts = np.asarray(
            [2, 3, 4, 6, 7, 8, 11, 12, 13, 15, 16, 17], dtype=int
        )
        parent_positions = np.asarray([1, 5, 10, 14], dtype=int)
        np.testing.assert_array_equal(
            parent_positions, self.data.get_parent_positions()
        )


class TestImporterPreprocessingStep(unittest.TestCase):
    def setUp(self):
        self.preprocessing = data.ImporterPreprocessingStep()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "data",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.preprocessing, attribute))

    def test_process_with_data_sets_data(self):
        self.preprocessing.process(data="foo")
        self.assertEqual("foo", self.preprocessing.data)

    def test_process_returns_processed_data(self):

        class MockImporterPreprocessingStep(data.ImporterPreprocessingStep):
            def _process(self, data=None):
                return data * 2

        preprocessing = MockImporterPreprocessingStep()
        preprocessing.data = "baz"
        self.assertEqual(preprocessing.data * 2, preprocessing.process())

    def test_instantiate_with_data_sets_data(self):
        test_data = "baz"
        preprocessing = data.ImporterPreprocessingStep(data=test_data)
        self.assertEqual(test_data, preprocessing.data)
