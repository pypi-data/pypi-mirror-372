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
Checks for the :class`_AbstractQteaTensor` which can be inherited via
double-inheritance with a unittest.TestCase to setup unittests for
any implementation of an :class:`_AbstractQteaTensor`.
"""

# pylint: disable=too-many-instance-attributes

import abc
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

from qtealeaves.tooling import QTeaLeavesError


class _AbstractTensorChecks(abc.ABC):
    # pylint: disable=attribute-defined-outside-init
    def setup_helper(self):
        """Setup helper setting some usefule class variables."""
        self.seed = [11, 13, 17, 19]
        np.random.seed(self.seed)

        self.tensor_backend = self.get_tensor_backend()
        self.setup_tensors()

        self.tol = self.tensors_rank2[0].dtype_eps * 10

    def _setup_tensors_for_basetensors(self):
        """Provide tensor lists for base tensors where links are integers anyway."""
        self.tensors_rank2 = [
            self.tensor_backend([2, 2], ctrl="R"),
            self.tensor_backend([2, 2], ctrl="R"),
        ]
        self.tensors_rank3 = [self.tensor_backend([2, 2, 2], ctrl="R")]
        self.tensors_rank4 = [self.tensor_backend([2, 2, 2, 2], ctrl="R")]

    @abc.abstractmethod
    def get_tensor_backend(self):
        """Get the tensor backend."""

    @abc.abstractmethod
    def setup_tensors(self):
        """
        Setting up some tensor examples.

        * self.tensors_rank2 (iterable)
        * self.tensors_rank3 (iterable)
        * self.tensors_rank4 (iterable)
        """

    @abc.abstractmethod
    # pylint: disable-next=invalid-name
    def setUp(self):
        """Setup method for :class:`unittest.TestCase`."""

    # --------------------------------------------------------------------------
    #                  Common tests of _AbstractQteaTensors
    # --------------------------------------------------------------------------
    #
    # Need to escape no-member for allowing calls to assert of unittest.TestCase
    # pylint: disable=no-member

    def test_invert_link_selection(self):
        """Test if the `_invert_link_selection` works."""
        # pylint: disable=protected-access
        with self.subTest(rank=2):
            ilinks2 = self.tensors_rank2[0]._invert_link_selection([0])
            self.assertTrue(ilinks2 == [1])

        with self.subTest(rank=3):
            ilinks3 = self.tensors_rank3[0]._invert_link_selection([1])
            self.assertTrue(ilinks3 == [0, 2])

        with self.subTest(rank=4):
            ilinks4 = self.tensors_rank4[0]._invert_link_selection([1, 3])
            self.assertTrue(ilinks4 == [0, 2])
        # pylint: enable=protected-access

    def test_split_qr(self):
        """Test the QR decomposition."""
        # rank-2 tensor
        with self.subTest(rank=2):
            for i, tens in enumerate(self.tensors_rank2):
                with self.subTest(tensor=i, links_q=[0]):
                    norm = tens.norm()
                    qtens, rtens = tens.split_qr([0], [1])
                    qtens.assert_unitary([0], self.tol)
                    self.assertLess(
                        abs(norm - rtens.norm()), self.tol, msg="norm fails"
                    )

                with self.subTest(tensor=i, links_q=[0], perm=[1, 0]):
                    norm = tens.norm()
                    qtens, rtens = tens.split_qr([0], [1], perm_left=[1, 0])
                    qtens.assert_unitary([1], self.tol)
                    self.assertLess(
                        abs(norm - rtens.norm()), self.tol, msg="norm fails"
                    )

        # rank-3 tensor
        with self.subTest(rank=3):
            for i, tens in enumerate(self.tensors_rank3):
                with self.subTest(tensor=i, links_q=[0, 1]):
                    norm = tens.norm()
                    qtens, rtens = tens.split_qr([0, 1], [2])
                    qtens.assert_unitary([0, 1], self.tol)
                    self.assertLess(
                        abs(norm - rtens.norm()), self.tol, msg="norm fails"
                    )

                with self.subTest(tensor=i, links_q=[0, 2]):
                    norm = tens.norm()
                    qtens, rtens = tens.split_qr([0, 2], [1])
                    qtens.assert_unitary([0, 1], self.tol)
                    self.assertLess(
                        abs(norm - rtens.norm()), self.tol, msg="norm fails"
                    )

                with self.subTest(tensor=i, links_q=[0, 2], perm=[2, 0, 1]):
                    norm = tens.norm()
                    qtens, rtens = tens.split_qr([0, 2], [1], perm_left=[2, 0, 1])
                    qtens.assert_unitary([1, 2], self.tol)
                    self.assertLess(
                        abs(norm - rtens.norm()), self.tol, msg="norm fails"
                    )

    def test_split_svd_normal(self):
        """Test the normal svd"""
        # pylint: disable-next=protected-access
        left, _, right = self.tensors_rank2[1]._split_svd_normal(
            self.tensors_rank2[1].elem
        )
        left = self.tensor_backend.from_elem_array(left)
        right = self.tensor_backend.from_elem_array(right)

        # Check unitary on left tensor
        left.assert_unitary([1], self.tol)

        # Check unitarity on right tensor
        right.assert_unitary([0], self.tol)

    def test_split_svd_eigvl(self):
        "Test the eigenvalue svd, possibly sparse"
        # pylint: disable-next=protected-access
        _, true_singvals, _ = self.tensors_rank2[1]._split_svd_normal(
            self.tensors_rank2[1].elem
        )

        for mode in ("E", "S"):
            # pylint: disable-next=protected-access
            left, singvals, right = self.tensors_rank2[1]._split_svd_eigvl(
                self.tensors_rank2[1].elem, "E", 5, "L"
            )
            left = self.tensor_backend.from_elem_array(left)
            right = self.tensor_backend.from_elem_array(right)

            # Check unitarity on right tensor
            right.assert_unitary([0], self.tol)

            # Check if singular values are correct
            true_singvals_t = self.tensor_backend.from_elem_array(
                true_singvals[: len(singvals)], device="cpu"
            )
            singvals = self.tensor_backend.from_elem_array(singvals, device="cpu")

            self.assertTrue(
                singvals.are_equal(true_singvals_t, self.tol),
                f"Singular values are correct with {mode} svd",
            )

    def test_split_svd_random(self):
        """Test the random svd"""
        # pylint: disable-next=protected-access
        _, true_singvals, _ = self.tensors_rank2[1]._split_svd_normal(
            self.tensors_rank2[1].elem
        )
        true_singvals = self.tensor_backend.from_elem_array(
            true_singvals[:5], device="cpu"
        )

        # pylint: disable-next=protected-access
        left, singvals, right = self.tensors_rank2[1]._split_svd_random(
            self.tensors_rank2[1].elem, 5
        )
        left = self.tensor_backend.from_elem_array(left)
        right = self.tensor_backend.from_elem_array(right)

        # Check unitary on left tensor
        left.assert_unitary([1], self.tol)

        # Check unitarity on right tensor
        right.assert_unitary([0], self.tol)

        # Check if singular values are correct
        singvals = self.tensor_backend.from_elem_array(singvals, device="cpu")
        self.assertTrue(
            singvals.are_equal(true_singvals, self.tol),
            "Singular values are correct with random svd",
        )

    # pylint: enable=no-member


# pylint: disable=no-member
class _AbstractTensorMPIChecks(abc.ABC):
    """Implements unittests for MPI methods of tensors."""

    # pylint: disable-next=invalid-name
    def setUp(self):
        """Setup method for :class:`unittest.TestCase`."""
        self.setup_helper()

        # Create symbolic link to qtealeaves next to main (for whatever reason)
        main = self.get_main()
        target_dir = Path(main).parent.absolute() / "qtealeaves"
        qtealeaves_dir = Path(os.getcwd()) / "qtealeaves"
        if os.path.isdir(qtealeaves_dir):
            os.symlink(qtealeaves_dir, target_dir)
            self.remove_symlink = [target_dir]
        else:
            self.remove_symlink = []

        # Same for qredtea (again if it exists)
        target_dir = Path(main).parent.absolute() / "qredtea"
        qredtea_dir = Path(os.getcwd()) / "qredtea"
        if os.path.isdir(qredtea_dir):
            os.symlink(qredtea_dir, target_dir)
            self.remove_symlink.append(target_dir)

    # pylint: disable-next=invalid-name
    def tearDown(self):
        """Tear down method for :class:`unittest.TestCase`."""
        for elem in self.remove_symlink:
            os.remove(elem)
        self.temp_dir.cleanup()

    def setup_helper(self):
        """Setup helper will be called my unittest's `setUp()`."""
        # pylint: disable=attribute-defined-outside-init
        self.seed = [11, 13, 17, 19]
        self.mpi_command = os.environ.get("QMATCHATEA_MPI_COMMAND", "mpiexec")

        self.tensor_backend = self.get_tensor_backend()
        self.comm = self.get_mpi_comm()

        # pylint: disable-next=consider-using-with
        self.temp_dir = tempfile.TemporaryDirectory()
        self.success_file = os.path.join(self.temp_dir.name, "success.txt")
        self.tracker = os.path.join(self.temp_dir.name, "trackers")
        self.tensors_rank_3 = self.get_tensors_rank_3()

    @abc.abstractmethod
    def get_mpi_comm(self):
        """Get the MPI communicator."""

    @abc.abstractmethod
    def get_mpi_types(self):
        """Get the MPI types as dictionary."""

    @abc.abstractmethod
    def get_tensor_backend(self):
        """Get the MPI types as dictionary."""

    @abc.abstractmethod
    def get_tensors_rank_3(self):
        """List of rank-3 tensors to be tested."""

    @abc.abstractmethod
    def get_main(self):
        """Name of the main method to be called."""

    @abc.abstractmethod
    def setup_seed(self):
        """Set the seed for the libraries one needs."""

    def write_success_file(self, success_file, msg):
        """
        Write the success file.

        Arguments
        ---------

        success_file : str
            Path where file should be.

        msg : str
            Content to be written in the file.
        """
        with open(success_file, "w+", encoding="utf-8") as fh:
            fh.write(msg + "\n")

    def run_mpi(self):
        """Resolve command line arguments to call right MPI check."""
        self.setup_helper()

        if self.comm.Get_size() == 1:
            raise QTeaLeavesError("Cannot run MPI unittest with one MPI thread.")

        test = sys.argv[1]
        success_file = sys.argv[2]
        if test == "mpi_send_recv":
            self.check_mpi_send_recv(success_file)
        elif test == "mpi_bcast":
            self.check_mpi_bcast(success_file)
        else:
            raise ValueError(f"Unknown test {test=}.")

    def run_via_subprocess(self, name):
        """
        Start the MPI call via a subprocess.

        Arguments
        ---------

        name : str
            Name of the test to identity which one to run.
        """
        print(
            "suggesting folder",
            os.getcwd(),
            os.path.exists(os.getcwd() + "/qtealeaves"),
        )
        cmd = [
            self.mpi_command,
            "-n",
            "4",
            "python3",
            self.get_main(),
            name,
            str(self.success_file),
        ]

        # pylint: disable-next=subprocess-run-check
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=os.environ,
            cwd=os.getcwd(),
            timeout=180,
        )
        stderr = result.stderr
        stdout = result.stdout.strip()
        success = result.returncode == 0

        msg = "\n".join(["stderr/out not empty", stdout, stderr])
        self.assertTrue(success, msg=msg)

        msg = "\n".join(["Success file missing", " ".join(cmd), "##", stdout, stderr])
        self.assertTrue(os.path.isfile(self.success_file), msg=msg)

    def check_mpi_send_recv(self, success_file):
        """Implementation of the MPI send / recv test (called via mpiexec etc)."""
        for tensor in self.tensors_rank_3:

            if self.comm.Get_rank() == 0:
                tensor.mpi_send(1, self.comm)
            elif self.comm.Get_rank() == 1:
                tensor_received = tensor.mpi_recv(0, self.comm, self.tensor_backend)

                if not tensor.are_equal(tensor_received):
                    raise QTeaLeavesError("Tensors are not equal.")

        if self.comm.Get_rank() == 1:
            # Let the process comparing tensors write the status
            self.write_success_file(success_file, "Test finished.")

    def test_mpi_send_recv(self):
        """Test MPI send and receive of a tensor."""
        self.run_via_subprocess("mpi_send_recv")

    def check_mpi_bcast(self, success_file):
        """Implementation of the MPI broadcast test (called via mpiexec etc)."""
        for tensor in self.tensors_rank_3:

            original = tensor.copy()
            if self.comm.Get_rank() != 0:
                # Set to zero
                tensor *= 0.0

            tensor_bcast = self.tensor_backend.tensor_cls.mpi_bcast(
                tensor, self.comm, self.tensor_backend
            )

            if not tensor_bcast.are_equal(original):
                raise QTeaLeavesError("Tensors are not equal.")

        if self.comm.Get_rank() == 0:
            self.write_success_file(success_file, "Test finished.")

    def test_mpi_bcast(self):
        """Test MPI broadcasting a tensor."""
        self.run_via_subprocess("mpi_bcast")


