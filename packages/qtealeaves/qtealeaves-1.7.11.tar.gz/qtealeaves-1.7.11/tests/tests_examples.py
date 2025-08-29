# This code is part of qtealeaves.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import io
import os
import tempfile
import unittest
import warnings
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np

from Examples.BoseHubbard_1d_groundstate import main as bose_hubbard1d
from Examples.BoseHubbard_2d_quench import main as bose_hubbard2d_quench
from Examples.Models_by_interaction_list import main as models_by_interaction_list
from Examples.QuantumIsing_1d_groundstate import main as qising1dgs
from Examples.QuantumIsing_1d_quench import main as qising1d_quench
from Examples.QuantumIsing_2d_groundstate import main as qising2dgs
from Examples.QuantumIsing_2d_groundstate import main as qising2dgs_th
from Examples.QuantumIsing_2d_quench import main as qising2d_quench

# from Examples.Logging_setup import main as logging # Logging not tested because he imports from the Examples folder
# from Examples.Parallel_Sampling import main as parallel_sampling # MPI required, not on build server
from Examples.QUBO_Solver import main as qubo_solver
from Examples.RydbergRb87_3d_groundstate import main as rydberg
from Examples.Simple_classification import main as simple_classification
from Examples.Singletfission_1d_quench import main as singletfission
from Examples.SpinGlass_1d_groundstate import main as spinglass
from Examples.XXZModel_1d_oqs import main as xxz_open

warnings.filterwarnings("ignore")


class TestExamples(unittest.TestCase):
    """Test that all the examples works correctly"""

    def setUp(self):
        """Define 'global' variables"""
        # Set seed
        np.random.seed(123)

        self.temp_dir = tempfile.TemporaryDirectory()
        self.in_folder = os.path.join(self.temp_dir.name, "INPUT")
        self.out_folder = os.path.join(self.temp_dir.name, "OUTPUT")
        self.io_string = io.StringIO()

    def tearDown(self):
        self.temp_dir.cleanup()
        return

    def test_check_completeness(self):
        """
        Test whether all the example from the Examples folder have been included in the unittest
        """

        this_path = Path(os.path.abspath(__file__))
        examples_path = this_path.parent.parent.absolute() / "Examples"
        whitelist = [
            "QuantumIsing_2d_groundstate_threaded.py",  # skipping due to threading
            "Parallel_Sampling.py",  # skipping due to MPI requirement
            "Logging_setup.py",  # skipping due to import of another example
        ]
        no_missing = True
        missing_list = []

        for file in examples_path.rglob("*.py"):
            with open(os.path.abspath(__file__), "r") as current_file:
                found = False
                for line in current_file:
                    if line.startswith("from Examples." + file.stem):
                        found = True
                        break
                if file.name in whitelist:
                    pass
                elif not found:
                    no_missing = False
                    missing_list.append(file.name)

        self.assertTrue(
            no_missing,
            "Missing unittest for the following examples files: " + str(missing_list),
        )

    def test_bose_hubbard1d(self):
        """
        Test the bose_hubbard1d example
        """
        with redirect_stdout(self.io_string):
            bose_hubbard1d(
                input_folder=self.in_folder,
                output_folder=self.out_folder,
                statics_method=1,
            )

    def test_bose_hubbard2d_quench(self):
        """
        Test the bose_hubbard2d_quench example
        """
        with redirect_stdout(self.io_string):
            bose_hubbard2d_quench(
                input_folder=self.in_folder, output_folder=self.out_folder, timesteps=10
            )

    # This test is commented since the example import another example
    # -> not working in this setup
    # def test_logging(self):
    #    """
    #    Test the logging example
    #    """
    #    if os.path.isdir(self.data_dir):
    #        rmtree(self.data_dir)
    #    self.io_string = io.StringIO()
    #    with redirect_stdout(self.io_string):
    #        logging()

    # This test is commented because it requires MPI
    # def test_parallel_sampling(self):
    #    """
    #    Test the parallel_sampling example
    #    """
    #    if os.path.isdir(self.data_dir):
    #        rmtree(self.data_dir)
    #    self.io_string = io.StringIO()
    #    with redirect_stdout(self.io_string):
    #        parallel_sampling()

    def test_qubo_solver(self):
        """
        Test the qubo_solver example
        """
        with redirect_stdout(self.io_string):
            qubo_solver(
                n_instances=3,
                input_folder=self.in_folder,
                output_folder=self.out_folder,
            )

    def test_qising1dgs(self):
        """
        Test the qising1dgs example
        """
        with redirect_stdout(self.io_string):
            qising1dgs(
                input_folder=self.in_folder,
                output_folder=self.out_folder,
                statics_method=1,
            )

    def test_qising1d_quench(self):
        """
        Test the qising1d_quench example
        """
        with redirect_stdout(self.io_string):
            qising1d_quench(
                input_folder=self.in_folder,
                output_folder=self.out_folder,
                timesteps=10,
                plot=False,
            )

    def test_models_by_interaction_list(self):
        """
        Test the models_by_interaction_list example.
        """
        with redirect_stdout(self.io_string):
            models_by_interaction_list(
                input_folder=self.in_folder, output_folder=self.out_folder
            )

    def test_qising2dgs(self):
        """
        Test the qising2dgs example
        """
        with redirect_stdout(self.io_string):
            qising2dgs(input_folder=self.in_folder, output_folder=self.out_folder)

    def test_qising2dgs_th(self):
        """
        Test the qising2dgs_th example
        """
        with redirect_stdout(self.io_string):
            qising2dgs_th(input_folder=self.in_folder, output_folder=self.out_folder)

    def test_qising2d_quench(self):
        """
        Test the qising2d_quench example
        """
        with redirect_stdout(self.io_string):
            qising2d_quench(
                input_folder=self.in_folder, output_folder=self.out_folder, timesteps=10
            )

    def test_rydberg(self):
        """
        Test the rydberg example
        """
        with redirect_stdout(self.io_string):
            rydberg(input_folder=self.in_folder, output_folder=self.out_folder)

    def test_simple_classification(self):
        """
        Test the simple_classification example
        """
        with redirect_stdout(self.io_string):
            simple_classification()

    def test_spinglass(self):
        """
        Test the spinglass example
        """
        with redirect_stdout(self.io_string):
            spinglass(
                input_folder=self.in_folder, output_folder=self.out_folder, plot=False
            )

    def test_xxz_open(self):
        """
        Test the bond_dimension example
        """
        with redirect_stdout(self.io_string):
            xxz_open(
                input_folder=self.in_folder, output_folder=self.out_folder, plot=False
            )

    def test_singlet_fission(self):
        """
        Test the singlet fission example
        """
        with redirect_stdout(self.io_string):
            singletfission(
                input_folder=self.in_folder,
                output_folder=self.out_folder,
                plot=False,
                timesteps=10,
            )
