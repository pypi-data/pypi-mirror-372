import copy
import logging
import unittest

import numpy as np

from evedata.evefile.controllers import mpskip, preprocessing
from evedata.evefile.entities import data


class TestRearrangeRawValues(unittest.TestCase):
    def setUp(self):
        self.processing = mpskip.RearrangeRawValues()
        self.data = np.ndarray(
            [12],
            dtype=np.dtype(
                [
                    ("PosCounter", "<i4"),
                    ("foo", "f8"),
                ]
            ),
        )
        self.data["PosCounter"] = np.array(
            [5, 6, 8, 9, 10, 12, 13, 14, 15, 17, 18, 19]
        )
        self.data["foo"] = np.arange(12)
        self.skip_data = data.SkipData()
        self.skip_data.position_counts = self.data["PosCounter"]
        self.skip_data.data = np.array([1, 2, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3])

    def test_instantiate_class(self):
        pass

    def test_is_preprocessing_step(self):
        self.assertIsInstance(self.processing, data.ImporterPreprocessingStep)

    def test_has_attributes(self):
        attributes = [
            "skip_data",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.processing, attribute))

    def test_splits_raw_values(self):
        self.processing.skip_data = self.skip_data
        result = self.processing.process(self.data)
        self.assertEqual(4, len(result))

    def test_with_weird_data_splits_raw_values(self):
        self.skip_data.data = np.array([1, 2, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3])
        self.processing.skip_data = self.skip_data
        result = self.processing.process(self.data)
        self.assertEqual(4, len(result))

    def test_sets_correct_positions(self):
        self.processing.skip_data = self.skip_data
        result = self.processing.process(self.data)
        self.assertListEqual([4, 7, 11, 16], list(result["PosCounter"]))


class MockEveFile:

    def __init__(self):
        self.scan = MockScanBoundary()
        self.scan_modules = {}

    def has_scan(self):
        return bool(self.scan)

    def add_scan_modules(self):
        for name, scan_scan_module in self.scan.scan.scan_modules.items():
            file_scan_module = MockFileScanModule()
            for attribute in ["id", "name", "parent"]:
                setattr(
                    file_scan_module,
                    attribute,
                    getattr(scan_scan_module, attribute),
                )
            for device_name, device in scan_scan_module.channels.items():
                file_scan_module.data[device_name] = copy.deepcopy(device)
            for device_name, device in scan_scan_module.axes.items():
                file_scan_module.data[device_name] = copy.deepcopy(device)
            self.scan_modules[name] = file_scan_module


class MockScanBoundary:

    def __init__(self):
        self.scan = MockScan()


class MockScan:

    def __init__(self):
        self.scan_modules = {}

    def add_scan_modules(self):
        outer_module = MockScanScanModule()
        outer_module.id = 1
        outer_module.name = "WL"
        outer_module.parent = 0
        outer_module.add_axis("nmEnerg:io2600wl2e.A")
        self.scan_modules.update({outer_module.id: outer_module})

        inner_module = MockScanScanModule()
        inner_module.id = 2
        inner_module.name = "Skip"
        inner_module.parent = 1
        channel_names = [
            "MPSKIP:euvr01chan1",
            "MPSKIP:euvr01skipcountchan1",
            "K0617:gw24126chan1",
            "A2980:gw24103chan1",
            "PPESM9:pi03500000.RBVchan1",
            "Energ:io2600e2wlchan1",
        ]
        for channel_name in channel_names:
            inner_module.add_channel(channel_name)
        inner_module.add_axis("Counter-mot")
        self.scan_modules.update({inner_module.id: inner_module})


