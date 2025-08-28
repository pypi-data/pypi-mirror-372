"""

*Entities representing a scan performed by the eve engine.*

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 2

Scans are defined in XML files using a schema called Scan Markup Language
(SCML). While these scan descriptions can be conveniently be modified using
the eve GUI, eventually the eve engine receives an SCML file with a scan
description that it executes.

The idea behind this module and the entire :mod:`scan <evedata.scan>`
subpackage is *not* to really parse the SCML file and provide means to
modify the scan description, but rather to represent those aspects important
for interpreting the resulting eveH5 files, besides all the relevant
metadata for the individual devices used.

An SCML file usually contains a scan block defining the actual scan, and the
entities of such a scan is what this module is concerned with. Other parts
of the SCML file are a setup part (not yet a block, as of SCML schema v9.2)
containing the description of the devices (detectors, motors, devices)
explicitly used in the scan, and a plugins section.


Overview
========

A first overview of the classes implemented in this module and their
hierarchy is given in the UML diagram below, :numref:`Fig. %s
<fig-uml_evedata-scan.scan_current_api>`.


.. _fig-uml_evedata-scan.scan_current_api:

.. figure:: /uml/evedata.scan.entities.scan_current.*
    :align: center
    :width: 750px

    Class hierarchy of the :mod:`scan.entities.scan
    <evedata.scan.entities.scan>` module, somewhat resembling the schema of
    the SCML file, but modified in light of implementing the classes
    contained in the module. As the scan module is already quite complicated,
    event and plot-related classes have been separated into their own
    modules. Hint: For a larger view, you may open the image in a separate
    tab. As it is vectorised (SVG), it scales well.


.. important::

    Note that for the time being, only a subset of the classes shown in the
    above UML diagram is implemented, and only the most relevant attributes
    of these classes.


As a comparison, shown below in :numref:`Fig. %s
<fig-uml_evedata-scan.scan_api>` is an UML diagram more closely resembling
the current state of affairs in the SCML schema (version 9.2).


.. _fig-uml_evedata-scan.scan_api:

.. figure:: /uml/evedata.scan.entities.scan.*
    :align: center
    :width: 750px

    Class hierarchy closely resembling the schema of the SCML file. As the
    scan module is already quite complicated, event and plot-related
    classes have been separated into their own modules. Hint: For a larger
    view, you may open the image in a separate tab. As it is vectorised
    (SVG), it scales well.




Module documentation
====================

"""

import logging
import os

import numpy as np

logger = logging.getLogger(__name__)


