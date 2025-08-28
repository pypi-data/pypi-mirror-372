r"""
.. include:: <isopub.txt>

*High-level Python object representation of a measurement.*

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 1

This module provides a high-level representation of a measurement as
manifested in an eveH5 file. Being a high-level, user-facing object
representation, technically speaking this module is a facade.

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

The big difference to the :mod:`evedata.evefile` subpackage: the
:mod:`evedata.measurement` subpackage abstracts from the underlying eveH5
file and its structure and provides aspects such as "filling" (*i.e.*, adding
data points for axes datasets to be able to plot arbitrary datasets against
each other).


Overview
========

A first overview of the classes implemented in this module and their
hierarchy is given in the UML diagram below.


.. figure:: /uml/evedata.measurement.boundaries.measurement.*
    :align: center

    Class hierarchy of the :mod:`measurement.boundaries.measurement
    <evedata.measurement.entities.measurement>` module. The
    :class:`Measurement
    <evedata.measurement.boundaries.measurement.Measurement>` facade inherits
    directly from its entities counterpart. The crucial extension here is
    the :attr:`data <Measurement.data>` attribute. This contains the actual
    data that should be plotted or processed further. Thus, the
    :class:`Measurement
    <evedata.measurement.boundaries.measurement.Measurement>` facade
    resembles the dataset concept known from the ASpecD framework and
    underlying, *i.a.*, the ``radiometry`` package. The
    :meth:`Measurement.set_axes() <Measurement.set_axes>` method
    takes care of "filling" (of the axes) if necessary. Furthermore, you can
    set the attribute of the underlying data object to obtain the data from,
    if it is not ``data``, but, *e.g.*, ``std`` or an option.


Key aspects
===========

The :mod:`measurement <evedata.measurement.boundaries.measurement>` module
is the high-level interface (facade) of the :mod:`evedata.measurement`
subpackage, abstracting much further away from the actual eveH5 files than
the :mod:`evefile <evedata.evefile.boundaries.evefile>` module in the
:mod:`evedata.evefile` subpackage. Hence, the key characteristics of the
module are:

* Stable interface to eveH5 files, regardless of their version.

  * Some features may only be available for newer eveH5 versions, though.

* Powerful abstractions on and beyond the device level.

  * Options to devices appear as attributes of the device objects, not as
    separate datasets.
  * Devices have clear, recognisable types, such as "multimeter", "MCA",
    "scientific camera", to name but a few.

* Access to the complete information contained in an eveH5 (and SCML) file,
  *i.e.*, data and scan description.
* Distinction between :attr:`data <Measurement.data>` and :attr:`devices
  <Measurement.devices>`:

  * Devices are all available devices used in the scan modules that
    produced some data.
  * Data is the current selection of devices to plot, process, or analyse
    data for.
  * Data always contains a *n*\D array with intensity values and
    corresponding axes.

* Distinction between :attr:`devices <Measurement.devices>` (setup),
  :attr:`beamline <Measurement.beamline>`, and :attr:`machine
  <Measurement.machine>`:

  * Devices are all available devices used in the scan modules that
    produced some data.
  * Beamline contains information from all devices that are part of the
    beamline, such as shutters, valves, and alike. Usually, only a few
    data points per scan are recorded for those devices, typically by
    means of snapshots.
  * Machine contains information regarding the actual synchrotron. These
    are "read-only" devices, and they may not be controlled by the
    measurement program, *i.e.* be actual monitors with time stamps rather
    than positions.

* **Data joining ("filling")** for ready-to-plot datasets.

  * Joining is only carried out for the currently selected devices in
    the "data" attribute.
  * Joining will generally be different for each combination of currently
    selected devices.
  * For details on joining, see the :mod:`joining
    <evedata.measurement.controllers.joining>` module.

* Actual **data are loaded on demand**, not when loading the file.

  * This does *not* apply to the metadata of the individual datasets.
    Those are read upon reading the file.
  * Reading data on demand should save time and resources, particularly
    for larger files.
  * Often, you are only interested in a subset of the available data.


Usage
=====

When using the :class:`Measurement` class, make sure you have a general
idea of the idea and architecture of the class. This means in particular:

* **Data are not stored as one large table**, with one column per "device",
  but in individual objects per device, mainly in the
  :attr:`devices <Measurement.devices>` attribute.
* One particular set of devices is usually assigned to be the **data to work
  on**, and stored in the :attr:`data <Measurement.data>` attribute,
  accordingly. Again, this is not a flat data array, but a composition of
  objects, containing data (*i.e.*, intensity values) and corresponding
  axes, together with the necessary metadata, such as quantity and unit.
  For further details, have a look at the :class:`Data
  <evedata.measurement.entities.measurement.Data>` class.
* **Data are loaded on demand**, *not* when loading the file. Hence, initial
  loading of a file should be pretty fast. If your file contains large
  data for an individual device, loading its data may take a bit when
  accessing them the first time.
* Joining ("filling") of data only takes place for those device data you
  explicitly set as "data to work on" (see above), and only the data of
  these devices will be made compatible. If you change either data or axes,
  this will generally result in a different join. For details on joining,
  see the :mod:`joining <evedata.measurement.controllers.joining>` module.
* The :class:`Measurement` class represents a **unit of data and metadata**.

Having that said, here you go with more details on how to use the
:class:`Measurement` class.


Loading eveH5 files
-------------------

Loading the contents of a data file of a measurement may be as simple as:

.. code-block::

    from evedata import Measurement

    measurement = Measurement()
    measurement.load(filename="my_measurement_file.h5")

Note that due to importing the :class:`Measurement` class into the main
namespace of the ``evedata`` package, you can import it directly from
there.

Of course, you could alternatively set the filename first,
thus shortening the :meth:`load` method call:

.. code-block::

    measurement = Measurement()
    measurement.filename = "my_measurement_file.h5"
    measurement.load()

There is even a third way -- instantiating the class already with a
given filename:

.. code-block::

    measurement = Measurement(filename="my_measurement_file.h5")
    measurement.load()

And yes, you can of course chain the object creation and loading the file
if you like. However, this leads to harder to read code and is therefore
*not* suggested.


Setting the data to work on
---------------------------

Measurements typically involve a large list of individual devices for
which data are recorded, and generally, the corresponding data are not of
same shape or length. However, typically you set the data of one device as
actual data (*i.e.*, intensity values or dependent variable), and the data of
another devices as axis values (independent variables). If the data are
incommensurable, some action needs to be taken to "broadcast" the axes
values to the dimension/shape of the data values. Otherwise, all typical
tasks such as plotting, processing, or analysis of the data would not be
possible.

If the scan you loaded the data from had the attributes
``preferredChannel`` and ``preferredAxis`` set, the data of the
corresponding devices will automatically be set to the :attr:`data
<Measurement.data>` attribute, and if necessary, the data made commensurable
(joined).

To explicitly set the data and/or axes to work on, two methods are
available: :meth:`Measurement.set_data` and :meth:`Measurement.set_axes`.
The name of these methods reflects their function:
:meth:`Measurement.set_data` sets the dependent variable, while
:meth:`Measurement.set_axes` sets the independent variable(s). In contrast
to the mathematical terms, the dependent variable takes precedence when
making the variables commensurate: the axes values will be changed if
necessary to fit the dimensions and shape of the data (dependent variable).

Whether you set channel or axes data as either axes or data is entirely
your choice. Thus, you can plot, *e.g.*, axes data as function of a
channel or another axis, as well as channel data as function of another
channel or axis.

Setting or changing the data to work on is as simple as calling two methods:

.. code-block::

    measurement.set_data(name="SimChan:01")
    measurement.set_axes(names=["SimMot:02"])

Note the slight difference in syntax for the two method calls: While
:meth:`Measurement.set_data` has a parameter ``name`` (singular) that is a
string, :meth:`Measurement.set_axes` has a parameter ``names`` (plural)
that is a list of device names, even if you set only one axis.

You need not set both, data and axes, if data had been set previously. If
you set only data, without any axes having been set previously,
axes values will automatically be filled with indices for you.

While devices are stored with their unique XML IDs as keys in the
:attr:`Measurement.devices` attribute, you can use either the unique XML
ID or the more readable and pronounceable name of the device to set either
data or axes.

As devices can have different attributes that can be used as data, you can
explicitly provide the attribute with the parameters ``field`` and
``fields``, respectively. One generic use case would be to set the axes
values to the positions data have been recorded for:

.. code-block::

    measurement.set_data(name="SimChan:01")
    measurement.set_axes(names=["SimChan:01"], fields=["positions"])

Other rather generic options would be the ``mean`` and ``std`` fields for
:class:`AverageChannelData
<evedata.evefile.entities.data.AverageChannelData>` and
:class:`IntervalChannelData
<evedata.evefile.entities.data.IntervalChannelData>`:

.. code-block::

    measurement.set_data(name="SimChan:01", field="mean")
    measurement.set_axes(names=["SimChan:01"])

In any case, you are responsible for setting valid attribute names a field
names. Otherwise, an :class:`AttributeError` will result.


Getting the names of the devices currently set as data
------------------------------------------------------

To get the names of the devices currently set as data and accompanying
axes, use the :attr:`Measurement.current_data` and
:attr:`Measurement.current_axes` attributes:

.. code-block::

    current_data = measurement.current_data
    current_axes = measurement.current_axes

Note that the names are the unique XML-IDs used as HDF5 dataset names. To
get the readable names, use :meth:`Measurement.get_name`:

.. code-block::

    current_data = measurement.get_name(measurement.current_data)
    current_axes = measurement.get_name(measurement.current_axes)

This is basically a convenience method for accessing the corresponding
metadata attribute of the device object:

.. code-block::

    current_data = measurement.devices[measurement.current_data].metadata.name

Furthermore, the :meth:`Measurement.get_name` method can handle both,
strings, *i.e.* single names, and lists of strings/names.


Getting the names of all available devices
------------------------------------------

As mentioned above, the devices are stored in the
:attr:`Measurement.devices` attribute with their unique XML IDs that are
not necessarily readable nor pronounceable. While you can set the axes and
data using either unique ID or name, you may sometimes be interested in
getting an overview of the names of all available devices. This can be
done using the :attr:`Measurement.device_names` attribute:

.. code-block::

    device_names = measurement.device_names  # returns a dict

This would result in a dict whose keys are the names and the values the
unique IDs. Make uss of the Python tools to get an iterable of all names.
To print all device names:

.. code-block::

    for name in measurement.device_names:
        print(name)

Of course, you could do the same for the unique IDs. However, in this 
case, simply iterate over the keys of the :attr:`Measurement.devices` 
attribute, and you're done.


Internals: What happens when reading an eveH5 file?
===================================================

Reading an eveH5 file is not as simple as reading contents of an HDF5 file
and present its contents as Python object hierarchy. At least, if you would
like to view, process, and analyse your data more conveniently, you should
not stop here. The idea behind the ``evedata`` package, and in parts behind
the :class:`Measurement` class, is to provide you as consumer of the data
with powerful abstractions and structured information. To this end,
a series of steps are necessary. Besides those described for the
underlying :class:`EveFile <evedata.evefile.boundaries.evefile.EveFile>`
class, these are:

* Copy all attributes from the :attr:`EveFile.metadata
  <evedata.evefile.boundaries.evefile.EveFile.metadata>` attribute to the
  :attr:`Measurement.metadata` attribute. |check|

* Copy the :attr:`EveFile.log_messages
  <evedata.evefile.boundaries.evefile.EveFile.log_messages>` attribute to the
  :attr:`Measurement.log_messages` attribute. |check|

* Move all data objects from the :attr:`EveFile.data
  <evedata.evefile.boundaries.evefile.EveFile.data>` attribute to the
  :attr:`Measurement.devices` attribute. |check|

  * Is this entirely true? How to deal with things such as current and
    lifetime that technically speaking belong to the machine section?

* Populate the :attr:`Measurement.machine` and :attr:`Measurement.beamline`
  attributes. |cross|

* Set the :attr:`Measurement.data` attribute with the data from the
  :attr:`EveFile.metadata.preferred_axis
  <evedata.evefile.entities.file.Metadata.preferred_axis>` and
  :attr:`EveFile.metadata.preferred_channel
  <evedata.evefile.entities.file.Metadata.preferred_channel>`
  attributes of the eveH5 file, if present. |check|

  * Set axis metadata (measure, unit). |check|
  * Join ("fill") data accordingly if necessary. |check|

* Copy the :attr:`EveFile.scan
  <evedata.evefile.boundaries.evefile.EveFile.scan>` attribute to the
  :attr:`Measurement.scan` attribute. |check|

* Copy the :attr:`EveFile.station
  <evedata.evefile.boundaries.evefile.EveFile.station>` attribute to the
  :attr:`Measurement.station` attribute. |cross|


Questions to address
====================

* How to deal with snapshots?

  * Currently, all devices from the snapshot section that are *not* as
    well part of the main section will end up in either
    :attr:`Measurement.machine` or :attr:`Measurement.beamline`.
  * Those snapshot devices that are part of the main section may be
    relevant for the filling, hence are stored in
    :attr:`Measurement.device_snapshots`.

* How to sensibly distinguish which of the datasets originally in the
  snapshot and monitor section belong to :attr:`Measurement.machine` and
  which to :attr:`Measurement.beamline`?

* How to deal with the :attr:`EveFile.position_timestamps
  <evedata.evefile.boundaries.evefile.EveFile.position_timestamps>` dataset?

  * This one is necessary for mapping monitor timestamps to positions,
    as well as to relate timestamps from log messages to positions or
    positions to absolute times, if necessary.
  * Could we deal with it internally, as we have a representation of the
    :obj:`EveFile <evedata.evefile.boundaries.evefile.EveFile>` object?

* Where to get metadata for machine, beamline, and samples from?


Module documentation
====================

"""

