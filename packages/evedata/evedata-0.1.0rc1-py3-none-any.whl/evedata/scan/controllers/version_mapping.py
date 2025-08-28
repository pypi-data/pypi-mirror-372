"""
.. include:: <isopub.txt>

*Mapping SCML contents to the entities of the scan subpackage.*

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 2

There are different versions of the schema underlying the SCML files.
Hence, mapping the contents of an SCML file to the data model of the
evedata package requires to get the correct mapper for the specific
version. This is the typical use case for the factory pattern.

Users of the module hence will typically only obtain a
:obj:`VersionMapperFactory` object to get the correct mappers for individual
files. Furthermore, "users" basically boils down to the :class:`Scan
<evedata.scan.boundaries.scan.Scan>` class. Therefore, users of
the `evedata` package usually do not interact directly with any of the
classes provided by this module.


Overview
========

Being version agnostic with respect to eveH5 and SCML schema versions is a
central aspect of the evedata package. This requires facilities mapping
the actual SCML files to the data model provided by the :mod:`entities
<evedata.scan.entities>` technical layer of the :mod:`scan <evedata.scan>`
subpackage. The :class:`File <evedata.evefile.boundaries.evefile.File>`
facade obtains the correct :obj:`VersionMapper` object via the
:class:`VersionMapperFactory`, providing a :class:`SCML
<evedata.scan.boundaries.scml.SCML>` resource object to the factory. It is
the duty of the factory to obtain the "version" attribute from the
:obj:`SCML <evedata.scan.boundaries.scml.SCML>` object.


.. figure:: /uml/evedata.scan.controllers.version_mapping.*
    :align: center

    Class hierarchy of the :mod:`evedata.scan.controllers.version_mapping`
    module, providing the functionality to map different SCML file
    schemas to the data structure provided by the :class:`Scan
    <evedata.scan.boundaries.scan.Scan>` and :class:`Station
    <evedata.scan.boundaries.scan.Station>` classes. The factory
    will be used to get the correct mapper for a given SCML file.
    For each SCML schema version, there exists an individual
    ``VersionMapperVxmy`` class dealing with the version-specific mapping.
    The idea behind the ``Mapping`` class is to provide simple mappings for
    attributes and alike that need not be hard-coded and can be stored
    externally, *e.g.* in YAML files. This would make it easier to account
    for (simple) changes.


For each SCML schema version, there exists an individual
``VersionMapperVxmy`` class dealing with the version-specific mapping.
Currently, we assume major and minor version numbers to be relevant. Hence,
the ``xmy`` suffix for the individual mapper classes. That
part of the mapping common to all versions of the SCML schema takes place
in the :class:`VersionMapper` parent class. The idea behind the ``Mapping``
class is to provide simple mappings for attributes and alike that can be
stored externally, *e.g.* in YAML files. This would make it easier to
account for (simple) changes.


General aspects
===============

Both, representing the SCML contents as well as mapping the information from
a given SCML file to their representing entities do not strive to preserve
the full information available. The ``evedata`` interface is in the
luxurious situation to *not* require all information nor to perform scans.
Hence, for the time being, only those parts necessary for interpreting an
eveH5 file and providing the valuable abstractions for the users are
obtained from an SCML file and mapped to the respective representations.

One particularly important aspect: **Only those scan modules that are
actually connected** (either to the root node or to another scan module) **are**
actually mapped and **contained in the list of scan modules.**


Mapping tasks for SCML schema up to v9.2
========================================

Currently, the structure of the entities in the :mod:`evedata.scan.entities`
subpackage is not stable, and furthermore, there is no overview how much the
SCML schema has changed for the different versions. Hence, the tasks
described here will definitely change and evolve over time.

* Map SCML metadata (version, location) |check|
* Map scan -- if it exists

  * Map scan metadata (repeat_count, comment, description, ...) (|check|)
  * Map scan modules (|check|)

    * Map basic metadata |check|
    * Map parent, appended, nested, is_nested |check|
    * Distinguish types of scan modules: "classic" *vs.* snapshot |check|
    * Extract list of detector channels and motor axes |check|
    * Map pre- and post-scans |check|
    * Map positionings |check|
    * Calculate number of positions per pass/total and actual positions
      |check|
    * Map plots? |cross|
    * Map remaining information? |cross|

* Map all devices |cross|

  * Map detectors
  * Map motors
  * Map devices


.. todo::

    Implement mapping of positions for axes using plugins as step function.
    The reason for not yet having implemented this case: these axes need to
    have access to another reference axis, and the current implementation
    cannot guarantee this axis being present.


Currently, there is a need to map at least basic information about the scan
modules, to proceed with several controllers from the
:mod:`evedata.evefile.controllers` subpackage: mpskip, separating datasets
of redefined channels, obtain set values for axes. For details, see the
respective section of the :doc:`/architecture` document.


.. important::

    Due to the reasons mentioned above (urgent need to map only basic
    information about the scan modules), the mapping of the SCML file
    contents to the entities from the :mod:`evedata.scan.entities`
    subpackage is only rudimentary. Therefore, both mapping and internal
    handling of the SCML/XML tree will probably change in the future.


Distinguishing types of scan modules
------------------------------------

Currently, only two types of scan modules are distinguished: "classical"
modules and snapshot modules. The distinction is based on the existence of
the tag ``<classic>``: if present, we have a "classical" scan module,
if not, we have a snapshot module.

For "classical" modules, both axes and channels are mapped, for static axis
or channel snapshot modules, axes or channels, respectively.


Creating positions for individual scan modules
----------------------------------------------

Currently, (up to eveH5 schema version 7), the storage layer does not resemble
nor preserve the structure of a scan, particularly its composition of distinct
scan modules. To allow for sensible access to the data, the ``evedata``
interface tries to reconstruct this structure, at least as long as the SCML
is available from the eveH5 file. This means that for each individual HDF5
dataset, the positions belonging to the individual scan modules need to be
known, as one and the same channel or axis can be used in different scan
modules. Hence, the mapper tries to calculate the number of positions per
pass for each scan module, the number of total positions for each scan
module, and finally the actual position (count)s for each scan module.

With the current way the engine stores the data, determining the actual
position counts belonging to each individual scan module is not possible in
full generality. Situations that may corrupt the algorithm to determine the
positions from the scan description or even make it impossible to proceed
contain:

* Axes positions defined as lists in external files.

  Axes positions can be loaded from external files. However, only the file
  name (and path) are stored in the SCML. There is no guarantee at all
  that the file contents are the same as they were during scan execution.
  Besides that, the ``evedata`` interface usually cannot access the file
  containing the positions. In case the axis whose positions are defined
  using an external file has *more* positions set than any other axis in the
  scan module (the same applies if it is the only axis in the scan module),
  the algorithm calculating the (number of) positions for the scan module
  will fail.

* External events leading to skipping execution of parts of a scan module.

  Generally, users can skip parts of a scan module. Similarly, events can be
  defined in scans that skip parts of a scan module given a specific
  condition. In both cases, these events will *not* be saved in any way in
  the resulting eveH5 file. Hence, there is no way in determining that an
  event occurred. This most probably leads to a full corruption of the
  positions determined by the algorithm.

* Scans containing the MPSKIP detector

  This is a special situation dealt with by the :mod:`mpskip
  <evedata.evefile.controllers.mpskip>` module. Intrinsically, the positions
  cannot be determined algorithmically. However, given certain assumptions
  discussed in the documentation of the :mod:`mpskip
  <evedata.evefile.controllers.mpskip>` module, mapping should be possible.

Besides these general problems with accurately determining the (number
of) positions per scan module, the algorithm generally proceeds as follows,
assuming a list of those scan modules to be available that are part of the
actual scan, together with the information on nesting and appending:

* For each scan module, obtain all axes, and for each axis, determine the
  number of positions. The maximum of the number of positions of all axes
  within a scan module defines the number of positions per pass of a scan
  module, stored in the :attr:`ScanModule.number_of_positions_per_pass
  <evedata.scan.entities.scan.ScanModule.number_of_positions_per_pass>`
  attribute.

* For each scan module, check the "number of measurements" parameter (known
  also as "measurements per point", MPP, or "valuecount" in the SCML schema),
  and multiply the number of positions per pass with its value, to obtain
  the correct number of positions per pass.

* For each scan module, determine whether a positioning takes place.
  Positionings get their own position (count) after all positions in the
  scan module have been accessed. In case of nested scan modules, the nested
  scan modules are executed for each individual position of the next-higher
  scan module. Hence, the parent scan module of a (series of) nested scan
  module(s) acts as a "for loop".

* For each scan module, determine whether it is nested, and if so, multiply
  the number of positions per pass by the number of positions of the
  next-higher scan module, stored in the :attr:`ScanModule.number_of_positions
  <evedata.scan.entities.scan.ScanModule.number_of_positions>` attribute.

* For each scan module, obtain the actual position counts, starting with the
  first scan module with parent ``0`` (defined as root node and start of the
  scan) and with ``1`` as first position (count), stored in the
  :attr:`ScanModule.positions <evedata.scan.entities.scan.ScanModule.positions>`
  attribute.


A general plausibility check is to compare the number of positions
calculated by this algorithm with the number of positions created during the
actual scan. The latter can be easily obtained using the special HDF5
dataset containing the mapping of position (count)s to timestamps.
Furthermore, obtaining the shape of the data in an HDF5 dataset is a "cheap"
operation *not* requiring reading the data themselves, hence, not breaking
with the general philosophy of the ``evedata`` interface to read data
usually only on demand.


Fundamental change of SCML schema with v10
==========================================

Most probably, the SCML schema will be changed quite substantially in the
future, based on all the experience with developing the ``evedata`` package
and the data models implemented therein.

Depending on how dramatic this changes will be, the mappers for versions up
to the current one (v9.x) and those of the next major version may differ
substantially.


Module documentation
====================

"""