class Scan:
    """
    Representation of all information available for a given scan.

    A scan consists of scan modules, a series of metadata, and different
    types of events.


    Attributes
    ----------
    repeat_count : :class:`int`
        Short description

    comment : :class:`str`
        Short description

    description : :class:`str`
        Short description

    scan_modules : :class:`dict`
        Scan modules the scan consists of.

        The keys are the unique IDs (UID) of the respective scan module,
        and the values :obj:`AbstractScanModule` objects. This allows for easy
        access of a given scan module given its UID.


    Examples
    --------
    The :class:`Scan` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.scan` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        self.repeat_count = 1
        self.comment = ""
        self.description = ""
        self.scan_modules = {}

    @property
    def mpskip_scan_module(self):
        """
        ID of the scan module containing the EPICS MPSKIP device.

        Convenience way to obtain the scan module ID (used as key in
        :attr:`scan_modules`) of the scan module containing the EPICS
        MPSKIP device. In case no matching module is available, it will
        be :obj:`None`, making tests quite simple.

        Returns
        -------
        mpskip_module_id : :class:`int` | :obj:`None`
            ID of the scan module or :obj:`None` in case of no match.

        """
        try:
            mpskip_module_id = [
                item.id
                for item in self.scan_modules.values()
                if item.has_mpskip()
            ][0]
        except IndexError:
            mpskip_module_id = None
        return mpskip_module_id

    @property
    def number_of_positions(self):
        """
        Number of positions created during the entire scan.

        To check for consistency whether the calculated number of
        positions for each of the scan modules is identical to the actual
        number of positions recorded, it is necessary to sum over the
        number of positions of each individual scan module.

        The following cases are known to be problematic or make this test
        impossible to pass:

        * Scans using the EPICS MPSKIP feature.

          In this case, the actually recorded number of positions for the
          MPSKIP scan module cannot be calculated, and the real scan will
          in (almost) all cases consist of less positions than
          theoretically possible.

        * Scans containing skip events.

          Similarly to the situation above, external events during the
          scan that cannot be foreseen impact the actual number of
          positions recorded for a scan. In contrast to the MPSKIP
          scenario, these events are (currently) not visible from the
          resulting measurement file.

        Returns
        -------
        number_of_positions : :class:`int`
            Number of positions created during the entire scan.

        """
        return int(
            np.sum(
                [
                    scan_module.number_of_positions
                    for scan_module in self.scan_modules.values()
                ]
            )
        )


class AbstractScanModule:
    r"""
    Abstract base class for scan modules.

    A scan consists of 1..\ *n* scan modules. Each scan module has a parent
    (the first defined scan module has the root node with 0 as its parent)
    and 0..1 appended and 0..1 nested scan modules.

    An appended scan module is executed once the current scan module is
    finished, while nested scan modules are executed for each position of
    the current scan module.


    Attributes
    ----------
    id : :class:`int`
        Unique ID of the scan module.

        The IDs are numeric and start with 1, as the root node is always 0.
        Hence, the first scan module defined will have 0 as its parent.

        Default: 1

    name : :class:`str`
        Name of the scan module.

        The scan module appears in the graphical representation eve GUI with
        this name. Hence, providing good names can be very valuable.

    parent : :class:`id`
        Unique ID of the parent scan module.

        In case of the first scan module, this is 0.

        Default: 0

    appended : :class:`int`
        Unique ID of the appended scan module.

        A scan module can have 0..1 appended and 0..1 nested scan modules.

        Default: None

    nested : :class:`int`
        Unique ID of the nested scan module.

        A scan module can have 0..1 appended and 0..1 nested scan modules.

        Default: None

    is_nested : :class:`bool`
        Whether the scan module itself is nested.

        A scan module can either be appended or nested. Given that the
        scan modules are unaware of the other scan modules and (currently)
        only contain IDs as references to their parent and appended or
        nested scan module, this information needs to be set from outside,
        *e.g.* during mapping by the :class:`VersionMapper
        <evedata.scan.controllers.version_mapping.VersionMapper>` class.

        Default: False

    number_of_positions : :class:`int`
        Number of positions created during the scan module.

        Positions are the fundamental quantisation of the data in eveH5
        files. Each position axes are moved to is assigned a "position
        count", *i.e.* a unique integer value. Furthermore, positionings
        of axes at the end of the scan module (in the "positioning phase")
        get their own position number.

        For snapshot modules, things are quite simple: Each snapshot
        module creates its own position, one per module.

        Default: 0

    number_of_positions_per_pass : :class:`int`
        Number of positions created during *one pass* of the scan module.

        Scan modules can be nested, and even though a given scan module
        is not nested itself, it can be in a chain of scan modules that
        are nested. Hence, the total number of positions created during a
        scan for a given scan module can be different from the number of
        positions during a single pass.

        Default: 0

    position_counts : :class:`numpy.array`
        Actual position counts created during the scan module.

        These position counts cannot necessarily be inferred from the
        definition of the scan module itself, but sometimes only be
        obtained from the actual measurement.


    Examples
    --------
    The :class:`AbstractScanModule` class is not meant to be used directly, as
    any entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.scan` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        self.id = 1  # noqa
        self.name = ""
        self.parent = 0
        self.appended = None
        self.nested = None
        self.is_nested = False
        self.number_of_positions = 0
        self.number_of_positions_per_pass = 0
        self.position_counts = None

    def has_mpskip(self):
        """
        Check whether a scan module uses the EPICS MPSKIP feature.

        The MPSKIP detector is a special EPICS workaround to, *i.a.*, store
        individual data points for an average channel. For details,
        see the :mod:`mpskip <evedata.evefile.controllers.mpskip>` module.

        To properly convert the datasets of the devices in a scan using
        the MPSKIP feature, we need to know which devices were part of the
        scan module containing the MPSKIP detector.

        This convenience method allows for easily checking whether the
        scan module contains the MPSKIP detector and allows the
        controllers handling the dataset conversion to do their work.

        The actual checking needs to be implemented in the subclasses,
        as otherwise, by default ``False`` will be returned.

        Returns
        -------
        has_mpskip : :class:`bool`
            Whether the scan module uses the EPICS MPSKIP feature

        """
        return False

    def has_device(self, name=""):  # noqa
        """
        Check whether a scan module contains a given device.

        Convenience method to check for a device name (its unique ID) in
        both, channels and axes.

        The actual checking needs to be implemented in the subclasses,
        as otherwise, by default ``False`` will be returned.

        Parameters
        ----------
        name : :class:`str`
            Name (unique ID) of the device

        Returns
        -------
        has_device : :class:`bool`
            Whether the scan module contains the given device

        """
        return False


class ScanModule(AbstractScanModule):
    """
    Representation of a "classical" scan module.

    This type of scan modules is the generic building block of all scans and
    very versatile. Mainly, it consists of detector channels and motor axes,
    as well as a series of events, pre- and post-scan options, positionings
    and plots.


    Attributes
    ----------
    id : :class:`int`
        Unique ID of the scan module.

        The IDs are numeric and start with 1, as the root node is always 0.
        Hence, the first scan module defined will have 0 as its parent.

        Default: 1

    name : :class:`str`
        Name of the scan module.

        The scan module appears in the graphical representation eve GUI with
        this name. Hence, providing good names can be very valuable.

    parent : :class:`id`
        Unique ID of the parent scan module.

        In case of the first scan module, this is 0.

        Default: 0

    appended : :class:`int`
        Unique ID of the appended scan module.

        A scan module can have 0..1 appended and 0..1 nested scan modules.

        Default: None

    nested : :class:`int`
        Unique ID of the nested scan module.

        A scan module can have 0..1 appended and 0..1 nested scan modules.

        Default: None

    is_nested : :class:`bool`
        Whether the scan module itself is nested.

        A scan module can either be appended or nested. Given that the
        scan modules are unaware of the other scan modules and (currently)
        only contain IDs as references to their parent and appended or
        nested scan module, this information needs to be set from outside,
        *e.g.* during mapping by the :class:`VersionMapper
        <evedata.scan.controllers.version_mapping.VersionMapper>` class.

        Default: False

    number_of_positions : :class:`int`
        Number of positions created during the scan module.

        Positions are the fundamental quantisation of the data in eveH5
        files. Each position axes are moved to is assigned a "position
        count", *i.e.* a unique integer value. Furthermore, positionings
        of axes at the end of the scan module (in the "positioning phase")
        get their own position number.

        For snapshot modules, things are quite simple: Each snapshot
        module creates its own position, one per module.

        Default: 0

    number_of_positions_per_pass : :class:`int`
        Number of positions created during *one pass* of the scan module.

        Scan modules can be nested, and even though a given scan module
        is not nested itself, it can be in a chain of scan modules that
        are nested. Hence, the total number of positions created during a
        scan for a given scan module can be different from the number of
        positions during a single pass.

        Default: 0

    position_counts : :class:`numpy.array`
        Actual position counts created during the scan module.

        These position counts cannot necessarily be inferred from the
        definition of the scan module itself, but sometimes only be
        obtained from the actual measurement.

    axes : :class:`dict`
        Motor axes actively being used in the scan module.

        The keys are the unique IDs (UID) of the axis, while the values are
        :obj:`Axis` objects. This allows for easy access of a given axis
        given its UID.

    channels : :class:`dict`
        Detector channels actively being used in the scan module.

        The keys are the unique IDs (UID) of the channel, while the values are
        :obj:`Channel` objects. This allows for easy access of a given channel
        given its UID.

    positionings : :class:`list`
        Positionings for individual axes of the scan module.

        Optionally, at the end of a pass of a scan module, axes contained
        in this scan module can be positioned by calculating a new
        position using the values of a given (optionally normalised) detector
        channel.

        Each element in the list is a :obj:`Positioning` object.

    pre_scan_settings : :class:`dict`
        Settings of individual devices before triggering axes or channels.

        The keys are the unique IDs (UID) of the devices, while the values
        are :obj:`PreScan` objects. This allows for easy access of a given
        device given its UID.

    post_scan_settings : :class:`dict`
        Settings of individual devices after triggering axes or channels.

        The keys are the unique IDs (UID) of the devices, while the values
        are :obj:`PostScan` objects. This allows for easy access of a given
        device given its UID.

    number_of_measurements : :class:`int`
        Number of measurements performed per axes position.

        Each measurement gets its individual position count.

        Default: 1


    Examples
    --------
    The :class:`ScanModule` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.scan` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.axes = {}
        self.channels = {}
        self.positionings = []
        self.pre_scan_settings = {}
        self.post_scan_settings = {}
        self.number_of_measurements = 1

    def has_mpskip(self):
        """
        Check whether a scan module uses the EPICS MPSKIP feature.

        The MPSKIP detector is a special EPICS workaround to, *i.a.*, store
        individual data points for an average channel. For details,
        see the :mod:`mpskip <evedata.evefile.controllers.mpskip>` module.

        To properly convert the datasets of the devices in a scan using
        the MPSKIP feature, we need to know which devices were part of the
        scan module containing the MPSKIP detector.

        This convenience method allows for easily checking whether the
        scan module contains the MPSKIP detector and allows the
        controllers handling the dataset conversion to do their work.

        Currently, the method checks for at least one detector channel
        whose ID starts with "MPSKIP".

        Returns
        -------
        has_mpskip : :class:`bool`
            Whether the scan module uses the EPICS MPSKIP feature

        """
        mpskip_channels = [
            item for item in self.channels if item.startswith("MPSKIP")
        ]
        return bool(mpskip_channels)

    def has_device(self, name=""):
        """
        Check whether a scan module contains a given device.

        Convenience method to check for a device name (its unique ID) in
        both, channels and axes.

        Parameters
        ----------
        name : :class:`str`
            Name (unique ID) of the device

        Returns
        -------
        has_device : :class:`bool`
            Whether the scan module contains the given device

        """
        return name in self.channels or name in self.axes


