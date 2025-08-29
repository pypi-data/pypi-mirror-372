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
Common permutations often used in tensor network methods.
"""
import numpy as np

__all__ = []


def _transpose_idx1(num_legs, contracted_idx):
    """Move second last index instead of last in `_transpose_idx`."""
    idxs = np.arange(num_legs)
    idxs[:-1] = _transpose_idx(num_legs - 1, contracted_idx)
    return idxs


def _transpose_idx2(num_legs, contracted_idx):
    """Move third last index instead of last in `_transpose_idx`."""
    idxs = np.arange(num_legs)
    idxs[:-2] = _transpose_idx(num_legs - 2, contracted_idx)
    return idxs


def _transpose_idx(num_legs, contracted_idx):
    """
    Transpose in the original order the indexes
    of a n-legs tensor contracted over the
    index `contracted_idx`

    Parameters
    ----------
    contracted_idx : int
        Index over which there has been a contraction

    Returns
    -------
    tuple
        Indexes for the transposition
    """
    if contracted_idx > num_legs - 1:
        raise ValueError(
            f"Cannot contract leg {contracted_idx} of tensor with {num_legs} legs"
        )
    # Until the contracted idx the ordering is correct
    idxs = np.arange(contracted_idx)
    # Then the last
    idxs = np.append(idxs, num_legs - 1)
    idxs = np.hstack((idxs, np.arange(contracted_idx, num_legs - 1)))

    return idxs