import logging
import sys

import numpy as np

from evedata.scan.entities import scan


logger = logging.getLogger(__name__)


class VersionMapperFactory:
    """
    Factory for obtaining the correct version mapper object.

    There are different versions of the schema underlying the SCML files.
    Hence, mapping the contents of an SCML file to the entities of the
    :mod:`scan <evedata.scan>` subpackage requires to get the correct mapper
    for the specific version. This is the typical use case for the factory
    pattern.


    Attributes
    ----------
    scml : :class:`evedata.scan.boundaries.scml.SCML`
        Python object representation of an SCML file

    Raises
    ------
    ValueError
        Raised if no SCML object is present


    Examples
    --------
    Using the factory is pretty simple. There are actually two ways how to
    set the scml attribute -- either explicitly or when calling the
    :meth:`get_mapper` method of the factory:

    .. code-block::

        factory = VersionMapperFactory()
        factory.scml = scml_object
        mapper = factory.get_mapper()

    .. code-block::

        factory = VersionMapperFactory()
        mapper = factory.get_mapper(scml=scml_object)

    In both cases, ``mapper`` will contain the correct mapper object,
    and ``scml_object`` contains the Python object representation of an
    SCML file.

    """

    def __init__(self):
        self.scml = None

    def get_mapper(self, scml=None):
        """
        Return the correct mapper for a given SCML file.

        For convenience, the returned mapper has its
        :attr:`VersionMapper.source` attribute already set to the
        ``scml`` object used to get the mapper for.

        Parameters
        ----------
        scml : :class:`evedata.scan.boundaries.scml.SCML`
            Python object representation of an SCML file

        Returns
        -------
        mapper : :class:`VersionMapper`
            Mapper used to map the SCML file contents to evedata structures.

        Raises
        ------
        ValueError
            Raised if no scml object is present

        """
        if scml:
            self.scml = scml
        if not self.scml:
            raise ValueError("Missing SCML object")
        version = self.scml.version.replace(".", "m")
        try:
            mapper = getattr(
                sys.modules[__name__], f"VersionMapperV{version}"
            )()
        except AttributeError as exc:
            raise AttributeError(f"No mapper for version {version}") from exc
        mapper.source = self.scml
        return mapper


