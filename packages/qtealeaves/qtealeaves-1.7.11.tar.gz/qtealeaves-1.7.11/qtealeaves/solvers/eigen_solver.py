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
The module contains solvers for the Krylov eigensolver as an API (multiplication
matrix-vector are passed as function, vector class needs only a few attributes).

**Attributes needed for vector class**

* `norm`
* `dot` for inner product between two vectors.
* `add_update(self, other, factor_self, factor_other)
* `__itruediv__`
* `__imul__`
* `abs`
* `dtype_eps`
* `shape`
"""

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals

import logging

import numpy as np

from .abstract_solver import _AbstractSolver

__all__ = ["EigenSolverH", "DenseTensorEigenSolverH"]

logger = logging.getLogger(__name__)


class EigenSolverH(_AbstractSolver):
    """
    Eigensolver for hermitian matrix.

    **Arguments**

    vec0 : vector to apply exponential matrix to / initial guess

    matvec_func : callable, multiplies matrix in exponential with vector.

    args_func : list, arguments for matvec_func

    kwargs_func : dict, keyword arguments for matvec_func

    injected_funcs : `None` or dictionary.
        If data types are missing necessary attributes, e.g., `real`, we
        allow to inject them. Right now only for `real`. Key must be
        the attribute name to be replaces. Callable takes one argument
        being the obj.
    """

    def __init__(
        self,
        vec0,
        matvec_func,
        conv_params,
        args_func=None,
        kwargs_func=None,
        injected_funcs=None,
    ):

        super().__init__(vec0, matvec_func, conv_params, args_func, kwargs_func)

        self.nn_max = conv_params.arnoldi_maxiter
        # with respect to how many basis vectors do we re-orthogonalize
        if conv_params.solver_reorthogonalize is None:
            self.reorthogonalize = self.nn_max
        else:
            self.reorthogonalize = conv_params.solver_reorthogonalize

        tolerance = conv_params.sim_params["arnoldi_tolerance"]
        if tolerance is None:
            tolerance = conv_params.sim_params["arnoldi_min_tolerance"]
        self.tolerance = tolerance

        if injected_funcs is not None:
            # Overwrite default injected_funcs dictionary
            self.injected_funcs = injected_funcs

        self.init_basis()

    def init_basis(self):
        """Initialize the basis and create diagonal / subdiagonal entries."""
        self.assert_normalization()

        self.diag = np.zeros(self.nn_max + 1)
        self.sdiag = np.zeros(self.nn_max)
        self.basis.append(self.vec.copy())

    def check_exit_criterion(self, ii, evecs_ii_0):
        """Return boolean if exit criterion is fullfilled, either precision or max iter."""
        if hasattr(self, "tridiag"):
            # Already for the dense-tensor solver
            precision_fom = evecs_ii_0 * self.tridiag.elem[ii, ii + 1]
        else:
            precision_fom = evecs_ii_0 * self.sdiag[ii]

        if abs(precision_fom) < self.tolerance:
            logger.info(
                "EigenSolverH converged in %d steps with %f", ii + 1, precision_fom
            )
            return True

        if ii + 1 == self.nn_max:
            logger.warning(
                "EigenSolverH stopped at max_iter with %2.14f (target %2.14f)",
                precision_fom,
                self.tolerance,
            )
            return True

        return False

    def solve(self):
        """Solver step executing iterations until new vector is returned."""

        for ii in range(self.nn_max):
            # Matrix-vector multiplication interface
            self.vec = self.func(self.vec, *self.args, **self.kwargs)

            overlap = self.vec.dot(self.basis[ii])
            self.vec.add_update(self.basis[ii], factor_other=-overlap)

            if ii > 0:
                self.vec.add_update(
                    self.basis[ii - 1], factor_other=-self.sdiag[ii - 1]
                )

            # Beyond numpy/cupy, problem started (range can be set with tensor of len 1,
            # single integer cannot be set with tensor of len 1 for jax/tensorflow?)
            # Moreover, overlap can be on device, not host.
            if self.vec.linear_algebra_library == "torch":
                self.diag[ii] = self.real(overlap)
            else:
                self.diag[ii : ii + 1] = self.vec.get_of(self.real(overlap))
            self.sdiag[ii] = self.vec.norm_sqrt()

            mat = np.diag(self.diag[: ii + 1])
            for jj in range(ii):
                mat[jj, jj + 1] = self.sdiag[jj]
                mat[jj + 1, jj] = self.sdiag[jj]

            evals, evecs = np.linalg.eigh(mat)

            # Check on exit criteria
            if self.check_exit_criterion(ii, evecs[ii, 0]):
                break

            # Re-orthogonalize with respect to last 'self.reorthogonalize' basis vectors
            idx_start = (ii + 1) - min(ii + 1, self.reorthogonalize)
            self.orthogonalize(ii, idx_start=idx_start)

            self.sdiag[ii] = self.vec.norm_sqrt()
            self.vec /= self.sdiag[ii]
            self.basis.append(self.vec.copy())

        # Build solution (expecting list of eigenvalues even if size-one)
        val = [evals[0]]
        vec = self.basis[0] * evecs[0, 0]

        for jj in range(1, ii + 1):
            vec.add_update(self.basis[jj], factor_other=evecs[jj, 0])

        return val, vec


class DenseTensorEigenSolverH(EigenSolverH):
    """
    Eigensolver for hermitian matrix and dense tensor backends. It
    contains some optimizations.

    Arguments
    ---------

    vec0 : :class:`_AbstractQteaBaseTensor`
        vector to apply exponential matrix to / initial guess. Tensors
        are considered in a flattened shape to consider them as vectors.
        Requires attribute `_elem` and assignment by slices.

    matvec_func : callable
        multiplies matrix in exponential with vector; the matrix must
        be passed via `args_func` and `kwargs_func`.

    args_func : list
       arguments for matvec_func

    kwargs_func : dict
        keyword arguments for matvec_func

    injected_funcs : `None` or dictionary.
        If data types are missing necessary attributes, e.g., `real`, we
        allow to inject them. Right now only for `real`. Key must be
        the attribute name to be replaces. Callable takes one argument
        being the obj.

    Details
    -------

    The following optimizations are done within this eigensolver for dense
    tensors, especially towards reducing the number of function calls.

    1) Basis is implemented as a batched tensor allowing to calculate
       overlaps for re-orthonormalization within one einsum call
    2) We have warmup steps without calls to the eigensolver of the dense
       matrix solving the eigenproblem in the Krylov space. Warmup steps
       will be calculated based on the steps to convergence in past
       calls (module-wide, not persistent between different calls to python)

    """

    tracker = {}

    def __init__(
        self,
        vec0,
        matvec_func,
        conv_params,
        args_func=None,
        kwargs_func=None,
        injected_funcs=None,
    ):
        super().__init__(
            vec0,
            matvec_func,
            conv_params,
            args_func=args_func,
            kwargs_func=kwargs_func,
            injected_funcs=injected_funcs,
        )

        # We need some einsum based on the rank
        if vec0.ndim > 5:
            raise NotImplementedError("Rank-6 and higher not implemented, but easy.")
        base = "abcde"[: vec0.ndim]
        self._einsum_ortho_a = f"{base},i{base}->i"
        self._einsum_ortho_b = f"i,i{base}->{base}"
        self._einsum_solve = f"i{base},i->{base}"

    def init_basis(self):
        """
        Initialize the basis and create auxiliary data structures to build
        the matrix solved in the Krylov space.
        """
        self.assert_normalization()

        dtype = self.vec.dtype_real()
        tensor_cls = type(self.vec)
        self.tridiag = tensor_cls(
            [self.nn_max + 1, self.nn_max + 1],
            ctrl="Z",
            dtype=dtype,
            device=self.vec.device,
        )
        dims = [self.nn_max + 1] + list(self.vec.elem.shape)
        self.basis = tensor_cls(
            dims,
            ctrl="Z",
            dtype=self.vec.dtype,
            device=self.vec.device,
        )

        # pylint: disable-next=protected-access
        self.basis._elem[0, :] = self.vec.elem

    def get_nn_warmup(self):
        """Warmup steps are used to build up the basis without checking tolerance yet."""
        num_solved = len(self.tracker.get(self.dim_problem, {}))
        if num_solved <= 10:
            # No (or not much) information, start with highest
            return self.nn_max - 1

        info = self.tracker[self.dim_problem]

        return int(info[1])

    def update_tracker(self, num_iter):
        """Update the tracker which is used to tune the warmup steps over the algorithm."""
        if self.dim_problem not in self.tracker:
            self.tracker[self.dim_problem] = (1, num_iter)

        info = self.tracker[self.dim_problem]

        info_0 = info[0] + 1
        info_1 = info[0] * info[1] / info_0 + num_iter / info_0

        self.tracker[self.dim_problem] = (info_0, info_1)

    def _append_vector(self, idx):
        """
        Details
        -------

        We rely on the following being a valid syntax.

        >> x = np.zeros([2, 2, 2])
        >> y = np.ones([2, 2])
        >> x[0, :] = y
        """
        # pylint: disable=protected-access
        sdiag = self.vec.norm_sqrt()
        self.tridiag._elem[idx, idx + 1] = sdiag
        self.tridiag._elem[idx + 1, idx] = sdiag
        self.vec /= sdiag
        self.basis._elem[idx + 1, :] = self.vec.elem
        # pylint: enable=protected-access

    def orthogonalize(self, idx_end, idx_start=None):
        """Orthogonalize the current `vec` against the basis of `idx_end` basis vectors."""
        if self.vec.is_dtype_complex:
            # We do not want to create a copy of basis here, the biggest array
            # in terms of memory even at the cost of some more kernel calls
            self.vec.conj_update()
            overlaps = self.vec.einsum(self._einsum_ortho_a, self.basis)
            overlaps.conj_update()
            self.vec.conj_update()
        else:
            overlaps = self.vec.einsum(self._einsum_ortho_a, self.basis)

        # pylint: disable-next=protected-access
        overlaps._elem[idx_end + 1 :] = 0
        correction = overlaps.einsum(self._einsum_ortho_b, self.basis)
        self.vec.add_update(correction, factor_other=-1.0)

        return overlaps

    def solve(self):
        """Solver step executing iterations until new vector is returned."""
        # pylint: disable=protected-access

        tdiag, teigh, twhere = self.vec.get_attr("diag", "linalg.eigh", "where")

        # Warmup steps (do not solve exp to get to a predefined minimum size)
        # -------------------------------------------------------------------

        nn_warmup = self.get_nn_warmup()
        for ii in range(nn_warmup):
            # Matrix-vector multiplication interface
            self.vec = self.func(self.vec, *self.args, **self.kwargs)
            self.basis._elem[ii + 1, :] = self.vec.elem

            overlap = self.orthogonalize(ii)
            self.tridiag._elem[ii, ii] = self.real(overlap.elem[ii])

            # Append will set first off-diagonal
            self._append_vector(ii)
            self.basis._elem[ii + 1, :] = self.vec._elem

        # Actual iterations checking convergence
        # --------------------------------------

        for ii in range(nn_warmup, self.nn_max):
            # Matrix-vector multiplication interface
            self.vec = self.func(self.vec, *self.args, **self.kwargs)
            self.basis._elem[ii + 1, :] = self.vec.elem

            overlap = self.orthogonalize(ii)
            self.tridiag._elem[ii, ii] = self.real(overlap.elem[ii])

            self._append_vector(ii)
            self.basis._elem[ii + 1, :] = self.vec._elem

            mat = self.tridiag._elem[: ii + 1, : ii + 1]
            evals, evecs = teigh(mat)

            # Check on exit criteria
            if self.check_exit_criterion(ii, evecs[ii, 0]):
                break

            self.orthogonalize(ii)

        # Update tracker
        # --------------

        tmp = tdiag(self.tridiag.elem[1:, :-1])[: ii + 1]
        iter_to_conv = int(twhere(evecs[: ii + 1, 0] * tmp < self.tolerance)[0][0])
        self.update_tracker(iter_to_conv)

        # Build solution
        # --------------
        #
        # return value is expected to be list of eigenvalues
        # even in size-one
        val = [evals[0].item()]

        tensor_cls = type(self.basis)
        weights = tensor_cls(
            [self.basis.shape[0]],
            ctrl="Z",
            dtype=self.basis.dtype,
            device=self.basis.device,
        )
        weights._elem[: len(evals)] = evecs[:, 0]
        vec = self.basis.einsum(self._einsum_solve, weights)

        return val, vec
        # pylint: enable=protected-access
