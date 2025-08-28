"""
*Information on measurements, often relevant for debugging purposes.*

Measurements often contain a lot of relevant information beyond the pure
data, such as the scan module structure of the scan as recreated from the
saved scan description (SCML file). Getting easy access to this kind of
information is particularly helpful if something went wrong or led to
unexpected results.

The functionality provided in this module focuses primarily on users
carrying out lower-level debug tasks, not normal end users who just want to
work with their data, as well as on the developers of the ``evedata``
package themselves. Note that the functionality operates mostly on
:obj:`EveFile <evedata.evefile.boundaries.evefile.EveFile>` objects,
hence the low-level user interface towards the eveH5 files, rather than the
high-level :obj:`Measurement
<evedata.measurement.boundaries.measurement.Measurement>` objects targeted
at end users.


Available functionality
=======================

* :class:`ScanModuleStructure`

  Collect basic information of the scan module structure of a scan.


Future plans
============

* :class:`EngineLogInformation` (preliminary name!)

  Collect information necessary to identify the engine log files.

  When something went wrong, one of the first steps admins usually try to do
  (if the incident is not too far in the past) is to have a look at the
  engine log files. However, currently it is rather tedious to identify the
  relevant log files, and although only with eveH5 structure v7.1 all
  relevant information will be available from an eveH5 file, a tool to
  collect the relevant information and do some "informed guessing" on older
  files is rather useful.

  The relevant information contains: timestamp of start and end of the
  measurement, host the engine runs on, user who started the engine,
  and the port the engine listens on (currently not available from the eveH5
  files).

* Extending the :class:`ScanModuleStructure` class

  * Display positionings for each scan module (if present)


Module documentation
====================

"""

import logging

from evedata.evefile.entities import data


logger = logging.getLogger(__name__)


