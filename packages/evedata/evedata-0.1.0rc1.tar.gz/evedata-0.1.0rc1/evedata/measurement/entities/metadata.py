r"""
*Metadata corresponding to a measurement.*

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 1

A measurement generally reflects all the data obtained during a
measurement. However, to plot data or to perform some analysis, usually we
need data together with an axis (or multiple axes for *n*\D data),
where data ("intensity values") and axis values come from different HDF5
datasets. Furthermore, there may generally be the need/interest to plot
arbitrary data against each other, *i.e.* channel data *vs.* channel data
and axis data *vs.* axis data, not only channel data *vs.* axis data. This
is the decisive difference between the :class:`Measurement entity
<evedata.measurement.entities.measurement.Measurement>` and the
:class:`Measurement facade
<evedata.measurement.boundaries.measurement.Measurement>`, with the latter
having the additional attributes for storing the data to work on.

Metadata are a crucial part of reproducibility. Furthermore, metadata allow
analysis routines to gain a "semantic" understanding of the data and hence
perform (at least some) actions unattended and fully automatically. While all
metadata corresponding to the individual devices used in recording data are
stored in the :attr:`metadata <evedata.evefile.entities.data.Data.metadata>`
attribute of the :class:`Data <evedata.evefile.entities.data.Data>` class
(and its descendants), there are other types of metadata that belong to the
measurement as such itself. These are modelled in the :mod:`metadata
<evedata.measurement.entities.metadata>` module in the :class:`Metadata
<evedata.measurement.entities.metadata.Metadata>` class.


Overview
========

A first overview of the classes implemented in this module and their
hierarchy is given in the UML diagram below.


.. figure:: /uml/evedata.measurement.entities.metadata.*
    :align: center

    While the :class:`Metadata
    <evedata.measurement.entities.metadata.Metadata>` class inherits directly
    from its counterpart from the :mod:`evedata.evefile.entities.file` module,
    it is extended in crucial ways, reflecting the aim for more reproducible
    measurements and having datasets containing all crucial information in
    one place. This involves information on both, the machine (BESSY-II, MLS)
    and the beamline, but on the sample(s) as well. Perhaps the ``sample``
    attribute should be a dictionary rather than a plain list, with (unique)
    labels for each sample as keys.


As of now, the eveH5 files do not contain any metadata regarding machine,
beamline, or sample(s). The names of the machine and beamline can most
probably be inferred, having the name of the beamline obviously allows to
assign the machine as well.

Given that one measurement (*i.e.* one scan resulting in one eveH5 file)
can span multiple samples, and will often do, in the future, at least some
basic information regarding the sample(s) should be added to the eveH5 file
and read and mapped accordingly to instances of the :class:`Sample
<evedata.measurement.entities.metadata.Sample>` class, one instance per
sample. Potentially, this allows to assign parts of the measured data to
individual samples and hence automate data processing and analysis, *e.g.*
splitting the data for the different samples into separate datasets/files.


Key aspects
===========

* xxx


Module documentation
====================

"""

import logging

from evedata.evefile.entities.file import Metadata as FileMetadata

logger = logging.getLogger(__name__)


class Metadata(FileMetadata):
    """
    Metadata of a given measurement resulting in an eveH5 file.

    As measurements result in individual files, there is a series of
    crucial metadata of such a measurement on this global level.

    In addition to the :class:`base class
    <evedata.evefile.entities.file.Metadata>`, information on the
    machine, beamline, and sample(s) measured are stored.


    Attributes
    ----------
    filename : :class:`str`
        Name (full path) of the eveH5 file.

    eveh5_version : :class:`str`
        Version of the eveH5 schema.

    eve_version : :class:`str`
        Version of the eve engine used to record the data.

    xml_version : :class:`str`
        Version of the schema used for the scan description (SCML/XML)

    measurement_station : :class:`str`
        Name of the measurement station used to record the data.

    start : :class:`datetime.datetime`
        Timestamp of the start of the measurement

    end : :class:`datetime.datetime`
        Timestamp of the end of the measurement

    description : :class:`str`
        User-entered description of the entire scan.

    simulation : :class:`bool`
        Flag signalling whether the measurement was a simulation.

        Default: ``False``

    preferred_axis : :class:`string`
        Name of the axis marked as preferred in the scan description.

        Default: ""

    preferred_channel : :class:`string`
        Name of the channel marked as preferred in the scan description.

        Default: ""

    preferred_normalisation_channel : :class:`string`
        Name of the channel marked as preferred for normalising.

        Default: ""

    sample : :class:`List`
        Metadata for each individual sample.

        Each element of the list is of type :class:`Sample`.

    machine : :class:`Machine`
        Metadata for the machine (BESSY-II, MLS) used for the measurement.

    beamline : :class:`Beamline`
        Metadata for the beamline used for the measurement.

    Raises
    ------
    exception
        Short description when and why raised

    """

    def __init__(self):
        super().__init__()
        self.sample = []
        self.machine = None
        self.beamline = None


class Sample:
    """
    Metadata of a given sample that has been measured.

    As multiple samples can be measured within one measurement,
    the :class:`Metadata` class associated with a :class:`Measurement
    <evedata.measurement.entities.measurement.Measurement>` contains a
    list of :obj:`Sample` objects in its :attr:`Metadata.sample` attribute.


    Attributes
    ----------
    name : :class:`str`
        Short, descriptive name of the sample

    id : :class:`str`
        Unique identifier of the sample

    """

    def __init__(self):
        self.name = ""
        self.id = ""  # pylint: disable=invalid-name
