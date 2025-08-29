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
Sparse matrix operators for simulations. The operator covers a single site
of a larger system.
"""

# pylint: disable=protected-access
# pylint: disable=too-many-locals
# pylint: disable=too-many-arguments

from copy import deepcopy

import numpy as np

from qtealeaves.tooling import QTeaLeavesError
from qtealeaves.tooling.parameterized import _ParameterizedClass

__all__ = ["SparseMatrixOperator", "SparseMatrixOperatorPy"]


class _BaseSPOTerm(_ParameterizedClass):
    matrices = ["_sp_mat"]

    def __init__(self, is_first, is_last, do_vecs):
        if is_first and is_last:
            raise QTeaLeavesError("1-site system not covered.")

        if is_first and do_vecs:
            self._sp_mat = np.zeros((1, 2), dtype=int)
        elif is_last and do_vecs:
            self._sp_mat = np.zeros((2, 1), dtype=int)
        else:
            self._sp_mat = np.zeros((2, 2), dtype=int)

        self._set_default_identities("_sp_mat", 1)

        # Local terms are fairly general
        self.local_terms = []
        self.local_prefactor = []
        self.local_pstrength = []
        self.local_is_oqs = []

    @property
    def shape(self):
        """Returns the dimension of the MPO matrix."""
        return self._sp_mat.shape

    def __iadd__(self, other):
        """
        In-place addition of two sparse MPOs.

        **Arguments**

        other : instance of `SparseMatrixOperator`
            Sparse MPO to be added to the existing one.
        """
        if not isinstance(other, type(self)):
            raise QTeaLeavesError("Data type not implemented for `__iadd__`.")

        # Adding two spMPOs

        for attr_name in self.matrices:
            mat = self._stack(getattr(self, attr_name), getattr(other, attr_name))
            setattr(self, attr_name, mat)

        self.local_terms += other.local_terms
        self.local_prefactor += other.local_prefactor
        self.local_pstrength += other.local_pstrength
        self.local_is_oqs += other.local_is_oqs

        return self

    def add_local(self, operator_id, pstrength, prefactor, is_oqs):
        """
        Add a local term to the MPO.

        **Arguments**

        operator_id : int
            Operator index being used as local term.

        pstrength : int
            Index being used as parameter in Hamiltonian.

        prefactor : scalar
            Scalar for the local term.

        is_oqs : bool
            Flag if term is Lindblad (`True`) or standard
            local term in the Hamiltonian (`False`).
        """
        self.local_terms.append(operator_id)
        self.local_pstrength.append(pstrength)
        self.local_prefactor.append(prefactor)
        self.local_is_oqs.append(is_oqs)

    def _add_term_kwargs(self, **kwargs):
        for key, value in kwargs.items():
            mat = self._stack(getattr(self, key), value)
            setattr(self, key, mat)

    def _add_matrix_attr(self, attr_name, dtype, value_id):
        setattr(self, attr_name, np.zeros(self._sp_mat.shape, dtype=dtype))
        self._set_default_identities(attr_name, value_id)

    def _set_default_identities(self, attr_name, value):
        mat = getattr(self, attr_name)
        if self._sp_mat.shape[0] == 1:
            mat[-1, -1] = value
        elif self._sp_mat.shape[1] == 1:
            mat[0, 0] = value
        else:
            mat[0, 0] = value
            mat[-1, -1] = value

        setattr(self, attr_name, mat)

    @staticmethod
    def _stack_matrices(mat1, mat2):
        """
        Stack to matrices for the MPO taking into account
        where local terms are etc.

        **Arguments**

        mat1 : np.ndarray
            Matrix for the first term.

        mat2 : np.ndarray
            Matrix for second term; cannot contain local terms.
        """
        n1, n2 = mat1.shape
        m1, m2 = mat2.shape

        if mat2[0, -1] != 0:
            raise QTeaLeavesError("No local can be in `mat2`.")

        l1 = n1 + m1 - 2
        l2 = n2 + m2 - 2

        imag_1 = np.sum(np.abs(np.imag(mat1)))
        imag_2 = np.sum(np.abs(np.imag(mat2)))
        if imag_1 > 0:
            mat_out = np.zeros((l1, l2), dtype=mat1.dtype)
        elif imag_2 > 0:
            mat_out = np.zeros((l1, l2), dtype=mat2.dtype)
        else:
            mat_out = np.zeros((l1, l2), dtype=mat1.dtype)

        # Upper left rectangle, lowest row left part, lower right corner
        mat_out[: n1 - 1, : n2 - 1] = mat1[: n1 - 1, : n2 - 1]
        mat_out[-1, : n2 - 1] = mat1[-1, : n2 - 1]
        mat_out[-1, -1] = mat1[-1, -1]

        # Prevents casting complex values warning if not justified
        mat2 = np.real_if_close(mat2)

        mat_out[n1 - 1 : l1 - 1, n2 - 1 : l2 - 1] = mat2[1:-1, 1:-1]
        mat_out[n1 - 1 : l1 - 1, 0] = mat2[1:-1, 0]
        mat_out[-1, n2 - 1 : l2 - 1] = mat2[-1, 1:-1]

        return mat_out

    @staticmethod
    def _stack_rowvec(vec1, vec2):
        """
        Stack to row-vector for the MPO taking into account
        where local terms are etc.

        **Arguments**

        vec1 : np.ndarray
            Vector for the first term.

        vec2 : np.ndarray
            Vector for second term; cannot contain local terms.
        """
        n1, n2 = vec1.shape
        m1, m2 = vec2.shape

        if n1 != 1 or m1 != 1:
            raise QTeaLeavesError("Ain't no row vector.")

        l1 = 1
        l2 = n2 + m2 - 2
        imag_1 = np.sum(np.abs(np.imag(vec1)))
        imag_2 = np.sum(np.abs(np.imag(vec2)))
        if imag_1 > 0:
            vec_out = np.zeros((l1, l2), dtype=vec1.dtype)
        elif imag_2 > 0:
            vec_out = np.zeros((l1, l2), dtype=vec2.dtype)
        else:
            vec_out = np.zeros((l1, l2), dtype=vec1.dtype)

        vec_out[0, : n2 - 1] = vec1[0, : n2 - 1]
        vec_out[0, -1] = vec1[0, -1]

        # Prevents casting complex values warning if not justified
        vec2 = np.real_if_close(vec2)

        vec_out[0, n2 - 1 : l2 - 1] = vec2[0, 1 : m2 - 1]

        return vec_out

    @staticmethod
    def _stack_colvec(vec1, vec2):
        """
        Stack to column vector for the MPO taking into account
        where local terms are etc.

        **Arguments**

        vec1 : np.ndarray
            Vector for the first term.

        vec2 : np.ndarray
            Vector for second term; cannot contain local terms.
        """
        n1, n2 = vec1.shape
        m1, m2 = vec2.shape

        if n2 != 1 or m2 != 1:
            raise QTeaLeavesError("Ain't no col vector.")

        l1 = n1 + m1 - 2
        l2 = 1
        imag_1 = np.sum(np.abs(np.imag(vec1)))
        imag_2 = np.sum(np.abs(np.imag(vec2)))
        if imag_1 > 0:
            vec_out = np.zeros((l1, l2), dtype=vec1.dtype)
        elif imag_2 > 0:
            vec_out = np.zeros((l1, l2), dtype=vec2.dtype)
        else:
            vec_out = np.zeros((l1, l2), dtype=vec1.dtype)

        vec_out[: n1 - 1, 0] = vec1[: n1 - 1, 0]
        vec_out[-1, 0] = vec1[-1, 0]

        # Prevents casting complex values warning if not justified
        vec2 = np.real_if_close(vec2)

        vec_out[n1 - 1 : l1 - 1, 0] = vec2[1 : m1 - 1, 0]

        return vec_out

    @staticmethod
    def _stack(mat1, mat2):
        """
        Stack to matrix or vector for the MPO taking into account
        where local terms are etc. Matrix or vector is chosen
        based on dimension.

        **Arguments**

        mat1 : np.ndarray
            Matrix or vector for the first term.

        mat2 : np.ndarray
            Matrix or vector for second term; cannot contain local terms.
        """
        n1, n2 = mat1.shape
        m1, m2 = mat2.shape

        if n1 == 1 and m1 == 1:
            # Row vector
            return SparseMatrixOperator._stack_rowvec(mat1, mat2)

        if n2 == 1 and m2 == 1:
            # Column vector
            return SparseMatrixOperator._stack_colvec(mat1, mat2)

        return SparseMatrixOperator._stack_matrices(mat1, mat2)


class SparseMatrixOperator(_BaseSPOTerm):
    """
    A single indexed sparse MPO representing one site.

    **Arguments**

    is_first : bool
        Flag if sparse matrix operator represents first site.

    is_last : bool
        Flag if sparse matrix operator represents last site.

    do_vecs : bool
        For periodic boundary conditions aiming at actual matrices
        for all sites, set to `False`. For `True`, the first and
        last site will use vectors.
    """

    matrices = ["_sp_mat", "_pstrengthid", "_prefactor"]

    def __init__(self, is_first, is_last, do_vecs):
        super().__init__(is_first, is_last, do_vecs)

        self._pstrengthid = np.ndarray(0)
        self._add_matrix_attr("_pstrengthid", int, -1)

        self._prefactor = np.ndarray(0)
        self._add_matrix_attr("_prefactor", np.float64, 1.0)

    def add_term(self, sp_mat, pstrengthid, prefactor):
        """
        Add another sparse MPO to the existing one via terms.

        **Arguments**

        sp_mat : integer np.ndarray
            Index matrix of MPO to be added.

        pstrengthid : integer np.ndarray
            Index of parameters of the MPO to be added.

        prefactor : np.ndarray
            Prefactors of the MPO to be added.
        """
        self._add_term_kwargs(
            _sp_mat=sp_mat, _pstrengthid=pstrengthid, _prefactor=prefactor
        )

    def get_list_tensors(self):
        """Generate a list of the unique indices used in the MPO."""
        list_tensors = list(self._sp_mat.flatten()) + self.local_terms
        list_tensors = list(set(list_tensors))

        if 0 in list_tensors:
            list_tensors.remove(0)

        return list_tensors

    def write(self, fh):
        """
        Write out the sparse MPO compatible with reading it in fortran.

        **Arguments**

        fh : open filehandle
            Information about MPO will be written here.
        """
        num_rows, num_cols = self.shape
        num_nonzero = np.sum(self._sp_mat > 0)

        list_tensors = self.get_list_tensors()
        num_tensors = len(list_tensors)

        # pylint: disable-next=bad-string-format-type
        fh.write("%d %d %d %d \n" % (num_rows, num_cols, num_nonzero, num_tensors))

        # contains parameterization (always for things written from python)
        fh.write("T \n")

        for ii in range(num_rows):
            for jj in range(num_cols):
                if self._sp_mat[ii, jj] == 0:
                    continue

                fh.write("%d %d %d \n" % (ii + 1, jj + 1, self._sp_mat[ii, jj]))

                # parameterization always as stated above
                fh.write("%d \n" % (self._pstrengthid[ii, jj]))
                fh.write("%30.15E \n" % (self._prefactor[ii, jj]))

        for ii in range(num_tensors):
            fh.write("%d \n" % (list_tensors[ii]))

        fh.write("%d \n" % (len(self.local_terms)))
        for ii, elem in enumerate(self.local_terms):
            pstrength = int(self.local_pstrength[ii])
            prefactor = self.local_prefactor[ii]
            is_oqs = "T" if self.local_is_oqs[ii] else "F"
            fh.write("%d %d %30.15E %s \n" % (elem, pstrength, prefactor, is_oqs))


# pylint: disable-next=too-many-instance-attributes
class SparseMatrixOperatorPy(_BaseSPOTerm):
    """
    Sparse MPO matrix for one site and the python implementation.
    """

    matrices = ["_sp_mat", "_pstrength", "_prefactor", "_weight"]

    def __init__(self, is_first, is_last, do_vecs, operator_eye, tensor_backend=None):
        if tensor_backend is None:
            raise NotImplementedError(
                "tensor_backend has to be set when on this level."
            )

        super().__init__(is_first, is_last, do_vecs)

        self.tensor_backend = tensor_backend
        dtype_np = np.array(
            tensor_backend.base_tensor_cls(
                [1],
                dtype=tensor_backend.dtype,
                device="cpu",
            ).elem
        ).dtype
        dtype_re = dtype_np.type(0).real.dtype

        self._pstrength = np.ndarray(0)
        self._add_matrix_attr("_pstrength", int, -1)

        self._prefactor = np.ndarray(0)
        self._add_matrix_attr("_prefactor", dtype_re, 1.0)

        self._weight = np.ndarray(0)
        self._add_matrix_attr("_weight", dtype_np, 1.0)

        self.tensors = {1: operator_eye}
        self._map_parameterized = {}
        self._imap_parameterized = {}

        self._contraction_counter = 0

    # --------------------------------------------------------------------------
    #                             Overwritten magic methods
    # --------------------------------------------------------------------------

    def __iter__(self):
        """Iterator over all the tensors of the ITPOTerm"""
        yield from self.tensors.values()

    # --------------------------------------------------------------------------
    #                               Properties
    # --------------------------------------------------------------------------

    @property
    def device(self):
        """Device where the tensor is stored."""
        for _, tensor in self.tensors.items():
            return tensor.device

        raise QTeaLeavesError("Running inquiery on empty SPOTerm.")

    @property
    def dtype(self):
        """Data type of the underlying arrays."""
        for _, tensor in self.tensors.items():
            return tensor.dtype

        raise QTeaLeavesError("Running inquiery on empty SPOTerm.")

    @property
    def ndim(self):
        """Rank of the underlying tensor extracted from the first element."""
        for _, elem in self.tensors.items():
            return elem.ndim

    def __iadd__(self, other):
        """Overwriting `+=` operator."""
        if (self.tensors is not None) or (other.tensors is not None):
            raise QTeaLeavesError("Cannot add sparse matrices after settings tensors.")

        super().__iadd__(other)
        return self

    # --------------------------------------------------------------------------
    #                                       Methods
    # --------------------------------------------------------------------------

    def convert(self, dtype, device):
        """Convert data type and device."""
        tensor = None
        for _, tensor in self.tensors.items():
            tensor.convert(dtype, device)

        if tensor is not None:
            self._prefactor = np.array(self._prefactor, dtype=tensor.dtype)

        if (tensor is not None) and (self._weight is not None):
            self._weight = np.array(self._weight, dtype=tensor.dtype)

    def add_term(self, sp_mat, pstrength, prefactor, weight, mapping):
        """
        Adding a non-local terms via its SPO matrix.

        **Arguments**

        sp_mat : np.ndarray

        pstrength : parameterized couplings via integer ID appearing again in mapping

        prefactor : scalar constant coupling

        weight : combining pstrength and prefactor with initial values

        mapping : dict, mapping integers from pstrength into parameterized values
            (where values can be strings, scalars, callables).
        """
        # Avoid idx=0 because is zero weight
        new_pstrength = pstrength.copy()

        for ii in range(pstrength.shape[0]):
            for jj in range(pstrength.shape[1]):
                if pstrength[ii, jj] == 0:
                    continue

                param = mapping[pstrength[ii, jj]]

                idx = self._map_parameterized.get(
                    param, len(self._map_parameterized) + 1
                )
                self._map_parameterized[param] = idx
                self._imap_parameterized[idx] = param

                new_pstrength[ii, jj] = idx

        if np.any(new_pstrength == -1):
            raise QTeaLeavesError

        self._add_term_kwargs(
            _sp_mat=sp_mat,
            _pstrength=new_pstrength,
            _prefactor=prefactor,
            _weight=weight,
        )

    def copy(self):
        """Actual copy of instance."""

        new = SparseMatrixOperatorPy(
            False, False, True, None, tensor_backend=self.tensor_backend
        )

        for elem in self.matrices:
            setattr(new, elem, getattr(self, elem).copy())

        new.local_terms = deepcopy(self.local_terms)
        new.local_prefactor = deepcopy(self.local_prefactor)
        new.local_pstrength = deepcopy(self.local_pstrength)
        new.local_is_oqs = deepcopy(self.local_is_oqs)

        new.tensors = {}
        for key, value in self.tensors.items():
            new.tensors[key] = value.copy()

        return new

    def collapse(self, params):
        """
        Collapse function recalculates local and interaction terms based on
        the new couplings passed via `params` dictionary.
        """
        # `collapse_interactions` makes copy of `_weight` needs to be called first
        self.collapse_interactions(params)
        self.collapse_local(params)

    def collapse_interactions(self, params):
        """
        Collapse function recalculates interaction terms based on
        the new couplings passed via `params` dictionary.
        """

        self._weight = self._prefactor.copy()
        for ii in range(self._sp_mat.shape[0]):
            for jj in range(self._sp_mat.shape[1]):
                if self._pstrength[ii, jj] in [-1, 0]:
                    # Local term and identities can have zero entries, too
                    continue

                pstrength = self._pstrength[ii, jj]
                param = self._imap_parameterized[pstrength]
                strength = self.eval_numeric_param(param, params)
                if strength is not None:
                    self._weight[ii, jj] *= strength

    def collapse_local(self, params):
        """Combine all local terms and write them in its element."""
        if len(self.local_terms) == 0:
            return

        if len(self.local_terms) == 1:
            self._sp_mat[-1, 0] = self.local_terms[0]
            weight = self.eval_numeric_param(self.local_pstrength[0], params)
            self._weight[-1, 0] = self.local_prefactor[0] * weight
            return

        nn = len(self.tensors) + 1
        factor_this = self.local_prefactor[0]
        weight = self.eval_numeric_param(self.local_pstrength[0], params)
        tensor = self.tensors[self.local_terms[0]] * factor_this * weight

        for ii in range(1, len(self.local_terms)):
            factor_other = self.local_prefactor[ii]
            weight = self.eval_numeric_param(self.local_pstrength[ii], params)
            tensor.add_update(
                self.tensors[self.local_terms[ii]], factor_other=factor_other * weight
            )

        self.tensors[nn] = tensor
        self._sp_mat[-1, 0] = nn
        self._weight[-1, 0] = 1.0

    def is_gpu(self, query=None):
        """Check if object itself or a device string `query` is a GPU."""
        tensor = None
        for _, tensor in self.tensors.items():
            return tensor.is_gpu(query=query)

        if query is not None:
            raise QTeaLeavesError("Running query on empty SPO; no tensor to check.")

        # If there is no tensor, it should be save to say it is not on the GPU
        # This assumption will be fine in terms of conversions.
        return False

    def update_couplings(self, params):
        """Update the coupling with a new params dictionary."""

        # Makes copy of `_weight` needs to be called first
        self.collapse_interactions(params)

        # Local terms
        # -----------

        if len(self.local_terms) == 1:
            weight = self.eval_numeric_param(self.local_pstrength[0], params)
            self._weight[-1, 0] = self.local_prefactor[0] * weight
        elif len(self.local_terms) > 1:
            nn = self._sp_mat[-1, 0]
            if nn != len(self.tensors):
                raise QTeaLeavesError("Will break.")

            del self.tensors[nn]

            self.collapse_local(params)

    def tensordot_with_tensor(self, tensor, cidx_self, cidx_tensor, perm_out=None):
        """Execute contraction of sparseMPO with tensors."""
        # Need an empty one
        ctens = SparseMatrixOperatorPy(
            False, False, True, None, tensor_backend=self.tensor_backend
        )
        ctens._sp_mat = deepcopy(self._sp_mat)
        ctens._pstrength = None
        ctens._prefactor = deepcopy(self._prefactor)
        ctens._weight = deepcopy(self._weight)
        ctens.tensors = {}

        ctens._contraction_counter += len(self.tensors)

        for ii, tens_self in self.tensors.items():
            tmp = tens_self.tensordot(tensor, (cidx_self, cidx_tensor))

            if perm_out is not None:
                tmp.transpose_update(perm_out)

            ctens.tensors[ii] = tmp

        return ctens

    def tensordot_with_tensor_left(self, tensor, cidx_tensor, cidx_self, perm_out=None):
        """Execute contraction of tensor with sparse MPO (tensor first arg in tensordot)."""
        # Need an empty one
        ctens = SparseMatrixOperatorPy(
            False, False, True, None, tensor_backend=self.tensor_backend
        )
        ctens._sp_mat = deepcopy(self._sp_mat)
        ctens._pstrength = None
        ctens._prefactor = deepcopy(self._prefactor)
        ctens._weight = deepcopy(self._weight)
        ctens.tensors = {}

        ctens._contraction_counter += len(self.tensors)

        for ii, tens_self in self.tensors.items():
            tmp = tensor.tensordot(tens_self, (cidx_tensor, cidx_self))

            if perm_out is not None:
                tmp.transpose_update(perm_out)

            ctens.tensors[ii] = tmp

        return ctens

    def matrix_multiply(self, other, cidx_self, cidx_other, perm_out=None):
        """
        Contract two sparse MPOs (rows/cols contracted automatically, permutation
        has to be on full).
        """

        n1, n3, contr_tasks, sum_tasks = self._contract_tasks(other)

        # Need an empty one
        ctens = SparseMatrixOperatorPy(
            False, False, True, None, tensor_backend=self.tensor_backend
        )
        ctens._sp_mat = np.zeros((n1, n3), dtype=int)
        ctens._pstrength = None
        ctens._prefactor = np.zeros((n1, n3), dtype=self._prefactor.dtype)
        ctens._weight = np.zeros((n1, n3), dtype=self._weight.dtype)
        ctens.tensors = {}

        # Contraction tasks (can be parallelized)
        # -----------------

        ctens._contraction_counter += len(contr_tasks)

        for key, idx in contr_tasks.items():
            key_a = key[0]
            key_b = key[1]

            tens_a = self.tensors[key_a]
            tens_b = other.tensors[key_b]

            cidx_a = cidx_self + [tens_a.ndim - 1]
            cidx_b = cidx_other + [0]

            tmp = tens_a.tensordot(tens_b, (cidx_a, cidx_b))
            if perm_out is not None:
                tmp.transpose_update(perm_out)

            ctens.tensors[idx] = tmp

        # Summation tasks (can be parallelized)
        # ---------------

        for rc_key, elems in sum_tasks.items():
            i1 = rc_key[0]
            i3 = rc_key[1]

            if len(elems) == 1:
                # Only one element, nothing to sum
                target, idx, weight = elems[0]
                ctens._sp_mat[i1, i3] = idx
                ctens._weight[i1, i3] = weight
                continue

            target, idx, weight = elems[0]
            tmp = deepcopy(ctens.tensors[idx])
            tmp = tmp * weight

            for elem_ii in elems[1:]:
                target, idx, weight_ii = elem_ii
                tmp.add_update(ctens.tensors[idx], factor_other=weight_ii)

            ctens.tensors[target] = tmp
            ctens._sp_mat[i1, i3] = target
            ctens._weight[i1, i3] = 1.0

        # Cleanup unnecessary items
        keys_to_delete = []
        for ii in self.tensors:
            if not np.any(ctens._sp_mat == ii):
                keys_to_delete.append(ii)

        for ii in keys_to_delete:
            del self.tensors[ii]

        return ctens

    def _contract_tasks(self, other):
        """Generate the tasks for the contraction and the following summations."""
        n1 = self._sp_mat.shape[0]
        n2 = self._sp_mat.shape[1]
        n3 = other._sp_mat.shape[1]

        if other._sp_mat.shape[0] != n2:
            raise QTeaLeavesError(
                "Matrix dimension mismatch in sparse operator.",
                self._sp_mat.shape,
                other._sp_mat.shape,
            )

        contr_tasks = {}
        sum_tasks = {}
        idx = 1

        for i1 in range(n1):
            for i2 in range(n2):
                if self._sp_mat[i1, i2] == 0:
                    continue

                for i3 in range(n3):
                    if other._sp_mat[i2, i3] == 0:
                        continue

                    # Found match
                    idx_this = self._sp_mat[i1, i2]
                    idx_other = other._sp_mat[i2, i3]

                    if (idx_this, idx_other) not in contr_tasks:
                        idx += 1
                        contr_tasks[(idx_this, idx_other)] = idx

                    idx_source = contr_tasks[(idx_this, idx_other)]

                    key = (i1, i3)
                    if key not in sum_tasks:
                        sum_tasks[key] = []
                        idx_target = idx
                    elif len(sum_tasks[key]) == 1:
                        # Need a unique index
                        idx += 1
                        idx_target = idx
                    else:
                        idx_target = sum_tasks[key][-1][0]

                    weight = self._weight[i1, i2] * other._weight[i2, i3]
                    sum_tasks[(i1, i3)].append((idx_target, idx_source, weight))

        return n1, n3, contr_tasks, sum_tasks
