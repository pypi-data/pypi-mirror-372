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
Spin operators.
"""

import numpy as np

from .tnoperators import TNOperators

__all__ = ["TNSpin12Operators", "TNSpin1Operators"]


class TNSpin12Operators(TNOperators):
    """
    Operators specifically targeted at spin 1/2 systems. The operators
    ``id``, ``sx``, ``sz``, ``n``= 1/2*(1-``sz``), and
    ``nz`` = 1/2*(1+``sz``) are provided by default.

    **Arguments**

    folder_operators : str, optional
        The name of the subfolder inside the input folder, where
        we store operators.
        Default to ``SPIN12``
    """

    def __init__(self):
        super().__init__()

        self["id"] = np.array([[1, 0], [0, 1.0]])
        self["sx"] = np.array([[0, 1], [1, 0.0]])
        self["sz"] = np.array([[1, 0], [0, -1.0]])
        self["n"] = np.array([[0, 0], [0, 1.0]])
        self["nz"] = np.array([[1, 0], [0, 0.0]])

        self["splus"] = np.array([[0, 1], [0, 0.0]])
        self["sminus"] = np.array([[0, 0], [1, 0.0]])


class TNSpin1Operators(TNOperators):
    """
    Operators specifically targeted at spin 1 systems.
    """

    def __init__(self):
        super().__init__()

        self["id"] = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        self["sx"] = (1.0 / np.sqrt(2.0)) * np.array(
            [[0.0, 1.0, 0.0], [1.0, 0.0, 1.0], [0.0, 1.0, 0.0]]
        )
        self["sy"] = (1.0 / np.sqrt(2.0)) * np.array(
            [[0.0, -1j, 0.0], [1j, 0.0, -1j], [0.0, 1j, 0.0]]
        )
        self["sz"] = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, -1.0]])