class VersionMapper:
    """
    Mapper for mapping the SCML file contents to data structures.

    This is the base class for all version-dependent mappers. Given that
    there are different versions of the SCML schema, each version gets
    handled by a distinct mapper subclass.

    To get an object of the appropriate class, use the
    :class:`VersionMapperFactory` factory.


    Attributes
    ----------
    source : :class:`evedata.scan.boundaries.scml.SCML`
        Python object representation of an SCML file

    destination : :class:`evedata.scan.boundaries.scan.Scan`
        High(er)-level data structure representing an SCML file

        Can alternatively be an :obj:`evedata.scan.boundaries.scan.Station`
        object.


    Examples
    --------
    Although the :class:`VersionMapper` class is *not* meant to be used
    directly, its use is prototypical for all the concrete mappers:

    .. code-block::

        mapper = VersionMapper()
        mapper.map(source=scml, destination=scan)

    Usually, you will obtain the correct mapper from the
    :class:`VersionMapperFactory`. In this case, the returned mapper has
    its :attr:`source` attribute already set for convenience:

    .. code-block::

        factory = VersionMapperFactory()
        mapper = factory.get_mapper(scml=scml)
        mapper.map(destination=scan)

    """

    def __init__(self):
        self.source = None
        self.destination = None

    def map(self, source=None, destination=None):
        """
        Map the SCML file contents to data structures.

        Parameters
        ----------
        source : :class:`evedata.scan.boundaries.scml.SCML`
            Python object representation of an SCML file

        destination : :class:`evedata.scan.boundaries.scan.Scan`
            High(er)-level evedata structure representing an SCML file

            Can alternatively be an
            :obj:`evedata.scan.boundaries.scan.Station` object.

        Raises
        ------
        ValueError
            Raised if either source or destination are not provided

        """
        if source:
            self.source = source
        if destination:
            self.destination = destination
        self._check_prerequisites()
        self._map()

    def _check_prerequisites(self):
        if not self.source:
            raise ValueError("Missing source to map from.")
        if not self.destination:
            raise ValueError("Missing destination to map to.")

    def _map(self):
        self._map_metadata()
        try:
            self._map_scan()
        except AttributeError:
            pass

    def _map_metadata(self):
        self.destination.version = self.source.version
        self.destination.location = self.source.root.find("location").text

    def _map_scan(self):
        pass