import logging

from evedata.evefile.boundaries.evefile import EveFile
from evedata.measurement.controllers import joining
from evedata.measurement.entities import measurement as entities

logger = logging.getLogger(__name__)


class Measurement(entities.Measurement):
    """
    High-level Python object representation of a measurement.

    This class serves as facade to the entire :mod:`evedata.measurement`
    subpackage and provides a rather high-level representation of the
    contents of an individual measurement, whose contents are stored in an
    eveH5 file.

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

    scan : :class:`evedata.evefile.entities.file.Scan`
        Description of the actual scan.

    station : :class:`Station`
        Description of the actual setup.

    data : :class:`evedata.measurement.entities.measurement.Data`
        Actual data that should be plotted or processed further.

        The attribute will usually be pre-filled with the data from the
        :attr:`Evefile.metadata.preferred_axis
        <evedata.evefile.entities.file.Metadata.preferred_axis>` and
        :attr:`EveFile.metadata.preferred_channel
        <evedata.evefile.entities.file.Metadata.preferred_channel>`
        attributes of the eveH5 file, if present. They can be set/changed
        using the :meth:`set_data` and :meth:`set_axes` methods.

    Parameters
    ----------
    filename : :class:`str`
        Name of the file to load data from

    join_type : :class:`str`
        Join type used to join data.

        Needs to be a valid class from the :mod:`joining
        <evedata.measurement.controllers.joining>` module.

        Default: "AxesLastFill"


    Examples
    --------
    Loading the contents of a data file of a measurement may be as simple as:

    .. code-block::

        from evedata import Measurement

        measurement = Measurement()
        measurement.load(filename="my_measurement_file.h5")

    Note that due to importing the :class:`Measurement` class into the main
    namespace of the ``evedata`` package, you can import it directly from
    there.

    Of course, you could alternatively set the filename first,
    thus shortening the :meth:`load` method call:

    .. code-block::

        measurement = Measurement()
        measurement.filename = "my_measurement_file.h5"
        measurement.load()

    There is even a third way -- instantiating the class already with a
    given filename:

    .. code-block::

        measurement = Measurement(filename="my_measurement_file.h5")
        measurement.load()

    If the attributes ``preferred_channel`` and ``preferred_axis`` are
    set, the data and corresponding axes are set as well. Otherwise,
    the :attr:`data` attribute will initially not contain any data. Use
    :meth:`set_data` and :meth:`set_axes` in this case:

    .. code-block::

        measurement.set_data(name="SimChan:02")
        measurement.set_axes(names=["SimMot:02"])

    Note that you can use both, the unique IDs of the devices and their
    more readable and pronounceable names they are known by. In the
    latter case, they are internally translated to the unique IDs.

    """

    def __init__(self, filename="", join_type="AxesLastFill"):
        super().__init__()
        self.data = entities.Data()
        self.filename = filename
        self._scan_module = "main"
        self._current_data = ()
        self._current_axes = []
        self._evefile = None
        self._join = None
        self.join_type = join_type

    @property
    def filename(self):
        """
        Name of the file to be loaded.

        Returns
        -------
        filename : :class:`str`
            Name of the file to be loaded.

        """
        return self.metadata.filename

    @filename.setter
    def filename(self, filename=""):
        self.metadata.filename = filename

    @property
    def current_data(self):
        """
        Name of the device currently set as data in :attr:`data`.

        Note that the name is the unique XML-ID used as HDF5 dataset name.
        To get the readable name, use :meth:`get_name`.

        Returns
        -------
        current_data : :class:`str`
            Name of the device currently set as data in :attr:`data`.

        """
        return self._current_data[0]

    @property
    def current_axes(self):
        """
        Names of the axes currently set as axes in :attr:`data`.

        Note that the names are the unique XML-IDs used as HDF5 dataset
        names. To get the readable names, use :meth:`get_name`.

        Returns
        -------
        current_axes : :class:`list`
            Names of the axes currently set as axes in :attr:`data`.

        """
        return [axis[0] for axis in self._current_axes]

    def get_current_data(self):
        """
        Get name and attribute of the device used as current data.

        In contrast to the :attr:`current_data` attribute, this method
        returns a tuple with the device name and attribute of that device
        used as data.

        Returns
        -------
        current_data : :class:`tuple`
            Name and attribute of the device used as current data.

        """
        return self._current_data

    def get_current_axes(self):
        """
        Get names and attributes of the devices used as current axes.

        In contrast to the :attr:`current_axes` attribute, this method
        returns a list of tuples with the device names and attributes of each
        device used as axis.

        Returns
        -------
        current_data : :class:`list`
            Name and attribute of each device used as current axes.

            Each element in the list is a tuple (``name``, ``attribute``).

        """
        return self._current_axes

    @property
    def join_type(self):
        """
        Join type used to join data.

        Needs to be a valid class from the :mod:`joining
        <evedata.measurement.controllers.joining>` module.

        Returns
        -------
        join_type : :class:`str`
            Join type used to join data.

        """
        return self._join_type

    @join_type.setter
    def join_type(self, join_type="AxesLastFill"):
        self._join_type = join_type
        self._join = joining.JoinFactory(measurement=self).get_join(join_type)

    def load(self, filename=""):
        """
        Load contents of an eveH5 file containing data.

        If the attributes ``preferred_channel`` and ``preferred_axis`` are
        set, the data and corresponding axes are set as well. Otherwise,
        the :attr:`data` attribute will initially not contain any data.
        Use :meth:`set_data` and :meth:`set_axes` in this case.

        Parameters
        ----------
        filename : :class:`str`
            Name of the file to load.

        """
        if filename:
            self.metadata.filename = filename
        self._load_evefile()
        self._map_scan()
        self._map_metadata()
        self._map_log_messages()
        self._map_scan_modules()
        self._map_snapshots()
        self._set_data()

    def _load_evefile(self):
        self._evefile = EveFile(filename=self.metadata.filename)
        self._evefile.load()

    def _map_scan(self):
        self.scan = self._evefile.scan

    def _map_metadata(self):
        attributes = [
            attribute
            for attribute in list(self._evefile.metadata.__dict__.keys())
            if not str(attribute).startswith("_")
        ]
        for attribute in attributes:
            setattr(
                self.metadata,
                attribute,
                getattr(self._evefile.metadata, attribute),
            )

    def _map_log_messages(self):
        self.log_messages = self._evefile.log_messages

    def _map_scan_modules(self):
        for key, value in self._evefile.scan_modules.items():
            self.scan_modules[key] = value

    def _map_snapshots(self):
        for key, value in self._evefile.snapshots.items():
            self.device_snapshots[key] = value

    def _set_data(self):
        if self.metadata.preferred_axis and self.metadata.preferred_channel:
            for scan_module_name, scan_module in self.scan_modules.items():
                if (
                    self.metadata.preferred_channel
                    in scan_module.device_names.values()
                ):
                    self.set_data(
                        name=self.metadata.preferred_channel,
                        scan_module=scan_module_name,
                    )
                if (
                    self.metadata.preferred_axis
                    in scan_module.device_names.values()
                ):
                    self.set_axes(
                        names=[self.metadata.preferred_axis],
                        scan_module=scan_module_name,
                    )

    def _set_axis_metadata_from_device(
        self, axis=None, device="", scan_module=""
    ):
        axis.quantity = (
            self.scan_modules[scan_module].data[device].metadata.name
        )
        axis.unit = self.scan_modules[scan_module].data[device].metadata.unit

    def set_data(self, scan_module="", name="", field=""):
        """
        Set data for the :attr:`data` attribute.

        The name is set to the :attr:`current_data` attribute as well.
        Furthermore, the axis metadata in the :attr:`data` attribute are
        set, *i.e.* "quantity" and "unit".

        Note that you can use both, the unique IDs of the devices and their
        more readable and pronounceable names they are known by. In the
        latter case, they are internally translated to the unique IDs.

        Some devices can have additional attributes with data that you
        want to operate on, *i.e.* set as data. In this case, provide the
        name of the attribute as ``field`` parameter.

        Parameters
        ----------
        name : :class:`str`
            Device name whose data should be set as data.

        scan_module : :class:`str`
            Scan module ID the device belongs to

        field : :class:`str`
            Field name of the device whose data should be set as data.

        """
        if not scan_module:
            scan_module = self._scan_module
        if name not in self.scan_modules[scan_module].data:
            name = self.scan_modules[scan_module].device_names[name]
        if not field:
            field = "data"
        if self._current_axes:
            data, *axes = self._join.join(
                scan_module=scan_module,
                data=(name, field),
                axes=self._current_axes,
            )
            for idx, axis in enumerate(axes):
                self.data.axes[idx].values = axis
        else:
            data = getattr(self.scan_modules[scan_module].data[name], field)
        self.data.data = data
        self._current_data = (name, field)
        self._set_axis_metadata_from_device(
            self.data.axes[-1], device=name, scan_module=scan_module
        )

    def set_axes(self, scan_module="", names=None, fields=None):
        r"""
        Set axes for the :attr:`data` attribute.

        The names are set to the :attr:`current_axes` attribute as well.
        Furthermore, the axes metadata in the :attr:`data` attribute are
        set for each axis, *i.e.* "quantity" and "unit".

        Note that you can use both, the unique IDs of the devices and their
        more readable and pronounceable names they are known by. In the
        latter case, they are internally translated to the unique IDs.

        Some devices can have additional attributes with data that you
        want to operate on, *i.e.* set as axes values. In this case, provide
        the names of the attributes as ``fields`` parameter. If you
        provide fields, the lists ``names`` and ``fields`` need to be of
        the same length.

        Parameters
        ----------
        names : :class:`list`
            Device names whose data should be set as axes data.

            Note that names is a list, as you can have *n*\D data with *n*>1.

        scan_module : :class:`str`
            Scan module ID the device belongs to

        fields : :class:`list`
            Field names of the devices whose data should be set as axes data.

            Note that fields is a list, as you can have *n*\D data with *n*>1.

        Raises
        ------
        ValueError
            Raised if no data are set axes could be set for.

        IndexError
            Raised if fields are given and not of same length as names.

        """
        if len(self.data.data) == 0:
            raise ValueError("No data to set axes for")
        if fields and (len(names) != len(fields)):
            raise IndexError("Names and fields need to be of same length")
        if not fields:
            fields = ["data"] * len(names)
        current_axes = []
        axes = []
        devices = []
        for idx, device in enumerate(names):
            if device not in self.scan_modules[scan_module].data:
                device = self.scan_modules[scan_module].device_names[device]
            current_axes.append((device, fields[idx]))
            axes.append(
                getattr(
                    self.scan_modules[scan_module].data[device], fields[idx]
                )
            )
            devices.append(device)
        self._current_axes = current_axes
        if self._current_data:
            _, *axes = self._join.join(
                data=self._current_data,
                axes=self._current_axes,
                scan_module=scan_module,
            )
        for idx, axis in enumerate(axes):
            self.data.axes[idx].values = axis
            self._set_axis_metadata_from_device(
                axis=self.data.axes[idx],
                device=devices[idx],
                scan_module=scan_module,
            )

    def get_name(self, device=None):
        """
        Get name of a corresponding unique device ID.

        Devices are stored in the :attr:`devices` attribute by their unique
        IDs. However, they usually have more readable and pronounceable
        names they are known by.

        Note that device names are not guaranteed to be unique. For all
        devices in the :attr:`devices` attribute, this should be the case,
        though.

        Parameters
        ----------
        device : :class:`str` | :class:`list`
            ID(s) of the device(s)

        Returns
        -------
        name : :class:`str` | :class:`list`
            Name(s) of the device(s)

            If ``device`` is a list, ``name`` will be a list, too.

        """
        if isinstance(device, (list, tuple)):
            name = [self._get_name(name) for name in device]
        else:
            name = self._get_name(device)
        return name

    def _get_name(self, device=""):
        name = ""
        for scan_module in self.scan_modules.values():
            if device in scan_module.data:
                name = scan_module.data[device].metadata.name
        return name
