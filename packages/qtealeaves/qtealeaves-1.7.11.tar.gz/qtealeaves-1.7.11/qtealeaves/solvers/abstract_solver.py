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
Abstract solver class implementing common methods of iterative solvers.
"""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-instance-attributes

import abc
import logging

import numpy as np

from qtealeaves.tooling import QTeaLeavesError

logger = logging.getLogger(__name__)


class _AbstractSolver(abc.ABC):
    """
    Iterative solvers act based on a generalized matrix-vector multiplication and
    build a Krylov space.

    Arguments
    ---------

    vec0 : :class:`_AbstractQteaTensor` or similar
        vector to apply exponential matrix to / initial guess. Tensors
        are considered in a flattened shape to consider them as vectors.
        (Other allowed classes need to provide a minimal set of class
        methods).

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
    """

    def __init__(self, vec0, matvec_func, conv_params, args_func, kwargs_func):
        self.vec = vec0
        self.conv_params = conv_params
        self.func = matvec_func
        self.args = [] if args_func is None else args_func
        self.kwargs = {} if kwargs_func is None else kwargs_func

        self.dim_problem = np.prod(vec0.shape)
        self._nn_max = self.dim_problem

        self.dtype_eps = vec0.dtype_eps
        self._tolerance = 0.0
        self.basis = []

        # Allows to inject functions used for some solver, to be set manually
        # in their __init__
        self.injected_funcs = {}

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
        self._nn_max = min(self.dim_problem, value)

    @property
    def tolerance(self):
        """Property of the target tolerance."""
        return self._tolerance

    @tolerance.setter
    def tolerance(self, value):
        """
        Setter for the tolerance considering the machine precision of the
        underlying tensor.
        """
        if 0 < value < self.vec.dtype_eps:
            logger.warning(
                "Non-zero Solver tolerance is smaller than machine precision. Resetting."
            )
            self._tolerance = self.dtype_eps
        else:
            # If tolerance == 0, then enforce max iterations ...
            # Or new tolerance bigger than machine precision
            self._tolerance = value

    @abc.abstractmethod
    def init_basis(self):
        """
        Initialize the basis and create auxiliary data structures to build
        the matrix solved in the Krylov space.
        """

    def assert_normalization(self):
        """Assert the normalization of the current vector."""
        value = self.vec.norm_sqrt()
        eps = abs(1 - value)
        if (eps > 1e3 * self.dtype_eps) and (not self.conv_params.data_type_switch):
            raise QTeaLeavesError(
                f"Expecting normalized vector, but {eps} for tolerance {self.tolerance}."
            )
        if eps > 10 * self.dtype_eps:
            logger.warning(
                "Expecting normalized vector, but %2.14f for tolerance %2.14f.",
                eps,
                self.tolerance,
            )

    def real(self, obj):
        """Supporting taking the real part of complex number via attribute or injected function."""
        if "real" in self.injected_funcs:
            return self.injected_funcs["real"](obj)

        return obj.real

    def abs(self, obj):
        """Supporting taking the absolute value of any number via attribute or injected function."""
        if "abs" in self.injected_funcs:
            return self.injected_funcs["abs"](obj)

        if hasattr(obj, "abs"):
            return obj.abs()

        tabs = self.vec.get_attr("abs")
        return tabs(obj)

    def orthogonalize(self, idx_end, idx_start=0):
        """Orthogonalize the current `vec` against the basis from `idx_start` to `idx_end`
        basis vectors."""
        for ket in self.basis[idx_start : idx_end + 1]:
            overlap = ket.dot(self.vec)
            if self.abs(overlap) > min(self.dtype_eps, self.tolerance):
                self.vec.add_update(ket, factor_other=-overlap)
