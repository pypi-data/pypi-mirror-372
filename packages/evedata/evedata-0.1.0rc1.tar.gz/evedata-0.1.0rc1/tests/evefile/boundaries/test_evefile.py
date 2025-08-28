import os
import struct
import unittest
import zlib

import h5py
import numpy as np

import evedata.evefile.entities.file
from evedata.evefile.boundaries import evefile


SCML = """<?xml version="1.0" encoding="UTF-8"?>
<tns:scml xsi:schemaLocation="http://www.ptb.de/epics/SCML scml.xsd"
    xmlns:tns="http://www.ptb.de/epics/SCML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <location>Test</location>
    <version>9.2</version>
    <scan>
        <repeatcount>42</repeatcount>
        <comment>test ccd time</comment>
        <savefilename>/messung/test/daten/2022/kw35/u49-test</savefilename>
        <confirmsave>false</confirmsave>
        <autonumber>true</autonumber>
        <savescandescription>true</savescandescription>
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
</tns:scml>"""


class DummyHDF5File:
    def __init__(self, filename=""):
        self.filename = filename

    def create(self, scml=True):
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
            main = c1.create_group("main")
            meta = c1.create_group("meta")
            simmot = main.create_dataset(
                "SimMot:01",
                data=np.ones(
                    [5],
                    dtype=np.dtype(
                        [("PosCounter", "<i4"), ("SimMot:01", "<f8")]
                    ),
                ),
            )
            simmot["PosCounter"] = np.linspace(1, 5, 5)
            simmot["SimMot:01"] = np.random.random(5)
            simmot.attrs["Name"] = np.bytes_(["foo"])
            simmot.attrs["Access"] = np.bytes_(["ca:foobar"])
            simmot.attrs["DeviceType"] = np.bytes_(["Axis"])
            simchan = main.create_dataset(
                "SimChan:01",
                data=np.ones(
                    [5],
                    dtype=np.dtype(
                        [("PosCounter", "<i4"), ("SimChan:01", "<f8")]
                    ),
                ),
            )
            simchan["PosCounter"] = np.linspace(1, 5, 5)
            simchan["SimChan:01"] = np.random.random(5)
            simchan.attrs["Name"] = np.bytes_(["bar"])
            simchan.attrs["Access"] = np.bytes_(["ca:barbaz"])
            simchan.attrs["DeviceType"] = np.bytes_(["Channel"])
            simchan.attrs["Detectortype"] = np.bytes_(["Standard"])
            data = np.ndarray(
                [10],
                dtype=np.dtype(
                    [("PosCounter", "<i4"), ("PosCountTimer", "<i4")]
                ),
            )
            poscounttimer = meta.create_dataset("PosCountTimer", data=data)
            poscounttimer.attrs["Unit"] = np.bytes_(["msecs"])
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


class TestEveFile(unittest.TestCase):
    def setUp(self):
        self.evefile = evefile.EveFile()
        self.filename = "file.h5"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "log_messages",
            "scan",
            "data",
            "snapshots",
            "monitors",
            "position_timestamps",
            "filename",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.evefile, attribute))

    def test_setting_filename_sets_metadata_filename(self):
        self.evefile.filename = self.filename
        self.assertEqual(self.evefile.metadata.filename, self.filename)

    def test_load_with_filename_sets_metadata_filename(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile.load(filename=self.filename)
        self.assertEqual(self.filename, self.evefile.metadata.filename)

    def test_load_without_filename_but_filename_set_keeps_filename(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile.filename = self.filename
        self.evefile.load()
        self.assertEqual(self.filename, self.evefile.metadata.filename)

    def test_load_sets_file_metadata(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile.load(filename=self.filename)
        root_mappings = {
            "eveh5_version": "7",
            "measurement_station": "Unittest",
        }
        for key, value in root_mappings.items():
            with self.subTest(key=key, val=value):
                self.assertEqual(getattr(self.evefile.metadata, key), value)

    def test_init_with_filename_sets_metadata_filename(self):
        file = evefile.EveFile(filename=self.filename)
        self.assertEqual(self.filename, file.metadata.filename)

    def test_get_data_returns_data_by_name(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.evefile.load(filename=self.filename)
        self.assertEqual(
            self.evefile.scan_modules["main"].data["SimMot:01"],
            self.evefile.get_data("foo"),
        )

    def test_get_data_list_returns_data_by_name_as_array(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.evefile.load(filename=self.filename)
        self.assertEqual(
            self.evefile.scan_modules["main"].data["SimMot:01"],
            self.evefile.get_data(["foo", "bar"])[0],
        )

    def test_data_have_correct_shape(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.evefile.load(filename=self.filename)
        self.assertEqual(
            5, len(self.evefile.scan_modules["main"].data["SimChan:01"].data)
        )
        self.assertEqual(
            5, len(self.evefile.scan_modules["main"].data["SimMot:01"].data)
        )

    def test_load_reads_scml(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile.load(filename=self.filename)
        self.assertEqual("9.2", self.evefile.scan.version)

    def test_has_scan_with_no_scan(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.evefile.load(filename=self.filename)
        self.assertIsInstance(self.evefile.has_scan(), bool)
        self.assertFalse(self.evefile.has_scan())

    def test_has_scan_with_scan(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=True)
        self.evefile.load(filename=self.filename)
        self.assertTrue(self.evefile.has_scan())

    def test_load_without_scml_creates_default_scan_module(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=False)
        self.evefile.load(filename=self.filename)
        self.assertTrue(self.evefile.scan_modules)
        self.assertIsInstance(
            self.evefile.scan_modules["main"],
            evedata.evefile.entities.file.ScanModule,
        )

    def test_load_with_scml_creates_scan_modules(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=True)
        self.evefile.load(filename=self.filename)
        self.assertTrue(self.evefile.scan_modules)
        for scan_module in self.evefile.scan_modules.values():
            self.assertIsInstance(
                scan_module,
                evedata.evefile.entities.file.ScanModule,
            )

    def test_load_with_scml_maps_scan_modules(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(scml=True)
        self.evefile.load(filename=self.filename)
        self.assertTrue(self.evefile.scan_modules)
        for scan_module in self.evefile.scan_modules.values():
            self.assertNotEqual(
                "main",
                scan_module.name,
            )
