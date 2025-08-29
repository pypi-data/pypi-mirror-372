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
Common support for MPI via mpi4py
"""

try:
    from mpi4py import MPI
except ImportError:
    MPI = None

# pickle in deepcopy fails if stored within the TN type
if MPI is not None:
    TN_MPI_TYPES = {
        # pylint: disable=c-extension-no-member
        "<c16": MPI.DOUBLE_COMPLEX,
        "<c8": MPI.COMPLEX,
        "<f4": MPI.REAL,
        "<f8": MPI.DOUBLE_PRECISION,
        "<i8": MPI.INT,
        # pylint: enable=c-extension-no-member
    }
else:
    TN_MPI_TYPES = {}
