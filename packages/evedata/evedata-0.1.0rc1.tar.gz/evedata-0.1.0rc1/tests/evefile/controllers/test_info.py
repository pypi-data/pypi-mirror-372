import contextlib
import io
import unittest

import numpy as np

from evedata.evefile.controllers import info
from evedata.evefile.entities import file, data


class TestScanModuleStructure(unittest.TestCase):
    def setUp(self):
        self.scan_module_structure = info.ScanModuleStructure()

    def test_instantiate_class(self):
        pass

    def test_instantiate_with_scan_modules_sets_scan_modules(self):
        scan_module = file.ScanModule()
        scan_module.id = 1
        scan_module.name = "Diodes"
        scan_module.position_counts = np.asarray([1])
        scan_modules = {1: scan_module}
        scan_module_structure = info.ScanModuleStructure(
            scan_modules=scan_modules
        )
        self.assertTrue(scan_module_structure.scan_modules)

    def test_create_sets_structure(self):
        scan_module = file.ScanModule()
        scan_module.id = 1
        scan_module.name = "Diodes"
        scan_module.position_counts = np.asarray([1])
        self.scan_module_structure.scan_modules = {1: scan_module}
        self.scan_module_structure.create()
        self.assertTrue(self.scan_module_structure.structure)

    def test_create_without_scan_modules_raises(self):
        self.scan_module_structure.scan_modules = None
        with self.assertRaisesRegex(ValueError, "No scan modules"):
            self.scan_module_structure.create()

    def test_create_sets_metadata_of_scan_module(self):
        scan_module = file.ScanModule()
        scan_module.id = 1
        scan_module.name = "Diodes"
        scan_module.position_counts = np.asarray([1, 2, 3])
        self.scan_module_structure.scan_modules = {1: scan_module}
        self.scan_module_structure.create()
        self.assertIn(
            f"{self.scan_module_structure.scan_module_marker}"
            f" {scan_module.id}:"
            f" {scan_module.name}",
            self.scan_module_structure.structure[0],
        )

    def test_create_sets_metadata_of_scan_modules(self):
        scan_module1 = file.ScanModule()
        scan_module1.id = 1
        scan_module1.name = "Diodes"
        scan_module1.appended = 2
        scan_module1.position_counts = np.asarray([1, 2, 3])
        self.scan_module_structure.scan_modules[scan_module1.id] = (
            scan_module1
        )
        scan_module2 = file.ScanModule()
        scan_module2.id = 2
        scan_module2.name = "MB"
        scan_module2.position_counts = np.asarray([4, 5, 6, 7, 8])
        self.scan_module_structure.scan_modules[scan_module2.id] = (
            scan_module2
        )
        self.scan_module_structure.create()
        self.assertIn(
            f"{self.scan_module_structure.scan_module_marker} "
            f"{scan_module1.id}: {scan_module1.name} - #"
            f"{len(scan_module1.position_counts)} ["
            f"{scan_module1.position_counts[0]}..{scan_module1.position_counts[-1]}]",
            self.scan_module_structure.structure[0],
        )
        self.assertIn(
            f"{self.scan_module_structure.scan_module_marker} "
            f"{scan_module2.id}: {scan_module2.name} - #"
            f"{len(scan_module2.position_counts)} ["
            f"{scan_module2.position_counts[0]}..{scan_module2.position_counts[-1]}]",
            self.scan_module_structure.structure[1],
        )

    def test_create_with_single_position_in_scan_module(self):
        scan_module = file.ScanModule()
        scan_module.id = 1
        scan_module.name = "Diodes"
        scan_module.position_counts = np.asarray([1])
        self.scan_module_structure.scan_modules = {1: scan_module}
        self.scan_module_structure.create()
        self.assertIn(
            f"{self.scan_module_structure.scan_module_marker} "
            f"{scan_module.id}: {scan_module.name} - #"
            f"{len(scan_module.position_counts)} [{scan_module.position_counts[0]}]",
            self.scan_module_structure.structure[0],
        )

    def test_create_with_multiple_positions_in_scan_module(self):
        scan_module = file.ScanModule()
        scan_module.id = 1
        scan_module.name = "Diodes"
        scan_module.position_counts = np.asarray([1, 2, 3, 4])
        self.scan_module_structure.scan_modules = {1: scan_module}
        self.scan_module_structure.create()
        self.assertIn(
            f"{self.scan_module_structure.scan_module_marker} "
            f"{scan_module.id}: {scan_module.name} - #"
            f"{len(scan_module.position_counts)} [{scan_module.position_counts[0]}.."
            f"{scan_module.position_counts[-1]}]",
            self.scan_module_structure.structure[0],
        )

    def test_create_with_nested_scan_modules_adds_indentation(self):
        scan_module1 = file.ScanModule()
        scan_module1.id = 1
        scan_module1.name = "Diodes"
        scan_module1.nested = 2
        scan_module1.position_counts = np.asarray([1, 2, 3])
        self.scan_module_structure.scan_modules[scan_module1.id] = (
            scan_module1
        )
        scan_module2 = file.ScanModule()
        scan_module2.id = 2
        scan_module2.name = "MB"
        scan_module2.position_counts = np.asarray([4, 5, 6, 7, 8])
        self.scan_module_structure.scan_modules[scan_module2.id] = (
            scan_module2
        )
        self.scan_module_structure.create()
        self.assertIn(
            f"{self.scan_module_structure.scan_module_marker} "
            f"{scan_module1.id}: {scan_module1.name} - #"
            f"{len(scan_module1.position_counts)} ["
            f"{scan_module1.position_counts[0]}..{scan_module1.position_counts[-1]}]",
            self.scan_module_structure.structure[0],
        )
        self.assertIn(
            f"{self.scan_module_structure.indentation}"
            f"{self.scan_module_structure.scan_module_marker} "
            f"{scan_module2.id}: {scan_module2.name} - #"
            f"{len(scan_module2.position_counts)} ["
            f"{scan_module2.position_counts[0]}..{scan_module2.position_counts[-1]}]",
            self.scan_module_structure.structure[1],
        )

    def test_create_with_de_nested_scan_modules_removes_indentation(self):
        scan_module1 = file.ScanModule()
        scan_module1.id = 1
        scan_module1.name = "Diodes"
        scan_module1.nested = 2
        scan_module1.appended = 3
        scan_module1.position_counts = np.asarray([1, 2, 3])
        self.scan_module_structure.scan_modules[scan_module1.id] = (
            scan_module1
        )
        scan_module2 = file.ScanModule()
        scan_module2.id = 2
        scan_module2.name = "MB"
        scan_module2.position_counts = np.asarray([4, 5, 6, 7, 8])
        self.scan_module_structure.scan_modules[scan_module2.id] = (
            scan_module2
        )
        scan_module3 = file.ScanModule()
        scan_module3.id = 3
        scan_module3.name = "DetX"
        scan_module3.position_counts = np.asarray([9, 10])
        self.scan_module_structure.scan_modules[scan_module3.id] = (
            scan_module3
        )
        self.scan_module_structure.create()
        self.assertIn(
            f"{self.scan_module_structure.scan_module_marker} "
            f"{scan_module1.id}: {scan_module1.name} - #"
            f"{len(scan_module1.position_counts)} ["
            f"{scan_module1.position_counts[0]}..{scan_module1.position_counts[-1]}]",
            self.scan_module_structure.structure[0],
        )
        self.assertIn(
            f"{self.scan_module_structure.indentation}"
            f"{self.scan_module_structure.scan_module_marker} "
            f"{scan_module2.id}: {scan_module2.name} - #"
            f"{len(scan_module2.position_counts)} ["
            f"{scan_module2.position_counts[0]}..{scan_module2.position_counts[-1]}]",
            self.scan_module_structure.structure[1],
        )
        self.assertEqual(
            f"{self.scan_module_structure.scan_module_marker} "
            f"{scan_module3.id}: {scan_module3.name} - #"
            f"{len(scan_module3.position_counts)} ["
            f"{scan_module3.position_counts[0]}..{scan_module3.position_counts[-1]}]",
            self.scan_module_structure.structure[2],
        )

    def test_create_with_axis_in_scan_module_adds_axis(self):
        scan_module = file.ScanModule()
        scan_module.id = 1
        scan_module.name = "Diodes"
        scan_module.position_counts = np.asarray([1])
        axis = data.AxisData()
        axis.metadata.id = "MotK7002:gw24807Col1scanner"
        axis.metadata.name = "Matrix_input"
        scan_module.data[axis.metadata.id] = axis
        self.scan_module_structure.scan_modules = {1: scan_module}
        self.scan_module_structure.create()
        self.assertIn(
            f"{self.scan_module_structure.device_indentation}"
            f"{self.scan_module_structure.axis_marker} "
            f"{axis.metadata.name} ({axis.metadata.id})",
            self.scan_module_structure.structure[1],
        )

    def test_create_with_channel_in_scan_module_adds_channel(self):
        scan_module = file.ScanModule()
        scan_module.id = 1
        scan_module.name = "Diodes"
        scan_module.position_counts = np.asarray([1])
        channel = data.ChannelData()
        channel.metadata.id = "K0617:gw24825chan1"
        channel.metadata.name = "Keithley_MSC"
        scan_module.data[channel.metadata.id] = channel
        self.scan_module_structure.scan_modules = {1: scan_module}
        self.scan_module_structure.create()
        self.assertIn(
            f"{self.scan_module_structure.device_indentation}"
            f"{self.scan_module_structure.channel_marker} "
            f"{channel.metadata.name} ({channel.metadata.id})",
            self.scan_module_structure.structure[1],
        )

    def test_create_with_axis_in_nested_scan_module_indents_axis(self):
        scan_module1 = file.ScanModule()
        scan_module1.id = 1
        scan_module1.name = "Diodes"
        scan_module1.nested = 2
        scan_module1.position_counts = np.asarray([1, 2, 3])
        self.scan_module_structure.scan_modules[scan_module1.id] = (
            scan_module1
        )
        scan_module2 = file.ScanModule()
        scan_module2.id = 2
        scan_module2.name = "MB"
        scan_module2.position_counts = np.asarray([4, 5, 6, 7, 8])
        self.scan_module_structure.scan_modules[scan_module2.id] = (
            scan_module2
        )
        axis = data.AxisData()
        axis.metadata.id = "MotK7002:gw24807Col1scanner"
        axis.metadata.name = "Matrix_input"
        scan_module2.data[axis.metadata.id] = axis
        self.scan_module_structure.create()
        self.assertIn(
            f"{self.scan_module_structure.indentation}"
            f"{self.scan_module_structure.device_indentation}"
            f"{self.scan_module_structure.axis_marker} "
            f"{axis.metadata.name} ({axis.metadata.id})",
            self.scan_module_structure.structure[2],
        )

    def test_structure_is_readonly(self):
        with self.assertRaises(AttributeError):
            self.scan_module_structure.structure = "Foo"  # noqa

    def test_print_creates_correct_output(self):
        scan_module = file.ScanModule()
        scan_module.id = 1
        scan_module.name = "Diodes"
        scan_module.position_counts = np.asarray([1, 2, 3])
        self.scan_module_structure.scan_modules = {1: scan_module}
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.scan_module_structure.print()
        self.assertIn(
            f"{self.scan_module_structure.scan_module_marker} "
            f"{scan_module.id}: {scan_module.name} - #"
            f"{len(scan_module.position_counts)} ["
            f"{scan_module.position_counts[0]}..{scan_module.position_counts[-1]}]",
            output.getvalue(),
        )
