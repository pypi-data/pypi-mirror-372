"""

*An interface towards measurements.*

Generally, the :mod:`measurement <evedata.measurement>` subpackage,
as mentioned already in the :doc:`Concepts </concepts>` section, provides the
interface towards the "user", where user mostly means the ``evedataviewer``
and ``radiometry`` packages. However, besides these two Python packages,
human users will want to use the ``evedata`` package as well. Hence,
it should be as human-friendly as possible.

What is the main difference between the :mod:`evefile <evedata.evefile>` and
the :mod:`measurement <evedata.measurement>` subpackages? Basically,
**the information contained in an eveH5 file needs to be "interpreted"** to
be able to process, analyse, and plot the data. While the :mod:`evefile
<evedata.evefile>` subpackage provides the necessary data structures to
faithfully represent all information contained in an eveH5 file,
the :mod:`measurement <evedata.measurement>` subpackage provides the result
of an "interpretation" of this information in a way that facilitates data
processing, analysis and plotting.

However, the :mod:`measurement <evedata.measurement>` subpackage is still
general enough to cope with all the different kinds of measurements the eve
measurement program can deal with. Hence, it may be a wise idea to create
dedicated dataset classes in the ``radiometry`` package for different types
of experiments. The NeXus file format may be a good source of inspiration
here, particularly their `application definitions
<https://manual.nexusformat.org/classes/applications/index.html>`_. The
``evedataviewer`` package in contrast aims at displaying whatever kind of
measurement has been performed using the eve measurement program. Hence it
will deal directly with :obj:`Measurement
<evedata.measurement.boundaries.measurement.Measurement>` (facade) objects
of the :mod:`measurement <evedata.measurement>` subpackage.


"""
