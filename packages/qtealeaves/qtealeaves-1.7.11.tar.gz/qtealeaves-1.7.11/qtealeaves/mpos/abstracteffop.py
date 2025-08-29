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
Abstract MPO terms defining the methods needed, e.g., for ground state search.
"""

import abc

from qtealeaves.tooling import QTeaLeavesError

__all__ = ["_AbstractEffectiveOperators"]


class _AbstractEffectiveOperators(abc.ABC):
    """
    Any effective operator or overlap.

    **Details**

    Effective operators should implement at least a dictionary
    functionality where the keys are made of a tuple of two
    entries, where each entry is the position of a tensor in
    the tensor network. The key `(pos_a, pos_b)` provides
    the effective operators of the tensor at `pos_a` contracted
    except for the link leading to the tensor at `pos_b`.
    The position itself can be implemented depending on the
    needs of the tensor networks, e.g., as integer or tuple
    of integers. Only each link needs a unique pair of positions.
    """

    # --------------------------------------------------------------------------
    #                               Properties
    # --------------------------------------------------------------------------

    @property
    @abc.abstractmethod
    def device(self):
        """Device where the tensor is stored."""

    @property
    @abc.abstractmethod
    def dtype(self):
        """Data type of the underlying arrays."""

    @property
    @abc.abstractmethod
    def num_sites(self):
        """Return the number of sites in the underlying system."""

    @property
    def has_oqs(self):
        """Return if effective operators is open system (if no support, always False)."""
        return False

    # --------------------------------------------------------------------------
    #                          Overwritten operators
    # --------------------------------------------------------------------------

    @abc.abstractmethod
    def __getitem__(self, idxs):
        """Get an entry from the effective operators."""

    @abc.abstractmethod
    def __setitem__(self, key, value):
        """Set an entry from the effective operators."""

    # --------------------------------------------------------------------------
    #                        Abstract effective operator methods
    # --------------------------------------------------------------------------

    @abc.abstractmethod
    def contr_to_eff_op(self, tensor, pos, pos_links, idx_out):
        """Calculate the effective operator along a link."""

    @abc.abstractmethod
    # pylint: disable-next=too-many-arguments
    def contract_tensor_lists(
        self, tensor, pos, pos_links, custom_ops=None, pre_return_hook=None
    ):
        """
        Linear operator to contract all the effective operators
        around the tensor in position `pos`. Used in the optimization.
        """

    @abc.abstractmethod
    def convert(self, dtype, device):
        """
        Convert underlying array to the specified data type inplace. Original
        site terms are preserved.
        """

    @abc.abstractmethod
    def setup_as_eff_ops(self, tensor_network, measurement_mode=False):
        """Set this sparse MPO as effective ops in TN and initialize."""

    # Potential next abstract methods (missing consistent interfaces
    # in terms of permutation, i.e., whole legs or just non-MPO legs)
    #
    # * tensordot_with_tensor
    # * tensordot_with_tensor_left
    # * matrix_matrix_mult

    # --------------------------------------------------------------------------
    #                            Effective operator methods
    # --------------------------------------------------------------------------

    def _helper_contract_to_eff_op(self, pos, pos_links, idx_out, keep_none=False):
        """
        Helper for contr_to_eff_op taking care of the inital steps.

        Arguments
        ---------

        pos : int, tuple (depending on TN)
            Position of tensor.

        pos_links : list of int, tuple (depending on TN)
            Position of neighboring tensors where the links
            in `tensor` lead to.

        idx_out : int
            Uncontracted link to be used for effective operator.

        Returns
        -------

        ops_list : List
            Effective operators for `contr_to_eff_op`.

        idx_list : List[int]
            Indices for `contr_to_eff_op`.

        key : tuple
            Key where to set newly calculated effective operator.

        ikey : tuple
            Inverse direction in comparison to ikey, e.g., to delete
            the entry which has become obsolete.
        """
        ops_list = []
        idx_list = []
        pos_link_out = None
        is_set = False
        for ii, pos_link in enumerate(pos_links):
            # detect the uncontracted link
            if ii == idx_out:
                pos_link_out = pos_link
                is_set = True
                continue

            if (pos_link is None) and (not keep_none):
                continue
            # get the tensor of the given positions
            pos_jj = self[(pos_link, pos)]
            ops_list.append(pos_jj)
            idx_list.append(ii)

        if not is_set:
            raise QTeaLeavesError(
                "Arguments for contraction effective operator mismatch"
                f" at position {pos} and idx_out={idx_out}."
            )

        # Key and key for inverse direction
        key = (pos, pos_link_out)
        ikey = (pos_link_out, pos)

        return ops_list, idx_list, key, ikey

    def print_summary(self):
        """Print summary of computational effort (by default no report)."""
