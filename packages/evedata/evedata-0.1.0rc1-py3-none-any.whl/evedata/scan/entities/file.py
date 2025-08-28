"""

*Entities representing an SCML file on the entire file level.*

Overview
========

A first overview of the classes implemented in this module and their
hierarchy is given in the UML diagram below.


.. figure:: /uml/evedata.scan.entities.file.*
    :align: center

    Class hierarchy of the :mod:`scan.entities.file
    <evedata.scan.entities.file>` module, closely resembling the schema of
    the SCML file. Currently, the location of the :class:`Plugin` class and
    its dependencies is not decided, as it is not entirely clear whether
    this information is relevant enough to be mapped.


.. important::

    Note that for the time being, only a subset of the classes shown in the
    above UML diagram are implemented, and only the most relevant attributes
    of these classes.



Module documentation
====================

"""

import logging

from evedata.scan.entities.scan import Scan

logger = logging.getLogger(__name__)


class File:
    """
    Representation of all information available from a given SCML file.

    An SCML file usually consists of a series of metadata, a scan block with
    the scan description, and a setup part with information of the
    detectors, motors, and devices used in a scan or available at a
    measurement station.

    The schema of the SCML file is defined in an XML schema definition (XSD)
    file. Furthermore, there exist several versions of the SCML schema the
    entities of the :mod:`entities <evedata.scan.entities>` subpackage are
    not concerned with.


    Attributes
    ----------
    location : :class:`str`
        Name of the measurement station the scan was executed at.

    scan : :class:`evedata.scan.entities.scan.Scan`
        Representation of all information available for the scan.


    Examples
    --------
    The :class:`File` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.scan` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        self.location = ""
        self.scan = Scan()
