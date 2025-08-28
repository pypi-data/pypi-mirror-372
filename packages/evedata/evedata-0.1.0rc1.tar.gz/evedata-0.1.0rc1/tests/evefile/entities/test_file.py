import contextlib
import datetime
import unittest
from io import StringIO

from evedata.evefile.entities import file, data


class TestFile(unittest.TestCase):
    def setUp(self):
        self.file = file.File()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "log_messages",
            "scan",
            "scan_modules",
            "snapshots",
            "monitors",
            "position_timestamps",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.file, attribute))


class TestMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = file.Metadata()

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
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))

    def test_print_prints_attribute_names(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            print(self.metadata)
        output = temp_stdout.getvalue().strip()
        attributes = [
            item for item in dir(self.metadata) if not item.startswith("_")
        ]
        for attribute in attributes:
            self.assertIn(attribute, output)


class TestScan(unittest.TestCase):
    def setUp(self):
        self.scan = file.Scan()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "author",
            "filename",
            "version",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.scan, attribute))


class TestLogMessage(unittest.TestCase):
    def setUp(self):
        self.log_message = file.LogMessage()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = ["timestamp", "message"]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.log_message, attribute))

    def test_from_string_sets_timestamp_and_message(self):
        string = "2024-07-25T10:04:03: Lorem ipsum"
        self.log_message.from_string(string)
        timestamp, message = string.split(": ", maxsplit=1)
        self.assertEqual(
            datetime.datetime.fromisoformat(timestamp),
            self.log_message.timestamp,
        )
        self.assertEqual(message, self.log_message.message)

    def test_print_prints_log_message(self):
        string = "2024-07-25T10:04:03: Lorem ipsum"
        self.log_message.from_string(string)
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            print(self.log_message)
        output = temp_stdout.getvalue().strip()
        self.assertEqual(string, output)


class TestScanModule(unittest.TestCase):
    def setUp(self):
        self.scan_module = file.ScanModule()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "id",
            "parent",
            "appended",
            "nested",
            "data",
            "position_counts",
            "device_names",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.scan_module, attribute))

    def test_device_names_returns_list_of_device_names(self):
        devices = {"foo": "foo:id", "bar": "bar:id"}
        for name, device_id in devices.items():
            device_data = data.MeasureData()
            device_data.metadata.name = name
            self.scan_module.data[device_id] = device_data
        self.assertDictEqual(devices, self.scan_module.device_names)
