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
The module contains a light-weight exact state emulator.
"""
import numpy as np
import numpy.linalg as nla
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from qtealeaves.tooling import QTeaLeavesError

__all__ = ["StateVector"]


class StateVector:
    """
    State vector class for handling small systems without
    the truncation of entanglement.

    **Arguments**

    num_sites : int
        Number of sites in the system.

    local_dim : int, optional
        Local dimension of the sites
        Default to 2.

    state : ``None`` or np.ndarray, optional
        Pure state passed as numpy array. If ``None``, the |0...0>
        state is initialized; otherwise, the state vector is
        initialized with the numpy array.
        Default to ``None``.

    dtype : type, optional
        Initial data type if no numpy array is passed as initial state.
        The data type might change when executing operations.
        Default to ``np.complex128``
    """

    def __init__(self, num_sites, local_dim=2, state=None, dtype=np.complex128):
        self._num_sites = num_sites

        if hasattr(local_dim, "__len__"):
            if len(local_dim) != num_sites:
                raise QTeaLeavesError(
                    "Lenght of local dim %d does not" % (len(local_dim))
                    + " match number of sites %d." % (num_sites)
                )
            self._local_dim = local_dim
        else:
            self._local_dim = [local_dim] * self.num_sites

        # Dimension of the full Hilbert space
        self._global_dim = np.prod(self.local_dim)

        if state is None:
            psi = np.zeros(self.global_dim, dtype=dtype)
            psi[0] = 1.0
            self._state = np.reshape(psi, self.local_dim)
        else:
            if state.ndim == 1:
                if self.global_dim != np.prod(state.shape):
                    raise QTeaLeavesError(
                        "Dimension of state vector "
                        + "%d does" % (np.prod(state.shape))
                        + " not match dimension of Hilbert "
                        + "space %d." % (self.global_dim)
                    )
            elif state.ndim != self.num_sites:
                raise QTeaLeavesError(
                    "Number of sites in state vector does not "
                    + "match the number of sites defined in the "
                    + "input (%d vs %d)" % (state.ndim, self.num_sites)
                )
            elif list(state.shape) != list(self.local_dim):
                raise QTeaLeavesError("Local dimensions are not matching.")

            self._state = np.reshape(state, self.local_dim)

    def __add__(self, other):
        """
        Add another state to the current state.

        **Arguments**

        other : :class:`StateVector`
            Second state in addition.

        **Returns**

        psi : :class:`StateVector`
             Result of addition.
        """
        if isinstance(other, np.ndarray):
            return StateVector(
                self.num_sites, local_dim=self.local_dim, state=self.state + other
            )

        if isinstance(other, StateVector):
            return StateVector(
                self.num_sites, local_dim=self.local_dim, state=self.state + other.state
            )

        raise QTeaLeavesError("Unknown type for other")

    def __truediv__(self, factor):
        """
        Division of state by a scalar.

        **Arguments**

        factor : real / complex
             Reciprocal scaling factor for the current state vector.

        **Returns**

        psi : :class:`StateVector`
            Result of the division.
        """
        if not np.isscalar(factor):
            raise TypeError("Division is only defined with a scalar number")

        return StateVector(
            self.num_sites, local_dim=self.local_dim, state=self._state / factor
        )

    def __getitem__(self, key):
        """
        Provide the call for list-syntax to access entries of the
        state vector.

        **Arguments**

        key : int
            index of the element which you want to retrieve
            labeled in the complete Hilbert space.

        **Returns**

        scalar : float / complex
            Entry of the state vector.
        """
        return self._state.flatten()[key]

    def __iadd__(self, other):
        """
        Add another state to the current state in-place.

        **Arguments**

        other : :class:`StateVector`, numpy ndarray
            Second state in addition.
        """
        if isinstance(other, np.ndarray):
            self._state += np.reshape(other, self.local_dim)

        elif isinstance(other, StateVector):
            self._state += other.state
        else:
            raise QTeaLeavesError("Unknown type for other")

        return self

    def __itruediv__(self, factor):
        """
        Divide the state through a scalar in-place.

        **Arguments**

        factor : real / complex
             Reciprocal scaling factor for the current state vector.
        """
        if not np.isscalar(factor):
            raise TypeError("Division is only defined with a scalar number")

        self._state /= factor

        return self

    def __imul__(self, factor):
        """
        Multiply the state by a scalar in-place.

        **Arguments**

        factor : real / complex
             Scaling factor for the current state vector.
        """
        if not np.isscalar(factor):
            raise TypeError("Multiplication is only defined with a scalar number")

        self._state *= factor

        return self

    def __isub__(self, other):
        """
        Subtract another state from the current state in-place.

        **Arguments**

        other : :class:`StateVector`, numpy ndarray
            Second state in subtraction.
        """
        if isinstance(other, np.ndarray):
            self._state -= np.reshape(other, self.local_dim)

        elif isinstance(other, StateVector):
            self._state -= other.state
        else:
            raise QTeaLeavesError("Unknown type for other")

        return self

    def __len__(self):
        """
        Provide number of sites in the state vector.
        """
        return self.num_sites

    def __matmul__(self, other):
        """
        Implements contractions between two objects with the @ operator.
        Enables calculation of the overlap <self | other>.

        **Arguments**

        other : instance of :class:`StateVector`
            Second object for contraction.

        **Returns**

        overlap : scalar
            Overlap between states if other is :class:`StateVector`
        """
        return other.dot(self)

    def __mul__(self, factor):
        """
        Multiply the state by a scalar.

        **Arguments**

        factor : real / complex
             Scaling factor for the current state vector.

        **Returns**

        psi : :class:`StateVector`
            Result of the multiplication.
        """
        if not np.isscalar(factor):
            raise TypeError("Multiplication is only defined with a scalar number")

        return StateVector(
            self.num_sites, local_dim=self.local_dim, state=self._state * factor
        )

    def __repr__(self):
        """
        Return the class name as representation.
        """
        return self.__class__.__name__

    def __sub__(self, other):
        """
        Subtract another state from the current state.

        **Arguments**

        other : :class:`StateVector`
            Second state in subtraction.

        **Returns**

        psi : :class:`StateVector`
             Result of subtract.
        """
        if isinstance(other, np.ndarray):
            return StateVector(
                self.num_sites, local_dim=self.local_dim, state=self.state - other
            )

        if isinstance(other, StateVector):
            return StateVector(
                self.num_sites, local_dim=self.local_dim, state=self.state - other.state
            )

        raise QTeaLeavesError("Unknown type for other")

    @property
    def num_sites(self):
        """
        Number of sites property.
        """
        return self._num_sites

    @property
    def local_dim(self):
        """
        Local dimension property. Returns the array of local dimensions.
        """
        return self._local_dim

    @property
    def global_dim(self):
        """
        Global dimension property. Returns scalar with the dimension of
        the full Hilbert space.
        """
        return self._global_dim

    @property
    def state(self):
        """
        State property.
        The state vector in the shape of a N-legged tensor for N sites.
        """
        return self._state

    @state.setter
    def state(self, value):
        """
        Setter for state, used to update the state vector.
        """
        self._state = value

    def apply_global_operator(self, global_op):
        """
        Applies a global operator to the state; the state is updated
        in-place.

        **Arguments**

        global_op : numpy ndarray, rank-2
            Global operator acting on the whole Hilbert space.

        **Returns**

        Return ``None``; instance of class is updated in-place.
        """
        if global_op.ndim != 2:
            raise QTeaLeavesError("Global operator must be rank-2.")

        if any(global_op.shape != self.global_dim):
            raise QTeaLeavesError(
                "Global operator must match the " + "Hilbert space dimension."
            )

        state = np.reshape(self.state, [global_op.shape[0]])
        self._state = np.reshape(global_op.dot(state), self.local_dim)

    def apply_two_site_operator(self, twosite_op, sites):
        """
        Applies a two-site operator to the state; the state is updated
        in-place.

        **Arguments**

        twosite_op : np.array, rank-4
            Two-site operator to apply. The contraction with the state
            is done over the links [2,3] of the operator.

        sites : list/np.array of len 2
            Sites indices on which to apply the operator.

        **Returns**

        Return ``None``; instance of class is updated in-place.
        """
        sites = np.array(sites)
        if len(sites) != 2:
            raise QTeaLeavesError(f"{len(sites)} sites passed for a two-site operator.")

        if np.max(sites) >= self._num_sites or any(site < 0 for site in sites):
            raise QTeaLeavesError(
                "Site index out of range. Cannot apply operator"
                f" on sites {sites} to {self._num_sites}-site system."
            )
        if twosite_op.ndim != 4:
            raise QTeaLeavesError("Two-site operator must be rank-4.")

        if (
            twosite_op.shape[0] != twosite_op.shape[2]
            or twosite_op.shape[1] != twosite_op.shape[3]
        ):
            raise QTeaLeavesError(
                "Shape mismatch, two-site operator cannot change local Hilbert"
                " space dimension."
            )

        if (
            twosite_op.shape[2] != self._local_dim[sites[0]]
            or twosite_op.shape[3] != self._local_dim[sites[1]]
        ):
            raise QTeaLeavesError(
                "Shape mismatch: local dimension in two-site operator"
                " doesn't match the state's local Hilbert space dimension."
            )

        # apply the operator
        self._state = np.tensordot(self._state, twosite_op, [sites, [2, 3]])

        # permute the legs into the original order
        permutation = np.arange(self._num_sites - 2)
        permutation = np.insert(permutation, sites[0], self._num_sites - 2)
        permutation = np.insert(permutation, sites[1], self._num_sites - 1)
        self._state = np.transpose(self._state, permutation)

    def dot(self, other):
        """
        Calculate the dot-product or overlap between two state vectors, i.e.,
        <self | other>.

        **Arguments**

        other : :class:`StateVector`, numpy ndarray
            Measure the overlap with this other state vector..

        **Returns**

        Scalar representing the overlap; complex valued.
        """
        if isinstance(other, np.ndarray):
            return np.conj(self.state.flatten()).dot(other.flatten())

        if isinstance(other, StateVector):
            return np.conj(self.state.flatten()).dot(other.state.flatten())

        raise QTeaLeavesError("Unknown type for other")

    def meas_global_operator(self, global_op):
        """
        Measure the expectation value of a global operator.

        **Arguments**

        global_op : numpy ndarray, rank-2
            Global operator acting on the whole Hilbert space.

        **Returns**

        Return scalar value with the expectation value.
        """
        state = np.reshape(self.state, [global_op.shape[0]])
        return np.real(np.conj(state).dot(global_op.dot(state)))

    def norm(self):
        """
        Calculate the norm of the state.

        **Returns**

        norm : float
            Real-valued scalar with the norm.
        """
        return np.real(np.sum(np.conj(self._state) * self._state))

    def norm_sqrt(self):
        """
        Calculate the square root of the norm of the state.

        **Returns**

        norm_sqrt : float
            The square root of the norm.
        """
        return np.sqrt(self.norm())

    def add_update(self, other, factor_this=None, factor_other=None):
        """
        Inplace addition as `self = factor_this * self + factor_other * other`.
        Exactly copied from the QteaTensor class (Feb 2024).

        **Arguments**

        other : same instance as `self`
            Will be added to `self`. Unmodified on exit.

        factor_this : scalar
            Scalar weight for tensor `self`.

        factor_other : scalar
            Scalar weight for tensor `other`
        """
        if (factor_this is None) and (factor_other is None):
            self.state += other.state
            return

        if factor_this is not None:
            self.state *= factor_this
            return

        if factor_other is None:
            self.state += other.state
            return

        self.state += factor_other * other.state

    def normalize(self):
        """
        Normalize the current state in-place.

        **Returns**

        psi : :class:`StateVector`
            Normalized version, same object as input (no copy)
        """
        self /= np.sqrt(self.norm())
        return self

    def reduced_rho(self, idx_keep):
        """
        Calculate the reduced density matrix of a subset of sites.

        **Arguments**

        idx_keep : int or list of ints
            The site or sites specified here will be in the
            reduced density matrix.

        **Results**

        rho_ijk : numpy ndarray, rank-2
            Reduced density matrix for all the specified sites.
        """
        if np.isscalar(idx_keep):
            idx_keep = np.array([idx_keep])
        else:
            idx_keep = np.array(idx_keep)

        if len(idx_keep) != len(set(idx_keep)):
            raise QTeaLeavesError("Entries must be unique")

        if np.max(idx_keep) > self.num_sites - 1:
            raise QTeaLeavesError("Site index out-of-bound.")

        if np.min(idx_keep) < 0:
            raise QTeaLeavesError("Site index cannot be negative.")

        # Collect indices to be contracted
        contr_idx = []
        for ii in range(self.num_sites):
            if ii not in idx_keep:
                contr_idx.append(ii)

        # Reduced rho with indices of sites kept in ascending order
        rho_ijk = np.tensordot(
            self._state, np.conj(self._state), [contr_idx, contr_idx]
        )

        # Sort them in the order passed by the call
        nn = len(idx_keep)
        perm = np.zeros(2 * nn, dtype=int)
        perm[idx_keep.argsort()] = np.arange(nn)
        perm[nn:] = perm[:nn] + nn

        rho_ijk = np.transpose(rho_ijk, perm)

        return rho_ijk

    def reduced_rho_i(self, ii):
        """
        Calculate the reduced density matrix for a single site.

        **Arguments**

        ii : int
            Get reduced density matrix for this site.

        **Returns**

        rho_i : numpy ndarray, rank-2
             Reduced density matrix for site ii.
        """
        contr_ind = list(range(ii)) + list(range(ii + 1, self.num_sites))
        return np.tensordot(self._state, np.conj(self._state), [contr_ind, contr_ind])

    def reduced_rho_ij(self, ii, jj):
        """
        Calculate the reduced density matrix for a single site.

        **Arguments**

        ii : int
            Get reduced density matrix for this site and site jj.

        jj : int
            Get reduced density matrix for this site and site ii.

        **Returns**

        rho_ij : numpy ndarray, rank-2
             Reduced density matrix for site ii and jj.
        """
        if ii < jj:
            contr_ind = (
                list(range(ii))
                + list(range(ii + 1, jj))
                + list(range(jj + 1, self.num_sites))
            )
        elif jj < ii:
            contr_ind = (
                list(range(jj))
                + list(range(jj + 1, ii))
                + list(range(ii + 1, self.num_sites))
            )
        else:
            raise QTeaLeavesError("Sites ii and jj are equal.")

        rho_ij = np.tensordot(self._state, np.conj(self._state), [contr_ind, contr_ind])

        if jj < ii:
            rho_ij = np.transpose(rho_ij, [1, 0, 3, 2])

        dim = rho_ij.shape[0] * rho_ij.shape[1]

        return np.reshape(rho_ij, [dim, dim])

    @classmethod
    def from_groundstate(cls, ham, num_sites, local_dim):
        """
        Initialize the state vector with the ground state of a
        Hamiltonian passed as a matrix.

        **Arguments**

        ham : numpy ndarray, rank-2
            Matrix of the system. Lower triangular part is
            sufficient since ``numpy.linalg.eigh`` is used.

        num_sites : int
            Number of sites in the system.

        local_dim : int
            Local dimension of the sites
        """
        use_sparse = isinstance(ham, sp.csr_matrix)

        if not use_sparse:
            # Use dense matrix
            _, vecs = nla.eigh(ham)
        else:
            ham_sp = sp.csr_matrix(ham)
            _, vecs = spla.eigsh(ham_sp, k=1, which="SA")

        groundstate = vecs[:, 0]

        obj = cls(num_sites, local_dim=local_dim, state=groundstate)

        return obj
