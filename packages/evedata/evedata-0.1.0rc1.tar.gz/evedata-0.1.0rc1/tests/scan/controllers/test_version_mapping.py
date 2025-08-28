import logging
import unittest
import xml.etree.ElementTree as ET

from string import Template

import numpy as np
from setuptools.namespaces import flatten

from evedata.scan.boundaries.scan import Scan
from evedata.scan.boundaries.scml import SCML
from evedata.scan.controllers import version_mapping
from evedata.scan.entities import scan


SCML_STRING = """<?xml version="1.0" encoding="UTF-8"?>
<tns:scml xsi:schemaLocation="http://www.ptb.de/epics/SCML scml.xsd"
    xmlns:tns="http://www.ptb.de/epics/SCML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <location>TEST</location>
    <version>9.0</version>
    <scan>
        <repeatcount>0</repeatcount>
        <comment>test ccd time</comment>
        <savefilename>/messung/test/daten/2024/kw${WEEK}/interval-detector-test-</savefilename>
        <confirmsave>false</confirmsave>
        <autonumber>true</autonumber>
        <savescandescription>true</savescandescription>
        <chain id="1">
            <pauseconditions/>
            <scanmodules>
                <scanmodule id="15">
                    <name>Dynamic Axis Snapshot</name>
                    <xpos>90</xpos>
                    <ypos>83</ypos>
                    <parent>0</parent>
                    <appended>16</appended>
                    <dynamic_axis_positions/>
                </scanmodule>
                <scanmodule id="16">
                    <name>Dynamic Channel Snapshot</name>
                    <xpos>179</xpos>
                    <ypos>128</ypos>
                    <parent>2</parent>
                    <appended>1</appended>
                    <dynamic_channel_values/>
                </scanmodule>
                <scanmodule id="1">
                    <name>SM 1</name>
                    <xpos>228</xpos>
                    <ypos>124</ypos>
                    <parent>15</parent>
                    <nested>2</nested>
                    <appended>3</appended>
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
                <scanmodule id="2">
                    <name>SM 1</name>
                    <xpos>228</xpos>
                    <ypos>124</ypos>
                    <parent>1</parent>
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
                        <prescan>
                            <id>K0617:gw24126.SCAN</id>
                            <value type="string">Passive</value>
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
                        <postscan>
                            <id>K0617:gw24126.SCAN</id>
                            <value type="string">.5 second</value>
                        </postscan>
                    </classic>
                </scanmodule>
                <scanmodule id="3">
                    <name>Static Axis Snapshot</name>
                    <xpos>147</xpos>
                    <ypos>57</ypos>
                    <parent>2</parent>
                    <appended>4</appended>
                    <save_axis_positions>
                        <smaxis>
                            <axisid>DiscPosSimMt:testrack01000</axisid>
                            <stepfunction>Plugin</stepfunction>
                            <positionmode>absolute</positionmode>
                            <plugin name="MotionDisabled">
                                <parameter name="location">/path/to/referenceadd</parameter>
                            </plugin>
                        </smaxis>
                    </save_axis_positions>
                </scanmodule>
                <scanmodule id="4">
                    <name>Static Channel Snapshot</name>
                    <xpos>333</xpos>
                    <ypos>77</ypos>
                    <parent>3</parent>
                    <save_channel_values>
                        <smchannel>
                            <channelid>SmCounter-det</channelid>
                            <standard/>
                        </smchannel>
                        <smchannel>
                            <channelid>bIICurrent:Mnt1chan1</channelid>
                            <standard/>
                        </smchannel>
                    </save_channel_values>
                </scanmodule>
                <scanmodule id="42">
                    <name>Not connected scan module</name>
                    <xpos>228</xpos>
                    <ypos>124</ypos>
                    <parent>-1</parent>
                    <appended>43</appended>
                    <nested>44</nested>
                    <classic>
                        <valuecount>1</valuecount>
                        <settletime>0.0</settletime>
                        <triggerdelay>0.0</triggerdelay>
                        <triggerconfirmaxis>false</triggerconfirmaxis>
                        <triggerconfirmchannel>false</triggerconfirmchannel>
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
                    </classic>
                </scanmodule>
                <scanmodule id="43">
                    <name>Not connected scan module</name>
                    <xpos>228</xpos>
                    <ypos>124</ypos>
                    <parent>42</parent>
                    <classic>
                        <valuecount>1</valuecount>
                        <settletime>0.0</settletime>
                        <triggerdelay>0.0</triggerdelay>
                        <triggerconfirmaxis>false</triggerconfirmaxis>
                        <triggerconfirmchannel>false</triggerconfirmchannel>
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
                    </classic>
                </scanmodule>
                <scanmodule id="44">
                    <name>Not connected scan module</name>
                    <xpos>228</xpos>
                    <ypos>124</ypos>
                    <parent>42</parent>
                    <classic>
                        <valuecount>1</valuecount>
                        <settletime>0.0</settletime>
                        <triggerdelay>0.0</triggerdelay>
                        <triggerconfirmaxis>false</triggerconfirmaxis>
                        <triggerconfirmchannel>false</triggerconfirmchannel>
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


MINIMAL_SCML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<tns:scml xsi:schemaLocation="http://www.ptb.de/epics/SCML scml.xsd"
    xmlns:tns="http://www.ptb.de/epics/SCML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <location>TEST</location>
    <version>9.0</version>
    <scan>
        <repeatcount>0</repeatcount>
        <comment>test</comment>
        <savefilename>/messung/test/daten/2024/kw42/interval-detector-test-</savefilename>
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
                    <classic>
                        <valuecount>1</valuecount>
                        <settletime>0.0</settletime>
                        <triggerdelay>0.0</triggerdelay>
                        <triggerconfirmaxis>false</triggerconfirmaxis>
                        <triggerconfirmchannel>false</triggerconfirmchannel>
                        $smaxis
                        $smchannel
                    </classic>
                </scanmodule>
            </scanmodules>
        </chain>
    </scan>
</tns:scml>"""


SCML_WITH_MIXED_SCAN_MODULES = """<?xml version="1.0" encoding="UTF-8"?>
<tns:scml xsi:schemaLocation="http://www.ptb.de/epics/SCML scml.xsd"
    xmlns:tns="http://www.ptb.de/epics/SCML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <location>TEST</location>
    <version>9.0</version>
    <scan>
        <repeatcount>0</repeatcount>
        <comment>test</comment>
        <savefilename>/messung/test/daten/2024/kw42/interval-detector-test-</savefilename>
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
                    <parent>16</parent>
                    <classic>
                        <valuecount>1</valuecount>
                        <settletime>0.0</settletime>
                        <triggerdelay>0.0</triggerdelay>
                        <triggerconfirmaxis>false</triggerconfirmaxis>
                        <triggerconfirmchannel>false</triggerconfirmchannel>
                    </classic>
                </scanmodule>
                <scanmodule id="16">
                    <name>Dynamic Channel Snapshot</name>
                    <xpos>179</xpos>
                    <ypos>128</ypos>
                    <parent>15</parent>
                    <appended>1</appended>
                    <dynamic_channel_values/>
                </scanmodule>
                <scanmodule id="15">
                    <name>Dynamic Axis Snapshot</name>
                    <xpos>90</xpos>
                    <ypos>83</ypos>
                    <parent>0</parent>
                    <appended>16</appended>
                    <dynamic_axis_positions/>
                </scanmodule>
            </scanmodules>
        </chain>
    </scan>
</tns:scml>"""