# pylint: enable=no-member


class _AbstractBaseTensorChecks(abc.ABC):
    def setup_helper(self):
        """Setup helper will be called my unittest's `setUp()`."""
        # Disable attribute outside init for this function only
        # pylint: disable=attribute-defined-outside-init
        self.seed = [11, 13, 17, 19]

        self.device = None
        self.dtype = None
        self.tensor_cls = None
        self.base_tensor_cls = None
        self.setup_types_devices()

        self.tensors_rank2 = None
        self.tensors_rank3 = None
        self.tensors_rank4 = None
        self.setup_tensors()

        self.tol = self.tensors_rank2[0].dtype_eps * 10

    @abc.abstractmethod
    def setup_seed(self):
        """Set the seed for the libraries one needs."""

    @abc.abstractmethod
    def setup_tensors(self):
        """
        Setting up some tensor examples.

        * self.tensors_rank2 (iterable)
        * self.tensors_rank3 (iterable)
        * self.tensors_rank4 (iterable)
        """

    @abc.abstractmethod
    def setup_types_devices(self):
        """
        Setting the following

        * self.dtype
        * self.device
        * self.tensor_cls
        * self.base_tensor_cls

        """

    def test_indexing(self):
        """Test setting a submatrix with numpy-like indexing."""
        t2a = self.tensors_rank2[0]
        t2b = self.tensors_rank2[1]
        t4a = self.tensors_rank4[0]

        t4a[0, :2, :2, 0] = t2a
        t4a[1, :2, :2, 1] = t2a
        t4a[1, :2, :2, 0] = t2b
        t4a[0, :2, :2, 1] = t2b
        reference_norm = 2 * (t2a.norm() + t2b.norm())
        actual_norm = t4a.norm()
        eps = abs(reference_norm - actual_norm)
        # pylint: disable-next=no-member
        self.assertLess(eps, 10 * t2a.dtype_eps)

    def test_split_qr(self):
        """Test the decomposition via QR."""
        # Rank-2
        # pylint: disable-next=no-member
        with self.subTest(rank=2):
            for tensor in self.tensors_rank2:
                norm = tensor.norm()
                qtens, rtens = tensor.split_qr([0], [1])

                qtens.assert_unitary([0], tol=10 * self.tol)

                norm_r = rtens.norm()
                eps = abs(norm_r - norm)
                # pylint: disable-next=no-member
                self.assertLess(eps, 10 * self.tol, "Norm of R not original norm.")

        # Rank-3, two-links in Q
        # pylint: disable-next=no-member
        with self.subTest(rank=3, links_q=[0, 1]):
            for tensor in self.tensors_rank3:
                norm = tensor.norm()
                qtens, rtens = tensor.split_qr([0, 1], [2])

                qtens.assert_unitary([0, 1], tol=10 * self.tol)

                norm_r = rtens.norm()
                eps = abs(norm_r - norm)
                # pylint: disable-next=no-member
                self.assertLess(eps, 10 * self.tol, "Norm of R not original norm.")

        # Rank-3, one-link in Q
        # pylint: disable-next=no-member
        with self.subTest(rank=3, links_q=[0]):
            for tensor in self.tensors_rank3:
                norm = tensor.norm()
                qtens, rtens = tensor.split_qr([0], [1, 2])

                qtens.assert_unitary([0], tol=10 * self.tol)

                norm_r = rtens.norm()
                eps = abs(norm_r - norm)
                # pylint: disable-next=no-member
                self.assertLess(eps, 10 * self.tol, "Norm of R not original norm.")

        # Rank-3, two-links in Q and permutation
        # pylint: disable-next=no-member
        with self.subTest(rank=3, links_q=[0, 2], perm=[0, 2, 1]):
            for tensor in self.tensors_rank3:
                norm = tensor.norm()
                qtens, rtens = tensor.split_qr([0, 2], [1], perm_left=[0, 2, 1])

                qtens.assert_unitary([0, 2], tol=10 * self.tol)

                norm_r = rtens.norm()
                eps = abs(norm_r - norm)
                # pylint: disable-next=no-member
                self.assertLess(eps, 10 * self.tol, "Norm of R not original norm.")

    def test_split_rq(self):
        """Test the decomposition via RQ."""

        # Rank-2
        # pylint: disable-next=no-member
        with self.subTest(rank=2):
            for tensor in self.tensors_rank2:
                norm = tensor.norm()
                rtens, qtens = tensor.split_rq([0], [1])

                qtens.assert_unitary([1], tol=10 * self.tol)

                norm_r = rtens.norm()
                eps = abs(norm_r - norm)
                # pylint: disable-next=no-member
                self.assertLess(eps, 10 * self.tol, "Norm of R not original norm.")

        # Rank-3, two-links in Q
        # pylint: disable-next=no-member
        with self.subTest(rank=3, links_q=[1, 2]):
            for tensor in self.tensors_rank3:
                norm = tensor.norm()
                rtens, qtens = tensor.split_rq([0], [1, 2])

                qtens.assert_unitary([1, 2], tol=10 * self.tol)

                norm_r = rtens.norm()
                eps = abs(norm_r - norm)
                # pylint: disable-next=no-member
                self.assertLess(eps, 10 * self.tol, "Norm of R not original norm.")

        # Rank-3, one-link in Q
        # pylint: disable-next=no-member
        with self.subTest(rank=3, links_q=[2]):
            for tensor in self.tensors_rank3:
                norm = tensor.norm()
                rtens, qtens = tensor.split_rq([0, 1], [2])

                qtens.assert_unitary([1], tol=10 * self.tol)

                norm_r = rtens.norm()
                eps = abs(norm_r - norm)
                # pylint: disable-next=no-member
                self.assertLess(eps, 10 * self.tol, "Norm of R not original norm.")

        # Rank-3, two-links in Q and permutation
        # pylint: disable-next=no-member
        with self.subTest(rank=3, links_q=[0, 2], perm=[1, 0, 2]):
            for tensor in self.tensors_rank3:
                norm = tensor.norm()
                rtens, qtens = tensor.split_rq([1], [0, 2], perm_right=[1, 0, 2])

                qtens.assert_unitary([0, 2], tol=10 * self.tol)

                norm_r = rtens.norm()
                eps = abs(norm_r - norm)
                # pylint: disable-next=no-member
                self.assertLess(eps, 10 * self.tol, "Norm of R not original norm.")
