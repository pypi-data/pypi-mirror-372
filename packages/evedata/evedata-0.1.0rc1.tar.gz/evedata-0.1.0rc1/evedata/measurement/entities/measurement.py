r"""
*Entities representing a measurement, typically read from an eveH5 file.*

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


Overview
========

A first overview of the classes implemented in this module and their
hierarchy is given in the UML diagram below. Key is the :class:`Measurement
entity <evedata.measurement.entities.measurement.Measurement>`.
:class:`Data` and :class:`Axis` seem not to be used here, but become
essential in the corresponding :class:`Measurement facade
<evedata.measurement.boundaries.measurement.Measurement>`. See
:numref:`Fig. %s <fig-uml_evedata.measurement.boundaries.measurement>` and
the :mod:`measurement.boundaries.measurement
<evedata.measurement.boundaries.measurement>` module for details.


.. figure:: /uml/evedata.measurement.entities.measurement.*
    :align: center

    Class hierarchy of the :mod:`measurement.entities.measurement
    <evedata.measurement.entities.measurement>` module. Currently, this
    diagram just reflects first ideas for a more abstract representation of a
    measurement as compared to the data model of the evefile subpackage.
    Devices in the scan_modules are all the detector(channel)s and motor(axe)s
    used in a scan. Distinguishing between detector(channel)s/motor(axe)s,
    beamline, and machine can (at least partially) happen based on the data
    type: detector(channel)s are :class:`ChannelData
    <evedata.evefile.entities.data.ChannelData>`, motor(axe)s are 
    :class:`AxisData <evedata.evefile.entities.data.AxisData>`. Machine 
    and beamline parameters are more tricky, as they can be 
    :class:`DeviceData <evedata.evefile.entities.data.DeviceData>` (from 
    the "monitor" section) as well as :class:`ChannelData 
    <evedata.evefile.entities.data.ChannelData>` (and :class:`AxisData 
    <evedata.evefile.entities.data.AxisData>` for shutters and alike?) 
    from the original "main" and "snapshot" sections. :class:`Scan` and 
    :class:`Setup` inherit directly from their counterparts in the 
    :mod:`evefile.entities.file <evedata.evefile.entities.file>` module. 
    :class:`Data` and :class:`Axis` seem not to be used here, but become 
    essential in the corresponding :class:`Measurement 
    <evedata.measurement.boundaries.measurement.Measurement>` facade. See 
    :numref:`Fig. %s <fig-uml_evedata.measurement.boundaries.measurement>` 
    for details.


Key aspects
===========

* The :class:`Measurement` class, although quite similar on first sight to
  the :class:`EveFile <evedata.evefile.boundaries.evefile.EveFile>` class,
  does not inherit from there nor from :class:`File
  <evedata.evefile.entities.file.File>`. Nevertheless, the contents of the
  attributes are in many cases the same objects as those of these other
  two classes.


Module documentation
====================

"""

import logging

import numpy as np

from evedata.measurement.entities.metadata import Metadata

logger = logging.getLogger(__name__)


class Measurement:
    """
    Representation of all information available for a given measurement.

    Individual measurements are saved in HDF5 files using a particular
    schema (eveH5). Besides file-level metadata, there are log messages,
    a scan description (originally an XML/SCML file), and the actual data.

    The data are organised in three functionally different sections:
    scan_modules, machine, and beamline.


    Attributes
    ----------
    scan_modules : :class:`dict`
        Modules the scan consists of.

        Each item is an instance of
        :class:`evedata.evefile.entities.file.ScanModule` and contains the
        data recorded within the given scan module.

        In case of no scan description present, a "dummy" scan module will
        be created containing *all* data.

    machine : :class:`dict`
        Data recorded from the machine involved in a measurement.

        Each item is an instance of
        :class:`evedata.evefile.entities.data.Data`.

    beamline : :class:`dict`
        Data recorded from the beamline involved in a measurement.

        Each item is an instance of
        :class:`evedata.evefile.entities.data.Data`.

    device_snapshots : :class:`dict`
        Snapshot data recorded from the devices involved in a scan.

        Each item is an instance of
        :class:`evedata.evefile.entities.data.MeasureData`.

        Snapshots reflect, as their name says, the state of the devices at a
        given point in time. Snapshots of devices involved in a scan are
        used in :mod:`data joining <evedata.measurement.controllers.joining>`
        to get additional reference points.

    metadata : :class:`evedata.measurement.entities.metadata.Metadata`
        Measurement metadata

    log_messages : :class:`list`
        Log messages from an individual measurement

        Each item in the list is an instance of
        :class:`evedata.evefile.entities.file.LogMessage`.

    scan : :class:`evedata.scan.boundaries.scan.Scan`
        Description of the actual scan.

    station : :class:`Station`
        Description of the actual setup.

    Raises
    ------
    exception
        Short description when and why raised

    """

    def __init__(self):
        self.scan_modules = {}
        self.machine = {}
        self.beamline = {}
        self.device_snapshots = {}
        self.metadata = Metadata()
        self.scan = None
        self.station = None
        self.log_messages = []


