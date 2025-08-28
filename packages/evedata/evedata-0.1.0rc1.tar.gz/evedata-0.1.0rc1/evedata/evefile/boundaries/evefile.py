"""

*High-level Python object representation of eveH5 file contents.*

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 1

This module provides a high-level representation of the contents of an eveH5
file. Being a high-level, user-facing object representation, technically
speaking this module is a facade. The corresponding resource
(persistence-layer-facing interface) would be the :mod:`eveh5
<evedata.evefile.boundaries.eveh5>` module.

The big difference to the :mod:`evedata.measurement` subpackage: the
:mod:`evedata.evefile` subpackage still is rather close to the eveH5 files
and rather generic. Furthermore, some aspects such as "filling" (
*i.e.*, adding data points for axes datasets to be able to plot
arbitrary datasets against each other) are *not* performed within the
:mod:`evedata.evefile` subpackage. Additional abstractions, such as
instruments, will be implemented in the :mod:`evedata.measurement`
subpackage. However, each eveH5 file can be represented by an :obj:`EveFile`
object, and the :mod:`evedata.measurement` subpackage will make use of this
module.


Overview
========

A first overview of the classes implemented in this module and their
hierarchy is given in the UML diagram below.


.. figure:: /uml/evedata.evefile.boundaries.evefile.*
    :align: center

    Class hierarchy of the :mod:`evedata.evefile.boundaries.evefile` module,
    providing the facade (user-facing interface) for an eveH5 file.
    Basically, it inherits from :class:`evedata.evefile.entities.file.File`
    and adds behaviour. Most of this behaviour is contributed by the various
    modules of the :mod:`controllers <evedata.evefile.controllers>`
    subpackage.


Key aspects
===========

While the :mod:`evefile <evedata.evefile.boundaries.evefile>` module is the
high-level interface (facade) of the :mod:`evedata.evefile` subpackage,
it is still, from a functional viewpoint, close to the actual eveH5 files,
providing a faithful representation of all information contained in an eveH5
(and SCML) file. Nevertheless, it is clearly an abstraction from the actual
data files. Hence, the key characteristics of the module are:

* Stable interface to eveH5 files, regardless of their version.

  * Some features may only be available for newer eveH5 versions, though.

* Organising data in scan modules.

  * For eveH5 files up to schema version 7, this means (trying to) recreate
    the scan (module) structure and requires an SCML file to be stored
    within the HDF5 file.
  * In case no SCML file is present, a "dummy" scan module will be created
    containing all datasets.

* Powerful abstractions on the device level.

  * Options to devices appear as attributes of the device objects, not as
    separate datasets.
  * Devices have clear, recognisable types, such as "multimeter", "MCA",
    "scientific camera", to name but a few.

* Access to the complete information contained in an eveH5 (and SCML) file,
  *i.e.*, data and scan description.
* **No data filling**, *i.e.*, generally no ready-to-plot datasets.

  * Data filling functionality is provided by the
    :mod:`evedata.measurement` subpackage.
  * The reason to *not* automatically fill data: being able to tell which
    data (points) have actually been recorded.

* Actual **data are loaded on demand**, not when loading the file.

  * This does *not* apply to the metadata of the individual datasets.
    Those are read upon reading the file.
  * Reading data on demand should save time and resources, particularly
    for larger files.
  * Often, you are only interested in a subset of the available data.


Usage
=====

Loading the contents of a data file of a measurement may be as simple as:

.. code-block::

    evefile = EveFile(filename="my_measurement_file.h5")
    evefile.load()



Internals: What happens when reading an eveH5 file?
===================================================

Reading an eveH5 file is not as simple as reading contents of an HDF5 file
and present its contents as Python object hierarchy. At least, if you would
like to view, process, and analyse your data more conveniently, you should
not stop here. The idea behind the ``evedata`` package, and in parts behind
the :class:`EveFile` class, is to provide you as consumer of the data with
powerful abstractions and structured information. To this end, a series of
steps are necessary:

* Check whether the eveH5 file contains the scan description (SCML) file.

  * If so, extract (up to eveH5 v7) and import the scan description.
  * If not, we're probably doomed, as some of the mappings are hard to do
    otherwise.

* Create scan modules

  * If an SCML file was read, these are the actual scan modules.
  * If no SCML file was read, there is only one "dummy" scan module named
    "main".

* Read the eveH5 file (actually, an HDF5 file).
* Get the correct :class:`VersionMapper
  <evedata.evefile.controllers.version_mapping.VersionMapper>` class.
* Map the file contents to the proper data structures provided by the
  ``evedata`` package.


Module documentation
====================

"""

import logging

from evedata.evefile.entities.file import File, ScanModule
from evedata.evefile.boundaries.eveh5 import HDF5File
from evedata.evefile.controllers import version_mapping


logger = logging.getLogger(__name__)