class MockSCML:
    def __init__(self):
        self.root = None
        self.version = ""

    def load(self, xml=SCML_STRING):
        self.root = ET.fromstring(xml)
        self.version = self.root.find("version").text


class MockScan:
    def __init__(self):
        self.version = ""
        self.location = ""
        self.scan = None


class TestVersionMapperFactory(unittest.TestCase):
    def setUp(self):
        self.factory = version_mapping.VersionMapperFactory()
        self.scml = MockSCML()
        self.scml.load()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "scml",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.factory, attribute))

    def test_get_mapper_returns_mapper(self):
        self.factory.scml = self.scml
        mapper = self.factory.get_mapper()
        self.assertIsInstance(mapper, version_mapping.VersionMapper)

    def test_get_mapper_with_scml_argument_sets_scml_property(self):
        self.factory.get_mapper(scml=self.scml)
        self.assertEqual(self.scml, self.factory.scml)

    def test_get_mapper_without_scml_raises(self):
        with self.assertRaises(ValueError):
            self.factory.get_mapper()

    def test_get_mapper_returns_correct_mapper(self):
        self.factory.scml = self.scml
        mapper = self.factory.get_mapper()
        self.assertIsInstance(mapper, version_mapping.VersionMapperV9m0)
        self.factory.scml.version = "9.1"
        mapper = self.factory.get_mapper()
        self.assertIsInstance(mapper, version_mapping.VersionMapperV9m1)
        self.factory.scml.version = "9.2"
        mapper = self.factory.get_mapper()
        self.assertIsInstance(mapper, version_mapping.VersionMapperV9m2)

    def test_get_mapper_with_unknown_version_raises(self):
        self.scml.version = "0"
        self.factory.scml = self.scml
        with self.assertRaises(AttributeError):
            self.factory.get_mapper()

    def test_get_mapper_sets_source_in_mapper(self):
        self.factory.scml = self.scml
        mapper = self.factory.get_mapper()
        self.assertEqual(self.scml, mapper.source)


class TestVersionMapper(unittest.TestCase):
    def setUp(self):
        self.mapper = version_mapping.VersionMapper()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "source",
            "destination",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.mapper, attribute))

    def test_map_without_source_raises(self):
        self.mapper.source = None
        with self.assertRaises(ValueError):
            self.mapper.map()

    def test_map_without_destination_raises(self):
        self.mapper.source = MockSCML()
        self.mapper.source.load()
        with self.assertRaises(ValueError):
            self.mapper.map()

    def test_map_sets_basic_metadata(self):
        self.mapper.source = MockSCML()
        self.mapper.source.load()
        destination = MockScan()
        self.mapper.map(destination=destination)
        self.assertEqual(self.mapper.source.version, destination.version)
        self.assertEqual(
            self.mapper.source.root.find("location").text,
            destination.location,
        )


