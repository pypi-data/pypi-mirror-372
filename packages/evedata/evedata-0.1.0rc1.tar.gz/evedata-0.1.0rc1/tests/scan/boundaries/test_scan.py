import os
import struct
import unittest
import zlib

from evedata.scan.boundaries import scan


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
    </scan>
    <plugins/>
    <detectors/>
    <motors/>
    <devices/>
</tns:scml>"""


class DummySCMLFile:
    def __init__(self, filename=""):
        self.filename = filename

    def create(self):
        with open(self.filename, "w") as file:
            file.write(SCML)


class DummyHDF5File:
    def __init__(self, filename=""):
        self.filename = filename

    def create(self):
        with open(self.filename, "wb") as file:
            file.write(b"EVEcSCML")
            compressed_scml = zlib.compress(bytes(SCML, "utf8"))
            file.write(struct.pack("!L", len(compressed_scml)))
            file.write(struct.pack("!L", len(SCML)))
            file.write(compressed_scml)


class TestFile(unittest.TestCase):
    def setUp(self):
        self.file = scan.File()
        self.filename = "file.scml"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "version",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.file, attribute))

    def test_load_with_filename_sets_filename(self):
        scmlfile = DummySCMLFile(filename=self.filename)
        scmlfile.create()
        self.file.load(filename=self.filename)
        self.assertEqual(self.filename, self.file.filename)

    def test_load_without_filename_but_filename_set_keeps_filename(self):
        scmlfile = DummySCMLFile(filename=self.filename)
        scmlfile.create()
        self.file.filename = self.filename
        self.file.load()
        self.assertEqual(self.filename, self.file.filename)

    def test_load_sets_metadata(self):
        scmlfile = DummySCMLFile(filename=self.filename)
        scmlfile.create()
        self.file.load(filename=self.filename)
        self.assertEqual(self.file.version, "9.2")


class TestScan(unittest.TestCase):
    def setUp(self):
        self.scan = scan.Scan()
        self.filename = "file.h5"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "location",
            "scan",
            "version",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.scan, attribute))

    def test_extract_with_filename(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.scan.extract(filename=self.filename)
        self.assertEqual(self.scan.version, "9.2")

    def test_extract_without_filename_but_filename_set(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.scan.filename = self.filename
        self.scan.extract()
        self.assertEqual(self.scan.version, "9.2")
