import os
import struct
import unittest
import zlib

import h5py
import numpy as np

import evedata.evefile.entities.data
from evedata.measurement.boundaries import measurement
from evedata.measurement.controllers import joining


SCML = """<?xml version="1.0" encoding="UTF-8"?>
<tns:scml xsi:schemaLocation="http://www.ptb.de/epics/SCML scml.xsd"
    xmlns:tns="http://www.ptb.de/epics/SCML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <location>TEST</location>
    <version>9.2</version>
    <scan>
        <repeatcount>0</repeatcount>
        <savefilename>/messung/test/daten/2022/kw35/u49-test</savefilename>
        <confirmsave>false</confirmsave>
        <autonumber>true</autonumber>
        <savescandescription>false</savescandescription>
        <chain id="1">
            <pauseconditions/>
            <scanmodules>
                <scanmodule id="1">
                    <name>SM 1</name>
                    <xpos>228</xpos>
                    <ypos>124</ypos>
                    <parent>0</parent>
                    <appended>2</appended>
                    <classic>
                        <valuecount>1</valuecount>
                        <settletime>0.0</settletime>
                        <triggerdelay>0.0</triggerdelay>
                        <triggerconfirmaxis>false</triggerconfirmaxis>
                        <triggerconfirmchannel>false</triggerconfirmchannel>
                        <smaxis>
                            <axisid>Counter-mot</axisid>
                            <stepfunction>Positionlist</stepfunction>
                            <positionmode>absolute</positionmode>
                            <positionlist>1, 2,3, 4 ,5</positionlist>
                        </smaxis>
                    </classic>
                </scanmodule>
                <scanmodule id="2">
                    <name>SM 2</name>
                    <xpos>228</xpos>
                    <ypos>124</ypos>
                    <parent>1</parent>
                    <classic>
                        <valuecount>1</valuecount>
                        <settletime>0.0</settletime>
                        <triggerdelay>0.0</triggerdelay>
                        <triggerconfirmaxis>false</triggerconfirmaxis>
                        <triggerconfirmchannel>false</triggerconfirmchannel>
                        <smaxis>
                            <axisid>Counter-mot</axisid>
                            <stepfunction>Positionlist</stepfunction>
                            <positionmode>absolute</positionmode>
                            <positionlist>1, 2,3, 4 ,5</positionlist>
                        </smaxis>
                    </classic>
                </scanmodule>
            </scanmodules>
        </chain>
    </scan>
    <plugins/>
    <detectors/>
    <motors/>
    <devices/>
</tns:scml>"""