class Channel:
    """
    Representation of a channel used in a scan module.

    Scan modules use detector channels and motor axes in their main phase.
    All relevant information regarding a channel with respect to its use in
    a scan module is contained in this class and classes inheriting from it.

    To get further information on the channel in general, its :attr:`id` can
    be used to look up this information in the ``setup`` part of the SCML
    file.


    Attributes
    ----------
    id : :class:`str`
        Unique ID of the channel.

        Each channel has a unique ID that is used internally to refer to it.
        The names displayed in the GUI are "given" names different from this
        ID, though. The HDF5 datasets in an eveH5 file use these UIDs as name.

    normalize_id : :class:`str`
        Unique ID of the channel used for normalization.

        Channels can be normalized by other channels, *i.e.* the values
        divided by the values obtained from the normalizing channel.

    deferred_trigger : :class:`bool`
        Whether the channel is triggered after all others in the scan module.

        For some channels, their value depends on other channels to be
        triggered. Hence, there are two times within a scan module when
        channels are triggered: the first is after triggering all axes and
        reading back their positions, the second is after triggering all
        (non-deferred) channels.

        Default: False


    Examples
    --------
    The :class:`Channel` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.scan` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        self.id = ""  # noqa
        self.normalize_id = ""
        self.deferred_trigger = False


class Axis:
    """
    Representation of an axis used in a scan module.

    Scan modules use detector channels and motor axes in their main phase.
    All relevant information regarding an axis with respect to its use in
    a scan module is contained in this class.

    To get further information on the axis in general, its :attr:`id` can
    be used to look up this information in the ``setup`` part of the SCML
    file.


    Attributes
    ----------
    id : :class:`str`
        Unique ID of the axis.

        Each axis has a unique ID that is used internally to refer to it.
        The names displayed in the GUI are "given" names different from this
        ID, though. The HDF5 datasets in an eveH5 file use these UIDs as name.

    step_function : :class:`StepFunction`
        Function used to determine the axis positions.

        Instance of a subclass of :class:`StepFunction`, depending on how
        the step function was defined in the SCML.

    position_mode : :class:`str`
        Mode used for positioning the axis.

        Possible values are: "absolute", "relative"

        If "relative", the axis positions are understood as  relative to
        another position value.

        Default: "absolute"


    Examples
    --------
    The :class:`Axis` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.scan` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self, sm_id=""):
        self.id = sm_id  # noqa
        self.step_function = StepFunction()
        self.position_mode = "absolute"
        self._positions = None

    @property
    def positions(self):
        """
        Values the axis should have been moved to ("set values").

        Whether the axis ever reached these positions is an entirely
        different matter that can be resolved by comparing these set
        values with the values recorded by the engine.

        If :attr:`step_function` is an instance of :class:`StepFile`,
        no positions can be inferred from the SCML file, as they are
        simply not contained.

        Returns
        -------
        positions : :class:`numpy.array`
            Set values the axis should have been moved to.

        """
        if self._positions is None:
            self._positions = self.step_function.positions
        return self._positions

    @positions.setter
    def positions(self, positions=None):
        self._positions = positions


class StaticSnapshotModule(AbstractScanModule):
    """
    Representation of static snapshot scan modules.

    Snapshot scan modules are used to record the state of devices at a given
    point in time (an individual position count). Historically, there are
    four different types of such snapshot scan modules: motor axes and
    detector channels, and static and dynamic each. This class is meant
    to represent static axes and channels snapshots.


    Attributes
    ----------
    id : :class:`int`
        Unique ID of the scan module.

        The IDs are numeric and start with 1, as the root node is always 0.
        Hence, the first scan module defined will have 0 as its parent.

        Default: 1

    name : :class:`str`
        Name of the scan module.

        The scan module appears in the graphical representation eve GUI with
        this name. Hence, providing good names can be very valuable.

    parent : :class:`id`
        Unique ID of the parent scan module.

        In case of the first scan module, this is 0.

        Default: 0

    appended : :class:`int`
        Unique ID of the appended scan module.

        A scan module can have 0..1 appended and 0..1 nested scan modules.

        Default: None

    nested : :class:`int`
        Unique ID of the nested scan module.

        A scan module can have 0..1 appended and 0..1 nested scan modules.

        Default: None

    is_nested : :class:`bool`
        Whether the scan module itself is nested.

        A scan module can either be appended or nested. Given that the
        scan modules are unaware of the other scan modules and (currently)
        only contain IDs as references to their parent and appended or
        nested scan module, this information needs to be set from outside,
        *e.g.* during mapping by the :class:`VersionMapper
        <evedata.scan.controllers.version_mapping.VersionMapper>` class.

        Default: False

    number_of_positions : :class:`int`
        Number of positions created during the scan module.

        Positions are the fundamental quantisation of the data in eveH5
        files. Each position axes are moved to is assigned a "position
        count", *i.e.* a unique integer value. Furthermore, positionings
        of axes at the end of the scan module (in the "positioning phase")
        get their own position number.

        For snapshot modules, things are quite simple: Each snapshot
        module creates its own position, one per module.

        Default: 1

    number_of_positions_per_pass : :class:`int`
        Number of positions created during *one pass* of the scan module.

        Scan modules can be nested, and even though a given scan module
        is not nested itself, it can be in a chain of scan modules that
        are nested. Hence, the total number of positions created during a
        scan for a given scan module can be different from the number of
        positions during a single pass.

        Default: 1

    position_counts : :class:`list` | :class:`numpy.array`
        Actual positions created during the scan module.

        These positions cannot necessarily be inferred from the definition
        of the scan module itself, but sometimes only be obtained from the
        actual measurement.

    axes : :class:`dict`
        Motor axes actively being used in the scan module.

        The keys are the unique IDs (UID) of the axis, while the values are
        :obj:`Axis` objects. This allows for easy access of a given axis
        given its UID.

    channels : :class:`dict`
        Detector channels actively being used in the scan module.

        The keys are the unique IDs (UID) of the channel, while the values are
        :obj:`Channel` objects. This allows for easy access of a given channel
        given its UID.


    Examples
    --------
    The :class:`StaticSnapshotModule` class is not meant to be used directly,
    as any entities, but rather indirectly by means of the respective
    facades in the boundaries technical layer of the :mod:`evedata.scan`
    subpackage. Hence, for the time being, there are no dedicated examples
    how to use this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.number_of_positions = 1
        self.number_of_positions_per_pass = 1
        self.axes = {}
        self.channels = {}


class Positioning:
    """
    Representation of an axis positioning as optional step in a scan module.

    An axis can be positioned in several ways after a scan module has been
    executed. The position the axis should be positioned at is determined
    by analysing the data of a given detector channel. This allows to
    perform setup scans in scan modules that are prepended to the scan
    modules performing the actual measurement, and have both, setup and
    actual measurement in one scan.

    A positioning gets its separate position (count) in the eveH5 file,
    and all positionings for all axes are performed after the main phase
    of the scan module has finished.


    Attributes
    ----------
    axis_id : :class:`str`
        Unique ID of the axis that shall be positioned.

    channel_id : :class:`str`
        Unique ID of the channel analysed to determine the axis position.

    normalize_channel_id : :class:`str`
        Unique ID of the channel used for normalization.

        Often, channels are normalized, and this normalization is crucial
        for proper positioning of an axis.

    type : :class:`str`
        The way the (new) axis position is calculated from the channel data.

        Currently, the following types are available:

        ====== =======================================
        Type   Parameter
        ====== =======================================
        PEAK   --
        CENTER threshold
        MAX    --
        MIN    --
        EDGE   number from left
        ====== =======================================

        If parameters are available, they are stored in the
        :attr:`parameters` attribute.

    parameters : :class:`dict`
        Parameters used to calculate the new position.

        Whether a given :attr:`type` has parameters can be seen from the
        table above.

    position : :class:`int`
        Actual position created during the scan.

        Positions are the fundamental quantisation of the data in eveH5
        files. Each position axes are moved to is assigned a "position
        count", *i.e.* a unique integer value. Furthermore, positionings
        of axes at the end of the scan module (in the "positioning phase")
        get their own position number.


    Examples
    --------
    The :class:`Positioning` class is not meant to be used directly,
    as any entities, but rather indirectly by means of the respective
    facades in the boundaries technical layer of the :mod:`evedata.scan`
    subpackage. Hence, for the time being, there are no dedicated examples
    how to use this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        self.axis_id = None
        self.channel_id = None
        self.normalize_channel_id = None
        self.type = ""
        self.parameters = {}
        self.position = None


class DynamicSnapshotModule(AbstractScanModule):
    """
    Representation of dynamic snapshot scan modules.

    Snapshot scan modules are used to record the state of devices at a given
    point in time (an individual position count). Historically, there are
    four different types of such snapshot scan modules: motor axes and
    detector channels, and static and dynamic each. This class is meant
    to represent dynamic axes and channels snapshots.


    Attributes
    ----------
    id : :class:`int`
        Unique ID of the scan module.

        The IDs are numeric and start with 1, as the root node is always 0.
        Hence, the first scan module defined will have 0 as its parent.

        Default: 1

    name : :class:`str`
        Name of the scan module.

        The scan module appears in the graphical representation eve GUI with
        this name. Hence, providing good names can be very valuable.

    parent : :class:`id`
        Unique ID of the parent scan module.

        In case of the first scan module, this is 0.

        Default: 0

    appended : :class:`int`
        Unique ID of the appended scan module.

        A scan module can have 0..1 appended and 0..1 nested scan modules.

        Default: None

    nested : :class:`int`
        Unique ID of the nested scan module.

        A scan module can have 0..1 appended and 0..1 nested scan modules.

        Default: None

    is_nested : :class:`bool`
        Whether the scan module itself is nested.

        A scan module can either be appended or nested. Given that the
        scan modules are unaware of the other scan modules and (currently)
        only contain IDs as references to their parent and appended or
        nested scan module, this information needs to be set from outside,
        *e.g.* during mapping by the :class:`VersionMapper
        <evedata.scan.controllers.version_mapping.VersionMapper>` class.

        Default: False

    number_of_positions : :class:`int`
        Number of positions created during the scan module.

        Positions are the fundamental quantisation of the data in eveH5
        files. Each position axes are moved to is assigned a "position
        count", *i.e.* a unique integer value. Furthermore, positionings
        of axes at the end of the scan module (in the "positioning phase")
        get their own position number.

        For snapshot modules, things are quite simple: Each snapshot
        module creates its own position, one per module.

        Default: 1

    number_of_positions_per_pass : :class:`int`
        Number of positions created during *one pass* of the scan module.

        Scan modules can be nested, and even though a given scan module
        is not nested itself, it can be in a chain of scan modules that
        are nested. Hence, the total number of positions created during a
        scan for a given scan module can be different from the number of
        positions during a single pass.

        Default: 1

    position_counts : :class:`list` | :class:`numpy.array`
        Actual positions created during the scan module.

        These positions cannot necessarily be inferred from the definition
        of the scan module itself, but sometimes only be obtained from the
        actual measurement.


    Examples
    --------
    The :class:`DynamicSnapshotModule` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    :mod:`evedata.scan` subpackage. Hence, for the time being, there are
    no dedicated examples how to use this class. Of course, you can
    instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.number_of_positions = 1
        self.number_of_positions_per_pass = 1


class AverageChannel(Channel):
    """
    Representation of an average channel used in a scan module.

    Scan modules use detector channels and motor axes in their main phase.
    All relevant information regarding a channel with respect to its use in
    a scan module is contained in this class and classes inheriting from it.

    To get further information on the channel in general, its :attr:`id` can
    be used to look up this information in the ``setup`` part of the SCML
    file.


    Attributes
    ----------
    id : :class:`str`
        Unique ID of the channel.

        Each channel has a unique ID that is used internally to refer to it.
        The names displayed in the GUI are "given" names different from this
        ID, though. The HDF5 datasets in an eveH5 file use these UIDs as name.

    normalize_id : :class:`str`
        Unique ID of the channel used for normalization.

        Channels can be normalized by other channels, *i.e.* the values
        divided by the values obtained from the normalizing channel.

    n_averages : :class:`int`
        Number of averages

    low_limit : :class:`float`
        Minimum value for first reading of the channel

        If set, the value of the channel is read and needs to be larger
        than this minimum value to start the comparison phase.

    max_attempts : :class:`float`
        Maximum number of attempts for reading the channel data.

    max_deviation : :class:`float`
        Maximum deviation allowed between two values in the comparison phase.

        If the :attr:`low_limit` is set, as soon as the value of the
        channel is larger than the low limit, the comparison phase starts.
        Here, two subsequent channel readouts need to be within the
        boundary set by :attr:`max_deviation`.

        However, no more than :attr:`max_attempts` channel readouts are done.


    Examples
    --------
    The :class:`AverageChannel` class is not meant to be used directly,
    as any entities, but rather indirectly by means of the respective
    facades in the boundaries technical layer of the :mod:`evedata.scan`
    subpackage. Hence, for the time being, there are no dedicated examples
    how to use this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.n_averages = 0
        self.low_limit = 0.0
        self.max_attempts = 0
        self.max_deviation = 0.0


class IntervalChannel(Channel):
    """
    Representation of an interval channel used in a scan module.

    Scan modules use detector channels and motor axes in their main phase.
    All relevant information regarding a channel with respect to its use in
    a scan module is contained in this class and classes inheriting from it.

    To get further information on the channel in general, its :attr:`id` can
    be used to look up this information in the ``setup`` part of the SCML
    file.


    Attributes
    ----------
    id : :class:`str`
        Unique ID of the channel.

        Each channel has a unique ID that is used internally to refer to it.
        The names displayed in the GUI are "given" names different from this
        ID, though. The HDF5 datasets in an eveH5 file use these UIDs as name.

    normalize_id : :class:`str`
        Unique ID of the channel used for normalization.

        Channels can be normalized by other channels, *i.e.* the values
        divided by the values obtained from the normalizing channel.

    trigger_interval : :class:`float`
        The interval/rate measurements are taken in seconds

    stopped_by : :class:`str`
        The channel which when finished stops the mean calculation.

        The attribute contains the unique ID of the corresponding channel.

        Note: This information is *not* included in the eveH5 files on the
        HDF5 layer up to eveH5 schema version 7.


    Examples
    --------
    The :class:`IntervalChannel` class is not meant to be used directly,
    as any entities, but rather indirectly by means of the respective
    facades in the boundaries technical layer of the :mod:`evedata.scan`
    subpackage. Hence, for the time being, there are no dedicated examples
    how to use this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.trigger_interval = 0.0
        self.stopped_by = ""


class PreScan:
    """
    Parameters for an option set in the pre-scan phase of a scan module.

    Before actually triggering axes and channels in a scan module, options
    of these devices can be set in the pre-scan phase, and afterwards in
    the post-scan phase. For the latter, see the :class:`PostScan` class.


    Attributes
    ----------
    id : :class:`str`
        Unique ID of the device.

        Each axis and channel has a unique ID that is used internally to
        refer to it. The names displayed in the GUI are "given" names
        different from this ID, though. The HDF5 datasets in an eveH5 file
        use these UIDs as name.

    value : any (scalar)
        Value to set the device option to.

        Can be of any type, as long as it is a scalar.


    Examples
    --------
    The :class:`PreScan` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.scan` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        self.id = ""  # noqa
        self.value = None


