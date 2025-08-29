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
Implement unittest for TN-ML as abstract class.
"""

# pylint: disable=too-many-instance-attributes

# All the assertX of the unittest class will run into linter checks otherwise
# pylint: disable=no-member

import abc
import contextlib
import os
import os.path
import tempfile

import numpy as np

from qtealeaves.convergence_parameters import TNConvergenceParameters
from qtealeaves.tooling import QTeaBackendError


def feature_map_func_0(mat):
    """Feature map for state |0> for sine-cosine feature map."""
    return np.cos(np.pi / 2 * mat)


def feature_map_func_1(mat):
    """Feature map for state |1> for sine-cosine feature map."""
    return np.sin(np.pi / 2 * mat)


def cosine_sine_feature_map(mat):
    """
    Feature map for sine-cosine feature map.

    Parameters
    ----------
    mat : np.ndarray
        Input matrix.

    Returns
    -------
    np.ndarray :
        Array where each feature is mapped to a vector,
        $$\\cos(\\pi / 2 \\cdot mat), \\sin(\\pi / 2 \\cdot mat)$$.
        The output has shape (..., 2).
    """

    cos = np.cos(np.pi * mat / 2)
    sin = np.sin(np.pi * mat / 2)

    assert np.allclose(cos**2 + sin**2, np.ones_like(cos))
    return np.stack([cos, sin], axis=-1)


# pylint: disable-next=too-many-public-methods
class _AbstractTNMLChecks(abc.ABC):
    """
    The abstract class for tensor network machine learning can be doubel-inherited
    together with a unittest.TestCase to test the machine learing of an ansatz.
    """

    # pylint: disable-next=invalid-name
    def setUp(self):
        """setUp method to be provided for unittest.TestCase."""
        np.random.seed([11, 13, 17, 19])

        self.ansatz = self._set_ansatz()
        self.tensor_backend = self._set_tensor_backend()

        # pylint: disable-next=consider-using-with
        self.temp_dir = tempfile.TemporaryDirectory()
        self.in_folder = os.path.join(self.temp_dir.name, "INPUT")
        self.out_folder = os.path.join(self.temp_dir.name, "OUTPUT")

        # Data set
        self.ml_data_mpo_cls = self._set_ml_data_mpo_cls()
        self.train_mpo = None
        self.valid_mpo = None
        self._stripe_data_set()

        # Convergence parameters
        self.conv_params = TNConvergenceParameters(
            max_bond_dimension=self.default_max_bond_dimension(),
            statics_method=2,
            max_iter=self.default_max_iter(),
            data_type="S",
            n_points_conv_check=4,
        )

        # Machine learning settings
        self.learning_rate = 1

    @abc.abstractmethod
    def _set_tensor_backend(self):
        """Define the tensor backend including data types, device, etc."""

    @abc.abstractmethod
    def _set_ml_data_mpo_cls(self):
        """Set the MLDataMPO class which is not necessarily accessible from here."""

    @abc.abstractmethod
    def _set_ansatz(self):
        """Set the tensor network class"""

    def default_max_bond_dimension(self):
        """Default bond dimension for convergence parameters."""
        return 8

    def default_max_iter(self):
        """Default number of iterations / sweeps for convergence parameters."""
        return 6

    def set_all_bond_dimensions(self, chi):
        """Set all the bond dimensions, i.e., max bond dimension and ini bond dimension."""
        self.conv_params.sim_params["max_bond_dimension"] = chi
        self.conv_params.ini_bond_dimension = chi

    def _stripe_data_set(self, nx=4, ny=4, num_samples=50):
        """Generate a data set with one horizontal or vertical stripe."""
        noise_level = 0.1
        data = noise_level * np.random.rand(2 * num_samples, nx, ny)
        labels = np.array(np.random.rand(2 * num_samples) < 0.5, dtype=int)

        for ii, label in enumerate(labels):
            # Generate one stripe
            if label == 0:
                data[ii, :, np.random.randint(0, ny)] = 0.5 + 0.5 * np.random.rand()
            else:
                data[ii, np.random.randint(0, nx), :] = 0.5 + 0.5 * np.random.rand()

        data = data.reshape([2 * num_samples, nx * ny])
        train_data = data[:num_samples, :]
        valid_data = data[num_samples:, :]

        train_labels = labels[:num_samples]
        valid_labels = labels[num_samples:]

        self.mpo_train = self.ml_data_mpo_cls.from_matrix(
            train_data,
            train_labels,
            num_samples // 2,
            self.tensor_backend,
            cosine_sine_feature_map,
        )

        self.mpo_valid = self.ml_data_mpo_cls.from_matrix(
            valid_data,
            valid_labels,
            num_samples // 2,
            self.tensor_backend,
            cosine_sine_feature_map,
        )

    # pylint: disable-next=invalid-name
    def tearDown(self):
        """
        Remove input and output folders again
        """
        self.temp_dir.cleanup()

        return

    def get_initial_guess(self, has_trivial_label_link=False, has_env_label_link=False):
        """Generate the initial guess for the ansatz."""
        classificator = self.ansatz.ml_initial_guess(
            self.conv_params,
            self.tensor_backend,
            "random",
            self.mpo_train,
            None,
            has_trivial_label_link=has_trivial_label_link,
            has_env_label_link=has_env_label_link,
        )

        return classificator

    def check_accuracy(self, classificator):
        """Calculate the accuracy of training and test data and assert 90% accuracy."""
        acc_train = self.mpo_train.get_accuracy(classificator)
        acc_valid = self.mpo_valid.get_accuracy(classificator)

        self.assertLess(1 - acc_train, 0.1, f"Bad training {acc_train=}.")
        self.assertLess(1 - acc_valid, 0.1, f"Bad validation {acc_valid=}.")

    def check_labellink(self, classificator, has_label_link):
        """
        Check the optimization of the one tensor with TN-ML approach for gradient
        and overlaps.
        """
        tensor = classificator[classificator.iso_center]
        if has_label_link:
            self.assertEqual(
                tensor.ndim, 4, "Expected label link and iso center rank-4."
            )
        else:
            self.assertEqual(
                tensor.ndim, 3, "Expected no label link and iso center rank-3."
            )

    def test_1site_linkfree(self):
        """
        Check the optimization of the one tensor with TN-ML approach for gradient
        and overlaps (no decompositions).
        """
        self.conv_params.sim_params["statics_method"] = 1
        classificator = self.get_initial_guess(has_trivial_label_link=True)
        _, _ = classificator.ml_optimize(
            self.mpo_train,
            self.learning_rate,
            "linkfree",
        )

        self.check_accuracy(classificator)
        self.check_labellink(classificator, False)

    def test_1site_linkfree_isofree(self):
        """
        Check the optimization of the one tensor with TN-ML approach for gradient
        and overlaps (no decompositions).
        """
        # A bit high on the iterations (unitary is difficult to optimize?)
        self.conv_params.sim_params["statics_method"] = 1
        self.conv_params.max_iter = 30
        classificator = self.get_initial_guess(has_trivial_label_link=True)

        classificator = self.get_initial_guess(has_trivial_label_link=True)
        _, _ = classificator.ml_optimize(
            self.mpo_train,
            self.learning_rate,
            "linkfree_isofree",
        )

        self.check_accuracy(classificator)
        self.check_labellink(classificator, False)

    def test_1site_labellink(self):  # DONE
        """
        Check the optimization of the one tensor with TN-ML approach for gradient
        and label link.
        """
        self.conv_params.sim_params["statics_method"] = 1
        classificator = self.get_initial_guess()
        _, _ = classificator.ml_optimize(
            self.mpo_train,
            self.learning_rate,
            "labellink",
        )

        self.check_accuracy(classificator)
        self.check_labellink(classificator, True)

    def test_1site_labellink_back(self):
        """
        Check the optimization of the one tensor with back propagation
        and label link.
        """
        if self.tensor_backend([1]).linear_algebra_library in ["numpy-cupy"]:
            # Checks that the right error is raised
            context = contextlib.suppress(QTeaBackendError)
        else:
            context = contextlib.nullcontext()

        with context:
            self.conv_params.sim_params["statics_method"] = 1
            classificator = self.get_initial_guess()
            _, _ = classificator.ml_optimize(
                self.mpo_train,
                self.learning_rate,
                "labellink_back",
            )

            self.check_accuracy(classificator)
            self.check_labellink(classificator, True)

    def future_1site_labelenv_back(self):
        """
        Check the optimization of the one tensor with back propagation
        and label link in the environment.
        """
        if self.tensor_backend([1]).linear_algebra_library in ["numpy-cupy"]:
            # Checks that the right error is raised
            context = contextlib.suppress(QTeaBackendError)
        else:
            context = contextlib.nullcontext()

        with context:
            self.conv_params.sim_params["statics_method"] = 1
            classificator = self.get_initial_guess(has_env_label_link=True)
            _, _ = classificator.ml_optimize(
                self.mpo_train,
                self.learning_rate,
                "labelenv_back",
            )

            self.check_accuracy(classificator)
            self.check_labellink(classificator, False)

    def future_1site_labelenv_back_isofree(self):
        """
        Check the optimization of the one tensor with back propagation
        and label link in the environment (no decompositions).
        """
        if self.tensor_backend([1]).linear_algebra_library in ["numpy-cupy"]:
            # Checks that the right error is raised
            context = contextlib.suppress(QTeaBackendError)
        else:
            context = contextlib.nullcontext()

        with context:
            self.conv_params.sim_params["statics_method"] = 1
            classificator = self.get_initial_guess(has_env_label_link=True)
            _, _ = classificator.ml_optimize(
                self.mpo_train,
                self.learning_rate,
                "labelenv_back_isofree",
            )

            self.check_accuracy(classificator)
            self.check_labellink(classificator, False)

    # def test_2site_linkfree_isofree(self):
    # Not possible, 2-site algorithms need an SVD to split the tensor.

    def test_2site_linkfree(self):
        """
        Check the optimization of the two tensors with TN-ML approach for gradient
        and overlap.
        """
        classificator = self.get_initial_guess(has_trivial_label_link=True)
        _, _ = classificator.ml_optimize(self.mpo_train, self.learning_rate, "linkfree")

        self.check_accuracy(classificator)
        self.check_labellink(classificator, False)

    def test_2site_labellink(self):
        """
        Check the optimization of the two tensors with TN-ML approach for gradient
        and label link.
        """
        classificator = self.get_initial_guess()
        _, _ = classificator.ml_optimize(
            self.mpo_train,
            self.learning_rate,
            "labellink",
        )

        self.check_accuracy(classificator)
        self.check_labellink(classificator, True)

    def test_2site_labellink_conj(self):
        """
        Check the optimization of the two tensors with TN-ML approach for
        conjugate gradient and label link.
        """
        classificator = self.get_initial_guess()
        _, _ = classificator.ml_optimize(
            self.mpo_train,
            self.learning_rate,
            "labellink_conj",
        )

        self.check_accuracy(classificator)
        self.check_labellink(classificator, True)

    def test_2site_labellink_back(self):
        """
        Check the optimization of the two tensors with back propagation
        and label link.
        """
        if self.tensor_backend([1]).linear_algebra_library in ["numpy-cupy"]:
            # Checks that the right error is raised
            context = contextlib.suppress(QTeaBackendError)
        else:
            context = contextlib.nullcontext()

        with context:
            classificator = self.get_initial_guess()
            _, _ = classificator.ml_optimize(
                self.mpo_train,
                self.learning_rate,
                "labellink_back",
            )

            self.check_accuracy(classificator)
            self.check_labellink(classificator, True)

    def future_2site_labelenv_back(self):
        """
        Check the optimization of the two tensors with back propagation
        and label link in the environment.
        """
        if self.tensor_backend([1]).linear_algebra_library in ["numpy-cupy"]:
            # Checks that the right error is raised
            context = contextlib.suppress(QTeaBackendError)
        else:
            context = contextlib.nullcontext()

        with context:
            classificator = self.get_initial_guess(has_env_label_link=True)
            _, _ = classificator.ml_optimize(
                self.mpo_train,
                self.learning_rate,
                "labelenv_back",
            )

            self.check_accuracy(classificator)
            self.check_labellink(classificator, False)

    def future_2site_labelenv_back_isofree(self):
        """
        Check the optimization of the two tensors with back propagation
        and label link in the environment (no decompositions).
        """
        if self.tensor_backend([1]).linear_algebra_library in ["numpy-cupy"]:
            # Checks that the right error is raised
            context = contextlib.suppress(QTeaBackendError)
        else:
            context = contextlib.nullcontext()

        with context:
            classificator = self.get_initial_guess(has_env_label_link=True)
            _, _ = classificator.ml_optimize(
                self.mpo_train,
                self.learning_rate,
                "labelenv_back_isofree",
            )

            self.check_accuracy(classificator)
            self.check_labellink(classificator, False)

    def future_full_tn_labelenv(self):
        """Check the optimization of the full TN with back propagation."""
        self.conv_params.max_iter = 30
        if self.tensor_backend([1]).linear_algebra_library in ["numpy-cupy"]:
            # Checks that the right error is raised
            context = contextlib.suppress(QTeaBackendError)
        else:
            context = contextlib.nullcontext()

        with context:
            classificator = self.get_initial_guess(has_env_label_link=True)
            _, _ = classificator.ml_optimize(
                self.mpo_train,
                self.learning_rate,
                "labelenv_back_fulltn",
            )

            self.check_accuracy(classificator)
            self.check_labellink(classificator, False)