class EveFile(File):
    """
    High-level Python object representation of eveH5 file contents.

    This class serves as facade to the entire :mod:`evedata.evefile`
    subpackage and provides a rather high-level representation of the
    contents of an individual eveH5 file.

    Individual measurements are saved in HDF5 files using a particular
    schema (eveH5). Besides file-level metadata, there are log messages,
    a scan description (originally an XML/SCML file), and the actual data.

    The data are organised in three functionally different sections: data,
    snapshots, and monitors.


    Attributes
    ----------
    metadata : :class:`evedata.evefile.entities.file.Metadata`
        File metadata

    log_messages : :class:`list`
        Log messages from an individual measurement

        Each item in the list is an instance of
        :class:`evedata.evefile.entities.file.LogMessage`.

    scan : :class:`evedata.evefile.entities.file.Scan`
        Description of the actual scan.

    scan_modules : :class:`dict`
        Modules the scan consists of.

        Each item is an instance of
        :class:`evedata.evefile.entities.file.ScanModule` and contains the
        data recorded within the given scan module.

        In case of no scan description present, a "dummy" scan module will
        be created containing *all* data.

    snapshots : :class:`dict`
        Device data recorded as snapshot during a measurement.

        Only those device data that are not options belonging to any of
        the devices in the :attr:`data` attribute are stored here.

        Each item is an instance of
        :class:`evedata.evefile.entities.data.Data`.

    monitors : :class:`dict`
        Device data monitored during a measurement.

        Each item is an instance of
        :class:`evedata.evefile.entities.data.Data`.

    position_timestamps : :class:`evedata.evefile.entities.data.TimestampData`
        Timestamps for each individual position.

        Monitors have timestamps (milliseconds since start of the scan)
        rather than positions as primary quantisation axis. This object
        provides a mapping between timestamps and positions and can be used
        to map monitor data to positions.


    Parameters
    ----------
    filename : :class:`str`
        Name of the file to be loaded.


    Raises
    ------
    exception
        Short description when and why raised


    Examples
    --------
    Loading the contents of a data file of a measurement may be as simple as:

    .. code-block::

        evefile = EveFile(filename="my_measurement_file.h5")
        evefile.load()


    .. todo::
        Shall the constructor be slightly changed, so that loading a file
        becomes standard? May be more convenient for the users. To retain
        testability, one could think of an additional parameter, like so:

        .. code-block::

            def __init__(self, filename="", load=True):
                ...
                if load:
                    self.load()

        This would just need an (anyway necessary) check for the filename
        to be present in the :meth:`load` method.


    """

    def __init__(self, filename=""):
        super().__init__()
        self.filename = filename

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

    def load(self, filename=""):
        """
        Load contents of an eveH5 file containing data.

        Parameters
        ----------
        filename : :class:`str`
            Name of the file to load.

        """
        if filename:
            self.metadata.filename = filename
        self._load_scml()
        self._create_scan_modules()
        self._read_and_map_eveh5_file()

    def _load_scml(self):
        self.scan.extract(filename=self.metadata.filename)

    def _create_scan_modules(self):
        if self.has_scan():
            for name, scan_module in self.scan.scan.scan_modules.items():
                self.scan_modules[name] = self._map_scan_module(scan_module)
        else:
            scan_module = ScanModule()
            self.scan_modules[scan_module.name] = scan_module

    @staticmethod
    def _map_scan_module(scan_module):
        new_scan_module = ScanModule()
        public_attributes = [
            attribute
            for attribute in scan_module.__dict__.keys()
            if not attribute.startswith("_")
        ]
        for attribute in public_attributes:
            setattr(
                new_scan_module, attribute, getattr(scan_module, attribute)
            )
        return new_scan_module

    def _read_and_map_eveh5_file(self):
        eveh5 = HDF5File()
        eveh5.read_attributes = True
        eveh5.close_file = False
        eveh5.read(filename=self.metadata.filename)
        mapper_factory = version_mapping.VersionMapperFactory()
        mapper = mapper_factory.get_mapper(eveh5)
        mapper.map(source=eveh5, destination=self)
        eveh5.close()

    def get_data(self, name=None):
        """
        Retrieve data objects by name.

        While generally, you can get the data objects by accessing the
        :attr:`data <evedata.evefile.entities.file.ScanModule>` attribute of
        the respective :attr:`scan_module` directly, there, they are stored
        using their HDF5 dataset name as key. Usually, however, data are
        accessed by their "given" name.

        Parameters
        ----------
        name : :class:`str` | :class:`list`
            Name or list of names of data to retrieve

        Returns
        -------
        data : :class:`evedata.evefile.entities.data.Data` | :class:`list`
            Data object(s) corresponding to the name(s).

            In case of a list of data objects, each object is of type
            :class:`evedata.evefile.entities.data.Data`.

        """
        data = []
        for scan_module in self.scan_modules.values():
            names = {
                item.metadata.name: key
                for key, item in scan_module.data.items()
            }
            if isinstance(name, (list, tuple)):
                for item in name:
                    data.append(scan_module.data[names[item]])
            else:
                data.append(scan_module.data[names[name]])
        if len(data) == 1:
            data = data[0]
        return data

    def has_scan(self):
        """
        Check whether a scan description is available.

        Convenience method useful for all the functionality that needs to
        know whether a scan description is available.

        Currently, the method checks whether the version attribute of the
        :attr:`scan` attribute has been set. In real cases, this should be
        a sufficient criterion to determine whether a scan description is
        available.

        Returns
        -------
        has_scan : :class:`bool`
            Whether a scan description is available.

        """
        return bool(self.scan.version)


if __name__ == "__main__":
    import timeit

    NUMBER = 10
    file = EveFile()
    FILENAME = "/messung/euvr/daten/2024/KW32_24/TOPPAN/00092.h5"
    time = timeit.timeit(
        "file.load(FILENAME)", number=NUMBER, globals=globals()
    )
    print(time / NUMBER)

    import cProfile

    cProfile.run("file.load(FILENAME)")