class PostScan:
    """
    Parameters for an option set in the post-scan phase of a scan module.

    Before actually triggering axes and channels in a scan module, options
    of these devices can be set in the pre-scan phase, and afterwards in
    the post-scan phase. For the former, see the :class:`PreScan` class.


    Attributes
    ----------
    id : :class:`str`
        Unique ID of the device.

        Each axis and channel has a unique ID that is used internally to
        refer to it. The names displayed in the GUI are "given" names
        different from this ID, though. The HDF5 datasets in an eveH5 file
        use these UIDs as name.

    value : any (scalar)
        Value to set the device option to.

        Can be of any type, as long as it is a scalar.

    reset_original_value : :class:`bool`
        Whether to reset the value to its original value.

        Default: False


    Examples
    --------
    The :class:`PostScan` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.scan` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        self.id = ""  # noqa
        self.value = None
        self.reset_original_value = False


class StepFunction:
    """
    Base class for step functions defining the steps of a motor axis.

    The eve measurement program allows for different ways of setting motor
    axis positions/steps. This class provides the generic interface.


    Examples
    --------
    The :class:`StepFunction` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.scan` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        self._positions = None

    @property
    def positions(self):
        """
        Set values the axis should have been moved to.

        In case the internal attribute containing the positions has not
        been set, the :meth:`calculate_positions` method is called (once).

        Returns
        -------
        positions : :class:`numpy.array`
            Set values the axis should have been moved to.

        """
        if self._positions is None:
            self.calculate_positions()
        return self._positions

    @positions.setter
    def positions(self, positions=None):
        self._positions = positions

    def calculate_positions(self):
        """
        Calculate the positions the axis should have been moved to.

        Positions can be obtained using the :attr:`positions` attribute.
        In case the attribute internally storing the positions has not yet
        been set, this method is called (once).

        All classes inheriting from :class:`StepFunction` implement the
        necessary functionality to obtain the set positions from the
        parameters given in the scan description.

        """


class StepRange(StepFunction):
    """
    Steps defined by start, stop, and step width.

    In contrast to :class:`StepRanges`, this class allows only one range.

    Another difference to the :class:`StepRanges` class: For all axes
    using :class:`StepRange`, you can define one axis to be the main axis,
    and this sets the number of steps for all other axes in this group.
    See :attr:`is_main_axis` for details.


    Attributes
    ----------
    mode : :class:`str`
        How to interpret the positions.

        Possible values are ``add`` and ``multiply``.

        In case of ``add``, positions are used as absolute positions or
        summand for the initial position at the start of the scan module,
        depending on how :attr:`Axis.position_mode` is set.

        Default: ``add``

    start : :class:`float`
        First value of the range.

    stop : :class:`float`
        Last value of the range.

    step_width : :class:`float`
        Width of the individual steps.

    is_main_axis : :class:`bool`
        Whether the axis is set as main axis.

        Only for axes with :class:`StepRange` step function,
        setting one of these axes as main axis defines the number of
        positions of the other axes in this group.

    Examples
    --------
    The :class:`StepRange` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.scan` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.mode = "add"
        self.start = 0.0
        self.stop = 0.0
        self.step_width = 0
        self.is_main_axis = False

    def calculate_positions(self):
        """
        Calculate the positions the axis should have been moved to.

        Positions can be obtained using the :attr:`positions` attribute.
        In case the attribute internally storing the positions has not yet
        been set, this method is called (once).

        If :attr:`step_width` is zero, the value of :attr:`start` is
        set (as numpy array).

        """
        if self.step_width == 0:
            self._positions = np.asarray(self.start, dtype=float)
        else:
            self._positions = np.arange(
                self.start,
                self.stop,
                self.step_width,
                dtype=float,
            )
            self._positions = np.append(self._positions, self.stop)


