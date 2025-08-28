"""

*An interface towards the eveH5 file format.*

Generally, the evefile functional layer, as mentioned already in the
:doc:`Concepts </concepts>` section, provides the interface towards the
persistence layer (eveH5 files). This is a rather low-level interface
focussing on a faithful representation of all information available in an
eveH5 file as well as the corresponding scan description (SCML), as long as
the latter is available.

Furthermore, the evefile functional layer provides a stable abstraction of
the contents of an eveH5 file and is hence *not* concerned with different
versions of both, the eveH5 file structure and the SCML schema. The data
model provided via its entities needs to be powerful (and modular) enough to
allow for representing all currently existing data files (regardless of
their eveH5 and SCML schema versions) and future-proof to not change
incompatibly (open-closed principle, the "O" in "SOLID) when new
requirements arise.


.. important::

    As the evefile functional layer is *not* meant as a (human-facing) user
    interface, it is *not* concerned with concepts such as "fill modes"
    (joining), but represents the data "as is". This means that the different
    data can generally not be plotted against each other. This is a
    deliberate decision, as joining data for a (two-dimensional) data array,
    although generally desirable for (simple) plotting purposes,
    masks/removes some highly important information, *e.g.* whether a value
    has not been measured in the first place, or whether obtaining a value
    has failed for some reason.


"""
