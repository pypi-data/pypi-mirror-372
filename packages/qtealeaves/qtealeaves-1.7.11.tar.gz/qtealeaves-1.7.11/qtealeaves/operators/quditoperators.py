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
Qudit operators.
"""

import numpy as np

from .tnoperators import TNOperators

__all__ = ["TN3levelsOperators", "TN4levelsOperators"]


class TN3levelsOperators(TNOperators):
    """
    Operators defined for Lambda-like three-level systems, e.g., used
    in the case of Rydberg systems.

    **Arguments**

    folder_operators : str, optional
        The name of the subfolder inside the input folder, where
        we store operators.
        Default to ``3levels``

    **Details**

    The three levels are labeled as: |0>, |1> and |r>.
    The following operators are defined: ``n0``, ``n1``, ``nr``,
    ``sx01``, ``sy01``, ``sz01``, ``n01``, ``n10``, ``n1r``, ``nr1``,
    ``sx1r``. The identity ``id`` is defined as well.
    """

    def __init__(self):
        super().__init__()

        self["id"] = np.eye(3)
        self["n0"] = np.diag([1, 0, 0])
        self["n1"] = np.diag([0, 1, 0])
        self["nr"] = np.diag([0, 0, 1])
        self["sx01"] = np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]])
        self["sy01"] = np.array([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]])
        self["sz01"] = np.array([[1, 0, 0], [0, -1, 0], [0, 0, 0]])
        self["n01"] = np.array([[0, 1, 0], [0, 0, 0], [0, 0, 0]])
        self["n10"] = np.array([[0, 0, 0], [1, 0, 0], [0, 0, 0]])
        self["n1r"] = np.array([[0, 0, 0], [0, 0, 1], [0, 0, 0]])
        self["nr1"] = np.array([[0, 0, 0], [0, 0, 0], [0, 1, 0]])
        self["sx1r"] = np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0]])


class TN4levelsOperators(TNOperators):
    """
    Operators defined for a 4-level system, e.g., targeting Rydberg
    systems with two low-energy states, one Rydberg state |r>, and
    one additional state |d> allowing a decay from |r> to |d>.

    **Arguments**

    folder_operators : str, optional
        The name of the subfolder inside the input folder, where
        we store operators.
        Default to ``4levels``

    **Details**

    The following operators are defined: ``n0``, ``n1``, ``nr``, ``nd``,
    ``sx01``, and ``sx1r``. The identity ``id`` is defined as well.
    """

    def __init__(self):
        super().__init__()

        self["id"] = np.eye(4)
        self["n0"] = np.diag([1, 0, 0, 0])
        self["n1"] = np.diag([0, 1, 0, 0])
        self["nr"] = np.diag([0, 0, 1, 0])
        self["nd"] = np.diag([0, 0, 0, 1])
        self["sx01"] = np.array(
            [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        )
        self["sy01"] = np.array(
            [[0, -1j, 0, 0], [1j, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        )
        self["sz01"] = np.array(
            [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        )
        self["n01"] = np.array([[0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
        self["n10"] = np.array([[0, 0, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
        self["n1r"] = np.array([[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
        self["nr1"] = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0]])
        self["sx1r"] = np.array(
            [[0, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 0]]
        )
        self["ndr"] = np.array(
            [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 1, 0.0]]
        )
        self["nrd"] = np.array(
            [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 0, 0.0]]
        )
