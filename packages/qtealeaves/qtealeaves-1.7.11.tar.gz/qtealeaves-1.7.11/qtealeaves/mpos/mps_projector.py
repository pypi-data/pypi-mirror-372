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
Class implementing the projectors of a MPS as effective operators.

We use the framework similar to effective operators, but for a tensor network
representing the object < psi0 | psi >, where psi is the current state (a variable),
and psi0 is the state we are projecting to (or projecting out).


* Projectors *
This allows us to compute the effective operators which represent the local overlap
<psi0|psi> at any position in the |psi> MPS.
To project out |psi0>, we compute (1-P)|psi> = |psi> - |psi0><psi0|psi>.
This is implemented in `project_out_projectors()` in the mps_simulator module.

* Excited state search *
This functionality is used in the iterative ground state search. The idea is to iteratively
optimize the energy, while orthogonalizing the state to all previously found eigenstates.
We do this at the level of the Lanczos vectors when diagonalizing the local problem at each tensor.
All previous states are loaded as `MPSProjector` objects into a list of effective
projectors (eff_proj), as an attribute of the MPS.
The `project_out_projectors()` function is then called as a `pre_return_hook` in the eigensolver
call, and orthogonalizes the result to all existing effective_projectors.

* Approximating a superposition of MPSs *
In a similar way, it is also possible to find a MPS which optimally represents some superposition
a_i psi_i. This is effectively an efficient way to sum (possibly many) MPSs, without doubling the
bond dimension at every summation step.
Given a list of psi_i and a dummy target state phi, psi_i are transformed into `MPSProjector`
objects of phi.
Then, each tensor of phi is replaced by a sum of a_i * proj_i, where proj_i is the tensor obtained
by contracting the i-th projector at a given position.
This functionality is implemented in `approximate_sum()` method of MPS in the mps_simulator module.
"""

# to solve circular imports as they are needed only for type hints
from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import TYPE_CHECKING

import numpy as np

# pylint: disable-next=no-name-in-module
from qtealeaves.tensors import _AbstractQteaTensor
from qtealeaves.tooling.permutations import _transpose_idx
from qtealeaves.tooling.qtealeavesexceptions import QTeaLeavesError

from .abstracteffop import _AbstractEffectiveOperators

if TYPE_CHECKING:
    from qtealeaves.emulator import MPS

logger = logging.getLogger(__name__)

__all__ = [
    "MPSProjector",
]


class MPSProjector(_AbstractEffectiveOperators):
    """
    Implements a projector to a given MPS state psi0
    as local effective operator.

    **Arguments**

    psi0 : :class:`MPS` | str
        The state to project to. Can be a MPS object or a path to a .pklmps file.
    """

    def __init__(self, psi0: MPS | str):
        if psi0.extension == "mps":
            self.psi0 = psi0
        else:
            raise QTeaLeavesError(
                f"MPSProjector requires psi0 in the MPS form, but got {type(psi0)}."
            )

        self._num_sites = psi0.num_sites
        self._device = psi0.tensor_backend.device
        self._dtype = psi0.tensor_backend.dtype
        self._has_oqs = False

        self._eff_ops = {}

    # --------------------------------------------------------------------------
    #                          Overwritten operators
    # --------------------------------------------------------------------------

    def __getitem__(self, key: int):
        """Get an entry from the effective operators."""
        return self._eff_ops[key]

    def __setitem__(self, key: int, value: _AbstractQteaTensor):
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

    def convert(self, dtype, device: str, stream=None):
        """
        Convert the _eff_ops to the specified data type inplace.
        """
        for tensor in self._eff_ops.values():
            tensor.convert(dtype, device, stream=stream)

    def contr_to_eff_op(
        self,
        tensor: _AbstractQteaTensor,
        pos: int,
        pos_links: Sequence[int],
        idx_out: int,
    ):
        """
        Contraction which moves the center of effective operators
        from pos to the neighbour linked by idx_out.

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

        # filter out operators on the physical links (position 1)
        # (then the order of the contraction is always optimal)
        filtered_op_idx = [(op, idx) for op, idx in zip(ops_list, idx_list) if idx != 1]
        if not filtered_op_idx:
            # no effective operators to contract
            result = self.psi0[pos].conj()
            result_perm = np.arange(self.psi0[pos].ndim)
        else:
            # one operator to contract
            if len(filtered_op_idx) > 1:
                raise NotImplementedError(
                    "Expected to contract only one operator, but got more."
                )

            op, idx = filtered_op_idx[0]
            # contract the self tensor with the effective operator
            result = self.psi0[pos].conj().tensordot(op, ((idx,), (0,)))
            # permutation to translate tensor cidx to the correct position
            # (when going from right to left this should be the identity
            #  permutation, unless it is a rank-4 tensor)
            result_perm = _transpose_idx(self.psi0[pos].ndim, idx)

        ## contract the effective operator with the tensor
        # find the indices across which to contract
        # They are the same for both tensors
        # pylint: disable-next=protected-access
        cidx = tensor._invert_link_selection([idx_out])
        self._eff_ops[key] = result.tensordot(
            tensor, (result_perm[cidx].tolist(), cidx)
        )
        # the result is an effective operators with two links,
        # the second is pointing towards the new tensor.

        del self._eff_ops[ikey]

    # pylint: disable-next=too-many-arguments
    def contract_tensor_lists(
        self,
        tensor: _AbstractQteaTensor,
        pos: int,
        pos_links: Sequence[int],
        custom_ops: None = None,
        pre_return_hook: None = None,
        cindex: int = 1,
    ):
        """
        Contract all effective operators around the tensor in position `pos`.

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

        # get the info on the links around the pos, excluding the physical link (-pos-2)
        ops_idx_list = [
            (self._eff_ops[(pos_link, pos)], ii)
            for ii, pos_link in enumerate(pos_links)
            if pos_link is not None and pos_link > -1
        ]

        # choose different tensordot order to avoid transposing the tensor
        for op, idx in ops_idx_list:
            if idx not in [0, 2]:
                raise NotImplementedError(
                    f"Expected to contract only with idx = 0 or 2, but got {idx}."
                )
            if idx == 0:
                tensor = op.tensordot(tensor, ((cindex,), (idx,)))
            else:
                tensor = tensor.tensordot(op, ((idx,), (cindex,)))

        return tensor

    # pylint: disable-next=too-many-arguments
    def contract_to_projector(
        self,
        tensor: _AbstractQteaTensor,  # pylint: disable=unused-argument
        pos: int,
        pos_links: Sequence[int],
        custom_ops: None = None,
        pre_return_hook: None = None,
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

    # pylint: disable-next=too-many-locals
    def setup_as_eff_ops(self, tensor_network: MPS, measurement_mode: bool = False):
        """
        Initialize the effective operators for the projectors of
        self.psi0 to the given tensor_network.

        This is done in three steps:
        (1) Set the effective operators in the physical layer to identities.
            This layer is "virtual" and is indicated as $-pos-2$.
        (2) Handle boundary tensors separately, as the dummy boundary links
            are indicated as `None`.
        (3) For all tensors in the network set the effective operators on
            the links towards other tensors.

        **Arguments**

        tensor_network : :class:`MPS`
            The state to be projected on. Has to be a MPS.

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
        # Fill the virtual physical layer with identities.
        # This is done for compatibility with _helper_contract_to_eff_op()
        # but the contraction is avoided in this implementation.
        for pos, tens in enumerate(psi):
            _, down, _ = psi.get_pos_links(pos)
            self._eff_ops[(down, pos)] = tens.eye_like(link=psi.local_dim[pos])

        # Step (2)
        # Handle the boundary tensors separately. Add others identities on link `None`.
        # Note that this link has dimension 1, i.e., it is a scalar, except for symmetries.
        if psi.iso_center > 0:
            self.psi0.move_pos(0, psi.tensor_backend.computational_device)
            psi.move_pos(0, psi.tensor_backend.computational_device)
            # pylint: disable-next=protected-access
            cidx = self.psi0[0]._invert_link_selection([2])
            self._eff_ops[(0, 1)] = self.psi0[0].conj().tensordot(psi[0], (cidx, cidx))
        if psi.iso_center < psi.num_sites - 1:
            self.psi0.move_pos(
                psi.num_sites - 1, psi.tensor_backend.computational_device
            )
            psi.move_pos(psi.num_sites - 1, psi.tensor_backend.computational_device)
            # pylint: disable-next=protected-access
            cidx = self.psi0[-1]._invert_link_selection([0])
            self._eff_ops[(psi.num_sites - 1, psi.num_sites - 2)] = (
                self.psi0[-1].conj().tensordot(psi[-1], (cidx, cidx))
            )
            self.psi0.move_pos(psi.num_sites - 1, psi.tensor_backend.memory_device)
            psi.move_pos(psi.num_sites - 1, psi.tensor_backend.memory_device)

        # Step (3)
        # Iterate through the tensors from left to default_iso_pos (rightmost tensor).
        # Added iteration from right to default_iso_pos if one wants to avoid initial iso_towards
        # (this case, `if psi.iso_center is None: psi.iso_towards(psi.default_iso_pos)` is needed).
        # The _eff_ops are defined on the links towards the next tensor.
        # Contract:
        #   ef ━a━ T1 ━ c      ef ━a━ T1 ━ c      c (1)
        #   ┃      ┃b          ┃      ┃           ┃
        #   ┃d     id     ---> ┃d     ┃b     ---> ef
        #   ┃      ┃e          ┃      ┃           ┃
        #   ┗━━━━━ T2*━ f      ┗━━━━━ T2*━ f      f (0)
        # Where T1 : tensor of psi,
        #       T2*: tensor of self.psi0, conjugated
        #       ef : the effective operators towards T1

        for pos in range(1, psi.iso_center):
            self.psi0.move_pos(pos, psi.tensor_backend.computational_device)
            psi.move_pos(pos, psi.tensor_backend.computational_device)
            # get the links of the tensor
            left, _, right = psi.get_pos_links(pos)

            # get the tensors
            t1 = psi[pos]
            t2 = self.psi0[pos].conj()
            left_eff = self._eff_ops[(left, pos)]

            # contract the tensor with the effective operators
            # "abc,da,dbf->fc"
            eff_op = left_eff.tensordot(t1, ((1,), (0,)))
            # pylint: disable-next=protected-access
            cidx = eff_op._invert_link_selection([2])
            eff_op = t2.tensordot(eff_op, (cidx, cidx))
            self._eff_ops[(pos, right)] = eff_op

            self.psi0.move_pos(pos, psi.tensor_backend.memory_device)
            psi.move_pos(pos, psi.tensor_backend.memory_device)
            left_eff.convert(device=psi.tensor_backend.memory_device)
        # we keep the eff_ops pointing towards the iso_center on the computational device

        # Iterate through the tensors from right to default_iso_pos.
        # The _eff_ops are defined on the links towards the previous tensor.
        # At the moment this is not used, but it is here for future compatibility.
        # Alberto - Dec 2024

        for pos in range(psi.num_sites - 2, psi.iso_center, -1):
            self.psi0.move_pos(pos, psi.tensor_backend.computational_device)
            psi.move_pos(pos, psi.tensor_backend.computational_device)
            # get the links of the tensor
            left, _, right = psi.get_pos_links(pos)

            # get the tensors
            t1 = psi[pos]
            t2 = self.psi0[pos].conj()
            right_eff = self._eff_ops[(right, pos)]

            # contract the tensor with the effective operators
            # "abc,fc,dbf->da"
            perm = _transpose_idx(t1.ndim, 2)
            # transpose is only needed for rank-4 tensors,
            # but this should not have much overhead since is just a view
            eff_op = right_eff.tensordot(t1, ((1,), (2,))).transpose(perm)
            # pylint: disable-next=protected-access
            cidx = eff_op._invert_link_selection([0])
            eff_op = t2.tensordot(eff_op, (cidx, cidx))
            self._eff_ops[(pos, left)] = eff_op

            self.psi0.move_pos(pos, psi.tensor_backend.memory_device)
            psi.move_pos(pos, psi.tensor_backend.memory_device)
            right_eff.convert(device=psi.tensor_backend.memory_device)
        # we keep the eff_ops pointing towards the iso_center on the computational device