class VersionMapperV9m0(VersionMapper):
    """
    Mapper for mapping SCML v9.0 file contents to data structures.

    .. note::

        Currently, most mapping is implemented in this class, and needs to
        be moved upwards in the inheritance hierarchy once this hierarchy
        exists.

        Furthermore, only a minimal set of mappings is currently performed,
        far from being a complete mapping of the contents of an SCML file.

    .. note::
        Only those scan modules that are actually connected (either to the
        root node or to another scan module) are actually mapped and
        contained in the list of scan modules.

    Attributes
    ----------
    source : :class:`evedata.scan.boundaries.scml.SCML`
        Python object representation of an SCML file

    destination : :class:`evedata.scan.boundaries.scan.Scan`
        High(er)-level data structure representing an SCML file


    Examples
    --------
    Mapping a given SCML file to the evedata structures is the same for
    each of the mappers:

    .. code-block::

        mapper = VersionMapperV9m0()
        mapper.map(source=scml, destination=scan)

    Usually, you will obtain the correct mapper from the
    :class:`VersionMapperFactory`. In this case, the returned mapper has
    its :attr:`source` attribute already set for convenience:

    .. code-block::

        factory = VersionMapperFactory()
        mapper = factory.get_mapper(scml=scml)
        mapper.map(destination=scan)

    """

    def _map_scan(self):
        self._map_scan_metadata()
        self._map_scan_modules()
        self._calculate_positions()

    def _map_scan_metadata(self):
        self.destination.scan.repeat_count = int(
            self.source.scan.find("repeatcount").text
        )
        if self.source.scan.find("comment") is not None:
            self.destination.scan.comment = self.source.scan.find(
                "comment"
            ).text

    def _map_scan_modules(self):
        scan_modules = {
            int(scan_module.get("id")): scan_module
            for scan_module in self.source.scan_modules
            if int(scan_module.find("parent").text) != -1
        }
        try:
            root_module_id = [
                smid
                for smid, scan_module in scan_modules.items()
                if int(scan_module.find("parent").text) == 0
            ][0]
        except IndexError:
            return
        connected_scan_module_ids = []

        def traverse(scan_module_id):
            connected_scan_module_ids.append(scan_module_id)
            scan_module = scan_modules[scan_module_id]
            if scan_module.find("nested") is not None:
                traverse(int(scan_module.find("nested").text))
            if scan_module.find("appended") is not None:
                traverse(int(scan_module.find("appended").text))

        traverse(root_module_id)

        connected_scan_modules = {
            int(scan_module.get("id")): scan_module
            for scan_module in self.source.scan_modules
            if int(scan_module.get("id")) in connected_scan_module_ids
        }
        for scan_module_id in connected_scan_module_ids:
            self.destination.scan.scan_modules[scan_module_id] = (
                self._map_scan_module(connected_scan_modules[scan_module_id])
            )
        nested_scan_modules = [
            int(scan_module.find("nested").text)
            for scan_module in connected_scan_modules.values()
            if scan_module.find("nested") is not None
        ]
        for scan_module in nested_scan_modules:
            self.destination.scan.scan_modules[scan_module].is_nested = True

    def _map_scan_module(self, element=None):
        scan_module = self._get_scan_module_instance(element)
        scan_module.id = int(element.attrib["id"])
        scan_module.name = element.find("name").text
        scan_module.parent = int(element.find("parent").text)
        try:
            scan_module.appended = int(element.find("appended").text)
        except AttributeError:
            pass
        try:
            scan_module.nested = int(element.find("nested").text)
        except AttributeError:
            pass
        for channel in element.iter("smchannel"):
            scan_module.channels[channel.find("channelid").text] = (
                self._map_scan_module_channel(channel)
            )
        for axis in element.iter("smaxis"):
            scan_module.axes[axis.find("axisid").text] = (
                self._map_scan_module_axis(
                    element=axis, scan_module=scan_module
                )
            )
        for pre_scan in element.iter("prescan"):
            scan_module.pre_scan_settings[pre_scan.find("id").text] = (
                self._map_scan_module_pre_scan(element=pre_scan)
            )
        for post_scan in element.iter("postscan"):
            scan_module.post_scan_settings[post_scan.find("id").text] = (
                self._map_scan_module_post_scan(
                    element=post_scan, scan_module=scan_module
                )
            )
        for positioning in element.iter("positioning"):
            scan_module.positionings.append(
                self._map_scan_module_positioning(positioning)
            )
        return scan_module

    @staticmethod
    def _get_scan_module_instance(element):
        if element.find("classic") is not None:
            scan_module = scan.ScanModule()
            scan_module.number_of_measurements = int(
                element.find("classic").find("valuecount").text
            )
        elif (
            element.find("dynamic_axis_positions") is not None
            or element.find("dynamic_channel_values") is not None
        ):
            scan_module = scan.DynamicSnapshotModule()
        else:
            scan_module = scan.StaticSnapshotModule()
        return scan_module

    @staticmethod
    def _map_scan_module_channel(element):
        if element.find("interval"):
            channel = scan.IntervalChannel()
            channel.trigger_interval = float(
                element.find("interval").find("triggerinterval").text
            )
            channel.stopped_by = (
                element.find("interval").find("stoppedby").text
            )
        else:
            if element.find("standard").find("averagecount") is not None:
                channel = scan.AverageChannel()
                parameters = {
                    "averagecount": {"n_averages": int},
                    "maxdeviation": {"max_deviation": float},
                    "minimum": {"low_limit": float},
                    "maxattempts": {"max_attempts": int},
                }
                for key, value in parameters.items():
                    parameter = element.find("standard").find(key)
                    if parameter is not None:
                        attribute, cast = list(value.items())[0]
                        setattr(channel, attribute, cast(parameter.text))
            else:
                channel = scan.Channel()
            deferred = element.find("standard").find("deferredtrigger")
            if deferred is not None and deferred.text.lower() == "true":
                channel.deferred_trigger = True
        channel.id = element.find("channelid").text
        normalize_id = element.find("normalize_id")
        if normalize_id is not None:
            channel.normalize_id = normalize_id.text
        return channel

    def _map_scan_module_axis(self, element=None, scan_module=None):
        axis = scan.Axis()
        axis.id = element.find("axisid").text
        step_function = element.find("stepfunction").text.lower()
        if step_function in ["multiply"]:
            axis.position_mode = "relative"
        else:
            axis.position_mode = element.find("positionmode").text
        try:
            if step_function == "plugin":
                axis.step_function = getattr(
                    self, f"_map_axis_stepfunction_{step_function}"
                )(element, scan_module)
            else:
                axis.step_function = getattr(
                    self, f"_map_axis_stepfunction_{step_function}"
                )(element)
        except AttributeError:
            logger.warning(
                "Step function '%s' not understood.", step_function
            )
        return axis

    def _map_axis_stepfunction_add(self, element):
        step_function = scan.StepRange()
        step_function.start = self._cast_value(
            element.find("startstopstep").find("start")
        )
        step_function.stop = self._cast_value(
            element.find("startstopstep").find("stop")
        )
        step_function.step_width = self._cast_value(
            element.find("startstopstep").find("stepwidth")
        )
        step_function.is_main_axis = (
            element.find("startstopstep").find("ismainaxis").text.lower()
            == "true"
        )
        return step_function

    def _map_axis_stepfunction_multiply(self, element):
        return self._map_axis_stepfunction_add(element)

    @staticmethod
    def _map_axis_stepfunction_positionlist(element):
        step_function = scan.StepList()
        step_function.position_list = element.find("positionlist").text
        return step_function

    @staticmethod
    def _map_axis_stepfunction_range(element):
        step_function = scan.StepRanges()
        step_function.position_list = (
            element.find("range").find("positionlist").text
        )
        return step_function

    @staticmethod
    def _map_axis_stepfunction_file(element):
        step_function = scan.StepFile()
        step_function.filename = element.find("stepfilename").text
        return step_function

    @staticmethod
    def _map_axis_stepfunction_plugin(element, scan_module):  # noqa
        step_function = scan.StepReference()
        step_function.scan_module = scan_module
        if element.find("plugin").attrib["name"].endswith("Multiply"):
            step_function.mode = "multiply"
        for parameter in element.find("plugin").findall("parameter"):
            if parameter.attrib["name"] in ["summand", "factor"]:
                step_function.parameter = float(parameter.text)
            if parameter.attrib["name"] == "referenceaxis":
                step_function.axis_id = parameter.text
        return step_function

    @staticmethod
    def _map_scan_module_positioning(element):
        positioning = scan.Positioning()
        positioning.axis_id = element.find("axis_id").text
        positioning.channel_id = element.find("channel_id").text
        normalize_channel = element.find("normalize_id")
        if normalize_channel is not None:
            positioning.normalize_channel_id = normalize_channel.text
        positioning.type = element.find("plugin").attrib["name"].lower()
        for parameter in element.find("plugin").iter("parameter"):
            if parameter.attrib["name"] != "location":
                positioning.parameters.update(
                    {parameter.attrib["name"]: parameter.text}
                )
        return positioning

    def _map_scan_module_pre_scan(self, element=None):
        pre_scan = scan.PreScan()
        pre_scan.id = element.find("id").text
        pre_scan.value = self._cast_value(element.find("value"))
        return pre_scan

    def _map_scan_module_post_scan(self, element=None, scan_module=None):
        post_scan = scan.PostScan()
        post_scan.id = element.find("id").text
        value = element.find("value")
        if value is not None:
            post_scan.value = self._cast_value(element.find("value"))
        reset_original_value = element.find("reset_originalvalue")
        if (
            reset_original_value is not None
            and reset_original_value.text == "true"
        ):
            post_scan.reset_original_value = True
            post_scan.value = scan_module.pre_scan_settings[
                post_scan.id
            ].value
        return post_scan

    @staticmethod
    def _cast_value(element):
        element_type = element.attrib["type"]
        types = {
            "double": float,
            "string": str,
            "int": int,
        }
        return types[element_type](element.text)

    def _calculate_positions(self):
        for scan_module in self.destination.scan.scan_modules.values():
            if not isinstance(scan_module, scan.DynamicSnapshotModule):
                try:
                    scan_module.number_of_positions_per_pass = max(
                        axis.positions.size
                        for axis in scan_module.axes.values()
                    )
                except ValueError:
                    pass
                scan_module.number_of_positions_per_pass *= (
                    scan_module.number_of_measurements
                )
                if scan_module.positionings:
                    scan_module.number_of_positions_per_pass += 1

        try:
            root_module_id = [
                mod.id
                for mod in self.destination.scan.scan_modules.values()
                if mod.parent == 0
            ][0]
            self._traverse_n_positions(root_module_id)
            self._traverse_positions(root_module_id)
        except IndexError:
            pass

    def _traverse_n_positions(self, scan_module_id, factor=1):
        scan_module = self.destination.scan.scan_modules[scan_module_id]
        scan_module.number_of_positions = (
            scan_module.number_of_positions_per_pass * factor
        )
        if scan_module.nested:
            factor = scan_module.number_of_positions
            if scan_module.positionings:
                factor -= 1
            self._traverse_n_positions(scan_module.nested, factor)
        if scan_module.appended:
            self._traverse_n_positions(scan_module.appended, factor)

    def _traverse_positions(self, scan_module_id, startpos=1):
        scan_module = self.destination.scan.scan_modules[scan_module_id]
        if scan_module.position_counts is None:
            scan_module.position_counts = np.array([], dtype=int)
        number_of_positions_per_pass = (
            scan_module.number_of_positions_per_pass
        )
        if hasattr(scan_module, "positionings") and scan_module.positionings:
            number_of_positions_per_pass -= 1
        for _ in range(number_of_positions_per_pass):
            scan_module.position_counts = np.append(
                scan_module.position_counts, startpos
            )
            startpos += 1
            if scan_module.nested:
                startpos = self._traverse_positions(
                    scan_module.nested, startpos
                )
        if hasattr(scan_module, "positionings") and scan_module.positionings:
            scan_module.position_counts = np.append(
                scan_module.position_counts, startpos
            )
            for positioning in scan_module.positionings:
                positioning.position = startpos
            startpos += 1
        if scan_module.appended:
            startpos = self._traverse_positions(
                scan_module.appended, startpos
            )
        return startpos


