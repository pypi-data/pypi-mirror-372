# This code is part of qtealeaves.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
Setup local unitary rotations before projective measurements.
"""

# pylint: disable=too-few-public-methods

import numpy as np

from qtealeaves.tooling import QTeaLeavesError

__all__ = ["UnitarySetupProjMeas"]


class UnitarySetupProjMeas:
    """
    Setup for applying unitaries prior to a projective measurement
    via `meas_projective`.

    Parameters
    ----------

    unitaries : list of xp.ndarrays of rank-2
        List of unitaries, which will be applied to the local
        Hilbert space according to the mode.
    mode : char
        Mode `R`, we draw randomly unitaries from the list
        and apply them before the projective measurement.
        Mode `S` select the unitary at the corresponding site,
        i.e., the i-th site applies always the i-th unitary.
    """

    def __init__(self, unitaries, mode="R"):
        self.unitaries = unitaries
        self.mode = mode

        if mode not in ["R", "S"]:
            raise ValueError("Unknown mode for UnitarySetupProjMeas.")

    def get_unitary(self, site_idx):
        """
        Retrieve the unitary for a site.

        Parameters
        ----------
        site_idx : int
            Get unitary for this site. Although it has to be passed always,
            it is only evaluated in `mode=S`.

        Returns
        -------
        unitary : np.ndarray of rank-2
            Tensor to be applied as local unitary to the site.
        """
        if self.mode == "R":
            idx = np.random.randint(len(self.unitaries))
            return self.unitaries[idx]

        if site_idx >= len(self.unitaries):
            raise QTeaLeavesError("List of provided unitaries not long enough.")

        return self.unitaries[site_idx]