class MockScanMultipleSkip(MockScan):

    def add_scan_modules(self):
        self.add_skip_scan_modules(offset=0)
        self.add_between_scan_module(smid=3)
        self.add_skip_scan_modules(offset=3)

    def add_skip_scan_modules(self, offset=0):
        outer_module = MockScanScanModule()
        outer_module.id = 1 + offset
        outer_module.name = f"WL{1 + offset}"
        outer_module.parent = 0 + offset
        outer_module.add_axis("nmEnerg:io2600wl2e.A")
        self.scan_modules.update({outer_module.id: outer_module})

        inner_module = MockScanScanModule()
        inner_module.id = 2 + offset
        inner_module.name = "Skip"
        inner_module.parent = 1 + offset
        channel_names = [
            "MPSKIP:euvr01chan1",
            "MPSKIP:euvr01skipcountchan1",
            "K0617:gw24126chan1",
            "A2980:gw24103chan1",
            "PPESM9:pi03500000.RBVchan1",
            "Energ:io2600e2wlchan1",
        ]
        for channel_name in channel_names:
            inner_module.add_channel(channel_name)
        inner_module.add_axis("Counter-mot")
        self.scan_modules.update({inner_module.id: inner_module})

    def add_between_scan_module(self, smid=0):
        between_module = MockScanScanModule()
        between_module.id = smid
        between_module.name = f"Between{smid}"
        between_module.parent = smid - 1
        between_module.add_axis("nmEnerg:io2600wl2e.A")
        self.scan_modules.update({between_module.id: between_module})


class MockScanScanModule:

    def __init__(self):
        self.id = -1
        self.name = ""
        self.parent = -1
        self.axes = {}
        self.channels = {}

    def has_mpskip(self):
        return bool(
            [name for name in self.channels if name.startswith("MPSKIP")]
        )

    def add_axis(self, id=""):
        axis = MockAxisChannel(id=id)
        axis.importer.append(MockDatasetImporter())
        self.axes.update({id: axis})

    def add_channel(self, id=""):
        channel = MockAxisChannel(id=id)
        channel.importer.append(MockDatasetImporter())
        self.channels.update({id: channel})


class MockAxisChannel:

    def __init__(self, id=""):
        self.id = id
        self.importer = []
        self.metadata = {"id": id}


class MockDatasetImporter:

    def __init__(self):
        self.source = ""
        self.preprocessing = []


class MockFileScanModule:

    def __init__(self):
        self.id = -1
        self.name = ""
        self.parent = -1
        self.data = {}
        self.positions = None


