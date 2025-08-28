"""
*Low-level Python object representation of SCML file contents.*

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 1

This module provides a low-level representation of the contents of an SCML
file that can be mapped to the :class:`Scan
<evedata.scan.boundaries.scan.Scan>` and :class:`Station
<evedata.scan.boundaries.scan.Station>` interfaces.  Being a low-level
object representation, technically speaking this module is a resource. The
corresponding facade (user-facing interface) would be the :mod:`scan
<evedata.scan.boundaries.scan>` module.


Overview
========

A first overview of the classes implemented in this module and their
hierarchy is given in the UML diagram below.


TBD


Key aspects
===========

Despite being a low-level interface to SCML files, the scml module
provides a series of abstractions and special behaviour summarised below:

* ...


Usage
=====

SCML files are XML files following a particular XML Schema Definition (XSD)
and contain potentially a scan definition and definitions for devices
(detectors, motors, devices).

SCML files can exist either as files in the file system, or can be loaded as
text from other places, *e.g.* the user block of an eveH5 HDF5 file. Hence,
there are two distinct methods for loading the contents of an SCML file.

In case of a file in the file system, use the :meth:`load` method:

.. code-block::

    scml = SCML()
    scml.load(filename="my_scml_file.scml")

In case of an SCML file read from, *e.g.*, the user block of an eveH5 HDF5
file, the contents of the SCML file will typically be contained in a
variable -- in our case ``scml_contents``:

.. code-block::

    scml = SCML()
    scml.from_string(xml=scml_contents)

In both cases, the :attr:`root` attribute will be set to the root element of
the SCML file read. Afterwards, you can access the other attributes,
:attr:`scan`, :attr:`scan_modules`, :attr:`detectors`, :attr:`motors`,
and :attr:`devices` as needed, to further process the contents of the SCML
file.


Module documentation
====================

"""

import logging
from xml.etree import ElementTree as ET  # noqa:N817


logger = logging.getLogger(__name__)