class Data:
    """
    Unit containing both, numeric data and corresponding axes.

    The data class ensures consistency in terms of dimensions between
    numerical data and axes.

    Parameters
    ----------
    data : :class:`numpy.ndarray`
        Numerical data

    axes : :class:`list`
        List of objects of type :class:`aspecd.dataset.Axis`

        The number of axes needs to be consistent with the dimensions of data.

        Axes will be set automatically when setting data. Hence,
        the easiest is to first set data and only afterwards set axis values.

    Raises
    ------
    IndexError
        Raised if number of axes is inconsistent with data dimensions

    IndexError
        Raised if axes values are inconsistent with data

    """

    def __init__(self, data=np.zeros(0), axes=None):
        self._data = data
        self._axes = []
        if axes is None:
            self._create_axes()
        else:
            self.axes = axes

    @property
    def data(self):
        """Get or set (numeric) data.

        .. note::
            If you set data that have different dimensions to the data
            previously stored in the dataset, the axes values will be
            set to an array with indices corresponding to the size of the
            respective data dimension. You will most probably assign proper
            axis values afterwards. On the other hand, all other
            information stored in the axis object will be retained, namely
            quantity, unit, and label.

        """
        return self._data

    @data.setter
    def data(self, data):
        old_shape = self._data.shape
        self._data = data
        if old_shape != data.shape:
            if self.axes[0].values.size == 0:
                self._create_axes()
            self._update_axes()

    @property
    def axes(self):
        """Get or set axes.

        If you set axes, they will be checked for consistency with the data.
        Therefore, first set the data and only afterwards the axes,
        with values corresponding to the dimensions of the data.

        Raises
        ------
        IndexError
            Raised if number of axes is inconsistent with data dimensions

        IndexError
            Raised if axes values are inconsistent with data dimensions

        """
        return self._axes

    @axes.setter
    def axes(self, axes):
        self._axes = axes
        self._check_axes()

    def _create_axes(self):
        self._axes = []
        missing_axes = self._data.ndim + 1
        # pylint: disable=unused-variable
        # pylint: disable=invalid-name
        for ax in range(missing_axes):
            self._axes.append(Axis())

    def _update_axes(self):
        """
        Update axes according to data

        .. note::
            It turned out to be a bad idea to automatically *remove* an
            axis, as you usually do not know which axis to remove. Hence,
            if some task reduces the dimensionality of the data, this task
            is responsible to adjust the axes as well (*i.e.*, remove the
            *correct* axis object from the list).
        """
        data_shape = self.data.shape
        if len(self.axes) < self.data.ndim + 1:
            self._axes.append(Axis())
        for index in range(self.data.ndim):
            if len(self.axes[index].values) != data_shape[index]:
                self.axes[index].values = np.arange(
                    data_shape[index], dtype=np.float64
                )

    def _check_axes(self):
        if len(self._axes) > self.data.ndim + 1:
            raise IndexError
        data_shape = self.data.shape
        for index in range(self.data.ndim):
            if len(self.axes[index].values) != data_shape[index]:
                raise IndexError


class Axis:
    """
    Axis for data.

    An axis contains always both, numerical values as well as the metadata
    necessary to create axis labels and to make sense of the numerical
    information.


    Attributes
    ----------
    quantity : :class:`str`
        quantity of the numerical data, usually used as first part of an
        automatically generated axis label

    unit : :class:`str`
        unit of the numerical data, usually used as second part of an
        automatically generated axis label

    symbol : :class:`str`
        symbol for the quantity of the numerical data, usually used as first
        part of an automatically generated axis label

    label : :class:`str`
        manual label for the axis, particularly useful in cases where no
        quantity and unit are provided or should be overwritten.


    .. note::
        There are three alternative ways of writing axis labels, one with
        using the quantity name and the unit, one with using the quantity
        symbol and the unit, and one using both, quantity name and symbol,
        usually separated by comma. Quantity and unit shall always be
        separated by a slash. Which way you prefer is a matter of personal
        taste and given context.


    Raises
    ------
    ValueError
        Raised when trying to set axis values to another type than numpy array

    IndexError
        Raised when trying to set axis values to an array with more than one
        dimension.
        Raised if index does not have the same length as values.

    """

    def __init__(self):
        self.label = ""
        self.quantity = ""
        self.symbol = ""
        self.unit = ""
        self._values = np.zeros(0)
        self._equidistant = None

    @property
    def values(self):
        """
        Get or set the numerical axis values.

        Values require to be a one-dimensional numpy array. Trying to set
        values to either a different type that cannot be converted to a
        numpy array or a numpy array with more than one dimension will raise
        a corresponding error.

        Raises
        ------
        ValueError
            Raised if axis values are of wrong type
        IndexError
            Raised if axis values are of wrong dimension, i.e. not a vector

        """
        return self._values

    @values.setter
    def values(self, values):
        if not isinstance(values, type(self._values)):
            values = np.asarray(values)
            if (
                not isinstance(values, type(self._values))
                or values.dtype != self._values.dtype
            ):
                raise ValueError(
                    f"Wrong type: expected {self._values.dtype}, "
                    f"got {values.dtype}"
                )
        if values.ndim > 1:
            raise IndexError("Values need to be one-dimensional")
        self._values = values
        self._set_equidistant_property()

    @property
    def equidistant(self):
        """Return whether the axes values are equidistant.

        True if the axis values are equidistant, False otherwise. None in
        case of no axis values.

        The property is set automatically if axis values are set and
        therefore read-only.

        While simple plotting of data values against non-uniform axes with
        non-equidistant values is usually straightforward, many processing
        steps rely on equidistant axis values in their simplest possible
        implementation.

        """
        return self._equidistant

    def _set_equidistant_property(self):
        if not self.values.size or not self.values.all():
            return
        differences = self.values[1:] - self.values[0:-1]
        self._equidistant = np.isclose(differences.max(), differences.min())