class TestVersionMapperV9m0(unittest.TestCase):
    def setUp(self):
        self.mapper = version_mapping.VersionMapperV9m0()
        self.logger = logging.getLogger(name="evedata")
        self.logger.setLevel(logging.ERROR)

    def test_instantiate_class(self):
        pass

    def test_map_sets_scan_metadata(self):
        self.mapper.source = SCML()
        self.mapper.source.from_string(xml=SCML_STRING)
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertEqual(
            int(self.mapper.source.scan.find("repeatcount").text),
            self.mapper.destination.scan.repeat_count,
        )
        self.assertEqual(
            self.mapper.source.scan.find("comment").text,
            self.mapper.destination.scan.comment,
        )

    def test_map_creates_correct_number_of_scan_modules(self):
        self.mapper.source = SCML()
        self.mapper.source.from_string(xml=SCML_STRING)
        destination = Scan()
        self.mapper.map(destination=destination)
        # Note: Disconnected scan modules have ID>=42 in our example source,
        #       to allow for simpler tests
        connected_scan_modules = [
            module
            for module in self.mapper.source.scan_modules
            if int(module.get("id")) < 42
        ]
        self.assertEqual(
            len(connected_scan_modules),
            len(self.mapper.destination.scan.scan_modules.keys()),
        )

    def test_map_creates_scan_modules_in_correct_order(self):
        self.mapper.source = SCML()
        self.mapper.source.from_string(xml=SCML_WITH_MIXED_SCAN_MODULES)
        destination = Scan()
        self.mapper.map(destination=destination)
        # Note: SM IDs are 15 > 16 > 1
        self.assertListEqual(
            [15, 16, 1],
            list(self.mapper.destination.scan.scan_modules.keys()),
        )

    def test_map_sets_scan_module_attributes(self):
        self.mapper.source = SCML()
        self.mapper.source.from_string(xml=SCML_STRING)
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertEqual(
            self.mapper.source.scan_modules[0].find("name").text,
            self.mapper.destination.scan.scan_modules[15].name,
        )
        self.assertEqual(
            int(self.mapper.source.scan_modules[0].attrib["id"]),
            self.mapper.destination.scan.scan_modules[15].id,
        )
        self.assertEqual(
            int(self.mapper.source.scan_modules[0].find("parent").text),
            self.mapper.destination.scan.scan_modules[15].parent,
        )
        self.assertEqual(
            int(self.mapper.source.scan_modules[0].find("appended").text),
            self.mapper.destination.scan.scan_modules[15].appended,
        )
        self.assertEqual(
            int(self.mapper.source.scan_modules[2].find("nested").text),
            self.mapper.destination.scan.scan_modules[1].nested,
        )

    def test_map_sets_is_nested_attribute(self):
        self.mapper.source = SCML()
        self.mapper.source.from_string(xml=SCML_STRING)
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertTrue(
            self.mapper.destination.scan.scan_modules[2].is_nested
        )

    def test_map_distinguishes_scan_module_types(self):
        self.mapper.source = SCML()
        self.mapper.source.from_string(xml=SCML_STRING)
        destination = Scan()
        self.mapper.map(destination=destination)
        classic_ids = [1, 2]
        static_snapshot_ids = [3, 4]
        dynamic_snapshot_ids = [15, 16]
        for sm_id in classic_ids:
            self.assertIsInstance(
                self.mapper.destination.scan.scan_modules[sm_id],
                scan.ScanModule,
            )
        for sm_id in static_snapshot_ids:
            self.assertIsInstance(
                self.mapper.destination.scan.scan_modules[sm_id],
                scan.StaticSnapshotModule,
            )
        for sm_id in dynamic_snapshot_ids:
            self.assertIsInstance(
                self.mapper.destination.scan.scan_modules[sm_id],
                scan.DynamicSnapshotModule,
            )

    def test_map_adds_channels_to_classic_scan_module(self):
        self.mapper.source = SCML()
        self.mapper.source.from_string(xml=SCML_STRING)
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertTrue(self.mapper.destination.scan.scan_modules[1].channels)
        for item in self.mapper.destination.scan.scan_modules[
            1
        ].channels.values():
            self.assertIsInstance(item, scan.Channel)
            self.assertTrue(item.id)

    def test_map_adds_axes_to_classic_scan_module(self):
        self.mapper.source = SCML()
        self.mapper.source.from_string(xml=SCML_STRING)
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertTrue(self.mapper.destination.scan.scan_modules[1].axes)
        for item in self.mapper.destination.scan.scan_modules[
            1
        ].axes.values():
            self.assertIsInstance(item, scan.Axis)
            self.assertTrue(item.id)

    def test_map_adds_channels_to_static_snapshot_module(self):
        self.mapper.source = SCML()
        self.mapper.source.from_string(xml=SCML_STRING)
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertTrue(self.mapper.destination.scan.scan_modules[4].channels)
        for item in self.mapper.destination.scan.scan_modules[
            4
        ].channels.values():
            self.assertIsInstance(item, scan.Channel)
            self.assertTrue(item.id)

    def test_map_adds_axes_to_static_snapshot_module(self):
        self.mapper.source = SCML()
        self.mapper.source.from_string(xml=SCML_STRING)
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertTrue(self.mapper.destination.scan.scan_modules[3].axes)
        for item in self.mapper.destination.scan.scan_modules[
            3
        ].axes.values():
            self.assertIsInstance(item, scan.Axis)
            self.assertTrue(item.id)

    def test_map_axis_with_unknown_step_function_logs(self):
        smaxis_add = """<smaxis>
                            <axisid>Timer1-mot-double</axisid>
                            <stepfunction>Nonexisting</stepfunction>
                            <positionmode>absolute</positionmode>
                        </smaxis>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis=smaxis_add, smchannel="")
        )
        destination = Scan()
        self.logger.setLevel(logging.WARN)
        with self.assertLogs(level=logging.WARN) as captured:
            self.mapper.map(destination=destination)
        self.assertEqual(len(captured.records), 1)
        self.assertEqual(
            captured.records[0].getMessage(),
            "Step function 'nonexisting' not understood.",
        )

    def test_map_axis_add_sets_step_function(self):
        smaxis_add = """<smaxis>
                            <axisid>Timer1-mot-double</axisid>
                            <stepfunction>Add</stepfunction>
                            <positionmode>absolute</positionmode>
                            <startstopstep>
                                <start type="double">1.0</start>
                                <stop type="double">5.0</stop>
                                <stepwidth type="double">1.0</stepwidth>
                                <ismainaxis>false</ismainaxis>
                            </startstopstep>
                        </smaxis>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis=smaxis_add, smchannel="")
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertIsInstance(
            self.mapper.destination.scan.scan_modules[1]
            .axes["Timer1-mot-double"]
            .step_function,
            scan.StepRange,
        )

    def test_map_axis_add_sets_position_mode(self):
        smaxis_add = """<smaxis>
                            <axisid>Timer1-mot-double</axisid>
                            <stepfunction>Add</stepfunction>
                            <positionmode>relative</positionmode>
                            <startstopstep>
                                <start type="double">1.0</start>
                                <stop type="double">5.0</stop>
                                <stepwidth type="double">1.0</stepwidth>
                                <ismainaxis>false</ismainaxis>
                            </startstopstep>
                        </smaxis>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis=smaxis_add, smchannel="")
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertEqual(
            "relative",
            self.mapper.destination.scan.scan_modules[1]
            .axes["Timer1-mot-double"]
            .position_mode,
        )

    def test_map_axis_add_sets_main_axis_true(self):
        smaxis_add = """<smaxis>
                            <axisid>Timer1-mot-double</axisid>
                            <stepfunction>Add</stepfunction>
                            <positionmode>relative</positionmode>
                            <startstopstep>
                                <start type="double">1.0</start>
                                <stop type="double">5.0</stop>
                                <stepwidth type="double">1.0</stepwidth>
                                <ismainaxis>true</ismainaxis>
                            </startstopstep>
                        </smaxis>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis=smaxis_add, smchannel="")
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertTrue(
            self.mapper.destination.scan.scan_modules[1]
            .axes["Timer1-mot-double"]
            .step_function.is_main_axis,
        )

    def test_map_axis_add_sets_main_axis_false(self):
        smaxis_add = """<smaxis>
                            <axisid>Timer1-mot-double</axisid>
                            <stepfunction>Add</stepfunction>
                            <positionmode>relative</positionmode>
                            <startstopstep>
                                <start type="double">1.0</start>
                                <stop type="double">5.0</stop>
                                <stepwidth type="double">1.0</stepwidth>
                                <ismainaxis>false</ismainaxis>
                            </startstopstep>
                        </smaxis>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis=smaxis_add, smchannel="")
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertFalse(
            self.mapper.destination.scan.scan_modules[1]
            .axes["Timer1-mot-double"]
            .step_function.is_main_axis,
        )

    def test_map_axis_add_sets_positions(self):
        smaxis_add = """<smaxis>
                            <axisid>Timer1-mot-double</axisid>
                            <stepfunction>Add</stepfunction>
                            <positionmode>absolute</positionmode>
                            <startstopstep>
                                <start type="double">1.0</start>
                                <stop type="double">5.0</stop>
                                <stepwidth type="double">1.0</stepwidth>
                                <ismainaxis>false</ismainaxis>
                            </startstopstep>
                        </smaxis>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis=smaxis_add, smchannel="")
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        np.testing.assert_array_equal(
            np.asarray(
                [1.0, 2.0, 3.0, 4.0, 5.0],
            ),
            self.mapper.destination.scan.scan_modules[1]
            .axes["Timer1-mot-double"]
            .positions,
        )

    def test_map_axis_positionlist_sets_positions(self):
        smaxis_positionlist = """<smaxis>
                            <axisid>Counter-mot</axisid>
                            <stepfunction>Positionlist</stepfunction>
                            <positionmode>absolute</positionmode>
                            <positionlist>1, 2,3, 4 ,5</positionlist>
                        </smaxis>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis=smaxis_positionlist, smchannel="")
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        np.testing.assert_array_equal(
            np.asarray([1, 2, 3, 4, 5]),
            self.mapper.destination.scan.scan_modules[1]
            .axes["Counter-mot"]
            .positions,
        )

    def test_map_axis_range_sets_positions(self):
        smaxis_range = """<smaxis>
                            <axisid>Counter-mot</axisid>
                            <stepfunction>Range</stepfunction>
                            <positionmode>absolute</positionmode>
                            <range>
                                <expression>1:5,1:2:5,1:5/2</expression>
                                <positionlist>1, 2, 3, 4, 5, 1, 3, 5, 1, 3, 5</positionlist>
                            </range>
                        </smaxis>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis=smaxis_range, smchannel="")
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        np.testing.assert_array_equal(
            np.asarray([1, 2, 3, 4, 5, 1, 3, 5, 1, 3, 5]),
            self.mapper.destination.scan.scan_modules[1]
            .axes["Counter-mot"]
            .positions,
        )

    def test_map_axis_file_sets_filename(self):
        smaxis_range = """<smaxis>
                            <axisid>Counter-mot</axisid>
                            <stepfunction>File</stepfunction>
                            <positionmode>absolute</positionmode>
                            <stepfilename>/nonexisting/file</stepfilename>
                        </smaxis>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis=smaxis_range, smchannel="")
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertEqual(
            "/nonexisting/file",
            self.mapper.destination.scan.scan_modules[1]
            .axes["Counter-mot"]
            .step_function.filename,
        )

    def test_map_axis_file_sets_positions_to_empty_array(self):
        smaxis_range = """<smaxis>
                            <axisid>Counter-mot</axisid>
                            <stepfunction>File</stepfunction>
                            <positionmode>absolute</positionmode>
                            <stepfilename>/nonexisting/file</stepfilename>
                        </smaxis>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis=smaxis_range, smchannel="")
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        np.testing.assert_array_equal(
            np.asarray([]),
            self.mapper.destination.scan.scan_modules[1]
            .axes["Counter-mot"]
            .positions,
        )

    def test_map_axis_file_logs_warning(self):
        smaxis_range = """<smaxis>
                            <axisid>Counter-mot</axisid>
                            <stepfunction>File</stepfunction>
                            <positionmode>absolute</positionmode>
                            <stepfilename>/nonexisting/file</stepfilename>
                        </smaxis>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis=smaxis_range, smchannel="")
        )
        destination = Scan()
        self.logger.setLevel(logging.WARN)
        with self.assertLogs(level=logging.WARN) as captured:
            self.mapper.map(destination=destination)
        self.assertEqual(len(captured.records), 1)
        self.assertEqual(
            captured.records[0].getMessage(),
            "Step function 'file' does not allow to obtain positions.",
        )

    def test_map_axis_plugin_sets_step_function(self):
        smaxis_plugin = """<smaxis>
                            <axisid>Counter-mot</axisid>
                            <stepfunction>Plugin</stepfunction>
                            <positionmode>absolute</positionmode>
                            <plugin name="ReferenceMultiply">
                                <parameter name="location">/path/to/referenceadd</parameter>
                                <parameter name="summand">5.0</parameter>
                                <parameter name="referenceaxis">Timer1-mot-double</parameter>
                            </plugin>
                        </smaxis>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis=smaxis_plugin, smchannel="")
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertIsInstance(
            self.mapper.destination.scan.scan_modules[1]
            .axes["Counter-mot"]
            .step_function,
            scan.StepReference,
        )
        self.assertEqual(
            "multiply",
            self.mapper.destination.scan.scan_modules[1]
            .axes["Counter-mot"]
            .step_function.mode,
        )
        self.assertEqual(
            5.0,
            self.mapper.destination.scan.scan_modules[1]
            .axes["Counter-mot"]
            .step_function.parameter,
        )
        self.assertEqual(
            "Timer1-mot-double",
            self.mapper.destination.scan.scan_modules[1]
            .axes["Counter-mot"]
            .step_function.axis_id,
        )
        self.assertEqual(
            self.mapper.destination.scan.scan_modules[1],
            self.mapper.destination.scan.scan_modules[1]
            .axes["Counter-mot"]
            .step_function.scan_module,
        )

    def test_map_axis_multiply_sets_positions(self):
        smaxis_multiply = """<smaxis>
                            <axisid>Counter-mot</axisid>
                            <stepfunction>Multiply</stepfunction>
                            <positionmode>absolute</positionmode>
                            <startstopstep>
                                <start type="int">1</start>
                                <stop type="int">5</stop>
                                <stepwidth type="int">1</stepwidth>
                                <ismainaxis>false</ismainaxis>
                            </startstopstep>
                        </smaxis>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis=smaxis_multiply, smchannel="")
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        np.testing.assert_array_equal(
            np.asarray(
                [1.0, 2.0, 3.0, 4.0, 5.0],
            ),
            self.mapper.destination.scan.scan_modules[1]
            .axes["Counter-mot"]
            .positions,
        )

    def test_map_axis_multiply_sets_position_mode_to_relative(self):
        smaxis_multiply = """<smaxis>
                            <axisid>Counter-mot</axisid>
                            <stepfunction>Multiply</stepfunction>
                            <positionmode>absolute</positionmode>
                            <startstopstep>
                                <start type="int">1</start>
                                <stop type="int">5</stop>
                                <stepwidth type="int">1</stepwidth>
                                <ismainaxis>false</ismainaxis>
                            </startstopstep>
                        </smaxis>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis=smaxis_multiply, smchannel="")
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertEqual(
            "relative",
            self.mapper.destination.scan.scan_modules[1]
            .axes["Counter-mot"]
            .position_mode,
        )

    def test_map_positionings(self):
        smaxis_positionings = """<smaxis>
                            <axisid>SimMt:testrack01000</axisid>
                            <stepfunction>Range</stepfunction>
                            <positionmode>absolute</positionmode>
                            <range>
                                <expression>1:20</expression>
                                <positionlist>1, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0</positionlist>
                            </range>
                        </smaxis>
                        <smchannel>
                            <channelid>mlsCurrent:Mnt1chan1</channelid>
                            <standard/>
                        </smchannel>
                        <positioning>
                            <axis_id>SimMt:testrack01000</axis_id>
                            <channel_id>mlsCurrent:Mnt1chan1</channel_id>
                            <plugin name="CENTER">
                                <parameter name="location">/path/to/plugin3</parameter>
                                <parameter name="threshold">50</parameter>
                            </plugin>
                        </positioning>
                        <positioning>
                            <axis_id>Counter-mot</axis_id>
                            <channel_id>mlsCurrent:Mnt1chan1</channel_id>
                            <plugin name="PEAK">
                                <parameter name="location">/path/to/plugin3</parameter>
                            </plugin>
                        </positioning>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis=smaxis_positionings, smchannel="")
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertTrue(
            self.mapper.destination.scan.scan_modules[1].positionings
        )
        self.assertEqual(
            2,
            len(self.mapper.destination.scan.scan_modules[1].positionings),
        )
        for positioning in self.mapper.destination.scan.scan_modules[
            1
        ].positionings:
            self.assertTrue(positioning.axis_id)
            self.assertTrue(positioning.channel_id)
            self.assertTrue(positioning.type)

    def test_map_positionings_parameters(self):
        smaxis_positionings = """<smaxis>
                            <axisid>SimMt:testrack01000</axisid>
                            <stepfunction>Range</stepfunction>
                            <positionmode>absolute</positionmode>
                            <range>
                                <expression>1:20</expression>
                                <positionlist>1, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0</positionlist>
                            </range>
                        </smaxis>
                        <smchannel>
                            <channelid>mlsCurrent:Mnt1chan1</channelid>
                            <standard/>
                        </smchannel>
                        <positioning>
                            <axis_id>SimMt:testrack01000</axis_id>
                            <channel_id>mlsCurrent:Mnt1chan1</channel_id>
                            <plugin name="CENTER">
                                <parameter name="location">/path/to/plugin3</parameter>
                                <parameter name="threshold">50</parameter>
                            </plugin>
                        </positioning>
                        <positioning>
                            <axis_id>Counter-mot</axis_id>
                            <channel_id>mlsCurrent:Mnt1chan1</channel_id>
                            <plugin name="EDGE">
                                <parameter name="location">/path/to/plugin3</parameter>
                                <parameter name="number from left">1</parameter>
                            </plugin>
                        </positioning>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis=smaxis_positionings, smchannel="")
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        for positioning in self.mapper.destination.scan.scan_modules[
            1
        ].positionings:
            self.assertTrue(positioning.parameters)

    def test_map_positionings_normalize(self):
        smaxis_positionings = """<smaxis>
                            <axisid>SimMt:testrack01000</axisid>
                            <stepfunction>Range</stepfunction>
                            <positionmode>absolute</positionmode>
                            <range>
                                <expression>1:20</expression>
                                <positionlist>1, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0</positionlist>
                            </range>
                        </smaxis>
                        <smchannel>
                            <channelid>mlsCurrent:Mnt1chan1</channelid>
                            <standard/>
                        </smchannel>
                        <positioning>
                            <axis_id>SimMt:testrack01000</axis_id>
                            <channel_id>mlsCurrent:Mnt1chan1</channel_id>
                            <normalize_id>mlsCurrent:Mnt1chan1</normalize_id>
                            <plugin name="CENTER">
                                <parameter name="location">/path/to/plugin3</parameter>
                                <parameter name="threshold">50</parameter>
                            </plugin>
                        </positioning>
                        <positioning>
                            <axis_id>Counter-mot</axis_id>
                            <channel_id>mlsCurrent:Mnt1chan1</channel_id>
                            <plugin name="EDGE">
                                <parameter name="location">/path/to/plugin3</parameter>
                                <parameter name="number from left">1</parameter>
                            </plugin>
                        </positioning>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis=smaxis_positionings, smchannel="")
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertEqual(
            "mlsCurrent:Mnt1chan1",
            self.mapper.destination.scan.scan_modules[1]
            .positionings[0]
            .normalize_channel_id,
        )

    def test_number_of_positions_per_pass(self):
        self.mapper.source = SCML()
        destination = Scan()
        scan_module = scan.ScanModule()
        axis_positions = {
            "1": np.asarray([1, 2, 3, 4, 5]),
            "2": np.asarray([3, 5, 7, 9]),
        }
        for id, positions in axis_positions.items():
            axis = scan.Axis(sm_id=id)
            axis.positions = positions
            scan_module.axes[id] = axis
        destination.scan.scan_modules[1] = scan_module
        scan_module = scan.ScanModule()
        axis_positions = {
            "1": np.asarray([1, 4, 5]),
            "2": np.asarray([3, 5, 7, 9]),
        }
        for id, positions in axis_positions.items():
            axis = scan.Axis(sm_id=id)
            axis.positions = positions
            scan_module.axes[id] = axis
        destination.scan.scan_modules[2] = scan_module
        self.mapper.destination = destination
        self.mapper._calculate_positions()
        for scan_module in self.mapper.destination.scan.scan_modules.values():
            self.assertTrue(scan_module.number_of_positions_per_pass)
            self.assertEqual(
                max(
                    [
                        axis.positions.size
                        for axis in scan_module.axes.values()
                    ]
                ),
                scan_module.number_of_positions_per_pass,
            )

    def test_number_of_positions_per_pass_with_positioning(self):
        self.mapper.source = SCML()
        destination = Scan()
        scan_module = scan.ScanModule()
        axis_positions = {
            "1": np.asarray([1, 2, 3, 4, 5]),
            "2": np.asarray([3, 5, 7, 9]),
        }
        for id, positions in axis_positions.items():
            axis = scan.Axis(sm_id=id)
            axis.positions = positions
            scan_module.axes[id] = axis
        scan_module.positionings.append(scan.Positioning())
        destination.scan.scan_modules[1] = scan_module
        self.mapper.destination = destination
        self.mapper._calculate_positions()
        for scan_module in self.mapper.destination.scan.scan_modules.values():
            self.assertEqual(
                max(
                    [
                        axis.positions.size
                        for axis in scan_module.axes.values()
                    ]
                )
                + 1,
                scan_module.number_of_positions_per_pass,
            )

    def test_map_number_of_positions_per_pass(self):
        smaxis_multiply = """<smaxis>
                            <axisid>Counter-mot</axisid>
                            <stepfunction>Multiply</stepfunction>
                            <positionmode>absolute</positionmode>
                            <startstopstep>
                                <start type="int">1</start>
                                <stop type="int">5</stop>
                                <stepwidth type="int">1</stepwidth>
                                <ismainaxis>false</ismainaxis>
                            </startstopstep>
                        </smaxis>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis=smaxis_multiply, smchannel="")
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertEqual(
            5,
            self.mapper.destination.scan.scan_modules[
                1
            ].number_of_positions_per_pass,
        )

    def test_map_number_of_measurements(self):
        smaxis = """<smaxis>
                            <axisid>SimMt:testrack01000</axisid>
                            <stepfunction>Range</stepfunction>
                            <positionmode>absolute</positionmode>
                            <range>
                                <expression>1:20</expression>
                                <positionlist>1, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0</positionlist>
                            </range>
                        </smaxis>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis=smaxis, smchannel="").replace(
                "<valuecount>1", "<valuecount>2"
            )
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertEqual(
            2,
            self.mapper.destination.scan.scan_modules[
                1
            ].number_of_measurements,
        )

    def test_map_n_positions_per_pass_w_multiple_measurements(self):
        smaxis = """<smaxis>
                            <axisid>Counter-mot</axisid>
                            <stepfunction>Multiply</stepfunction>
                            <positionmode>absolute</positionmode>
                            <startstopstep>
                                <start type="int">1</start>
                                <stop type="int">5</stop>
                                <stepwidth type="int">1</stepwidth>
                                <ismainaxis>false</ismainaxis>
                            </startstopstep>
                        </smaxis>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis=smaxis, smchannel="").replace(
                "<valuecount>1", "<valuecount>2"
            )
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertEqual(
            5 * 2,
            self.mapper.destination.scan.scan_modules[
                1
            ].number_of_positions_per_pass,
        )

    def test_number_of_positions_with_appended_scan_module(self):
        self.mapper.source = SCML()
        destination = Scan()
        scan_module = scan.ScanModule()
        scan_module.appended = 2
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3, 4, 5])
        scan_module.axes["1"] = axis
        destination.scan.scan_modules[1] = scan_module
        scan_module = scan.ScanModule()
        scan_module.parent = 1
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3, 4, 5])
        scan_module.axes["1"] = axis
        destination.scan.scan_modules[2] = scan_module
        self.mapper.destination = destination
        self.mapper._calculate_positions()
        for scan_module in self.mapper.destination.scan.scan_modules.values():
            self.assertTrue(scan_module.number_of_positions)
            self.assertEqual(5, scan_module.number_of_positions)

    def test_number_of_positions_with_nested_scan_module(self):
        self.mapper.source = SCML()
        destination = Scan()
        scan_module = scan.ScanModule()
        scan_module.nested = 2
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3, 4, 5])
        scan_module.axes["1"] = axis
        destination.scan.scan_modules[1] = scan_module
        scan_module = scan.ScanModule()
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3, 4, 5])
        scan_module.axes["1"] = axis
        destination.scan.scan_modules[2] = scan_module
        self.mapper.destination = destination
        self.mapper._calculate_positions()
        for scan_module in self.mapper.destination.scan.scan_modules.values():
            self.assertTrue(scan_module.number_of_positions)
        self.assertEqual(
            5,
            self.mapper.destination.scan.scan_modules[1].number_of_positions,
        )
        self.assertEqual(
            25,
            self.mapper.destination.scan.scan_modules[2].number_of_positions,
        )

    def test_number_of_positions_with_doubly_nested_scan_module(self):
        self.mapper.source = SCML()
        destination = Scan()
        scan_module = scan.ScanModule()
        scan_module.nested = 2
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3, 4, 5])
        scan_module.axes["1"] = axis
        destination.scan.scan_modules[1] = scan_module
        scan_module = scan.ScanModule()
        scan_module.nested = 3
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3, 4, 5])
        scan_module.axes["1"] = axis
        destination.scan.scan_modules[2] = scan_module
        scan_module = scan.ScanModule()
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3, 4, 5])
        scan_module.axes["1"] = axis
        destination.scan.scan_modules[3] = scan_module
        self.mapper.destination = destination
        self.mapper._calculate_positions()
        for scan_module in self.mapper.destination.scan.scan_modules.values():
            self.assertTrue(scan_module.number_of_positions)
        self.assertEqual(
            5,
            self.mapper.destination.scan.scan_modules[1].number_of_positions,
        )
        self.assertEqual(
            5 * 5,
            self.mapper.destination.scan.scan_modules[2].number_of_positions,
        )
        self.assertEqual(
            5 * 5 * 5,
            self.mapper.destination.scan.scan_modules[3].number_of_positions,
        )

    def test_number_of_positions_with_triply_nested_scan_module(self):
        self.mapper.source = SCML()
        destination = Scan()
        scan_module = scan.ScanModule()
        scan_module.nested = 2
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3, 4, 5])
        scan_module.axes["1"] = axis
        destination.scan.scan_modules[1] = scan_module
        scan_module = scan.ScanModule()
        scan_module.nested = 3
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3, 4])
        scan_module.axes["1"] = axis
        destination.scan.scan_modules[2] = scan_module
        scan_module = scan.ScanModule()
        scan_module.nested = 4
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3])
        scan_module.axes["1"] = axis
        destination.scan.scan_modules[3] = scan_module
        scan_module = scan.ScanModule()
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2])
        scan_module.axes["1"] = axis
        destination.scan.scan_modules[4] = scan_module
        self.mapper.destination = destination
        self.mapper._calculate_positions()
        for scan_module in self.mapper.destination.scan.scan_modules.values():
            self.assertTrue(scan_module.number_of_positions)
        self.assertEqual(
            5,
            self.mapper.destination.scan.scan_modules[1].number_of_positions,
        )
        self.assertEqual(
            5 * 4,
            self.mapper.destination.scan.scan_modules[2].number_of_positions,
        )
        self.assertEqual(
            5 * 4 * 3,
            self.mapper.destination.scan.scan_modules[3].number_of_positions,
        )
        self.assertEqual(
            5 * 4 * 3 * 2,
            self.mapper.destination.scan.scan_modules[4].number_of_positions,
        )

    def test_number_of_positions_w_nested_scan_module_and_positionings(self):
        self.mapper.source = SCML()
        destination = Scan()
        scan_module = scan.ScanModule()
        scan_module.nested = 2
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3, 4, 5])
        scan_module.axes["1"] = axis
        scan_module.positionings.append(scan.Positioning())
        destination.scan.scan_modules[1] = scan_module
        scan_module = scan.ScanModule()
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3, 4, 5])
        scan_module.axes["1"] = axis
        destination.scan.scan_modules[2] = scan_module
        self.mapper.destination = destination
        self.mapper._calculate_positions()
        for scan_module in self.mapper.destination.scan.scan_modules.values():
            self.assertTrue(scan_module.number_of_positions)
        self.assertEqual(
            6,
            self.mapper.destination.scan.scan_modules[1].number_of_positions,
        )
        self.assertEqual(
            25,
            self.mapper.destination.scan.scan_modules[2].number_of_positions,
        )

    def test_positions_with_nested_scan_module(self):
        self.mapper.source = SCML()
        destination = Scan()
        scan_module = scan.ScanModule()
        scan_module.nested = 2
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3, 4, 5])
        scan_module.axes["1"] = axis
        destination.scan.scan_modules[1] = scan_module
        scan_module = scan.ScanModule()
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3, 4, 5])
        scan_module.axes["1"] = axis
        destination.scan.scan_modules[2] = scan_module
        self.mapper.destination = destination
        self.mapper._calculate_positions()
        for scan_module in self.mapper.destination.scan.scan_modules.values():
            self.assertIsNotNone(scan_module.position_counts)
        np.testing.assert_array_equal(
            np.linspace(1, 25, 5),
            self.mapper.destination.scan.scan_modules[1].position_counts,
        )
        np.testing.assert_array_equal(
            np.array(
                [
                    [2, 3, 4, 5, 6],
                    [8, 9, 10, 11, 12],
                    [14, 15, 16, 17, 18],
                    [20, 21, 22, 23, 24],
                    [26, 27, 28, 29, 30],
                ]
            ).flatten(),
            self.mapper.destination.scan.scan_modules[2].position_counts,
        )

    def test_positions_with_nested_and_appended_scan_module(self):
        self.mapper.source = SCML()
        destination = Scan()
        scan_module = scan.ScanModule()
        scan_module.nested = 2
        scan_module.appended = 3
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3])
        scan_module.axes["1"] = axis
        destination.scan.scan_modules[1] = scan_module
        scan_module = scan.ScanModule()
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3])
        scan_module.axes["1"] = axis
        destination.scan.scan_modules[2] = scan_module
        scan_module = scan.ScanModule()
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3])
        scan_module.axes["1"] = axis
        destination.scan.scan_modules[3] = scan_module
        self.mapper.destination = destination
        self.mapper._calculate_positions()
        for scan_module in self.mapper.destination.scan.scan_modules.values():
            self.assertIsNotNone(scan_module.position_counts)
        np.testing.assert_array_equal(
            np.linspace(1, 3 * 3, 3),
            self.mapper.destination.scan.scan_modules[1].position_counts,
        )
        np.testing.assert_array_equal(
            np.array(
                [
                    [2, 3, 4],
                    [6, 7, 8],
                    [10, 11, 12],
                ]
            ).flatten(),
            self.mapper.destination.scan.scan_modules[2].position_counts,
        )
        np.testing.assert_array_equal(
            np.linspace(13, 15, 3),
            self.mapper.destination.scan.scan_modules[3].position_counts,
        )

    def test_positions_with_appended_scan_module_and_positioning(self):
        self.mapper.source = SCML()
        destination = Scan()
        scan_module = scan.ScanModule()
        scan_module.appended = 2
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3, 4, 5])
        scan_module.axes["1"] = axis
        scan_module.positionings.append(scan.Positioning())
        destination.scan.scan_modules[1] = scan_module
        scan_module = scan.ScanModule()
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3, 4, 5])
        scan_module.axes["1"] = axis
        destination.scan.scan_modules[2] = scan_module
        self.mapper.destination = destination
        self.mapper._calculate_positions()
        for scan_module in self.mapper.destination.scan.scan_modules.values():
            self.assertIsNotNone(scan_module.position_counts)
        np.testing.assert_array_equal(
            np.linspace(1, 6, 6),
            self.mapper.destination.scan.scan_modules[1].position_counts,
        )
        np.testing.assert_array_equal(
            np.linspace(7, 11, 5),
            self.mapper.destination.scan.scan_modules[2].position_counts,
        )

    def test_positions_with_nested_scan_module_and_positioning(self):
        self.mapper.source = SCML()
        destination = Scan()
        scan_module = scan.ScanModule()
        scan_module.nested = 2
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1])
        scan_module.axes["1"] = axis
        scan_module.positionings.append(scan.Positioning())
        destination.scan.scan_modules[1] = scan_module
        scan_module = scan.ScanModule()
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3, 4, 5])
        scan_module.axes["1"] = axis
        destination.scan.scan_modules[2] = scan_module
        self.mapper.destination = destination
        self.mapper._calculate_positions()
        for scan_module in self.mapper.destination.scan.scan_modules.values():
            self.assertIsNotNone(scan_module.position_counts)
        np.testing.assert_array_equal(
            np.array([1, 7]),
            self.mapper.destination.scan.scan_modules[1].position_counts,
        )
        np.testing.assert_array_equal(
            np.linspace(2, 6, 5),
            self.mapper.destination.scan.scan_modules[2].position_counts,
        )

    def test_positions_with_nested_scan_modules_with_positioning(self):
        self.mapper.source = SCML()
        destination = Scan()
        scan_module = scan.ScanModule()
        scan_module.nested = 2
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1])
        scan_module.axes["1"] = axis
        destination.scan.scan_modules[1] = scan_module
        scan_module = scan.ScanModule()
        scan_module.appended = 3
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3, 4, 5])
        scan_module.axes["1"] = axis
        scan_module.positionings.append(scan.Positioning())
        destination.scan.scan_modules[2] = scan_module
        scan_module = scan.ScanModule()
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3, 4, 5])
        scan_module.axes["1"] = axis
        scan_module.positionings.append(scan.Positioning())
        destination.scan.scan_modules[3] = scan_module
        self.mapper.destination = destination
        self.mapper._calculate_positions()
        for scan_module in self.mapper.destination.scan.scan_modules.values():
            self.assertIsNotNone(scan_module.position_counts)
        np.testing.assert_array_equal(
            np.array([1]),
            self.mapper.destination.scan.scan_modules[1].position_counts,
        )
        np.testing.assert_array_equal(
            np.linspace(2, 7, 6),
            self.mapper.destination.scan.scan_modules[2].position_counts,
        )
        self.assertEqual(
            6,
            self.mapper.destination.scan.scan_modules[
                2
            ].number_of_positions_per_pass,
        )
        self.assertEqual(
            7,
            self.mapper.destination.scan.scan_modules[2]
            .positionings[0]
            .position,
        )
        np.testing.assert_array_equal(
            np.linspace(8, 13, 6),
            self.mapper.destination.scan.scan_modules[3].position_counts,
        )
        self.assertEqual(
            6,
            self.mapper.destination.scan.scan_modules[
                3
            ].number_of_positions_per_pass,
        )
        self.assertEqual(
            13,
            self.mapper.destination.scan.scan_modules[3]
            .positionings[0]
            .position,
        )

    def test_positions_with_positioning_sets_positioning_position(self):
        self.mapper.source = SCML()
        destination = Scan()
        scan_module = scan.ScanModule()
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3, 4, 5])
        scan_module.axes["1"] = axis
        scan_module.positionings.append(scan.Positioning())
        destination.scan.scan_modules[1] = scan_module
        self.mapper.destination = destination
        self.mapper._calculate_positions()
        self.assertEqual(
            6,
            self.mapper.destination.scan.scan_modules[1]
            .positionings[0]
            .position,
        )

    def test_positions_with_dynamic_snapshot_scan_module(self):
        self.mapper.source = SCML()
        destination = Scan()
        scan_module = scan.DynamicSnapshotModule()
        scan_module.appended = 2
        destination.scan.scan_modules[1] = scan_module
        scan_module = scan.ScanModule()
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3, 4, 5])
        scan_module.axes["1"] = axis
        destination.scan.scan_modules[2] = scan_module
        self.mapper.destination = destination
        self.mapper._calculate_positions()
        for scan_module in self.mapper.destination.scan.scan_modules.values():
            self.assertIsNotNone(scan_module.position_counts)
        np.testing.assert_array_equal(
            np.linspace(2, 6, 5),
            self.mapper.destination.scan.scan_modules[2].position_counts,
        )

    def test_positions_with_nested_scan_module_and_different_order(self):
        self.mapper.source = SCML()
        destination = Scan()
        scan_module = scan.ScanModule()
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3, 4, 5])
        scan_module.axes["1"] = axis
        destination.scan.scan_modules[2] = scan_module
        scan_module = scan.ScanModule()
        scan_module.nested = 2
        axis = scan.Axis(sm_id="1")
        axis.positions = np.asarray([1, 2, 3, 4, 5])
        scan_module.axes["1"] = axis
        destination.scan.scan_modules[1] = scan_module
        self.mapper.destination = destination
        self.mapper._calculate_positions()
        for scan_module in self.mapper.destination.scan.scan_modules.values():
            self.assertIsNotNone(scan_module.position_counts)
        np.testing.assert_array_equal(
            np.linspace(1, 25, 5),
            self.mapper.destination.scan.scan_modules[1].position_counts,
        )
        np.testing.assert_array_equal(
            np.array(
                [
                    [2, 3, 4, 5, 6],
                    [8, 9, 10, 11, 12],
                    [14, 15, 16, 17, 18],
                    [20, 21, 22, 23, 24],
                    [26, 27, 28, 29, 30],
                ]
            ).flatten(),
            self.mapper.destination.scan.scan_modules[2].position_counts,
        )

    def test_map_channel_sets_deferred_trigger(self):
        smchannel = """<smchannel>
                            <channelid>mlsCurrent:Mnt1chan1</channelid>
                            <standard>
                                <deferredtrigger>true</deferredtrigger>
                            </standard>
                        </smchannel>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis="", smchannel=smchannel)
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertTrue(
            self.mapper.destination.scan.scan_modules[1]
            .channels["mlsCurrent:Mnt1chan1"]
            .deferred_trigger,
        )

    def test_map_channel_sets_interval_channel(self):
        smchannel = """<smchannel>
                            <channelid>mlsCurrent:Mnt2chan1</channelid>
                            <standard>
                                <sendreadyevent>true</sendreadyevent>
                            </standard>
                        </smchannel>
                        <smchannel>
                            <channelid>mlsCurrent:Mnt1lifeTimechan1</channelid>
                            <interval>
                                <triggerinterval>0.1</triggerinterval>
                                <stoppedby>mlsCurrent:Mnt2chan1</stoppedby>
                            </interval>
                        </smchannel>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis="", smchannel=smchannel)
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertIsInstance(
            self.mapper.destination.scan.scan_modules[1].channels[
                "mlsCurrent:Mnt1lifeTimechan1"
            ],
            scan.IntervalChannel,
        )
        self.assertEqual(
            0.1,
            self.mapper.destination.scan.scan_modules[1]
            .channels["mlsCurrent:Mnt1lifeTimechan1"]
            .trigger_interval,
        )
        self.assertEqual(
            "mlsCurrent:Mnt2chan1",
            self.mapper.destination.scan.scan_modules[1]
            .channels["mlsCurrent:Mnt1lifeTimechan1"]
            .stopped_by,
        )

    def test_channel_sets_normalise_id(self):
        smchannel = """<smchannel>
                            <channelid>mlsCurrent:Mnt2chan1</channelid>
                            <normalize_id>mlsCurrent:Mnt1lifeTimechan1</normalize_id>
                            <standard/>
                        </smchannel>
                        <smchannel>
                            <channelid>mlsCurrent:Mnt1lifeTimechan1</channelid>
                            <standard/>
                        </smchannel>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis="", smchannel=smchannel)
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertEqual(
            "mlsCurrent:Mnt1lifeTimechan1",
            self.mapper.destination.scan.scan_modules[1]
            .channels["mlsCurrent:Mnt2chan1"]
            .normalize_id,
        )

    def test_interval_channel_sets_normalise_id(self):
        smchannel = """<smchannel>
                            <channelid>mlsCurrent:Mnt2chan1</channelid>
                            <normalize_id>mlsCurrent:Mnt1lifeTimechan1</normalize_id>
                            <interval>
                                <triggerinterval>1.0</triggerinterval>
                                <stoppedby>mlsCurrent:Mnt1chan1</stoppedby>
                            </interval>
                        </smchannel>
                        <smchannel>
                            <channelid>mlsCurrent:Mnt1lifeTimechan1</channelid>
                            <standard/>
                        </smchannel>
                        <smchannel>
                            <channelid>mlsCurrent:Mnt1chan1</channelid>
                            <standard>
                                <sendreadyevent>true</sendreadyevent>
                            </standard>
                        </smchannel>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis="", smchannel=smchannel)
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertEqual(
            "mlsCurrent:Mnt1lifeTimechan1",
            self.mapper.destination.scan.scan_modules[1]
            .channels["mlsCurrent:Mnt2chan1"]
            .normalize_id,
        )

    def test_map_channel_sets_average_channel(self):
        smchannel = """<smchannel>
                            <channelid>mlsCurrent:Mnt1lifeTimechan1</channelid>
                            <standard>
                                <averagecount>5</averagecount>
                                <maxdeviation>5.0</maxdeviation>
                                <minimum>1.0E-5</minimum>
                                <maxattempts>10</maxattempts>
                            </standard>
                        </smchannel>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis="", smchannel=smchannel)
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertIsInstance(
            self.mapper.destination.scan.scan_modules[1].channels[
                "mlsCurrent:Mnt1lifeTimechan1"
            ],
            scan.AverageChannel,
        )
        self.assertEqual(
            5,
            self.mapper.destination.scan.scan_modules[1]
            .channels["mlsCurrent:Mnt1lifeTimechan1"]
            .n_averages,
        )
        self.assertEqual(
            5.0,
            self.mapper.destination.scan.scan_modules[1]
            .channels["mlsCurrent:Mnt1lifeTimechan1"]
            .max_deviation,
        )
        self.assertEqual(
            1e-5,
            self.mapper.destination.scan.scan_modules[1]
            .channels["mlsCurrent:Mnt1lifeTimechan1"]
            .low_limit,
        )
        self.assertEqual(
            10,
            self.mapper.destination.scan.scan_modules[1]
            .channels["mlsCurrent:Mnt1lifeTimechan1"]
            .max_attempts,
        )

    def test_map_prescan(self):
        smchannel = """<prescan>
                            <id>SimMt:testrack01000.LLM</id>
                            <value type="double">30</value>
                        </prescan>
                        <prescan>
                            <id>K0617:gw24126.SCAN</id>
                            <value type="string">Passive</value>
                        </prescan>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis="", smchannel=smchannel)
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        pre_scan_settings = self.mapper.destination.scan.scan_modules[
            1
        ].pre_scan_settings
        self.assertTrue(pre_scan_settings)
        for item in pre_scan_settings.values():
            self.assertIsInstance(item, scan.PreScan)
            self.assertTrue(item.id)
            self.assertTrue(item.value)
        self.assertIsInstance(
            pre_scan_settings["SimMt:testrack01000.LLM"].value, float
        )
        self.assertIsInstance(
            pre_scan_settings["K0617:gw24126.SCAN"].value, str
        )

    def test_map_postscan(self):
        smchannel = """<prescan>
                            <id>SimMt:testrack01000.LLM</id>
                            <value type="double">30</value>
                        </prescan>
                        <postscan>
                            <id>SimMt:testrack01000.LLM</id>
                            <reset_originalvalue>true</reset_originalvalue>
                        </postscan>
                        <postscan>
                            <id>K0617:gw24126.SCAN</id>
                            <value type="string">.5 second</value>
                        </postscan>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis="", smchannel=smchannel)
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        post_scan_settings = self.mapper.destination.scan.scan_modules[
            1
        ].post_scan_settings
        self.assertTrue(post_scan_settings)
        for item in post_scan_settings.values():
            self.assertIsInstance(item, scan.PostScan)
            self.assertTrue(item.id)
        self.assertTrue(
            post_scan_settings["SimMt:testrack01000.LLM"].reset_original_value
        )
        self.assertIsInstance(
            post_scan_settings["K0617:gw24126.SCAN"].value, str
        )

    def test_map_postscan_sets_original_value(self):
        smchannel = """<prescan>
                            <id>SimMt:testrack01000.LLM</id>
                            <value type="double">30</value>
                        </prescan>
                        <postscan>
                            <id>SimMt:testrack01000.LLM</id>
                            <reset_originalvalue>true</reset_originalvalue>
                        </postscan>"""
        template = Template(MINIMAL_SCML_TEMPLATE)
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=template.substitute(smaxis="", smchannel=smchannel)
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        pre_scan_settings = self.mapper.destination.scan.scan_modules[
            1
        ].pre_scan_settings
        post_scan_settings = self.mapper.destination.scan.scan_modules[
            1
        ].post_scan_settings
        self.assertEqual(
            pre_scan_settings["SimMt:testrack01000.LLM"].value,
            post_scan_settings["SimMt:testrack01000.LLM"].value,
        )


class TestVersionMapperV9m1(unittest.TestCase):
    def setUp(self):
        self.mapper = version_mapping.VersionMapperV9m1()

    def test_instantiate_class(self):
        pass

    def test_map_sets_scan_metadata(self):
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=SCML_STRING.replace("<version>9.0", "<version>9.1")
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertEqual(
            int(self.mapper.source.scan.find("repeatcount").text),
            self.mapper.destination.scan.repeat_count,
        )
        self.assertEqual(
            self.mapper.source.scan.find("comment").text,
            self.mapper.destination.scan.comment,
        )


class TestVersionMapperV9m2(unittest.TestCase):
    def setUp(self):
        self.mapper = version_mapping.VersionMapperV9m2()

    def test_instantiate_class(self):
        pass

    def test_map_sets_scan_metadata(self):
        self.mapper.source = SCML()
        self.mapper.source.from_string(
            xml=SCML_STRING.replace("<version>9.0", "<version>9.2")
        )
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertEqual(
            int(self.mapper.source.scan.find("repeatcount").text),
            self.mapper.destination.scan.repeat_count,
        )
        self.assertEqual(
            self.mapper.source.scan.find("comment").text,
            self.mapper.destination.scan.comment,
        )
