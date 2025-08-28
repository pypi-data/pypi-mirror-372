import os
import unittest
import xml.etree.ElementTree as ET

from evedata.scan.boundaries import scml


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
        <repeatcount>0</repeatcount>
        <savefilename>/messung/test/daten/2022/kw35/u49-test</savefilename>
        <confirmsave>false</confirmsave>
        <autonumber>true</autonumber>
        <savescandescription>false</savescandescription>
        <chain id="1">
            <pauseconditions/>
            <scanmodules>
                <scanmodule id="15">
                    <name>Dynamic Axis Snapshot</name>
                    <xpos>90</xpos>
                    <ypos>83</ypos>
                    <parent>0</parent>
                    <appended>1</appended>
                    <dynamic_axis_positions/>
                </scanmodule>
                <scanmodule id="1">
                    <name>SM 1</name>
                    <xpos>228</xpos>
                    <ypos>124</ypos>
                    <parent>15</parent>
                    <classic>
                        <valuecount>1</valuecount>
                        <settletime>0.0</settletime>
                        <triggerdelay>0.0</triggerdelay>
                        <triggerconfirmaxis>false</triggerconfirmaxis>
                        <triggerconfirmchannel>false</triggerconfirmchannel>
                        <prescan>
                            <id>SimMt:testrack01000.LLM</id>
                            <value type="double">30</value>
                        </prescan>
                        <smaxis>
                            <axisid>Timer1-mot-double</axisid>
                            <stepfunction>Add</stepfunction>
                            <positionmode>absolute</positionmode>
                            <startstopstep>
                                <start type="double">1.0</start>
                                <stop type="double">5.0</stop>
                                <stepwidth type="double">1.0</stepwidth>
                                <ismainaxis>false</ismainaxis>
                            </startstopstep>
                        </smaxis>
                        <smchannel>
                            <channelid>mlsCurrent:Mnt1chan1</channelid>
                            <interval>
                                <triggerinterval>0.01</triggerinterval>
                                <stoppedby>Timer1-det-double</stoppedby>
                            </interval>
                        </smchannel>
                        <smchannel>
                            <channelid>Timer1-det-double</channelid>
                            <standard>
                                <averagecount>500</averagecount>
                                <sendreadyevent>true</sendreadyevent>
                            </standard>
                        </smchannel>
                        <postscan>
                            <id>SimMt:testrack01000.LLM</id>
                            <reset_originalvalue>true</reset_originalvalue>
                        </postscan>
                    </classic>
                </scanmodule>
            </scanmodules>
        </chain>
        <monitoroptions type="none"/>
    </scan>
    <plugins/>
    <detectors>
        <detector>
            <class>Timer</class>
            <name>detSecTime</name>
            <id>detSecTime</id>
            <channel>
                <class></class>
                <name>Time</name>
                <id>Timer1-det-double</id>
                <read>
                    <access method="GETCB" type="double" transport="local">Timer</access>
                </read>
            </channel>
        </detector>
    </detectors>
    <motors>
        <motor>
            <class>Timer</class>
            <name>motSecTimer</name>
            <id>motSecTimer</id>
            <axis>
                <class></class>
                <name>Timer</name>
                <id>Timer1-mot-double</id>
                <goto>
                    <access method="GETPUTCB" type="double" transport="local">Timer</access>
                </goto>
                <position>
                    <access method="GETCB" type="double" transport="local">Timer</access>
                </position>
                <stop>
                    <access method="PUT" type="int" transport="local">no stop available</access>
                    <value type="int">0</value>
                </stop>
            </axis>
        </motor>
    </motors>
    <devices>
        <device>
            <class></class>
            <name>EVE_SCAN_STATUS</name>
            <id>genPu:fcm:eveStatusmenu</id>
            <value>
                <access method="GETCB" type="string" transport="ca" monitor="true">genPu:fcm:eveStatusmenu</access>
                <value type="string">idle, busy</value>
            </value>
            <option>
                <name>Value</name>
                <id>ValuegenPu:fcm:eveStatusmenu</id>
                <value>
                    <access method="GETCB" type="string" transport="ca" monitor="true">genPu:fcm:eveStatusmenu</access>
                </value>
                <displaygroup>summary</displaygroup>
            </option>
        </device>
    </devices>
