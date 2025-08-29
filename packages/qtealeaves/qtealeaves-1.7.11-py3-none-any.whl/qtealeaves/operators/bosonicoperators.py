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
Bosonic operators.
"""

import numpy as np

from .tnoperators import TNOperators

__all__ = ["TNBosonicOperators"]


class TNBosonicOperators(TNOperators):
    """
    Operators specifically targeted at bosonic systems. The operators
    ``id``, ``b``, ``bdagger``, ``n``, and ``nint`` are provided by default.

    **Arguments**

    folder_operators : str
        The name of the subfolder inside the input folder, where
        we store operators.

    **Details**

    The truncation of the Fock-space can be set via the keys ``fock_space_nmin``
    and ``fock_space_nmax``. By default, the local dimension is four including
    the levels 0, 1, 2, and 3.
    """

    def __init__(self):
        super().__init__()

        # Define operators via callable allowing to specify Fock space cutoff
        self["id"] = self.get_id
        self["n"] = self.get_n
        self["nint"] = self.get_nint
        self["b"] = self.get_b
        self["bdagger"] = self.get_bdagger

    @staticmethod
    def get_id(params):
        """
        Define the identity operator.
        """
        nmin = params.get("fock_space_nmin", 0)
        nmax = params.get("fock_space_nmax", 3)

        return np.eye(nmax - nmin + 1)

    @staticmethod
    def get_n(params):
        """
        Define the number operator.
        """
        nmin = params.get("fock_space_nmin", 0)
        nmax = params.get("fock_space_nmax", 3)

        return np.diag(np.arange(nmin, nmax + 1))

    @staticmethod
    def get_nint(params):
        """
        Define the on-site interaction operator 0.5 * n * (n - 1).
        """
        nmin = params.get("fock_space_nmin", 0)
        nmax = params.get("fock_space_nmax", 3)

        return np.diag(0.5 * np.arange(nmin, nmax + 1) * np.arange(nmin - 1, nmax))

    @staticmethod
    def get_b(params):
        """
        Define the bosonic annihilation operator.
        """
        nmin = params.get("fock_space_nmin", 0)
        nmax = params.get("fock_space_nmax", 3)

        return np.sqrt(np.diag(np.arange(nmin, nmax + 2)))[1:, :-1]

    @staticmethod
    def get_bdagger(params):
        """
        Define the bosonic creation operator.
        """
        nmin = params.get("fock_space_nmin", 0)
        nmax = params.get("fock_space_nmax", 3)

        return np.sqrt(np.diag(np.arange(nmin, nmax + 2)))[:-1, 1:]
