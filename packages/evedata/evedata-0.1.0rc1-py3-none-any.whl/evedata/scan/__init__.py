"""

*An interface towards scans.*

The :mod:`scan <evedata.scan>` functional layer contains all classes
necessary to represent the contents of an SCML file. The general idea behind
is to have all relevant information contained in the scan description and
saved together with the data in the eveH5 file at hand. The SCML file is
generally stored within the eveH5 file, and it is the information used by
the GUI of the measurement program. One big advantage of having the
information of the SCML file as compared to the information stored in the
eveH5 file itself: The structure of the scan is available, making it
possible to infer much more information relevant for interpreting the data.


One big difference between the SCML schema and the class hierarchy defined
in this functional layer: As the evedata package can safely assume only ever
to receive validated SCML files, some of the types of attributes are more
relaxed as compared to the schema definition. This makes it much easier to
map the types to standard Python types.

"""
