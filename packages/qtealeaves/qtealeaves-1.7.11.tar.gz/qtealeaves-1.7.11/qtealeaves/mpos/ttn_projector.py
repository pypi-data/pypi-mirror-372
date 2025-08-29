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
Class implementing the projectors of a TTN as effective operators.

We use the framework similar to effective operators, but for a tensor network
representing the object < psi0 | psi >, where psi is the current state (a variable),
and psi0 is the state we are projecting to (or projecting out).


* Projectors *
This allows us to compute the effective operators which represent the local overlap
<psi0|psi> at any position in the |psi> TTN.
To project out |psi0>, we compute (1-P)|psi> = |psi> - |psi0><psi0|psi>.
This is implemented in `project_out_projectors()` in the ttn_simulator module.

* Excited state search *
This functionality is used in the iterative ground state search. The idea is to iteratively
optimize the energy, while orthogonalizing the state to all previously found eigenstates.
We do this at the level of the Lanczos vectors when diagonalizing the local problem at each tensor.
All previous states are loaded at `TTNProjector` objects into a list of effective
projectors (eff_proj), as an attribute of the TTN.
The `project_out_projectors()` function is then called as a `pre_return_hook` in the eigensolver
call, and orthogonalizes the result to all existing effective_projectors.

* Approximating a superposition of TTNs *
In a similar way, it is also possible to find a TTN which optimally represents some superposition
a_i psi_i. This is effectively an efficient way to sum (possibly many) TTNs, without doubling the
bond dimension at every summation step.
Given a list of psi_i and a dummy target state phi, psi_i are transformed into `TTNProjector`
objects of phi.
Then, each tensor of phi is replaced by a sum of a_i * proj_i, where proj_i is the tensor obtained
by contracting
the i-th projector at a given position.
This functionality is implemented in `approximate_sum()` method of TTN in the ttn_simulator module.
"""

# pylint: disable=too-many-arguments

import logging

from qtealeaves.tooling.permutations import _transpose_idx
from qtealeaves.tooling.qtealeavesexceptions import QTeaLeavesError

from .abstracteffop import _AbstractEffectiveOperators

logger = logging.getLogger(__name__)

__all__ = [
    "TTNProjector",
]


class TTNProjector(_AbstractEffectiveOperators):
    """
    Implements a projector to a given TTN state psi0
    as local effective operator.

    **Arguments**

    psi0 : :class:`TTN` | str
        The state to project to. Can be a TTN object or a path to a .pklttn file.
    """

    def __init__(self, psi0):
        if psi0.extension == "ttn":
            psi0.iso_towards(psi0.default_iso_pos)
            self.psi0 = psi0
        else:
            raise QTeaLeavesError(
                f"TTNProjector requires psi0 in the TTN form, but got {type(psi0)}."
            )

        # we assume binary trees all over the place
        self.psi0.assert_binary_tree()

        self._num_sites = psi0.num_sites
        self._device = psi0.tensor_backend.device
        self._dtype = psi0.tensor_backend.dtype
        self._has_oqs = False

        self._eff_ops = {}

    # --------------------------------------------------------------------------
    #                          Overwritten operators
    # --------------------------------------------------------------------------

    def __getitem__(self, key):
        """Get an entry from the effective operators."""
        return self._eff_ops[key]

    def __setitem__(self, key, value):
        """Set an entry from the effective operators."""
        self._eff_ops[key] = value

    # --------------------------------------------------------------------------
    #                        Abstract effective operator methods
    # --------------------------------------------------------------------------

    @property
    def num_sites(self):
        """Number of sites property."""
        return self._num_sites

    @property
    def device(self):
        """Device where the tensor is stored."""
        return self._device

    @property
    def dtype(self):
        """Data type of the underlying arrays."""
        return self._dtype

    @property
    def has_oqs(self):
        """Return if effective operators is open system (if no support, always False)."""
        return self._has_oqs

    def convert(self, dtype, device, stream=None):
        """
        Convert the _eff_ops to the specified data type inplace.
        """
        for _, tensor in self._eff_ops.items():
            tensor.convert(dtype, device, stream=stream)

    # pylint: disable-next=too-many-locals
    def contr_to_eff_op(self, tensor, pos, pos_links, idx_out):
        """
        Contraction which moves the center of effective operators
        from pos to the neighbour linked by idx_out.
        Assumes binary trees.

        **Arguments**

        tensor : :class:`_AbstractQteaTensor`
            Tensor to be contracted to effective operator.

        pos : int, tuple (depending on TN)
            Position of tensor.

        pos_links : list of int, tuple (depending on TN)
            Position of neighboring tensors where the links
            in `tensor` lead to.

        idx_out : int
            Uncontracted link to be used for effective operator.
        """
        # get the information from the helper
        ops_list, idx_list, key, ikey = self._helper_contract_to_eff_op(
            pos, pos_links, idx_out
        )
        idx_op_list = list(zip(idx_list, ops_list))

        # CONTRACTION
        # do the first one by hand to get result
        # the op is always contracted along index 1
        idx, op = idx_op_list[0]
        result = tensor.tensordot(op, ((idx,), (1,)))
        perm_out = _transpose_idx(tensor.ndim, idx)
        result.transpose_update(perm_out)

        # continue in a loop for the rest
        for idx, op in idx_op_list[1:]:
            result = result.tensordot(op, ((idx,), (1,)))
            perm_out = _transpose_idx(result.ndim, idx)
            result.transpose_update(perm_out)

        # contract with the complex conjugate

        # find the indices across which to contract
        # They are the same for both tensors
        # pylint: disable-next=protected-access
        cidx = tensor._invert_link_selection([idx_out])
        conj_t = self.psi0[pos].conj()
        result = conj_t.tensordot(result, (cidx, cidx))
        # the result is an effective operators with two links,
        # the second is pointing towards the new tensor.

        del self._eff_ops[ikey]
        self._eff_ops[key] = result

    # pylint: disable-next=too-many-locals
    def contract_tensor_lists(
        self, tensor, pos, pos_links, custom_ops=None, pre_return_hook=None, cindex=1
    ):
        """
        Contract all effective operators around the tensor in position `pos`.
        Assumes binary trees.

        **Arguments**

        tensor : :class:`_AbstractQteaTensor`
            Tensor to be contracted to effective operator.

        pos : int, tuple (depending on TN)
            Position of tensor.

        pos_links : list of int, tuple (depending on TN)
            Position of neighboring tensors where the links
            in `tensor` lead to.

        custom_ops : None
            Not used.

        pre_return_hook : None
            Not used.

        cindex : int
            The index along which to contract the effective operators.
            For contract_tensor_lists use 1, to contract to the tensor.
            For contract_to_projector use 0.

        **Returns**
            The tensor with all surrounding effective operators contracted.
        """
        if custom_ops is not None:
            raise NotImplementedError(
                f"Got {custom_ops=}." + "Nothing is implemented here, expected None."
            )

        if pre_return_hook is not None:
            raise QTeaLeavesError(
                f"Expected pre_return_hook = None, but is set to {pre_return_hook}."
            )

        # get the info on the links around the pos
        ops_list = []
        idx_list = []
        for ii, pos_link in enumerate(pos_links):
            # pos_link will be None for the symmetry selector
            # link of the (0,0) tensor, which is handled
            # separately.
            if pos_link is not None:
                pos_jj = self._eff_ops[(pos_link, pos)]
                ops_list.append(pos_jj)
                idx_list.append(ii)

        # zipped list of indices and operators, sorted according to the index
        idx_op_list = list(zip(idx_list, ops_list))

        #####################################
        # Contract all effective operators

        # do the first one by hand to get result
        idx, op = idx_op_list[0]
        result = tensor.tensordot(op, ((idx,), (cindex,)))
        perm_out = _transpose_idx(tensor.ndim, idx)
        result.transpose_update(perm_out)

        # continue in a loop for the rest
        for idx, op in idx_op_list[1:]:
            result = result.tensordot(op, ((idx,), (cindex,)))
            perm_out = _transpose_idx(result.ndim, idx)
            result.transpose_update(perm_out)

        return result

    # pylint: disable=unused-argument
    def contract_to_projector(
        self,
        tensor,
        pos,
        pos_links,
        custom_ops=None,
        pre_return_hook=None,
    ):
        """
        Contraction to obtain the effective operators of the projector |psi0><psi0| at position pos.
        Contracts the self.psi0[pos] tensor with effective operators surrounding the tensor at pos
        along index 0.

        ** Arguments **
        tensor : None
            Not used
        pos : tuple[int]
            Position at which we are contracting the effective projectors.
        pos_links : list[tuple[int]]
            Positions of tensors where the links in the current tensor lead to.
        custom_ops : None
            Not used.
        pre_return_hook : None
            Not used.

        ** Returns **
            The tensor with all surrounding effective projectors contracted.
            Represents a local overlap between psi and psi0 at the given position.

        """
        # The tensor we want to contract with is the conjugate of self.psi0 at the given position.
        psi0conj = self.psi0[pos].conj()
        projector = self.contract_tensor_lists(
            psi0conj,
            pos,
            pos_links,
            custom_ops=custom_ops,
            pre_return_hook=pre_return_hook,
            cindex=0,
        )
        # The projector is the conjugate of the above contraction
        return projector.conj()

    # pylint: enable=unused-argument

    # pylint: disable-next=too-many-locals
    def setup_as_eff_ops(self, tensor_network, measurement_mode=False):
        """
        Initialize the effective operators for the projectors of
        self.psi0 to the given tensor_network.

        This is done in three steps:
        (1) Set the effective operators in the physical layer to identities.
        (2) For all layers except the top one; iterate through the tensors
            and set the effective operator on the link to the parent.
        (3) In the top layer, handle the effective operator between (0,0) and (0,1)
            separately.
        Assumes binary trees.

        **Arguments**

        tensor_network : :class:`TTN`
            The state to be projected on. Has to be a TTN.

        measurement_mode : bool
            Unused. Cannot measure.
        """
        if measurement_mode:
            raise QTeaLeavesError(
                f"Did not expect to have {measurement_mode=}"
                + " in effective projectors."
            )

        # make the notation a bit easier
        psi = tensor_network
        if psi.iso_center != psi.default_iso_pos:
            psi.iso_towards(psi.default_iso_pos)

        # Step (1)
        # Fill the bottom layer with identities.
        for tndx in range(2**psi.num_layers):
            lndx = psi.num_layers - 1

            pos_tensor = (lndx, tndx)
            pos_child_left = (lndx + 1, 2 * tndx)
            pos_child_right = (lndx + 1, 2 * tndx + 1)

            key_left = (pos_child_left, pos_tensor)
            key_right = (pos_child_right, pos_tensor)

            tensor = psi[pos_tensor]
            link_left = tensor.links[0]
            link_right = tensor.links[1]

            # You want the identity to have links 0 : down, 1 : up.
            identity_left = tensor.eye_like(link=link_left)
            identity_right = tensor.eye_like(link=link_right)

            self._eff_ops[key_left] = identity_left
            self._eff_ops[key_right] = identity_right

        # Step (2)
        # Iterate through the layers from the bottom up.
        # Treat the top layer separately!
        # The _eff_ops are defined on the links towards the children.
        # Contract:
        #              T1        1
        #             / \        |
        #            ef ef  ---> ef
        #             \ /        |
        #              T2*       0
        # Where T1 : tensor of psi,
        #       T2*: tensor of self.psi0, conjugated
        #       ef : the effective operators on the children legs of T1
        for ii in range(psi.num_layers - 1):
            # lndx is the actual layer index, counting from the
            # bottom layer as 0
            lndx = psi.num_layers - ii - 1

            # number of tensors in the layer
            num_tensors = 2 ** (lndx + 1)
            for tndx in range(num_tensors):
                pos_tensor = (lndx, tndx)
                pos_child_left = (lndx + 1, 2 * tndx)
                pos_child_right = (lndx + 1, 2 * tndx + 1)

                # get the two tensors
                top_tensor = psi[pos_tensor]
                bottom_tensor = self.psi0[pos_tensor].conj()

                # get the keys for the _eff_ops dictionary

                # pylint: disable-next=protected-access
                _, info = psi._get_parent_info(pos=pos_tensor)
                pos_parent = tuple(info[:2])

                key_parent = (pos_tensor, pos_parent)
                key_left = (pos_child_left, pos_tensor)
                key_right = (pos_child_right, pos_tensor)

                # get the existing effective operators
                effop_left = self._eff_ops[key_left]
                effop_right = self._eff_ops[key_right]

                # Now the contractions.
                # The order is chosen to avoid permuting the links in the end.
                result = bottom_tensor.tensordot(effop_right, ((1,), (0,)))
                result = result.tensordot(effop_left, ((0,), (0,)))
                result = result.tensordot(top_tensor, ((1, 2), (1, 0)))

                # result is a two-legged tensor
                # order: 0 - down, 1 - up
                self._eff_ops[key_parent] = result

        # Step (3)
        # Treat the top two tensors separately.
        # Both have _eff_ops on all children already.
        # The missing one is on the link between (0,0) and (0,1).
        # Contract the (0,1), and (0,1)* as top and bottom, and the
        # effective operators on the children links of (0,1).
        top_01 = psi[(0, 1)]
        bottom_01 = self.psi0[(0, 1)].conj()

        # this is an iterator
        # pylint: disable-next=protected-access
        child_info = psi._iter_children_pos(pos=(0, 1))
        pos_child_left = tuple(next(child_info)[:2])
        pos_child_right = tuple(next(child_info)[:2])

        # the existing effective operators
        effop_left = self._eff_ops[(pos_child_left, (0, 1))]
        effop_right = self._eff_ops[(pos_child_right, (0, 1))]

        # the contraction
        result = bottom_01.tensordot(effop_right, ((1,), (0,)))
        result = result.tensordot(effop_left, ((0,), (0,)))
        result = result.tensordot(top_01, ((1, 2), (1, 0)))

        self._eff_ops[((0, 1), (0, 0))] = result