class ScanModuleStructure:
    """
    Collect basic information of the scan module structure of a scan.

    Operating on the :attr:`EveFile.scan_modules
    <evedata.evefile.boundaries.evefile.EveFile.scan_modules>` attribute of
    the :class:`EveFile <evedata.evefile.boundaries.evefile.EveFile>` class,
    this class extracts and collects basic information on the scan modules the
    given scan consists of. Hence, this class is basically aimed at
    debugging purposes, or for providing a first overview of the scan
    structure and the devices in each of the scan modules.

    The (abbreviated) output showing the scan module structure of a real
    measurement file may look like:

    .. code-block:: none

        + 1: Dynamic Axis Snapshot - #1 [1]
        + 2: Dynamic Channel Snapshot - #1 [2]
        + 3: Motor - #47 [3..555]
            A Det-S (OMSMn:pi01700000)
            A Det-P (OMSMn:pi01700001)
            ...
          + 4: Motor - #56 [4..272]
              A SX700-Wavelength (nmEnerg:io1200000wl2e)
              C Keysight_1 (A2980:23303chan1)

    As you can see from this example, the output attempts to have minimal
    markup, to allow to focus on the contents. For each of the scan modules
    (marked by a ``+``), the ID, name, number of positions and first (and
    last) position are extracted. For each of the devices of a scan module,
    the type (A: axis, C: channel), the name and ID are extracted. The names
    are those used in the GUI of the measurement program, while the IDs are
    what you will find when opening an eveH5 file (*e.g.*, with the
    ``hdfview`` program).

    The resulting structure can be excessively configured, using the
    respective attributes described below. However, usually the default
    should be fine, and it is designed with a minimum markup in mind.

    .. note::

        Operating on the :attr:`EveFile.scan_modules
        <evedata.evefile.boundaries.evefile.EveFile.scan_modules>` attribute of
        the :class:`EveFile <evedata.evefile.boundaries.evefile.EveFile>`
        class, the resulting scan structure may not in all details reflect
        the original scan module structure, particularly given that the
        special MPSKIP scans will usually be processed already. See the
        :mod:`mpskip <evedata.evefile.controllers.mpskip>` module for details.


    Attributes
    ----------
    scan_modules : :class:`dict`
        Scan modules read from a given eveH5 file containing the SCML file.

        Typically, this is the :attr:`EveFile.scan_modules
        <evedata.evefile.boundaries.evefile.EveFile.scan_modules>` attribute of
        the :class:`EveFile <evedata.evefile.boundaries.evefile.EveFile>`
        class.

    scan_module_marker : :class:`str`
        Marker used to label a scan module.

        Default: ``+``

    axis_marker : :class:`str`
        Marker used to label an axis contained in a scan module.

        Default: ``A``

    channel_marker : :class:`str`
        Marker used to label a channel contained in a scan module.

        Default: ``C``

    indentation : :class:`str`
        Indentation used to label nested scan modules (and their devices).

        Default: two spaces

    device_indentation : :class:`str`
        Indentation used to label devices of scan modules.

        Default: four spaces


    Parameters
    ----------
    scan_modules : :class:`dict`
        Scan modules read from a given eveH5 file containing the SCML file.

        Typically, this is the :attr:`EveFile.scan_modules
        <evedata.evefile.boundaries.evefile.EveFile.scan_modules>` attribute of
        the :class:`EveFile <evedata.evefile.boundaries.evefile.EveFile>`
        class.


    Raises
    ------
    ValueError
        Raised if no scan modules are available to operate on.


    Examples
    --------
    Suppose you have loaded an eveH5 file using the :class:`EveFile
    <evedata.evefile.boundaries.evefile.EveFile>` class, and the loaded eveH5
    file contained the scan description (SCML file).

    .. code-block::

        eve_file = EveFile()
        eve_file.load(filename="my_measurement_file.h5")

        scan_module_structure = ScanModuleStructure(eve_file.scan_modules)
        scan_module_structure.create()

    This would create a textual overview of the scan structure in terms of
    its scan modules and the devices contained in each of the scan modules,
    and store this as a list of strings in the :attr:`structure` attribute.

    However, usually you are interested in a straight output of the
    structure, as you would like to debug something. Hence, simply replace
    :meth:`create` with :meth:`print` and you are done:

    .. code-block::

        eve_file = EveFile()
        eve_file.load(filename="my_measurement_file.h5")

        scan_module_structure = ScanModuleStructure(eve_file.scan_modules)
        scan_module_structure.print()

    This will create an output similar to what is shown as an example above
    at the beginning of the class documentation.

    """

    def __init__(self, scan_modules=None):
        if scan_modules is None:
            scan_modules = {}
        self.scan_modules = scan_modules

        self.scan_module_marker = "+"
        self.axis_marker = "A"
        self.channel_marker = "C"
        self.indentation = "  "
        self.device_indentation = "    "

        self._structure = []
        self._indentation_level = 0

    @property
    def structure(self):
        """
        Structure of the scan modules and their devices.

        The structure is created using the :meth:`create` method, and it can
        be plotted conveniently using the :meth:`print` method.

        Returns
        -------
        structure : :class:`list`
            Structure of the scan modules and their devices.

            Each element is of type :class:`str`.

        """
        return self._structure

    def create(self):
        """
        Create the basic information of the scan module structure of a scan.

        The resulting information is contained in the :attr:`structure`
        attribute and can be printed conveniently using the :meth:`print`
        method.
        """
        if not self.scan_modules:
            raise ValueError("No scan modules")
        for scan_module in self.scan_modules.values():
            self._create_scan_module_information(scan_module)
            for device in scan_module.data.values():
                self._create_device_information(device)
            if scan_module.nested:
                self._indentation_level += 1
            elif not scan_module.appended:
                self._indentation_level -= 1

    def _create_scan_module_information(self, scan_module):
        indentation = self.indentation * self._indentation_level
        if len(scan_module.position_counts) > 1:
            position_counts = (
                f"{scan_module.position_counts[0]}.."
                f"{scan_module.position_counts[-1]}"
            )
        else:
            position_counts = f"{scan_module.position_counts[0]}"
        self._structure.append(
            f"{indentation}{self.scan_module_marker} "
            f"{scan_module.id}: {scan_module.name} - #"
            f"{len(scan_module.position_counts)} [{position_counts}]"
        )

    def _create_device_information(self, device):
        indentation = self.indentation * self._indentation_level
        if isinstance(device, data.AxisData):
            marker = self.axis_marker
        elif isinstance(device, data.ChannelData):
            marker = self.channel_marker
        else:
            marker = "?"
        self._structure.append(
            f"{indentation}{self.device_indentation}{marker} "
            f"{device.metadata.name} ({device.metadata.id})"
        )

    def print(self):
        """
        Print the basic information of the scan module structure of a scan.

        Convenience method to print the contents of the :attr:`structure`
        attribute of the class line-by-line. Intern, the :meth:`create`
        method is called first, to ensure the correct output being printed.

        """
        self.create()
        for line in self._structure:
            print(line)