class TestMpskip(unittest.TestCase):
    def setUp(self):
        self.mapper = mpskip.Mpskip()
        self.logger = logging.getLogger(name="evedata")
        self.logger.setLevel(logging.WARNING)
        self.source = MockEveFile()
        self.source.scan.scan.add_scan_modules()
        self.source.add_scan_modules()
        skipdata = data.SkipData()
        skipdata.position_counts = np.asarray([2, 3, 5, 6, 7, 9, 10, 11])
        self.source.scan_modules[2].data["skipdata"] = skipdata

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "source",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.mapper, attribute))

    def test_map_without_source_raises(self):
        self.mapper.source = None
        with self.assertRaises(ValueError):
            self.mapper.map()

    def test_map_with_source_sets_source(self):
        self.mapper.map(source=self.source)
        self.assertEqual(self.source, self.mapper.source)

    def test_map_without_scan_logs(self):
        source = MockEveFile()
        source.scan = None
        self.logger.setLevel(logging.DEBUG)
        with self.assertLogs(level=logging.DEBUG) as captured:
            self.mapper.map(source=source)
        self.assertEqual(len(captured.records), 1)
        self.assertEqual(
            captured.records[0].getMessage(),
            "No scan, hence no mpskip mapping.",
        )

    def test_map_removes_mpskip_module_from_scan_modules(self):
        self.mapper.map(source=self.source)
        self.assertNotIn(
            "Skip",
            [sm.name for sm in self.mapper.source.scan_modules.values()],
        )

    def test_map_adds_channels_to_parent_scan_module(self):
        self.mapper.map(source=self.source)
        self.assertTrue(self.mapper.source.scan_modules[1].data)

    def test_map_does_not_add_mpskip_channels_to_parent_scan_module(self):
        self.mapper.map(source=self.source)
        self.assertFalse(
            [
                name
                for name in self.mapper.source.scan_modules[1].data
                if name.startswith("MPSKIP")
            ]
        )

    def test_map_does_not_add_counter_axis_to_parent_scan_module(self):
        self.mapper.map(source=self.source)
        self.assertFalse(
            [
                name
                for name in self.mapper.source.scan_modules[1].data
                if name.startswith("Counter-mot")
            ]
        )

    def test_map_creates_axis_objects_for_rbv_devices(self):
        self.mapper.map(source=self.source)
        rbv_devices = [
            device
            for name, device in self.mapper.source.scan_modules[
                1
            ].data.items()
            if "RBV" in name
        ]
        for device in rbv_devices:
            self.assertIsInstance(device, data.AxisData)

    def test_map_copies_attributes_from_rbv_devices(self):
        self.mapper.map(source=self.source)
        rbv_devices = [
            device
            for name, device in self.mapper.source.scan_modules[
                1
            ].data.items()
            if "RBV" in name
        ]
        for device in rbv_devices:
            self.assertTrue(device.importer)

    def test_map_adds_preprocessing_steps_to_devices(self):
        self.mapper.map(source=self.source)
        for name, device in self.mapper.source.scan_modules[1].data.items():
            if name.startswith("nmEnerg"):  # dirty fix to skip existing axis
                continue
            self.assertIsInstance(
                device.importer[0].preprocessing[0],
                preprocessing.SelectPositions,
            )
            self.assertIsInstance(
                device.importer[0].preprocessing[1],
                mpskip.RearrangeRawValues,
            )

    def test_map_replaces_select_position_preprocessing_step(self):
        for scan_module in self.source.scan_modules.values():
            for name, dataset in scan_module.data.items():
                if not name.startswith("skip"):
                    preprocessing_step = preprocessing.SelectPositions()
                    dataset.importer.append(MockDatasetImporter())
                    dataset.importer[0].preprocessing.append(
                        preprocessing_step
                    )
        self.mapper.map(source=self.source)
        for name, device in self.mapper.source.scan_modules[1].data.items():
            self.assertIsInstance(
                device.importer[0].preprocessing[0],
                preprocessing.SelectPositions,
            )
            if name.startswith("nmEnerg"):  # dirty fix to skip existing axis
                continue
            self.assertIsInstance(
                device.importer[0].preprocessing[1],
                mpskip.RearrangeRawValues,
            )

    def test_map_creates_average_channel_objects_for_non_rbv_devices(self):
        self.mapper.map(source=self.source)
        non_rbv_devices = [
            device
            for name, device in self.mapper.source.scan_modules[
                1
            ].data.items()
            if "RBV" not in name and not name.startswith("nmEnerg")
        ]
        for device in non_rbv_devices:
            self.assertIsInstance(device, data.AverageChannelData)

    def test_map_copies_attributes_from_non_rbv_devices(self):
        self.mapper.map(source=self.source)
        non_rbv_devices = [
            device
            for name, device in self.mapper.source.scan_modules[
                1
            ].data.items()
            if "RBV" not in name and not name.startswith("nmEnerg")
        ]
        for device in non_rbv_devices:
            self.assertTrue(device.importer)

    def test_map_creates_normalized_average_channel_objects(self):
        channel_name = "K0617:gw24126chan1"
        normalized_channel = data.SinglePointNormalizedChannelData()
        normalized_channel.importer.append(MockDatasetImporter())
        self.source.scan_modules[2].data[channel_name] = normalized_channel
        self.mapper.map(source=self.source)
        self.assertIsInstance(
            self.mapper.source.scan_modules[1].data[channel_name],
            data.AverageNormalizedChannelData,
        )

    def test_map_maps_skipdata_metadata_for_average_channels(self):
        n_averages = 42
        self.source.scan_modules[2].data[
            "skipdata"
        ].metadata.n_averages = n_averages
        self.mapper.map(source=self.source)
        non_rbv_devices = [
            device
            for name, device in self.mapper.source.scan_modules[
                1
            ].data.items()
            if "RBV" not in name and not name.startswith("nmEnerg")
        ]
        for device in non_rbv_devices:
            self.assertEqual(device.metadata.n_averages, n_averages)

    def test_mapping_skipdata_metadata_does_not_change_pv(self):
        self.source.scan_modules[2].data["skipdata"].metadata.pv = "foo"
        channel_name = "K0617:gw24126chan1"
        normalized_channel = data.SinglePointNormalizedChannelData()
        normalized_channel.metadata.pv = channel_name
        normalized_channel.importer.append(MockDatasetImporter())
        self.source.scan_modules[2].data[channel_name] = normalized_channel
        self.mapper.map(source=self.source)
        self.assertEqual(
            channel_name,
            self.mapper.source.scan_modules[1].data[channel_name].metadata.pv,
        )

    def test_map_adds_preprocessing_step_to_parent_devices(self):
        self.source.scan_modules[2].data["skipdata"].position_counts = (
            np.asarray([2, 3, 5, 6, 7, 9, 10, 11])
        )
        dataset = self.source.scan_modules[1].data["nmEnerg:io2600wl2e.A"]
        preprocessing_step = preprocessing.SelectPositions()
        dataset.importer.append(MockDatasetImporter())
        dataset.importer[0].preprocessing.append(preprocessing_step)
        self.mapper.map(source=self.source)
        device = self.mapper.source.scan_modules[1].data[
            "nmEnerg:io2600wl2e.A"
        ]
        self.assertIsInstance(
            device.importer[0].preprocessing[0],
            preprocessing.SelectPositions,
        )
        np.testing.assert_array_equal(
            np.asarray([1, 4, 8]),
            device.importer[0].preprocessing[0].position_counts,
        )

    def test_map_sets_positions_in_parent_scan_module(self):
        self.source.scan_modules[2].data["skipdata"].position_counts = (
            np.asarray([2, 3, 5, 6, 7, 9, 10, 11])
        )
        self.mapper.map(source=self.source)
        np.testing.assert_array_equal(
            np.asarray([1, 4, 8]), self.source.scan_modules[1].position_counts
        )

    def test_map_two_mpskips_adds_preprocessing_step_to_parent_devices(self):
        self.source.scan.scan = MockScanMultipleSkip()
        self.source.scan.scan.add_scan_modules()
        self.source.add_scan_modules()
        self.source.scan_modules[2].data["skipdata"] = data.SkipData()
        self.source.scan_modules[5].data["skipdata"] = data.SkipData()
        self.source.scan_modules[2].data["skipdata"].position_counts = (
            np.asarray([2, 3, 5, 6, 7, 9, 10, 11])
        )
        self.source.scan_modules[5].data["skipdata"].position_counts = (
            np.asarray([14, 15, 16, 18, 19, 21, 22, 23])
        )
        dataset = self.source.scan_modules[1].data["nmEnerg:io2600wl2e.A"]
        preprocessing_step = preprocessing.SelectPositions()
        dataset.importer.append(MockDatasetImporter())
        dataset.importer[0].preprocessing.append(preprocessing_step)
        dataset = self.source.scan_modules[4].data["nmEnerg:io2600wl2e.A"]
        preprocessing_step = preprocessing.SelectPositions()
        dataset.importer.append(MockDatasetImporter())
        dataset.importer[0].preprocessing.append(preprocessing_step)
        self.mapper.map(source=self.source)
        device = self.mapper.source.scan_modules[1].data[
            "nmEnerg:io2600wl2e.A"
        ]
        self.assertIsInstance(
            device.importer[0].preprocessing[0],
            preprocessing.SelectPositions,
        )
        np.testing.assert_array_equal(
            np.asarray([1, 4, 8]),
            device.importer[0].preprocessing[0].position_counts,
        )
        device = self.mapper.source.scan_modules[4].data[
            "nmEnerg:io2600wl2e.A"
        ]
        self.assertIsInstance(
            device.importer[0].preprocessing[0],
            preprocessing.SelectPositions,
        )
        np.testing.assert_array_equal(
            np.asarray([13, 17, 20]),
            device.importer[0].preprocessing[0].position_counts,
        )

    def test_map_two_mpskips_sets_positions_in_parent_scan_module(self):
        self.source.scan.scan = MockScanMultipleSkip()
        self.source.scan.scan.add_scan_modules()
        self.source.add_scan_modules()
        self.source.scan_modules[2].data["skipdata"] = data.SkipData()
        self.source.scan_modules[5].data["skipdata"] = data.SkipData()
        self.source.scan_modules[2].data["skipdata"].position_counts = (
            np.asarray([2, 3, 5, 6, 7, 9, 10, 11])
        )
        self.source.scan_modules[5].data["skipdata"].position_counts = (
            np.asarray([14, 15, 16, 18, 19, 21, 22, 23])
        )
        self.mapper.map(source=self.source)
        np.testing.assert_array_equal(
            np.asarray([1, 4, 8]), self.source.scan_modules[1].position_counts
        )