class DummyHDF5File:
    def __init__(self, filename=""):
        self.filename = filename

    def create(self, set_preferred=True, add_snapshot=False, scml=True):
        with h5py.File(self.filename, "w") as file:
            file.attrs["EVEH5Version"] = np.bytes_(["7"])
            file.attrs["Version"] = np.bytes_(["2.0"])
            file.attrs["XMLversion"] = np.bytes_(["9.2"])
            file.attrs["Comment"] = np.bytes_([""])
            file.attrs["Location"] = np.bytes_(["Unittest"])
            file.attrs["StartTimeISO"] = np.bytes_(["2024-06-03T12:01:32"])
            file.attrs["EndTimeISO"] = np.bytes_(["2024-06-03T12:01:37"])
            file.attrs["Simulation"] = np.bytes_(["no"])
            c1 = file.create_group("c1")
            if set_preferred:
                c1.attrs["preferredAxis"] = np.bytes_(["SimMot:01"])
                c1.attrs["preferredChannel"] = np.bytes_(["SimChan:01"])
            main = c1.create_group("main")
            meta = c1.create_group("meta")
            snapshot = c1.create_group("snapshot")
            simmot = main.create_dataset(
                "SimMot:01",
                data=np.ndarray(
                    [5],
                    dtype=np.dtype(
                        [("PosCounter", "<i4"), ("SimMot:01", "<f8")]
                    ),
                ),
            )
            simmot["PosCounter"] = np.linspace(1, 5, 5)
            simmot["SimMot:01"] = np.random.random(5)
            simmot.attrs["Name"] = np.bytes_(["foo"])
            simmot.attrs["Unit"] = np.bytes_(["eV"])
            simmot.attrs["Access"] = np.bytes_(["ca:foobar"])
            simmot.attrs["DeviceType"] = np.bytes_(["Axis"])
            simmot2 = main.create_dataset(
                "SimMot:02",
                data=np.ndarray(
                    [7],
                    dtype=np.dtype(
                        [("PosCounter", "<i4"), ("SimMot:02", "<f8")]
                    ),
                ),
            )
            simmot2["PosCounter"] = np.linspace(2, 8, 7)
            simmot2["SimMot:02"] = np.random.random(7)
            simmot2.attrs["Name"] = np.bytes_(["baf"])
            simmot2.attrs["Unit"] = np.bytes_(["nm"])
            simmot2.attrs["Access"] = np.bytes_(["ca:foobaz"])
            simmot2.attrs["DeviceType"] = np.bytes_(["Axis"])
            simchan = main.create_dataset(
                "SimChan:01",
                data=np.ndarray(
                    [5],
                    dtype=np.dtype(
                        [("PosCounter", "<i4"), ("SimChan:01", "<f8")]
                    ),
                ),
            )
            simchan["PosCounter"] = np.linspace(1, 5, 5)
            simchan["SimChan:01"] = np.random.random(5)
            simchan.attrs["Name"] = np.bytes_(["bar"])
            simchan.attrs["Unit"] = np.bytes_(["A"])
            simchan.attrs["Access"] = np.bytes_(["ca:barbaz"])
            simchan.attrs["DeviceType"] = np.bytes_(["Channel"])
            simchan.attrs["Detectortype"] = np.bytes_(["Standard"])
            simchan2 = main.create_dataset(
                "SimChan:02",
                data=np.ndarray(
                    [7],
                    dtype=np.dtype(
                        [("PosCounter", "<i4"), ("SimChan:02", "<f8")]
                    ),
                ),
            )
            simchan2["PosCounter"] = np.linspace(2, 8, 7)
            simchan2["SimChan:02"] = np.random.random(7)
            simchan2.attrs["Name"] = np.bytes_(["baz"])
            simchan2.attrs["Unit"] = np.bytes_(["mA"])
            simchan2.attrs["Access"] = np.bytes_(["ca:bazfoo"])
            simchan2.attrs["DeviceType"] = np.bytes_(["Channel"])
            simchan2.attrs["Detectortype"] = np.bytes_(["Standard"])
            data = np.ndarray(
                [8],
                dtype=np.dtype(
                    [("PosCounter", "<i4"), ("PosCountTimer", "<i4")]
                ),
            )
            data["PosCounter"] = np.linspace(1, 8, 8)
            data["PosCountTimer"] = np.linspace(42, 826, 8)
            poscounttimer = meta.create_dataset("PosCountTimer", data=data)
            poscounttimer.attrs["Unit"] = np.bytes_(["msecs"])

            log_messages = [
                b"2024-07-25T10:04:03: Lorem ipsum",
                b"2024-07-25T10:05:23: dolor sit amet",
            ]
            file.create_dataset("LiveComment", data=np.asarray(log_messages))
            if add_snapshot:
                simmot = snapshot.create_dataset(
                    "SimMot:01",
                    data=np.ndarray(
                        [2],
                        dtype=np.dtype(
                            [("PosCounter", "<i4"), ("SimMot:01", "<f8")]
                        ),
                    ),
                )
                simmot["PosCounter"] = np.asarray([1, 9])
                simmot["SimMot:01"] = np.random.random(2)
                simmot.attrs["Name"] = np.bytes_(["foo"])
                simmot.attrs["Unit"] = np.bytes_(["eV"])
                simmot.attrs["Access"] = np.bytes_(["ca:foobar"])
                simmot.attrs["DeviceType"] = np.bytes_(["Axis"])
                simchan = snapshot.create_dataset(
                    "SimChan:01",
                    data=np.ndarray(
                        [2],
                        dtype=np.dtype(
                            [("PosCounter", "<i4"), ("SimChan:01", "<f8")]
                        ),
                    ),
                )
                simchan["PosCounter"] = np.asarray([1, 9])
                simchan["SimChan:01"] = np.random.random(2)
                simchan.attrs["Name"] = np.bytes_(["bar"])
                simchan.attrs["Unit"] = np.bytes_(["A"])
                simchan.attrs["Access"] = np.bytes_(["ca:barbaz"])
                simchan.attrs["DeviceType"] = np.bytes_(["Channel"])
                simchan.attrs["Detectortype"] = np.bytes_(["Standard"])
                simchan3 = snapshot.create_dataset(
                    "SimChan:03",
                    data=np.ndarray(
                        [2],
                        dtype=np.dtype(
                            [("PosCounter", "<i4"), ("SimChan:03", "<f8")]
                        ),
                    ),
                )
                simchan3["PosCounter"] = np.asarray([1, 9])
                simchan3["SimChan:03"] = np.random.random(2)
                simchan3.attrs["Name"] = np.bytes_(["bazfoo"])
                simchan3.attrs["Unit"] = np.bytes_(["A"])
                simchan3.attrs["Access"] = np.bytes_(["ca:bazfoo"])
                simchan3.attrs["DeviceType"] = np.bytes_(["Channel"])
                simchan3.attrs["Detectortype"] = np.bytes_(["Standard"])
        if scml:
            self.add_scml()

    def add_scml(self):
        with open(self.filename, "rb") as file:
            hdf5_contents = file.read()
        with open(self.filename, "wb") as file:
            file.write(b"EVEcSCML")
            compressed_scml = zlib.compress(bytes(SCML, "utf8"))
            file.write(struct.pack("!L", len(compressed_scml)))
            file.write(struct.pack("!L", len(SCML)))
            file.write(compressed_scml)
            offset = 512
            if len(compressed_scml) > offset:
                offset = 2 ** (len(compressed_scml) - 1).bit_length()
            file.write(bytearray(offset - len(compressed_scml) - 16))
            file.write(hdf5_contents)


