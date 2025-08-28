"""
*High-level Python object representation of SCML file contents.*

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 1

This module provides a high-level representation of the contents of an SCML
file. Being a high-level, user-facing object representation, technically
speaking this module is a facade. The corresponding resource
(persistence-layer-facing interface) would be the :mod:`scml
<evedata.scan.boundaries.scml>` module.


Overview
========

A first overview of the classes implemented in this module and their
hierarchy is given in the UML diagram below.


.. figure:: /uml/evedata.scan.boundaries.scan.*
    :align: center

    Class hierarchy of the :mod:`scan.boundaries.scan
    <evedata.scan.boundaries.scan>` module, providing the facades for the
    scan and setup descriptions. Currently, the basic idea is to inherit
    from the :class:`File <evedata.scan.entities.file.File>`class and extend
    it accordingly, adding behaviour and implementing the :class:`File
    <evedata.scan.boundaries.scan.File>` interface. The difference between
    the :meth:`load() <evedata.scan.boundaries.scan.File.load>` and
    :meth:`extract() <evedata.scan.boundaries.scan.Scan.extract>` methods:
    While :meth:`load() <evedata.scan.boundaries.scan.File.load>` loads a
    file from the file system, :meth:`extract()
    <evedata.scan.boundaries.scan.Scan.extract>` extracts the SCML from the
    user block of a given HDF5 file.


When loading an SCML/XML file, the :class:`SCML
<evedata.scan.boundaries.scml.SCML>` class is called to read the actual XML,
and afterwards, the contents are mapped to the entities defined in the
:mod:`entities <evedata.scan.entities>` subpackage.


Key aspects
===========

The key characteristics of the module are:

* Stable interface to SCML files, regardless of their version.

  * Some features may only be available for newer SCML versions, though.

* Access to the complete relevant information contained in an SCML file.


Usage
=====

Loading the scan description contained in an eveH5 data file of a measurement
may be as simple as:

.. code-block::

    from evedata.scan.boundaries.scan import Scan

    scan = Scan()
    scan.extract(filename="my_measurement_file.h5")



Internals: What happens when reading an SCML file?
==================================================

...


Module documentation
====================

"""

import logging
import struct
import zlib

from evedata.scan.boundaries.scml import SCML
from evedata.scan.controllers.version_mapping import VersionMapperFactory
from evedata.scan.entities.file import File as SCMLFile


logger = logging.getLogger(__name__)


class File:
    """
    Interface class for SCML files.

    There are two distinct XML files following the SCML schema definition,
    represented by the :class:`Scan` and :class:`Station` classes. The
    :class:`Scan` class contains the scan description and information on all
    devices directly used in scan modules, while the :class:`Station` class
    represents the XML file loaded by the engine when executing a scan that
    contains information on all devices available for a given measurement
    station. Both, :class:`Scan` and :class:`Station`, share a lot of
    functionality that is available from and defined in this interface.


    Attributes
    ----------
    version : :class:`str`
        Schema version of the SCML file.


    Examples
    --------
    Being an interface, this class is not meant to be used directly,
    but only by using one of the classes implementing it: :class:`Scan` and
    :class:`Station`.

    """

    def __init__(self):
        super().__init__()
        self.version = ""
        self.filename = ""
        self._scml = SCML()

    def load(self, filename=""):
        """
        Load contents of an SCML file.

        Parameters
        ----------
        filename : :class:`str`
            Name of the file to load.

        """
        if filename:
            self.filename = filename
        self._scml.load(filename=self.filename)
        self._map()

    def _map(self):
        mapper_factory = VersionMapperFactory()
        mapper = mapper_factory.get_mapper(self._scml)
        # noinspection PyTypeChecker
        mapper.map(source=self._scml, destination=self)


class Scan(File, SCMLFile):
    """
    High-level Python object representation of a scan description.

    This class serves as facade to the entire :mod:`evedata.scan`
    subpackage and provides a rather high-level representation of the
    contents of the scan description stored in an individual SCML file.


    Attributes
    ----------
    version : :class:`str`
        Schema version of the SCML file represented by this class.

    location : :class:`str`
        Name of the measurement station the scan was executed at.

    scan : :class:`evedata.scan.entities.scan.Scan`
        Representation of all information available for the scan.

    Raises
    ------
    exception
        Short description when and why raised


    Examples
    --------
    Loading the scan description contained in an eveH5 data file of a
    measurement may be as simple as:

    .. code-block::

        scan = Scan()
        scan.extract(filename="my_measurement_file.h5")

    If you are ever in the situation to load a separate SCML file, this is
    possible as well:

    .. code-block::

        scan = Scan()
        scan.load(filename="my_scan_description.scml")

    In most cases, however, you need not be concerned with loading the
    SCML file at all, as the :class:`EveFile
    <evedata.evefile.boundaries.evefile.EveFile>` and :class:`Measurement
    <evedata.measurement.boundaries.measurement.Measurement>` classes will
    take care of that for you.

    """

    def __init__(self):  # noqa
        super().__init__()
        self._marker = b"EVEcSCML"

    def extract(self, filename=""):
        """
        Extract SCML from the user part of an eveH5 file.

        Parameters
        ----------
        filename : :class:`str`
            Name of the file to load.


        A short description of the way the scan description (SCML) is
        contained in eveH5 files:

        * Generally, the SCML is located at the beginning of the file,
          therefore interpreted by HDF5 as "user data".
        * The first eight bytes of an eveH5 file containing the SCML read
          "EVEcSCML".
        * The next four bytes are the length of the compressed SCML file
          (encoded as big-endian unsigned integer, "!L").
        * The next four bytes are the length of the uncompressed SCML file
          (encoded as big-endian unsigned integer, "!L") - an information
          that is not needed here.
        * The next (length compressed SCML file) bytes are the
          ZIP-compressed contents of the actual SCML file.
        * As a user data block in HDF5 files needs to be 2^n bytes long,
          the remaining space to the next power of 2 is padded with zeros.

        """
        if not filename:
            filename = self.filename
        with open(filename, "rb") as file:
            marker = file.read(8)
            if marker == self._marker:
                compressed_length = struct.unpack("!L", file.read(4))[0]
                file.read(4)  # Uncompressed length, not needed here
                self._scml.from_string(
                    xml=zlib.decompress(file.read(compressed_length)).decode()
                )
                self._map()
