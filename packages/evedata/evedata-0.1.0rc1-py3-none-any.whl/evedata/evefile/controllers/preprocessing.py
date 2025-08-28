"""
*Changing (preprocessing) data during import.*

Data as read from an HDF5 dataset often need to be processed in some way.
Due to the intrinsic strategy of the evedata package to load data only
*on demand*, this cannot simply be done during mapping, but needs to be
hooked in to the :class:`DataImporter
<evedata.evefile.entities.data.DataImporter>` class. Hence, all the
preprocessing steps implemented here inherit from
:class:`ImporterPreprocessingStep
<evedata.evefile.entities.data.ImporterPreprocessingStep>`.

Note that in this module, only the (more) generic preprocessing steps are
implemented. More specific preprocessing steps may be implemented in other
modules of the :mod:`controllers <evedata.evefile.controllers>` subpackage as
well. One example is the :mod:`mpskip <evedata.evefile.controllers.mpskip>`
module.


Overview
========

The following preprocessing steps have been implemented so far:

* :class:`SelectPositions`

  Extract rows of data corresponding to a list of positions.


Module documentation
====================

"""

import logging

import numpy as np

from evedata.evefile.entities.data import ImporterPreprocessingStep


logger = logging.getLogger(__name__)


class SelectPositions(ImporterPreprocessingStep):
    """
    Extract rows of data corresponding to a list of positions.

    When splitting datasets, only part of the data contained in an HDF5
    dataset need to be retained. Typically, extracting the correct rows
    relies on a list of known positions.

    This preprocessing step returns those rows whose values in the first
    column correspond to the values provided as :attr:`positions`


    Attributes
    ----------
    position_counts : :class:`list` | :class:`numpy.ndarray`
        Position counts of the dataset to be selected.

        These position counts are interpreted as values in the first column
        of the corresponding HDF5 dataset. Typically, this is the
        "position count".


    Examples
    --------
    Selecting positions from a given dataset requires a list or array of
    positions, and of course the corresponding data:

    .. code-block::

        task = SelectPositions()
        task.positions = [2, 4, 5]
        result = task.process(data)

    The selected data are returned by :meth:`process`, as shown above.

    """

    def __init__(self):
        super().__init__()
        self.position_counts = []

    def _process(self, data=None):
        if self.position_counts is not None:
            data = data[
                np.nonzero(
                    np.isin(data[data.dtype.names[0]], self.position_counts)
                )[0]
            ]
        return data
