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
Exception classes for quantum tea leaves.
"""

__all__ = [
    "QTeaError",
    "QTeaBackendError",
    "QTeaLeavesError",
    "QTeaOPESError",
]


class QTeaError(Exception):
    """
    Generic error for all Quantum TEA libraries. qtealeaves is the right
    place in the dependency tree to define this error class.
    """


class QTeaLeavesError(QTeaError):
    """Generic error for the qtealeaves library."""


class QTeaOPESError(QTeaLeavesError):
    """Error for sampling with OPES."""


class QTeaBackendError(QTeaLeavesError):
    """Error for problems with the linear algebra backend."""