</tns:scml>"""


class DummySCMLFile:
    def __init__(self, filename=""):
        self.filename = filename

    def create(self):
        with open(self.filename, "w") as file:
            file.write(SCML)


class TestSCML(unittest.TestCase):
    def setUp(self):
        self.scml = scml.SCML()
        self.filename = "file.scml"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "root",
            "version",
            "scan_modules",
            "detectors",
            "motors",
            "devices",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.scml, attribute))

    def test_load_sets_root(self):
        scmlfile = DummySCMLFile(filename=self.filename)
        scmlfile.create()
        self.scml.load(filename=self.filename)
        self.assertTrue(self.scml.root)
        self.assertIsInstance(self.scml.root, ET.Element)

    def test_load_sets_version(self):
        scmlfile = DummySCMLFile(filename=self.filename)
        scmlfile.create()
        self.scml.load(filename=self.filename)
        self.assertEqual("9.2", self.scml.version)

    def test_load_without_filename_raises(self):
        with self.assertRaises(FileNotFoundError):
            self.scml.load()

    def test_from_string_sets_root(self):
        self.scml.from_string(SCML)
        self.assertTrue(self.scml.root)
        self.assertIsInstance(self.scml.root, ET.Element)

    def test_from_string_sets_version(self):
        self.scml.from_string(SCML)
        self.assertEqual("9.2", self.scml.version)

    def test_from_string_without_string_raises(self):
        with self.assertRaisesRegex(ValueError, "Missing XML string"):
            self.scml.from_string()

    def test_scan_modules_returns_list_of_elements(self):
        scmlfile = DummySCMLFile(filename=self.filename)
        scmlfile.create()
        self.scml.load(filename=self.filename)
        self.assertTrue(self.scml.scan_modules)
        for scan_module in self.scml.scan_modules:
            self.assertIsInstance(scan_module, ET.Element)

    def test_scan_modules_without_root_returns_empty_list(self):
        self.assertListEqual([], self.scml.scan_modules)

    def test_scan_returns_scan_element(self):
        scmlfile = DummySCMLFile(filename=self.filename)
        scmlfile.create()
        self.scml.load(filename=self.filename)
        self.assertTrue(self.scml.scan)
        self.assertEqual("scan", self.scml.scan.tag)

    def test_scan_without_root_returns_none(self):
        self.assertIsNone(self.scml.scan)

    def test_detectors_returns_list_of_elements(self):
        scmlfile = DummySCMLFile(filename=self.filename)
        scmlfile.create()
        self.scml.load(filename=self.filename)
        self.assertTrue(self.scml.detectors)
        for detector in self.scml.detectors:
            self.assertIsInstance(detector, ET.Element)
            self.assertEqual("detector", detector.tag)

    def test_detectors_without_root_returns_empty_list(self):
        self.assertListEqual([], self.scml.detectors)

    def test_motors_returns_list_of_elements(self):
        scmlfile = DummySCMLFile(filename=self.filename)
        scmlfile.create()
        self.scml.load(filename=self.filename)
        self.assertTrue(self.scml.motors)
        for motor in self.scml.motors:
            self.assertIsInstance(motor, ET.Element)
            self.assertEqual("motor", motor.tag)

    def test_motors_without_root_returns_empty_list(self):
        self.assertListEqual([], self.scml.motors)

    def test_devices_returns_list_of_elements(self):
        scmlfile = DummySCMLFile(filename=self.filename)
        scmlfile.create()
        self.scml.load(filename=self.filename)
        self.assertTrue(self.scml.devices)
        for device in self.scml.devices:
            self.assertIsInstance(device, ET.Element)
            self.assertEqual("device", device.tag)

    def test_devices_without_root_returns_empty_list(self):
        self.assertListEqual([], self.scml.devices)