class StepRanges(StepFunction):
    """
    Steps defined by one or multiple ranges.

    In contrast to :class:`StepRange`, this class allows more than one
    range to be set. The positions of all ranges are added together.


    Attributes
    ----------
    expression : :class:`str`
        Definition understood by the eve GUI to define ranges

        The actual positions are taken from the positions list contained
        in the SCML as well. Hence, no (re)calculation using the
        expression is performed.

    position_list : :class:`str`
        Comma-separated list of positions as text.


    Examples
    --------
    The :class:`StepRanges` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.scan` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.expression = ""
        self.position_list = ""

    def calculate_positions(self):
        """
        Calculate the positions the axis should have been moved to.

        Positions can be obtained using the :attr:`positions` attribute.
        In case the attribute internally storing the positions has not yet
        been set, this method is called (once).

        Positions are calculated by simply splitting the string contained
        in :attr:`position_list` at the comma and convert the numbers to
        floats.

        """
        if self.position_list:
            self._positions = np.asarray(
                [float(item) for item in self.position_list.split(",")]
            )


class StepReference(StepFunction):
    """
    Steps defined by reference to another axis.

    Allows to set the actual axis position by reference to another axis.

    .. note::

        Currently (version 2.1), the eve engine accepts only to reference
        axes from the same scan module, meaning that the axis has the same
        number of positions as the reference axis.

        The intended behaviour for referencing axes *outside* the current
        scan module is currently ill-defined. Despite the error displayed,
        the engine saves "0" as position(s) to the respective axis,
        with as many positions as total positions in the respective scan
        module.


    Attributes
    ----------
    mode : :class:`str`
        How to interpret the positions.

        Possible values are ``add`` and ``multiply``.

        In case of ``add``, positions are used as absolute positions or
        summand for the initial position at the start of the scan module,
        depending on how :attr:`Axis.position_mode` is set.

        Default: ``add``

    parameter : :class:`float`
        Summand or factor used to calculate the position given the reference.

    axis_id : :class:`str`
        Unique ID of the axis used as reference.

    scan_module : :class:`ScanModule`
        Reference to the scan module the axis is defined in.

        To calculate the positions, we need to check whether the reference
        axis given by :attr:`axis_id` is in the current scan module.


    Examples
    --------
    The :class:`StepReference` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.scan` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.mode = "add"
        self.parameter = 0.0
        self.axis_id = ""
        self.scan_module = None

    def calculate_positions(self):
        """
        Calculate the positions the axis should have been moved to.

        Positions can be obtained using the :attr:`positions` attribute.
        In case the attribute internally storing the positions has not yet
        been set, this method is called (once).

        If :attr:`scan_module` is not set or the reference axis defined in
        :attr:`axis_id` not found in the scan module, a numpy array with
        "0.0" as element is set, in line with the current behaviour
        of the eve engine.

        """
        if not self.scan_module:
            self._positions = np.asarray([0.0])
        else:
            try:
                reference_axis_positions = self.scan_module.axes[
                    self.axis_id
                ].step_function.positions
                if self.mode == "add":
                    self._positions = (
                        reference_axis_positions + self.parameter
                    )
                else:
                    self._positions = (
                        reference_axis_positions * self.parameter
                    )
            except KeyError:
                self._positions = np.asarray([0.0])


class StepFile(StepFunction):
    """
    Steps defined using an external file.

    The general problem with defining steps using an external file: Only
    the filename is provided in the scan description, and the actual file
    read at some point between loading and executing the scan by the
    engine. The time between defining the scan and actually loading the
    contents of the external file referenced by its filename can be
    everything between seconds and years. Hence, there is currently no way
    to get *any* information on the positions from the scan description.


    Attributes
    ----------
    filename : :class:`str`
        Path and name of the file containing the positions.

        The file contains one position per line.

        .. important::
            Even if the file exists and is accessible, there is no
            guarantee that the positions read from the file are the actual
            positions used during the scan, as the file may have been
            changed in the meantime.


    Examples
    --------
    The :class:`StepFile` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.scan` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.filename = ""

    def calculate_positions(self):
        """
        Calculate the positions the axis should have been moved to.

        Positions can be obtained using the :attr:`positions` attribute.
        In case the attribute internally storing the positions has not yet
        been set, this method is called (once).

        If the attribute :attr:`filename` is set and the file accessible,
        the contents of the file are read and set as positions. Otherwise,
        a warning is logged and an empty numpy array set as positions.

        """
        if self.filename and os.path.exists(self.filename):
            self._positions = np.loadtxt(self.filename)
        else:
            logger.warning(
                "Step function 'file' does not allow to obtain positions."
            )
            self._positions = np.asarray([])


class StepList(StepFunction):
    """
    Steps defined using list of positions.

    Probably the most generic way of defining positions for an axis:
    provide a comma-separated list of values.


    Attributes
    ----------
    position_list : :class:`str`
        Comma-separated list of positions


    Examples
    --------
    The :class:`StepList` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the :mod:`evedata.scan` subpackage.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.position_list = ""

    def calculate_positions(self):
        """
        Calculate the positions the axis should have been moved to.

        Positions can be obtained using the :attr:`positions` attribute.
        In case the attribute internally storing the positions has not yet
        been set, this method is called (once).

        Positions are calculated by simply splitting the string contained
        in :attr:`position_list` at the comma and convert the numbers to
        floats.

        """
        if self.position_list:
            self._positions = np.asarray(
                [float(item) for item in self.position_list.split(",")]
            )
