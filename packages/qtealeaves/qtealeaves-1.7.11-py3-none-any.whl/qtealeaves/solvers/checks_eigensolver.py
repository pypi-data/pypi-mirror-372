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
Implement unittest for eigensolvers as abstract class.
"""

# pylint: disable=too-many-locals

import abc
import os
import tempfile

import numpy as np

from .eigen_solver import DenseTensorEigenSolverH, EigenSolverH


class _AbstractEigenSolverChecks(abc.ABC):
    """
    Abstract checks; with double-inheritence with `unittest.TestCase`, they
    act as unittests.
    """

    def get_device(self):
        """Return the string for the device, by default CPU if not overwritten."""
        return "cpu"

    @abc.abstractmethod
    def get_convergence_parameters_cls(self):
        """
        Return class for convergence parameters (avoid any problems with
        cyclic imports).
        """

    @abc.abstractmethod
    def get_tensor_backend_double_real(self):
        """Return the tensor backend for real double precision tensors."""

    @abc.abstractmethod
    def get_tensor_backend_double_complex(self):
        """Return the tensor backend for real double precision tensors."""

    # pylint: disable-next=invalid-name
    def setUp(self):
        """
        Provide some default settings.
        """
        np.random.seed([11, 13, 17, 19])

        self.conv = self.get_convergence_parameters_cls()(
            max_bond_dimension=1, cut_ratio=1e-16, max_iter=10
        )

        # pylint: disable-next=consider-using-with
        self.temp_dir = tempfile.TemporaryDirectory()
        self.in_folder = os.path.join(self.temp_dir.name, "INPUT")
        self.out_folder = os.path.join(self.temp_dir.name, "OUTPUT")

    # pylint: disable-next=invalid-name
    def tearDown(self):
        """
        Remove input and output folders again
        """
        self.temp_dir.cleanup()

        return

    # --------------------------------------------------------------------------
    #                                 Direct tests on eigensolver
    # --------------------------------------------------------------------------

    def base_eigensolver_h(self, solver_cls, tensor_backend):
        """Base routine for testing an eigensolver class with any (dense) backend."""
        mat = tensor_backend([16, 16], ctrl="R")
        mat_t = mat.conj().transpose([1, 0])
        mat += mat_t

        teigh, tabs, tsum = mat.get_attr("linalg.eigh", "abs", "sum")
        evals, evecs = teigh(mat.elem)

        vec = tensor_backend([16], ctrl="R")
        vec.normalize()

        def matvec_func(vec, mat):
            return mat.tensordot(vec, ([1], [0]))

        tabs, treal = vec.get_attr("abs", "real")
        injected_funcs = {"abs": tabs}
        if mat.linear_algebra_library == "tensorflow":
            injected_funcs["real"] = treal

        solver = solver_cls(
            vec, matvec_func, self.conv, args_func=[mat], injected_funcs=injected_funcs
        )
        e_val, e_vec = solver.solve()

        eps_val = tabs(e_val[0] - evals[0])

        tol = 100 * mat.dtype_eps

        # pylint: disable-next=no-member
        self.assertLess(
            eps_val, tol, msg="Eigenvalue not within tolerance for EigenSolverH."
        )

        eps_overlap = tabs(1 - tabs(tsum(e_vec.conj().elem * evecs[:, 0])))

        # Have to test via overlap because complex vectors have a degree of freedom
        # in the phase
        # pylint: disable-next=no-member
        self.assertLess(
            eps_overlap, tol, msg="Eigenvector not within tolerance for EigenSolverH."
        )

    def test_eigensolver_h_real(self):
        """Test eigensolver for float64."""
        solver_cls = EigenSolverH
        tensor_backend = self.get_tensor_backend_double_real()
        self.base_eigensolver_h(solver_cls, tensor_backend)

    def test_eigensolver_h_complex(self):
        """Test eigensolver for double complex."""
        solver_cls = EigenSolverH
        tensor_backend = self.get_tensor_backend_double_complex()
        self.base_eigensolver_h(solver_cls, tensor_backend)

    def test_densetensor_eigensolver_h_real(self):
        """Test eigensolver for dense tensors and float64."""
        tensor_backend = self.get_tensor_backend_double_real()
        solver_cls = DenseTensorEigenSolverH
        self.base_eigensolver_h(solver_cls, tensor_backend)

    def test_densetensor_eigensolver_h_complex(self):
        """Test eigensolver for dense tensors and double complex."""
        tensor_backend = self.get_tensor_backend_double_complex()
        solver_cls = DenseTensorEigenSolverH
        self.base_eigensolver_h(solver_cls, tensor_backend)
