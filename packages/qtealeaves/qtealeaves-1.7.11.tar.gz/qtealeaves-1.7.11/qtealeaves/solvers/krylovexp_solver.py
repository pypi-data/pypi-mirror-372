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
The module contains solvers for the Krylov exponential as an API (multiplication
matrix-vector are passed as function, vector class needs only a few attributes).

**Attributes needed for vector class**

* `norm`
* `dot` for inner product between two vectors.
* `add_update(self, other, factor_self, factor_other)
* `__itruediv__`
* `__imul__`
"""

# pylint: disable=dangerous-default-value
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments

import logging
from collections import namedtuple
from copy import deepcopy

import numpy as np
import scipy.sparse.linalg as ssla

from .abstract_solver import _AbstractSolver

__all__ = ["KrylovSolverH", "KrylovSolverNH"]

logger = logging.getLogger(__name__)

"""Holds convergence information for a Krylov solver run."""
KrylovInfo = namedtuple("KrylovInfo", ("converged", "num_iter", "precision_fom"))


class KrylovSolverH(_AbstractSolver):
    """
    Krylov solver for exponential of hermitian matrix.

    **Arguments**

    vec0 : vector to apply exponential matrix to.

    prefactor : prefactor scalar in exponential

    matvec_func : callable, multiplies matrix in exponential with vector.

    conv_params : instance of TNConvergenceParameters.

    args_func : list, arguments for matvec_func

    kwargs_func : dict, keyword arguments for matvec_func
    """

    def __init__(
        self, vec0, prefactor, matvec_func, conv_params, args_func=[], kwargs_func={}
    ):
        super().__init__(vec0, matvec_func, conv_params, args_func, kwargs_func)

        self.prefactor = prefactor

        self.nn_max = conv_params.krylov_maxiter
        # with respect to how many basis vectors do we re-orthogonalize
        if conv_params.solver_reorthogonalize is None:
            self.reorthogonalize = self.nn_max
        else:
            self.reorthogonalize = conv_params.solver_reorthogonalize
        self.tolerance = conv_params.krylov_tol

        self.init_basis()

    def init_basis(self):
        """Initialize the basis and create diagonal / subdiagonal entries."""
        self.diag = np.zeros(self.nn_max)
        self.sdiag = np.zeros(self.nn_max)
        self.sdiag_0 = self.vec.norm_sqrt()

        self.vec /= self.sdiag_0
        self.basis.append(deepcopy(self.vec))

    def solve(self):
        """Sovler step executing iterations until new vector is returned."""
        converged = False
        for ii in range(self.nn_max):
            nn = ii + 1

            # Matrix-vector multiplication interface
            self.vec = self.func(self.vec, *self.args, **self.kwargs)

            diag_native = self.basis[ii].dot(self.vec)
            self.diag[ii] = np.real(diag_native)
            # reorthogonalize with respect to last two explicitly
            self.vec.add_update(self.basis[ii], factor_other=-self.diag[ii])
            self.vec.add_update(
                self.basis[ii - 1], factor_other=-self.basis[ii - 1].dot(self.vec)
            )
            # Reorthogonalize with respect to last 'self.reorthogonalize' basis vectors,
            # excluding last two which were done in previous lines
            idx_start = (ii + 1) - min(ii + 1, self.reorthogonalize)
            self.orthogonalize(ii - 2, idx_start=idx_start)

            self.sdiag[ii] = self.vec.norm_sqrt()
            krylov_exp_mat = np.zeros((ii + 1, ii + 1))
            krylov_exp_mat += np.diag(self.diag[: ii + 1])

            for jj in range(ii):
                krylov_exp_mat[jj, jj + 1] = self.sdiag[jj]
                krylov_exp_mat[jj + 1, jj] = self.sdiag[jj].conj()

            krylov_exp_mat = ssla.expm(self.prefactor * krylov_exp_mat)

            precision_fom = abs(2.0 * self.sdiag[ii] * krylov_exp_mat[ii, 0])
            if precision_fom < self.tolerance:
                converged = True
                logger.info(
                    "KrylovSolverH converged in %d steps with %.1e", nn, precision_fom
                )
                break

            self.vec /= self.sdiag[ii]
            self.basis.append(deepcopy(self.vec))

        else:
            logger.warning("KrylovSolverH stopped at max_iter with %.1e", precision_fom)

        # Calculate solution
        self.vec = deepcopy(self.basis[0])
        self.vec *= krylov_exp_mat[0, 0]

        for jj in range(1, nn):
            self.vec.add_update(self.basis[jj], factor_other=krylov_exp_mat[jj, 0])

        self.vec *= self.sdiag_0
        return self.vec, KrylovInfo(converged, nn, precision_fom)


class KrylovSolverNH(_AbstractSolver):
    """
    Krylov solver for exponential of non-hermitian matrix.

    **Arguments**

    vec0 : vector to apply exponential matrix to.

    prefactor : prefactor scalar in exponential

    matvec_func : callable, multiplies matrix in exponential with vector.

    args_func : list, arguments for matvec_func

    kwargs_func : dict, keyword arguments for matvec_func
    """

    def __init__(
        self, vec0, prefactor, matvec_func, conv_params, args_func=[], kwargs_func={}
    ):
        super().__init__(vec0, matvec_func, conv_params, args_func, kwargs_func)

        self.prefactor = prefactor

        self.nn_max = conv_params.krylov_maxiter
        self.tolerance = conv_params.krylov_tol

        self.init_basis()

    @property
    def nn_max(self):
        """Property of the maximum Krylov vectors."""
        return self._nn_max

    @nn_max.setter
    def nn_max(self, value):
        """
        Setter for the maximum number of Krylov vectors considering the
        dimension of the problem.
        """
        # Non-hermitian solver has a corner-case for one iteration with
        # a zero matrix [[0]]; unittest says we need at least two iterations
        self._nn_max = min(max(2, self.dim_problem), value)

    def init_basis(self):
        """Initialize the basis and create diagonal / subdiagonal entries."""
        dim = self.nn_max
        self.hessenberg = np.zeros((dim, dim), dtype=np.complex128)
        self.norm0 = self.vec.norm_sqrt()

        self.vec /= self.norm0

        self.basis.append(self.vec.copy())

    def solve(self):
        """Solver step executing iterations until new vector is returned."""
        converged = False
        for ii in range(self.nn_max):
            nn = ii + 1

            # Matrix-vector multiplication interface
            self.vec = self.func(self.vec, *self.args, **self.kwargs)

            # Iteration after matrix-vector multiplication
            for jj in range(ii):
                self.hessenberg[jj, ii] = self.vec.dot(self.basis[jj])
                self.hessenberg[jj, ii] = self.basis[jj].dot(self.vec)
                self.vec.add_update(
                    self.basis[jj], factor_other=-self.hessenberg[jj, ii]
                )

            norm = self.vec.norm_sqrt()
            if ii + 1 < self.nn_max:
                self.hessenberg[ii + 1, ii] = norm

            if ii == 0:
                # It is just a 1x1 matrix with entry zero, thus exp(0) = 1
                krylov_exp_mat = np.ones((1, 1))
            else:
                krylov_exp_mat = ssla.expm(
                    self.prefactor * self.hessenberg[: ii + 1, : ii + 1]
                )

            precision_fom = abs(2.0 * norm * krylov_exp_mat[0, 0])

            if precision_fom < self.tolerance:
                converged = True
                logger.info(
                    "KrylovSolverNH converged in %d steps with %f", nn, precision_fom
                )
                break

            self.vec /= norm
            self.basis.append(self.vec.copy())

        else:
            logger.warning("KrylovSolverNH stopped at max_iter with %f", precision_fom)

        # Calculate solution
        vec = self.basis[0]
        vec *= self.norm0 * krylov_exp_mat[0, 0]

        for jj in range(1, nn):
            factor = self.norm0 * krylov_exp_mat[jj, 0]
            vec.add_update(self.basis[jj], factor_other=factor)

        return vec, KrylovInfo(converged, nn, precision_fom)
