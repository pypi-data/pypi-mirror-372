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
Sparse matrix product operators for simulations. This MPO covers a
full system with a list of `SparseMatrixOperator`.
"""

# pylint: disable=protected-access
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
import logging

import numpy as np

from qtealeaves.tensors.tensor_backend import TensorBackend
from qtealeaves.tooling import QTeaLeavesError
from qtealeaves.tooling.permutations import _transpose_idx
from qtealeaves.tooling.restrictedclasses import _RestrictedList

from .abstracteffop import _AbstractEffectiveOperators
from .sparsematrixoperator import SparseMatrixOperator, SparseMatrixOperatorPy

__all__ = ["SparseMPO", "SparseMatrixProductOperator"]

logger = logging.getLogger(__name__)


class SparseMatrixProductOperator:
    """
    Indexed sparse MPO for a set of sites.

    **Arguments**

    params : dict
        Parameterization of a simulation.

    model : instance of `QuantumModel`
        The physical model to be converted into an MPO.

    operator_map : dict
        Mapping the operators to their integer IDs.

    param_map : dict
        Mapping the parameters to their integer IDs.
    """

    def __init__(self, params, model, operator_map, param_map):
        ll = model.get_number_of_sites(params)
        ll_xyz = model.get_number_of_sites_xyz(params)

        self.sp_mat_ops = []
        for ii in range(ll):
            self.sp_mat_ops.append(SparseMatrixOperator(ii == 0, ii + 1 == ll, True))

        for term in model.hterms:
            sp_mat_ops_new = term.get_sparse_matrix_operators(
                ll_xyz,
                params,
                operator_map,
                param_map,
                SparseMatrixOperator,
                dim=model.dim,
            )
            self.add_terms(sp_mat_ops_new)

    def add_terms(self, sp_mat_ops_list):
        """
        Add a list of `SparseMatrixOperators` to the existing
        one in-place.

        **Arguments**

        sp_mat_ops_list : list of `SparseMatrixOperators`
            Another interaction to be added to the MPO.
        """
        ll = len(self.sp_mat_ops)
        nn = len(sp_mat_ops_list)

        if ll != nn:
            raise QTeaLeavesError("Can only combine same lengths.")

        for ii in range(ll):
            self.sp_mat_ops[ii] += sp_mat_ops_list[ii]

    def write(self, fh):
        """
        Write out the sparse MPO compatible with reading it in fortran.

        **Arguments**

        fh : open filehandle
            Information about MPO will be written here.
        """
        nn = len(self.sp_mat_ops)
        fh.write("%d \n" % (nn))
        fh.write("-" * 32 + "\n")

        for ii in range(nn):
            self.sp_mat_ops[ii].write(fh)
            fh.write("-" * 32 + "\n")


class SparseMPOSites(_RestrictedList):
    """SparseMPOSites contains the physical terms."""

    class_allowed = SparseMatrixOperatorPy

    def __init__(self, num_sites, operators, do_vecs=True, tensor_backend=None):
        if tensor_backend is None:
            raise NotImplementedError(
                "tensor_backend has to be set when on this level."
            )

        super().__init__()

        for ii in range(num_sites):
            operator_eye = operators[(ii, "id")]
            site = SparseMatrixOperatorPy(
                ii == 0,
                ii + 1 == num_sites,
                do_vecs,
                operator_eye,
                tensor_backend=tensor_backend,
            )
            self.append(site)

    def update_couplings(self, params):
        """Load couplings from an update params dictionary."""
        for elem in self:
            elem.update_couplings(params)


class SparseMPO(_AbstractEffectiveOperators):
    """
    Representation of a sparseMPO for python.
    """

    def __init__(self, num_sites, operators, do_vecs=True, tensor_backend=None):
        super().__init__()

        if tensor_backend is None:
            logger.warning("Setting default tensor backend because not passed.")
            tensor_backend = TensorBackend()

        self.site_terms = SparseMPOSites(
            num_sites, operators, do_vecs=do_vecs, tensor_backend=tensor_backend
        )

        self.eff_ops = {}

        # tracking
        self._contraction_counter = {}

        # for convert
        self._tensor_network = None

        # store mode on indexing when possible
        self._do_indexing = None

    # --------------------------------------------------------------------------
    #                               Properties
    # --------------------------------------------------------------------------

    @property
    def device(self):
        """Device where the tensor is stored."""
        for _, elem in self.eff_ops.items():
            return elem.device

        return None

    @property
    def dtype(self):
        """Data type of the underlying arrays."""
        for _, elem in self.eff_ops.items():
            return elem.dtype

        return None

    @property
    def num_sites(self):
        """Return the number of sites in the underlying system."""
        return len(self.site_terms)

    # --------------------------------------------------------------------------
    #                          Overwritten operators
    # --------------------------------------------------------------------------

    def __getitem__(self, key):
        """Get an entry from the effective operators."""
        return self.eff_ops[key]

    def __setitem__(self, key, value):
        """Set an entry from the effective operators."""
        if not isinstance(value, SparseMatrixOperatorPy):
            raise TypeError("`site_term` must be an SparseMatrixOperatorPy.")

        self.eff_ops[key] = value

    # --------------------------------------------------------------------------
    #     Abstract effective operator methods requiring implementation here
    # --------------------------------------------------------------------------

    # pylint: disable-next=too-many-locals
    def contr_to_eff_op(self, tensor, pos, pos_links, idx_out):
        """Contract operator lists with tensors T and Tdagger to effective operator."""
        ops_list = []
        idx_list = []
        pos_link_out = None
        for ii, pos_link in enumerate(pos_links):
            if ii == idx_out:
                pos_link_out = pos_link
                continue

            if pos_link is None:
                continue

            pos_jj = self.eff_ops[(pos_link, pos)]
            ops_list.append(pos_jj)
            idx_list.append(ii)

        if pos_link_out is None:
            raise QTeaLeavesError(
                "Arguments for contraction effective operator mismatch."
            )

        # Key and key for inverse direction
        key = (pos, pos_link_out)
        ikey = (pos_link_out, pos)
        c_counter = self._contraction_counter.get(key, 0)

        # Different loop starts are beneficial
        if idx_out > np.max(idx_list):
            # From left to right
            idx_start = 0
            stride = 1

        elif idx_out < np.min(idx_list):
            # Looping backwards requires flipping links - avoid for now
            idx_start = 0
            stride = 1
            ## From right to left
            # idx_start = len(idx_list) - 1
            # stride = -1

        else:
            # To get contractable stuff, we start right
            # of the gap and move rightwards
            stride = 1
            for ii, elem in enumerate(idx_list):
                if elem > idx_out:
                    idx_start = ii

        # Contract tree tensor with sparse MPO
        cidx = idx_list[idx_start]

        perm_out = _transpose_idx(tensor.ndim, cidx)
        perm_out[perm_out == tensor.ndim - 1] += 1
        perm_out = [tensor.ndim - 1] + list(perm_out) + [tensor.ndim + 1]

        ctens = ops_list[idx_start].tensordot_with_tensor_left(
            tensor, [cidx], [2], perm_out=perm_out
        )

        c_counter += ctens._contraction_counter
        ctens._contraction_counter = 0

        ii = idx_start
        for _ in range(len(idx_list) - 1):
            ii += stride
            if ii == len(idx_list):
                ii = 0

            if stride > 0:
                mat_b = ops_list[ii]

                # Need offset of one as we have link to the left now
                cidx_a = [idx_list[ii] + 1]
                cidx_b = [2]
                perm_out = _transpose_idx(ctens.ndim - 1, cidx_a[0])
                perm_out = list(perm_out) + [ctens.ndim - 1]
                ctens = ctens.matrix_multiply(mat_b, cidx_a, cidx_b, perm_out=perm_out)

            else:
                mat_a = ops_list[ii]

                # Need offset of one as we have link to the left now (cidx_b)
                cidx_a = [2]
                cidx_b = [idx_list[ii] + 1]
                perm_out = _transpose_idx(ctens.ndim - 2, idx_list[ii])
                perm_out += 1
                perm_out = [0] + list(perm_out) + [ctens.ndim - 1]
                ctens = mat_a.matrix_multiply(ctens, cidx_a, cidx_b, perm_out=perm_out)

            c_counter += ctens._contraction_counter
            ctens._contraction_counter = 0

        # Contract with complex conjugated
        cidx_a = tensor._invert_link_selection([idx_out])
        cidx_b = [ii + 1 for ii in cidx_a]

        # We get a four-link tensor
        perm_out = [1, 0, 2, 3]
        ctens = ctens.tensordot_with_tensor_left(
            tensor.conj(), cidx_a, cidx_b, perm_out=perm_out
        )

        c_counter += ctens._contraction_counter
        ctens._contraction_counter = 0

        if ikey in self.eff_ops:
            del self.eff_ops[ikey]

        self.eff_ops[key] = ctens
        self._contraction_counter[key] = c_counter

    # pylint: disable-next=too-many-locals, too-many-arguments
    def contract_tensor_lists(
        self, tensor, pos, pos_links, custom_ops=None, pre_return_hook=None
    ):
        """
        Linear operator to contract all the effective operators
        around the tensor in position `pos`. Used in the optimization.
        """
        if custom_ops is None:
            ops_list = []
            idx_list = []
            for ii, pos_link in enumerate(pos_links):
                if pos_link is None:
                    continue

                pos_jj = self.eff_ops[(pos_link, pos)]
                ops_list.append(pos_jj)
                idx_list.append(ii)
        else:
            # Required for time evolution backwards step on R-tensor
            ops_list = custom_ops
            idx_list = list(range(len(ops_list)))

        # Find the best start of the loop with an sparse MPO with just one
        # row if possible
        idx_start = 0
        for ii, elem in enumerate(ops_list):
            if elem is None:
                pass
            elif elem._sp_mat.shape[0] == 1:
                idx_start = ii
                break

        # Contract tree tensor with sparse MPO
        cidx = idx_list[idx_start]

        perm_out = _transpose_idx(tensor.ndim, cidx)
        perm_out[perm_out == tensor.ndim - 1] += 1
        perm_out = [tensor.ndim - 1] + list(perm_out) + [tensor.ndim + 1]

        ctens = ops_list[idx_start].tensordot_with_tensor_left(
            tensor, [cidx], [2], perm_out=perm_out
        )

        c_counter = self._contraction_counter.get(pos, 0)
        c_counter += ctens._contraction_counter
        ctens._contraction_counter = 0

        ii = idx_start
        for _ in range(len(idx_list) - 1):
            ii += 1
            if ii == len(idx_list):
                ii = 0

            op_ii = ops_list[ii]
            if ops_list[ii] is None:
                continue

            cidx_a = [idx_list[ii] + 1]
            cidx_b = [2]
            perm_out = _transpose_idx(ctens.ndim - 1, cidx_a[0])
            perm_out = list(perm_out) + [ctens.ndim - 1]
            ctens = ctens.matrix_multiply(op_ii, cidx_a, cidx_b, perm_out=perm_out)

            c_counter += ctens._contraction_counter
            ctens._contraction_counter = 0

        shape = ctens._sp_mat.shape
        if shape[0] != shape[1]:
            raise QTeaLeavesError("Failed to contract to square sparse MPO", shape)

        if shape[0] == 1:
            idx = ctens._sp_mat[0, 0]
            weight = ctens._weight[0, 0]
            ctens = ctens.tensors[idx]

            if abs(weight - 1.0) > 1e-14:
                ctens = ctens * weight

            ctens.remove_dummy_link(ctens.ndim - 1)
            ctens.remove_dummy_link(0)
        else:
            # we can take the trace by hand here
            tmp = None
            for ii in range(shape[0]):
                jj = ctens._sp_mat[ii, ii]
                if jj == 0:
                    continue

                tmp2 = ctens.tensors[jj].copy()
                tmp2.trace_one_dim_pair([0, tmp2.ndim - 1])

                if tmp is None:
                    tmp = tmp2
                    if abs(ctens._weight[ii, ii] - 1) > 1e-14:
                        tmp = tmp * ctens._weight[0, 0]
                else:
                    factor_other = ctens._weight[ii, ii]
                    tmp.add_update(tmp2, factor_other=factor_other)

            if tmp is None:
                # Can be treated if we find any operator and multiply by zero?
                raise QTeaLeavesError("Diagonal empty in SPO.")
            ctens = tmp

        self._contraction_counter[pos] = c_counter

        if pre_return_hook is not None:
            ctens = pre_return_hook(ctens)

        return ctens

    def convert(self, dtype, device):
        """
        Convert underlying array to the speificed data type inplace. Original
        site terms are preserved.
        """
        if (self.dtype == dtype) and (self.device == device):
            return

        # We could detect up-conversion and down-conversion. Only for
        # conversion to higher precisions, we have to copy from the
        # site terms again which are in double precision
        if self._tensor_network is None:
            raise QTeaLeavesError("convert needs tensor network to be set.")

        for ii, key in enumerate(self._tensor_network._iter_physical_links()):
            self[key] = self.site_terms[ii]

        for _, elem in self.eff_ops.items():
            elem.convert(dtype, device)

    # --------------------------------------------------------------------------
    #                    Overwriting methods from parent class
    # --------------------------------------------------------------------------

    def print_summary(self):
        """Print summary of computational effort."""

        mode_str = f"(indexing={self._do_indexing})"
        logger.info("%s Contraction summary SPO %s %s", "=" * 20, mode_str, "=" * 20)

        total = 0
        for key, value in self._contraction_counter.items():
            logger.info("Count %s = %s", key, value)
            total += value

        logger.info("Total contractions %s", total)
        logger.info("^" * 60)

    # --------------------------------------------------------------------------
    #                          Methods specific to SPO
    # --------------------------------------------------------------------------

    def update_couplings(self, params):
        """Load couplings from an update params dictionary."""
        self.site_terms.update_couplings(params)
        # self.collapse(params)

    # pylint: disable-next=too-many-locals
    def add_dense_mpo_list(self, dense_mpo_list, params, indexed_spo=True):
        """Add terms for :class:`DenseMPOList` to the SparseMPO."""
        is_oqs = False
        num_sites = self.num_sites

        self._do_indexing = indexed_spo

        for mpo in dense_mpo_list:
            if len(mpo) == 1:
                # Local term

                op = mpo[0].operator
                idx = mpo[0].site

                match = None
                for kk, val in self.site_terms[idx].tensors.items():
                    if op == val:
                        match = kk
                        break

                if match is None or (not indexed_spo):
                    match = len(self.site_terms[idx].tensors) + 1
                    self.site_terms[idx].tensors[match] = op

                self.site_terms[idx].add_local(
                    match, mpo[0].pstrength, mpo[0].weight, is_oqs
                )

                continue

            if len(mpo) == 2:
                if mpo[0].site + 1 == mpo[1].site:
                    # We have a nearest neighbor interaction

                    op_l = mpo[0].operator
                    op_r = mpo[1].operator

                    idx_l = mpo[0].site
                    idx_r = mpo[1].site

                    pre_l = mpo[0].weight
                    pre_r = mpo[1].weight

                    total_l = mpo[0].total_scaling
                    total_r = mpo[1].total_scaling

                    match_l = None
                    match_r = None

                    pdict = {
                        1: mpo[0].pstrength,
                        2: mpo[1].pstrength,
                    }

                    for kk, val in self.site_terms[idx_l].tensors.items():
                        if op_l == val:
                            match_l = kk
                            break

                    if match_l is None or (not indexed_spo):
                        match_l = len(self.site_terms[idx_l].tensors) + 1
                        self.site_terms[idx_l].tensors[match_l] = op_l

                    for kk, val in self.site_terms[idx_r].tensors.items():
                        if op_r == val:
                            match_r = kk
                            break

                    if match_r is None or (not indexed_spo):
                        match_r = len(self.site_terms[idx_r].tensors) + 1
                        self.site_terms[idx_r].tensors[match_r] = op_r

                    if idx_l == 0:
                        shape_l = (1, 3)
                    else:
                        shape_l = (2, 3)

                    if idx_r + 1 == num_sites:
                        shape_r = (3, 1)
                    else:
                        shape_r = (3, 2)

                    sp_mat_l = np.zeros(shape_l, dtype=int)
                    sp_mat_r = np.zeros(shape_r, dtype=int)

                    prefactor_l = np.zeros(shape_l, dtype=np.float64)
                    prefactor_r = np.zeros(shape_r, dtype=np.float64)

                    weight_l = np.zeros(shape_l, dtype=np.complex128)
                    weight_r = np.zeros(shape_r, dtype=np.complex128)

                    params_l = np.zeros(shape_l, dtype=int)
                    params_r = np.zeros(shape_r, dtype=int)

                    sp_mat_l[-1, 1] = match_l
                    prefactor_l[-1, 1] = pre_l
                    weight_l[-1, 1] = total_l
                    params_l[-1, 1] = 1

                    sp_mat_r[1, 0] = match_r
                    prefactor_r[1, 0] = pre_r
                    weight_r[1, 0] = total_r
                    params_r[1, 0] = 2

                    self.site_terms[idx_l].add_term(
                        sp_mat_l, params_l, prefactor_l, weight_l, pdict
                    )
                    self.site_terms[idx_r].add_term(
                        sp_mat_r, params_r, prefactor_r, weight_r, pdict
                    )

                    continue

            raise NotImplementedError(
                "Sparse-MPO beyond nearest-neighbor interactions."
            )

        for elem in self.site_terms:
            elem.collapse_local(params)

    def to_str(self):
        """String representation with sparse-matrix elements."""
        str_buffer = "\n" + "*" * 60 + "\n"

        str_buffer += f"Number of sites : {len(self.site_terms)}\n\n"

        for ii, elem in enumerate(self):
            str_buffer += f"Site {ii}\n"
            str_buffer += str(elem._sp_mat) + "\n"
            str_buffer += str(elem._weight) + "\n"

            str_buffer += "\n"

        return str_buffer

    def setup_as_eff_ops(self, tensor_network, measurement_mode=False):
        """Set this sparse MPO as effective ops in TN and initialize."""
        if measurement_mode:
            raise ValueError("SPO has no measurement mode.")

        self._tensor_network = tensor_network

        for ii, key in enumerate(tensor_network._iter_physical_links()):
            self.eff_ops[key] = self.site_terms[ii].copy()

        self.convert(tensor_network.dtype, tensor_network.device)

        tensor_network.eff_op = self
        tensor_network.build_effective_operators()