class TestMeasurement(unittest.TestCase):
    def setUp(self):
        self.measurement = measurement.Measurement()
        self.filename = "file.h5"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "scan_modules",
            "machine",
            "beamline",
            "device_snapshots",
            "metadata",
            "scan",
            "station",
            "log_messages",
            "data",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.measurement, attribute))

    def test_setting_filename_sets_metadata_filename(self):
        self.measurement.filename = self.filename
        self.assertEqual(self.measurement.metadata.filename, self.filename)

    def test_load_with_filename_sets_metadata_filename(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        self.assertEqual(self.filename, self.measurement.metadata.filename)

    def test_load_without_filename_but_filename_set_keeps_filename(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.filename = self.filename
        self.measurement.load()
        self.assertEqual(self.filename, self.measurement.metadata.filename)

    def test_load_sets_file_metadata(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        root_mappings = {
            "eveh5_version": "7",
            "measurement_station": "Unittest",
        }
        for key, value in root_mappings.items():
            with self.subTest(key=key, val=value):
                self.assertEqual(
                    getattr(self.measurement.metadata, key), value
                )

    def test_init_with_filename_sets_metadata_filename(self):
        file = measurement.Measurement(filename=self.filename)
        self.assertEqual(self.filename, file.metadata.filename)

    def test_load_sets_log_messages(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        self.assertTrue(self.measurement.log_messages)

    def test_load_sets_scan_modules(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        self.assertTrue(self.measurement.scan_modules)
        for item in self.measurement.scan_modules.values():
            self.assertIsInstance(
                item, evedata.evefile.entities.file.ScanModule
            )

    def test_load_sets_device_snapshots(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(add_snapshot=True)
        self.measurement.load(filename=self.filename)
        self.assertTrue(self.measurement.device_snapshots)
        for item in self.measurement.device_snapshots.values():
            self.assertIsInstance(
                item, evedata.evefile.entities.data.MeasureData
            )

    def test_load_sets_data_to_preferred_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.measurement.load(filename=self.filename)
        np.testing.assert_array_equal(
            self.measurement.data.data,
            self.measurement.scan_modules["main"].data["SimChan:01"].data,
        )
        np.testing.assert_array_equal(
            self.measurement.data.axes[0].values,
            self.measurement.scan_modules["main"].data["SimMot:01"].data,
        )

    def test_load_does_not_set_data_if_no_preferred_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(set_preferred=False)
        self.measurement.load(filename=self.filename)
        self.assertEqual(0, len(self.measurement.data.data))
        self.assertEqual(0, len(self.measurement.data.axes[0].values))

    def test_load_with_preferred_data_sets_axis_metadata(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.measurement.load(filename=self.filename)
        self.assertEqual(
            self.measurement.scan_modules["main"]
            .data[self.measurement.metadata.preferred_axis]
            .metadata.name,
            self.measurement.data.axes[0].quantity,
        )
        self.assertEqual(
            self.measurement.scan_modules["main"]
            .data[self.measurement.metadata.preferred_axis]
            .metadata.unit,
            self.measurement.data.axes[0].unit,
        )
        self.assertEqual(
            self.measurement.scan_modules["main"]
            .data[self.measurement.metadata.preferred_channel]
            .metadata.name,
            self.measurement.data.axes[1].quantity,
        )
        self.assertEqual(
            self.measurement.scan_modules["main"]
            .data[self.measurement.metadata.preferred_channel]
            .metadata.unit,
            self.measurement.data.axes[1].unit,
        )

    def test_load_maps_scan(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.measurement.load(filename=self.filename)
        self.assertTrue(self.measurement.scan)
        self.assertTrue("9.2", self.measurement.scan.version)

    def test_preferred_data_sets_current_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.measurement.load(filename=self.filename)
        self.assertEqual("SimChan:01", self.measurement.current_data)

    def test_preferred_data_sets_current_axes(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.measurement.load(filename=self.filename)
        self.assertListEqual(["SimMot:01"], self.measurement.current_axes)

    def test_set_data_sets_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.measurement.load(filename=self.filename)
        name = "SimChan:02"
        self.measurement.set_data(name=name)
        np.testing.assert_array_equal(
            self.measurement.data.data,
            self.measurement.scan_modules["main"].data[name].data,
        )

    def test_set_data_sets_current_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.measurement.load(filename=self.filename)
        name = "SimChan:02"
        self.measurement.set_data(name=name)
        self.assertEqual(name, self.measurement.current_data)

    def test_current_data_is_read_only(self):
        with self.assertRaises(AttributeError):
            self.measurement.current_data = "foo"  # noqa

    def test_get_current_data_returns_tuple(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.measurement.load(filename=self.filename)
        self.assertEqual(
            (self.measurement.current_data, "data"),
            self.measurement.get_current_data(),
        )

    def test_get_current_axes_returns_list_of_tuples(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.measurement.load(filename=self.filename)
        self.assertListEqual(
            [(self.measurement.current_axes[0], "data")],
            self.measurement.get_current_axes(),
        )

    def test_set_data_sets_axis_metadata(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.measurement.load(filename=self.filename)
        name = "SimChan:02"
        self.measurement.set_data(name=name)
        self.assertEqual(
            self.measurement.scan_modules["main"].data[name].metadata.name,
            self.measurement.data.axes[1].quantity,
        )
        self.assertEqual(
            self.measurement.scan_modules["main"].data[name].metadata.unit,
            self.measurement.data.axes[1].unit,
        )

    def test_set_data_with_name_sets_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.measurement.load(filename=self.filename)
        dataset_id = "SimChan:02"
        name = (
            self.measurement.scan_modules["main"]
            .data[dataset_id]
            .metadata.name
        )
        self.measurement.set_data(name=name)
        np.testing.assert_array_equal(
            self.measurement.data.data,
            self.measurement.scan_modules["main"].data[dataset_id].data,
        )

    def test_set_axes_sets_axes(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.measurement.load(filename=self.filename)
        name = "SimMot:02"
        self.measurement.set_axes(names=[name], scan_module="main")
        common_elements = (
            self.measurement.scan_modules["main"]
            .data[name]
            .position_counts[
                np.isin(
                    self.measurement.scan_modules["main"]
                    .data[name]
                    .position_counts,
                    self.measurement.scan_modules["main"]
                    .data[self.measurement.current_data]
                    .position_counts,
                )
            ]
        )
        data_indices = np.searchsorted(
            self.measurement.scan_modules["main"]
            .data[self.measurement.current_data]
            .position_counts,
            common_elements,
        )
        axes_indices = np.searchsorted(
            self.measurement.scan_modules["main"].data[name].position_counts,
            common_elements,
        )
        np.testing.assert_array_equal(
            self.measurement.data.axes[0].values[data_indices],
            self.measurement.scan_modules["main"]
            .data[name]
            .data[axes_indices],
        )

    def test_set_axes_sets_current_axes(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.measurement.load(filename=self.filename)
        name = "SimMot:02"
        self.measurement.set_axes(names=[name], scan_module="main")
        self.assertListEqual([name], self.measurement.current_axes)

    def test_current_axes_is_read_only(self):
        with self.assertRaises(AttributeError):
            self.measurement.current_axes = ["foo"]  # noqa

    def test_set_axes_sets_axis_metadata(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.measurement.load(filename=self.filename)
        name = "SimMot:02"
        self.measurement.set_axes(names=[name], scan_module="main")
        self.assertEqual(
            self.measurement.scan_modules["main"].data[name].metadata.name,
            self.measurement.data.axes[0].quantity,
        )
        self.assertEqual(
            self.measurement.scan_modules["main"].data[name].metadata.unit,
            self.measurement.data.axes[0].unit,
        )

    def test_set_axes_with_name_sets_axes(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.measurement.load(filename=self.filename)
        dataset_id = "SimMot:02"
        name = (
            self.measurement.scan_modules["main"]
            .data[dataset_id]
            .metadata.name
        )
        self.measurement.set_axes(names=[name], scan_module="main")
        common_elements = (
            self.measurement.scan_modules["main"]
            .data[dataset_id]
            .position_counts[
                np.isin(
                    self.measurement.scan_modules["main"]
                    .data[dataset_id]
                    .position_counts,
                    self.measurement.scan_modules["main"]
                    .data[self.measurement.current_data]
                    .position_counts,
                )
            ]
        )
        data_indices = np.searchsorted(
            self.measurement.scan_modules["main"]
            .data[self.measurement.current_data]
            .position_counts,
            common_elements,
        )
        axes_indices = np.searchsorted(
            self.measurement.scan_modules["main"]
            .data[dataset_id]
            .position_counts,
            common_elements,
        )
        np.testing.assert_array_equal(
            self.measurement.data.axes[0].values[data_indices],
            self.measurement.scan_modules["main"]
            .data[dataset_id]
            .data[axes_indices],
        )

    def test_get_name_returns_name(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.measurement.load(filename=self.filename)
        dataset_id = "SimMot:02"
        name = (
            self.measurement.scan_modules["main"]
            .data[dataset_id]
            .metadata.name
        )
        self.assertEqual(name, self.measurement.get_name(dataset_id))

    def test_get_name_with_list_returns_list_of_names(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.measurement.load(filename=self.filename)
        dataset_id = ["SimMot:02", "SimChan:01"]
        names = [
            self.measurement.scan_modules["main"].data[device].metadata.name
            for device in dataset_id
        ]
        self.assertListEqual(names, self.measurement.get_name(dataset_id))

    def test_set_data_if_no_preferred_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(set_preferred=False, scml=False)
        self.measurement.load(filename=self.filename)
        name = "SimChan:01"
        self.measurement.set_data(name=name)
        np.testing.assert_array_equal(
            self.measurement.data.data,
            self.measurement.scan_modules["main"].data[name].data,
        )

    def test_set_axes_if_no_preferred_data_raises(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(set_preferred=False)
        self.measurement.load(filename=self.filename)
        name = "SimMot:01"
        with self.assertRaisesRegex(ValueError, "No data to set axes for"):
            self.measurement.set_axes(names=[name])

    def test_set_data_with_field_name(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.measurement.load(filename=self.filename)
        name = "SimChan:01"
        field = "position_counts"
        self.measurement.set_data(name=name, field=field)
        np.testing.assert_array_equal(
            self.measurement.data.data,
            getattr(self.measurement.scan_modules["main"].data[name], field),
        )

    def test_set_axes_with_field_name(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.measurement.load(filename=self.filename)
        name = "SimMot:01"
        field = "position_counts"
        self.measurement.set_axes(
            names=[name], fields=[field], scan_module="main"
        )
        np.testing.assert_array_equal(
            self.measurement.data.axes[0].values,
            getattr(self.measurement.scan_modules["main"].data[name], field),
        )

    def test_set_axes_with_different_length_of_names_and_fields_raises(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.measurement.load(filename=self.filename)
        names = ["SimMot:01"]
        fields = ["position_counts", "data"]
        with self.assertRaisesRegex(
            IndexError, "Names and fields need to " "be of same length"
        ):
            self.measurement.set_axes(
                names=names, fields=fields, scan_module="main"
            )

    def test_set_data_joins_axes(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.measurement.load(filename=self.filename)
        name = "SimChan:02"
        self.measurement.set_data(name=name)
        common_positions = np.intersect1d(
            self.measurement.scan_modules["main"].data[name].position_counts,
            self.measurement.scan_modules["main"]
            .data[self.measurement.current_axes[0]]
            .position_counts,
        ).astype(int)
        axes_positions = np.isin(
            self.measurement.scan_modules["main"]
            .data[self.measurement.current_axes[0]]
            .position_counts,
            common_positions,
        )
        np.testing.assert_array_equal(
            self.measurement.data.axes[0].values[
                np.arange(len(axes_positions))[axes_positions] - 1
            ],
            self.measurement.scan_modules["main"]
            .data[self.measurement.current_axes[0]]
            .data[np.arange(len(axes_positions))[axes_positions]],
        )

    def test_set_axes_joins_axes(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.measurement.load(filename=self.filename)
        name = "SimMot:02"
        self.measurement.set_axes(names=[name], scan_module="main")
        common_positions = np.intersect1d(
            self.measurement.scan_modules["main"]
            .data[self.measurement.current_data]
            .position_counts,
            self.measurement.scan_modules["main"].data[name].position_counts,
        ).astype(int)
        axes_positions = np.isin(
            self.measurement.scan_modules["main"]
            .data[self.measurement.current_axes[0]]
            .position_counts,
            common_positions,
        )
        self.assertEqual(
            len(self.measurement.data.data),
            len(self.measurement.data.axes[0].values),
        )
        np.testing.assert_array_equal(
            self.measurement.data.axes[0].values[common_positions - 1],
            self.measurement.scan_modules["main"]
            .data[self.measurement.current_axes[0]]
            .data[axes_positions],
        )

    def test_join_type_returns_correct_type(self):
        self.assertEqual("AxesLastFill", self.measurement.join_type)

    def test_join_type_sets_join(self):
        self.measurement.join_type = "Join"
        self.assertIsInstance(self.measurement._join, joining.Join)
        self.assertFalse(
            isinstance(self.measurement._join, joining.AxesLastFill)
        )