class SCML:
    """
    Representation of an SCML file.

    SCML files are XML files following a distinct schema and can contain
    descriptions of a scan performed by the engine as well as a list of
    devices (detectors, motors, devices), either those actually used in a
    scan or those of the entire measurement station.

    Currently, to read the SCML file, the :mod:`xml.etree.ElementTree`
    module gets used. Furthermore, the attributes :attr:`scan`,
    :attr:`scan_modules`, :attr:`detectors`, :attr:`motors`,
    and :attr:`devices` contain crucial parts of the SCML, simplifying
    further processing and mapping of the SCML contents to Python objects
    from the :mod:`scan.entities <evedata.scan.entities>` subpackage.


    Attributes
    ----------
    root : :class:`xml.etree.ElementTree.Element`
        Root element of the SCML file read.

    version : :class:`str`
        Schema version of the SCML file loaded.

        The reason behind directly mapping this information here is to allow
        the :class:`VersionMapperFactory
        <evedata.scan.controllers.version_mapper.VersionMapperFactory>` to
        return the correct :obj:`VersionMapper
        <evedata.scan.controllers.version_mapper.VersionMapper>` object.


    Examples
    --------
    SCML files are XML files following a particular XML Schema Definition
    (XSD) and contain potentially a scan definition and definitions for
    devices (detectors, motors, devices).

    SCML files can exist either as files in the file system, or can be
    loaded as text from other places, *e.g.* the user block of an eveH5 HDF5
    file. Hence, there are two distinct methods for loading the contents of
    an SCML file.

    In case of a file in the file system, use the :meth:`load` method:

    .. code-block::

        scml = SCML()
        scml.load(filename="my_scml_file.scml")

    In case of an SCML file read from, *e.g.*, the user block of an eveH5
    HDF5 file, the contents of the SCML file will typically be contained in a
    variable -- in our case ``scml_contents``:

    .. code-block::

        scml = SCML()
        scml.from_string(xml=scml_contents)

    In both cases, the :attr:`root` attribute will be set to the root
    element of the SCML file read. Afterwards, you can access the other
    attributes, :attr:`scan`, :attr:`scan_modules`, :attr:`detectors`,
    :attr:`motors`, and :attr:`devices` as needed, to further process the
    contents of the SCML file.

    """

    def __init__(self):
        self.root = None
        self.version = ""

    @property
    def scan(self):
        """
        Scan block of the SCML file.

        Note that not every SCML/XML file necessarily contains a scan block.
        Those XML files describing the devices (detectors, motors, devices)
        available at a measurement station do *not* contain a scan block.

        Returns
        -------
        scan : :class:`xml.etree.ElementTree.Element`
            Scan element of the SCML file.

        """
        try:
            scan = next(self.root.iter("scan"))
        except AttributeError:
            scan = None
        return scan

    @property
    def scan_modules(self):
        """
        Scan modules contained in the scan block of the SCML file.

        Note that not every SCML/XML file necessarily contains a scan block.
        Those XML files describing the devices (detectors, motors, devices)
        available at a measurement station do *not* contain a scan block.

        Returns
        -------
        modules : :class:`list`
            Scan modules of the SCML file.

            Each element in the list is an
            :obj:`xml.etree.ElementTree.Element` object.

            Empty list if no SCML has been read or no scan modules could be
            found in the SCML file.

        """
        if self.root:
            modules = list(self.root.iter("scanmodule"))
        else:
            modules = []
        return modules

    @property
    def detectors(self):
        """
        Detectors defined in the SCML file.

        In case of an SCML file with a scan block, only those detectors
        actively used in the scan are contained. In case of an SCML/XML file
        describing the measurement station, all detectors defined and
        potentially available at this measurement station are contained.

        Returns
        -------
        detectors : :class:`list`
            Detectors defined in the SCML file.

            Each element in the list is an
            :obj:`xml.etree.ElementTree.Element` object.

            Empty list if no SCML has been read or no detectors could be
            found in the SCML file.

        """
        if self.root:
            detectors = list(self.root.iter("detector"))
        else:
            detectors = []
        return detectors

    @property
    def motors(self):
        """
        Motors defined in the SCML file.

        In case of an SCML file with a scan block, only those motors
        actively used in the scan are contained. In case of an SCML/XML file
        describing the measurement station, all motors defined and
        potentially available at this measurement station are contained.

        Returns
        -------
        motors : :class:`list`
            Motors defined in the SCML file.

            Each element in the list is an
            :obj:`xml.etree.ElementTree.Element` object.

            Empty list if no SCML has been read or no motors could be
            found in the SCML file.

        """
        if self.root:
            motors = list(self.root.iter("motor"))
        else:
            motors = []
        return motors

    @property
    def devices(self):
        """
        Devices defined in the SCML file.

        In case of an SCML file with a scan block, only those devices
        actively used in the scan are contained. In case of an SCML/XML file
        describing the measurement station, all devices defined and
        potentially available at this measurement station are contained.

        Returns
        -------
        devices : :class:`list`
            Devices defined in the SCML file.

            Each element in the list is an
            :obj:`xml.etree.ElementTree.Element` object.

            Empty list if no SCML has been read or no devices could be
            found in the SCML file.

        """
        if self.root:
            devices = list(self.root.iter("device"))
        else:
            devices = []
        return devices

    def load(self, filename=""):
        """
        Load SCML file and parse contents.

        The :attr:`root` element is set to the document root of the SCML
        file read.

        Parameters
        ----------
        filename : :class:`str`
            Name (path) of the SCML file

        """
        tree = ET.parse(filename)  # noqa: B314
        self.root = tree.getroot()
        self.version = self.root.find("version").text

    def from_string(self, xml=""):
        """
        Load SCML file from string and parse contents.

        The :attr:`root` element is set to the document root of the SCML
        file read.

        Parameters
        ----------
        xml : :class:`str`
            String representation of an SCML file.

        Raises
        ------
        ValueError
            Raised if no XML string is provided.

        """
        if not xml:
            raise ValueError("Missing XML string")
        self.root = ET.fromstring(xml)  # noqa: B314
        self.version = self.root.find("version").text