class VersionMapperV9m1(VersionMapperV9m0):
    """
    Mapper for mapping SCML v9.1 file contents to data structures.

    .. note::

        SCML schema versions 9.0 and 9.1 differ only in their version
        number. Hence, this is an empty class delegating everything to its
        parent.

    Attributes
    ----------
    source : :class:`evedata.scan.boundaries.scml.SCML`
        Python object representation of an SCML file

    destination : :class:`evedata.scan.boundaries.scan.Scan`
        High(er)-level data structure representing an SCML file


    Examples
    --------
    Mapping a given SCML file to the evedata structures is the same for
    each of the mappers:

    .. code-block::

        mapper = VersionMapperV9m1()
        mapper.map(source=scml, destination=scan)

    Usually, you will obtain the correct mapper from the
    :class:`VersionMapperFactory`. In this case, the returned mapper has
    its :attr:`source` attribute already set for convenience:

    .. code-block::

        factory = VersionMapperFactory()
        mapper = factory.get_mapper(scml=scml)
        mapper.map(destination=scan)

    """


class VersionMapperV9m2(VersionMapperV9m0):
    """
    Mapper for mapping SCML v9.2 file contents to data structures.

    .. note::

        SCML schema versions 9.0 and 9.2 differ only in their version
        number. Hence, this is an empty class delegating everything to its
        parent.

    Attributes
    ----------
    source : :class:`evedata.scan.boundaries.scml.SCML`
        Python object representation of an SCML file

    destination : :class:`evedata.scan.boundaries.scan.Scan`
        High(er)-level data structure representing an SCML file


    Examples
    --------
    Mapping a given SCML file to the evedata structures is the same for
    each of the mappers:

    .. code-block::

        mapper = VersionMapperV9m2()
        mapper.map(source=scml, destination=scan)

    Usually, you will obtain the correct mapper from the
    :class:`VersionMapperFactory`. In this case, the returned mapper has
    its :attr:`source` attribute already set for convenience:

    .. code-block::

        factory = VersionMapperFactory()
        mapper = factory.get_mapper(scml=scml)
        mapper.map(destination=scan)

    """
