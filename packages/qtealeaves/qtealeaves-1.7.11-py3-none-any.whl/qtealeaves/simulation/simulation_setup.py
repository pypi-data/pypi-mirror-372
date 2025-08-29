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
The setup for a simulation with the aTTN or TTN network bringing together all
pieces, e.g., the model, and the observables.
"""

# pylint: disable=too-many-lines, too-many-locals

import hashlib
import json
import logging
import multiprocessing as mprc
import os
import os.path
import shutil
import sys
from copy import deepcopy
from pathlib import Path
from time import sleep
from warnings import warn

import numpy as np

from qtealeaves.modeling import LocalTerm
from qtealeaves.tensors import TensorBackend
from qtealeaves.tooling import QteaJsonEncoder, QTeaLeavesError
from qtealeaves.tooling.parameterized import _ParameterizedClass

from .ed_simulation import run_ed_simulation
from .tn_simulation import run_tn_simulation

__all__ = ["QuantumGreenTeaSimulation", "ATTNSimulation", "DynamicsQuench"]

logger = logging.getLogger(__name__)

PYTHON_ED_BACKENDS = [0]
PYTHON_TN_BACKENDS = [1, 2, 3, 4, 5, 6, 7, 8, 9]
PYTHON_BACKENDS = PYTHON_ED_BACKENDS + PYTHON_TN_BACKENDS


class DisentanglerPositionException(Exception):
    """
    Class of exceptions raised when aTTN disentanglers are
    placed on the invalid position. Raised within the
    `check_disentangler_position` function.
    """


# pylint: disable-next=too-many-instance-attributes
class QuantumGreenTeaSimulation(_ParameterizedClass):
    """
    Simulation class containing the model, the operators, the convergence
    settings, and the observables.

    **Arguments**

    model : instance of :class:`QuantumModel`
        Defines the model, i.e., the Hamiltonian of the system.

    operators : instance of :class:`TNOperators`
        Defines the operators used in the model and the observables.

    convergence : instance of :class:`TNConvergenceParameters`
        Specifies the convergence parameters for the simulation,
        for example the bond dimension.

    observables : instance of :class:`TNObservables`
        Defines which observables to measure in the simulation. For details,
        check the specific observable class.

    folder_name_input : str, or callable; optional
        Specifies the folder where the input is stored. Will be created
        if not existing. Path can contain subfolders and can be parametrized via
        `params` dictionary.
        Default to `input`.

    folder_name_output : str, or callable; optional
        Specifies the folder where the output is stored. Will be created
        if not existing. Path can contain subfolders and can be parametrized via
        `params` dictionary.
        Default to `output`.

    tn_type : int, optional
        Specifies which tensor network ansatz is used. The options are `5` for TTN,
        `6` for MPS, `7` for aTTN, `8` for TTOs, `9` for LPTNs. `0` is
        reserved for ED simulations.
        Default to `6`.

    py_tensor_backend : :class:`TensorBackend`
        Setup for tensor backend in python - here define which tensor class,
        device, and dtype to use. For now, has to be compatible with the
        `tensor_backend` option of simulation configuration.

    mpo_mode : int, optional
        Choosing the MPO representation inside the simulation, where
        the value `-1` enables an auto-selection (falls to iTPO).
        The other values are TPO via iTPO (`0`), iTPO (`1`), iTPO with
        update (`2`, for quenches), iTPO with compression (`3`), and sparse
        MPO (`10`, partially enabled), indexed sparse MPO (`11`, partially enabled)
        Default to `-1`.

    disentangler : None or np.ndarray, optional
        If the aTTN is used, the disentangler positions can be passed
        as a 2d numpy array with n rows and 2 columns, where n is the
        number of disentanglers. The indices must be passed as python
        indices starting from 0 in the mapped 1d system. The other option is
        to set it to None, in that case the disentangler positions are automatically
        selected if the tensor network is aTTN.
        Default to None.

    has_log_file : bool, optional
        Flag if log file should be created instead of writing
        the output to standard out. If False, all output will
        go to standard out.
        Default to False (no log file)

    store_checkpoints : bool, optional
        If True, the state will be written to a file after each
        sweep in the ground state search and after each time step
        in a time evolution. Ground state searches have the option
        to write checkpoints also after each tensor optimization,
        which the algorithm can decide on without control by the
        user. If `True`, the `delete_existing_folder` argument in
        ``QuantumGreenTeaSimulation.run()`` must be `False`.
        Default to True.

    tensor_backend : None, optional
        (Deprecated argument. Any input will be ignored.)
        Default to `None`.

    **Reserved keywords of the simulation dictionary**

    The following keywords cannot be used for adapting simulations to the
    needs by the user, but have a predefined meaning. Additional predefined
    keywords may be imported, e.g., when using a specific model or a specific
    set of operators.

    * `continue_file` : load file at the beginning of the simulation.
    * `use_mpo_from_continue_file` : bool (Python only). Use MPO stored
      in continue file.
    * `seed` : seed for random number generators.
    * `SymmetrySector`
    * `SymmetryGenerators`
    * `SymmetryTypes`
    * `Quenches`
    * `ed_sparse` : bool, use in exact state emulator to
      switch between sparse and dense Hamiltonian.
    * `sweep_order` : defines the sweep order for the statics (python only)
    * `exclude_from_hash` : dictionary entries that will be excluded from hash.
    * `num_excited_states` : number of excited states to search for.
    * `start_dynamics_from` : which state to use for the dynamics.

    **Details**

    1) Checkpoints vs continue files: checkpointing is used to restart the same
       simulation. Continue files can be used to set the input state across
       simulations, but the simulation will start always at the beginning with
       this user-provided input state.
    2) Hashing: hashes are generated to identify that a simulation setup did
       not change. For example, changes in a simulation which uses checkpoints
       can be detected this way.
    """

    # pylint: disable-next=too-many-arguments
    def __init__(
        self,
        model,
        operators,
        convergence,
        observables,
        folder_name_input="input",
        folder_name_output="output",
        file_name_input="TTN.in",
        tn_type=6,
        py_tensor_backend=TensorBackend(),
        mpo_mode=-1,
        disentangler=None,
        has_log_file=False,
        store_checkpoints=True,
        tensor_backend=None,
    ):

        if tensor_backend is not None:
            warn(
                "tensor_backend is inferred by the py_tensor_backend."
                "This parameter is deprecated and is ignored."
            )

        self.model = model
        self.operators = operators
        self.convergence = convergence
        self.observables = observables

        self.file_name_input = file_name_input
        self.folder_name_input = folder_name_input
        self.folder_name_output = folder_name_output

        self.version_input_processor = 3
        self.tn_type = tn_type
        self.mpo_mode = mpo_mode

        self.disentangler = disentangler
        self.disentangler_eval = None

        self.has_log_file = has_log_file
        self.store_checkpoints = store_checkpoints

        self.py_tensor_backend = py_tensor_backend

    @staticmethod
    def checkpoint_params_hash(params):
        """Generate hash of a simulation to identify if checkpointed simulation."""
        exclude_from_hash = params.get("exclude_from_hash", [])

        if len(exclude_from_hash) == 0:
            dict_for_hash = params
        else:
            dict_for_hash = {}
            for key, value in params.items():
                if key in exclude_from_hash:
                    continue

                dict_for_hash[key] = value

        params_str = json.dumps(dict_for_hash, sort_keys=True, cls=QteaJsonEncoder)
        return hashlib.sha256(params_str.encode("utf-8")).hexdigest()

    def get_groundstate_energy(self, params):
        """
        (DEPRECATED) Rudimentary way to extract the ground state energy via the
        convergence file.

        **Arguments**

        params : dict
            The parameter dictionary, which is required to obtain
            the output folder.

        **Details**

        Use ``get_static_obs`` in future.
        """
        warn("`get_groundstate_energy` is deprecated.")

        num_trajectories = self.observables.get_num_trajectories(params=params)
        if num_trajectories > 1:
            raise QTeaLeavesError(
                "`get_groundstate_energy` not available for quantum trajectories."
            )

        folder_name_output = self.eval_str_param(self.folder_name_output, params)
        line = None
        # pylint: disable-next=no-member
        with open(os.path.join(folder_name_output, "convergence.log"), "r") as fh:
            for line in fh:
                pass

        if line is None:
            raise QTeaLeavesError("Reading ground state energy from empty file.")

        return float(line.split()[1])

    def get_static_obs(self, params):
        """
        Return a dictionary with all observables of the static simulation,
        e.g., the ground state search. For evolutions in temperature,
        i.e., LPTNs, a list of dictionaries is returned.

        **Arguments**

        params : dict
            The parameter dictionary, which is required to obtain
            the output folder.
        """
        folder_name_output = self.eval_str_param(self.folder_name_output, params)

        tn_type = self.eval_numeric_param(self.tn_type, params)
        if tn_type in [3, 9]:
            # LPTN statics have multiple measurements in temperature
            static_obs_list = []

            max_iter = self.convergence.eval_numeric_param(
                self.convergence.max_iter, params
            )

            meas_freq = self.convergence.eval_numeric_param(
                self.convergence.measure_obs_every_n_iter, params
            )

            for ii in range(max_iter):
                if (ii + 1 != max_iter) and ((ii + 1) % meas_freq != 0):
                    # no measurement took place
                    continue

                obs_dict = self.observables.read(
                    "static_obs_%08d.dat" % (ii + 1), folder_name_output, params
                )
                static_obs_list.append(obs_dict)

            return static_obs_list

        # Simulations with one final measurement at the end of the statics
        results = self.observables.read("static_obs.dat", folder_name_output, params)

        num_excited_states = params.get("num_excited_states", 0)
        if num_excited_states > 0:
            # If we have excited states, read these as well.
            # In this case, return a list.
            results = [
                results,
            ]

            for excited_ii in range(1, params["num_excited_states"] + 1):
                excited_fname = f"static_obs_excited{excited_ii:03d}.dat"
                total_path = os.path.join(folder_name_output, excited_fname)
                if os.path.isfile(total_path):
                    # One scenario is that the job fails after finding a few,
                    # but not all excited states. We still want to be able to parse such results.
                    results.append(
                        self.observables.read(excited_fname, folder_name_output, params)
                    )

            # sort the results according to the energy
            results.sort(key=lambda x: x["energy"])

        return results

    def get_dynamic_obs(self, params):
        """
        Return dictionaries with all observables of the static simulation,
        e.g., the dynamics. You obtain a nested list, the outer list is
        iterating over the quenches; the inner list over the time steps
        of each quench.

        **Arguments**

        params : dict
            The parameter dictionary, which is required to obtain
            the output folder.

        """
        folder_name_output = self.eval_str_param(self.folder_name_output, params)

        all_results = []

        idx = 0
        for _, quench in enumerate(params["Quenches"]):
            quench_results = []
            warning_count = 0

            # According to the convention in iter_params_dts we have
            # three cases
            #
            # * dt > 0: step belonging to the time evolution
            # * dt == 0: measurement
            # * dt < 0: skipped measurement (nothing to read)
            for dt in quench.iter_params_dts(params):
                if isinstance(dt, complex):
                    # Evolution step for sure, no measurement
                    continue
                if dt > 0.0:
                    # Evolution step, no measurement
                    continue

                idx += 1

                if np.isclose(dt, 0.0):
                    # Only dt == 0 are measurements by convention - time
                    # evolution step treated with continue in 1st if-case
                    file_name = "dyn_obs%08d_%08d.dat" % (1, idx)

                    # Try to read, and warn if the file does not exist.
                    # Do not warn more than three times for each quench.
                    # Cannot test with a single `os.path.isfile` as
                    # observables might be split into trajectories.
                    try:
                        quench_results.append(
                            self.observables.read(file_name, folder_name_output, params)
                        )

                    except FileNotFoundError:
                        if warning_count < 3:
                            warn(
                                f"File {folder_name_output}/{file_name} not found. Skipping."
                            )
                        if warning_count == 3:
                            warn("Further warnings will be suppressed.")
                        warning_count += 1
                        # If the folder is missing append None
                        # instead of the result dictionary.
                        quench_results.append(None)

            all_results.append(quench_results)

        return all_results

    def extend_params(self, params):
        """
        Extend the parameters list and if the number of quantum trajectories
        is > 1, add to params the trajectory id and seed.

        **Arguments**

        params : dict or list of dicts
            The parameter dictionary or dictionaries, which is required
            to obtain the output folder.
        """
        if isinstance(params, dict):
            # convert params into a list
            params = [params]

        params_ext = []
        for elem in params:
            num_trajectories = self.observables.get_num_trajectories(params=elem)
            if num_trajectories == 1:
                params_ext.append(elem)
            else:
                for ii in range(num_trajectories):
                    tmp = deepcopy(elem)
                    tmp["trajectory_id"] = self.observables.get_id_trajectories(ii)
                    tmp["seed"] = self.observables.get_seed_trajectories(tmp)
                    params_ext.append(tmp)
        return params_ext

    def run(self, params, delete_existing_folder=False, nthreads=1):
        """
        Run a simulation or multiple simulations possibly via threading.

        **Arguments**

        params : dict or list of dicts
            The parameter dictionary or dictionaries, which is required
            to obtain the output folder.

        delete_existing_folder : bool, optional
            If flag is True, existing folder with potential results
            will be overwritten without warning. If False, an error
            is raised if the folders already exist.
            If `True`, `store_checkpoints` must be `False`.
            Default to False

        nthreads : int, optional
            If number of threads greater is one, we launch serial
            simulations. If greater than one, multiple threads
            are started to run simulations in parallel.
            Default to 1.

        **Details**

        We auto-select backends depending on the `tn_type` specified
        for the simulation.

        * Exact diagonalization
        * Python tensor network backend
        * Fortran tensor network backend

        If you run the threaded version, set the OMP_NUM_THREADS
        and MKL_NUM_THREADS (executable compiled with ifort)
        accordingly. The number of threads defined here times
        the OMP_NUM_THREADS should not exceed the number of your
        processors.

        If running the TTN time evolution, workflow is the following:

        #1 Loading the initial TTN state :
            This can be either a random TTN, or the TTN read from a
            user-set file.
        #2 Groundstate search to set the initial condition :
            There are two options - initial condition is the groundstate
            of the specified Hamiltonian, or initial condition is a TTN
            from file set by a user.
            The groundstate is found by iterative search, therefore if
            the initial condition is set by user, put `max_iter=0` in
            convergence parameters. Otherwise, set `max_iter>0`.
        #3 Perform a time evolution starting from the obtained
            initial condition.
        """
        # create a new list for the parameter to add different
        # entries in the case of quantum trajectories
        params_ext = self.extend_params(params=params)

        # Check that we don't accidentally delete the current or
        # parent directory
        if delete_existing_folder:
            for elem in params_ext:
                folder_name_input = self.observables.get_folder_trajectories(
                    self.folder_name_input, elem
                )
                folder_name_output = self.observables.get_folder_trajectories(
                    self.folder_name_output, elem
                )

                # pylint: disable-next=no-member
                current_path = Path(os.getcwd())
                # pylint: disable-next=no-member
                input_path = Path(os.path.abspath(folder_name_input))
                # pylint: disable-next=no-member
                output_path = Path(os.path.abspath(folder_name_output))

                inout_folder_danger = []
                # True if in/out folder is the same as the current folder
                inout_folder_danger.append(input_path == current_path)
                inout_folder_danger.append(output_path == current_path)
                # True if in/out folder is a parent folder of the current folder
                inout_folder_danger.append(input_path in current_path.parents)
                inout_folder_danger.append(output_path in current_path.parents)

                inout_folder_is_dangerous = any(inout_folder_danger)
                if inout_folder_is_dangerous:
                    raise ValueError(
                        "Preventing the deleting of current/parent folder. "
                        "If delete_existing_folder is True, input or output "
                        "folders cannot be set to the current folder or any "
                        "parent folder."
                    )

        # Now we have a list
        if nthreads == 1:
            for elem in params_ext:
                self.run_single(elem, delete_existing_folder=delete_existing_folder)
        else:
            self.run_threaded(
                params_ext,
                delete_existing_folder=delete_existing_folder,
                nthreads=nthreads,
            )
        return

    def status(self, params):
        """
        Returns tuple of three integers containing the number of simulations
        not started, number of simulation started but not finished, and the
        number of finished simulations.

        **Arguments**

        params : dict or list of dicts
            The parameter dictionary or dictionaries, which is required
            to obtain the output folder.
        """
        # create a new list for the parameter to add different
        # entries in the case of quantum trajectories
        params_ext = self.extend_params(params=params)

        num_unstarted = 0
        num_interrupted = 0
        num_finished = 0

        for elem in params_ext:
            folder_name_output = self.observables.get_folder_trajectories(
                self.folder_name_output, elem
            )

            finished_json = os.path.join(folder_name_output, "has_finished.json")
            if os.path.isfile(finished_json):
                num_finished += 1
                continue

            dyn_checkpoints = os.path.join(
                folder_name_output, "has_dyn_checkpoints.txt"
            )
            if os.path.isfile(dyn_checkpoints):
                # Dynamics started, but did not finish
                num_interrupted += 1
                continue

            stat_checkpoints = os.path.join(
                folder_name_output, "has_stat_checkpoints.txt"
            )
            if os.path.isfile(stat_checkpoints):
                # Statics started, but did not finish
                num_interrupted += 1
                continue

            # Did not reach first checkpoint of statics, consider it as simulation
            # which did not start yet
            num_unstarted += 1

        return num_unstarted, num_interrupted, num_finished

    # pylint: disable-next=too-many-statements, too-many-branches
    def write_input_single(self, params, delete_existing_folder):
        """
        Write the input files for a simulation.

        **Arguments**

        params : dict
            The parameter dictionary, which is required to obtain
            the output folder.

        delete_existing_folder : bool
            If flag is True, existing folder with potential results
            will be overwritten without warning. If False, an error
            is raised if the folders already exist.
            If `True`, `store_checkpoints` must be `False`.
        """
        folder_name_input = self.observables.get_folder_trajectories(
            self.folder_name_input, params
        )
        folder_name_output = self.observables.get_folder_trajectories(
            self.folder_name_output, params
        )
        sim_hash_file = os.path.join(folder_name_input, "sim_hash.json")
        tn_type = self.eval_numeric_param(self.tn_type, params)

        if self.store_checkpoints and delete_existing_folder:
            raise ValueError("Cannot delete folders and rely on checkpoints.")

        sim_hash = self.checkpoint_params_hash(params)

        # There are three options:
        #
        # * delete_existing_folder=True, store_checkpoints=False
        # * delete_existing_folder=False, store_checkpoints=False
        # * delete_existing_folder=False, store_checkpoints=True
        if delete_existing_folder:
            # Delete existing folder, checkpoints cannot be activated.

            # pylint: disable-next=no-member
            if os.path.isdir(folder_name_input):
                shutil.rmtree(folder_name_input)

            # pylint: disable-next=no-member
            if os.path.isdir(folder_name_output):
                shutil.rmtree(folder_name_output)

        elif not self.store_checkpoints:
            # No checkpoints and not deleting existing folders
            # pylint: disable-next=no-member
            if os.path.isdir(folder_name_input) or os.path.isdir(folder_name_output):
                raise ValueError(
                    "Folder exists, but neither checkpoints nor deleting activated."
                )

        # pylint: disable-next=no-member
        elif os.path.isdir(folder_name_input) and os.path.isdir(folder_name_output):
            with open(sim_hash_file, "r") as fh:
                jdic = json.load(fh)
                previous_sim_hash = jdic["sim_hash"]

            if previous_sim_hash != sim_hash:
                # This is not a simulation which is continued
                raise QTeaLeavesError(
                    "Trying to continue simulation with different params."
                )
            if tn_type in [0] + PYTHON_TN_BACKENDS:
                # python simulation can restart via `simulation.run`

                # Setup logging (output folder has been created)
                if not logger.parent.level:
                    logger.parent.setLevel(logging.INFO)
                if self.has_log_file:
                    log_file = os.path.join(folder_name_output, "sim.log")
                    logging.basicConfig(filename=log_file)
                    logging.captureWarnings(True)
                # log to console if no handler was provided
                elif not logging.getLogger(__package__).hasHandlers():
                    logging.basicConfig(stream=sys.stdout)
                return None

        # pylint: disable-next=no-member
        if os.path.isdir(folder_name_input) or os.path.isdir(folder_name_output):
            # raise error, this can only happen if user was interfering by hand
            raise ValueError("Input / output folder: one exists, one does not exist.")

        # pylint: disable-next=no-member
        if not os.path.isdir(folder_name_output):
            # pylint: disable-next=no-member
            os.makedirs(folder_name_output)
        # pylint: disable-next=no-member
        if not os.path.isdir(folder_name_input):
            # pylint: disable-next=no-member
            os.makedirs(folder_name_input)

        # Store the simulation hash
        sim_hash_jdic = {"sim_hash": sim_hash}
        with open(sim_hash_file, "w+") as fh:
            json.dump(sim_hash_jdic, fh)

        # Setup logging (after output folder has been created)
        # no further action should be required by the user in order
        # to have meaningful output, we thus set qtealeaves.simulation
        # logger to INFO level (unless already explicitly set)
        # node: python's default for the root logger is WARNING
        # note: in order for .parent to have the expected behaviour,
        # the "qtealeaves.simulation" must be registered in advance
        if not logger.parent.level:
            logger.parent.setLevel(logging.INFO)
        if self.has_log_file:
            log_file = os.path.join(folder_name_output, "sim.log")
            logging.basicConfig(filename=log_file)
            logging.captureWarnings(True)
        # log to console if no handler was provided
        elif not logging.getLogger(__package__).hasHandlers():
            logging.basicConfig(stream=sys.stdout)

        if tn_type in [1, 2, 3, 4]:
            logger.warning(
                "This is a Fortran backend. It is deprecated. The simulation switches to python"
            )

        return None

    def run_single(self, params, delete_existing_folder=False):
        """
        Run simulation specified via the parameter dictionary.

        **Arguments**

        params : dict
            The parameter dictionary, which is required to obtain
            the output folder.

        delete_existing_folder : bool, optional
            If flag is True, existing folder with potential results
            will be overwritten without warning. If False, an error
            is raised if the folders already exist.
            If `True`, `store_checkpoints` must be `False`.
            Default to False

        **Details**

        We auto-select backends depending on the `tn_type` specified
        for the simulation.

        * Exact diagonalization
        * Python tensor network backend
        """

        tn_type = self.eval_numeric_param(self.tn_type, params)
        if tn_type in [2, 7]:
            # check the positions before starting an actual simulation
            _ = self.check_disentangler_position(
                params, self.eval_numeric_param(self.disentangler, params)
            )
            # the positions are evaluated in the run_simulation itself
            # to avoid potential overwriting in running multiple simulations

        self.write_input_single(params, delete_existing_folder)

        if tn_type in PYTHON_ED_BACKENDS:
            # Run ED simulation
            run_ed_simulation(self, params)
        elif tn_type in PYTHON_TN_BACKENDS:
            # Run pyTN simulation (TTN or MPS)
            run_tn_simulation(self, params)
        else:
            raise ValueError(f"Unknown backend {tn_type=}.")

        return

    def run_threaded(self, params, delete_existing_folder=False, nthreads=4):
        """
        Run simulation specified via the parameter dictionary.

        **Arguments**

        params : list
            List of the parameter dictionaries, which is required to obtain
            the output folder.

        delete_existing_folder : bool, optional
            If flag is True, existing folder with potential results
            will be overwritten without warning. If False, an error
            is raised if the folders already exist.
            If `True`, `store_checkpoints` must be `False`.
            Default to False

        nthreads : int, optional
            Number of threads to start multiple simulations in
            parallel.
            Default to 4.
        """
        if nthreads == 1:
            # Route back to serial code ...
            self.run(
                params, delete_existing_folder=delete_existing_folder, nthreads=nthreads
            )
            return

        # number of threads should not exceed length of parameter list
        nthreads = min(nthreads, len(params))

        # Fill list with the first nthreads simulations
        job_list = []
        for ii in range(nthreads):
            next_args = (self, params[ii], delete_existing_folder)
            next_simulation = mprc.Process(target=_run_single_thread, args=next_args)

            next_simulation.start()
            job_list.append(next_simulation)

        # Replace jobs whenever one finishes ...
        next_check = -1
        ii = nthreads
        while ii < len(params):
            for jj in range(nthreads):
                next_check += 1
                if next_check == nthreads:
                    next_check = 0

                if not job_list[next_check].is_alive():
                    next_args = (self, params[ii], delete_existing_folder)
                    next_simulation = mprc.Process(
                        target=_run_single_thread, args=next_args
                    )

                    next_simulation.start()
                    job_list[next_check] = next_simulation
                    ii += 1

                    break

                if jj + 1 == nthreads:
                    # None of the jobs was finished; wait for 10s
                    sleep(10)

        # All jobs launched ... now order does not matter for join
        for ii in range(nthreads):
            job_list[ii].join()

        return

    def autoselect_disentangler(self, params):
        """
        Given a number of sites and Hamiltonian, the function
        automatically chooses the positions for aTTN disentanglers.

        The function iterates through all possible pairs and puts the disentanglers
        according to the following:
        - we prioritize the disentanglers which support the links of the highest
        bond dimension, i.e. the ones in the highest layers
        - we place disentanglers to a position only if it fully lays on the MPO term
        (this has proved to be a successful tactics)
        - we skip DE positions which violate the restrictions in
        `check_disentangler_position()` function
        - we skip DE positions which connect the links whose dimensions cannot
        grow more than maximal bond dimension (lower layers of the tree)

        Parameters
        ----------
        params : dict
            Dictionary with the simulation parameters.

        Return
        ------
        auto_dis : np.array
            Disentangler positions.
        """
        # Total number of sites in the system
        ll_1d_mapped = self.model.get_number_of_sites(params)
        lattice_size = self.model.eval_lvals(params)
        bond_dim = self.eval_numeric_param(
            self.convergence.sim_params["max_bond_dimension"], params
        )
        local_dim = int(self.operators.get_local_links(ll_1d_mapped, params)[0])
        # The array in which the DE positions will be added
        auto_dis = []

        # for checking if there is an interaction term at the DE
        interactions = []
        for term in self.model.hterms:
            if not isinstance(term, LocalTerm):
                all_interactions = term.get_interactions(lattice_size, params)
                for single_interaction in all_interactions:
                    interactions.append(single_interaction[1])

        # we iterate over all the site pairs to find the best DE positions

        # to support the highest bond dim links, first loop over pairs at
        # different halves, then quarters, etc.
        sites_in_group = ll_1d_mapped // 2
        # loop until we reach the smallest division
        # pylint: disable-next=too-many-nested-blocks
        for _ in range(int(np.log2(ll_1d_mapped)) - 1):
            # no disentangler needed if maximal possible dimension of
            # connecting link is smaller than the bond_dim
            max_dim = local_dim**sites_in_group
            if max_dim < bond_dim:
                break

            # how many groups we have for a certain division. For example, if
            # the division is in quarters, there will be 4 groups.
            num_groups = ll_1d_mapped // sites_in_group

            for group in range(0, num_groups, 2):
                # We iterate over combinations of pairs where first and second site
                # belong to different groups

                # Priority is given to the disentanglers connected to the sites
                # which are physically closer, i.e. cover more entanglement.
                for ii in range(sites_in_group - 1, -1, -1):
                    for jj in range(sites_in_group):
                        # find the indices of sites within the first and second group
                        site1 = group * sites_in_group + ii
                        site2 = (group + 1) * sites_in_group + jj

                        # these are the indices of the sites of new potential disentangler
                        de_position = [site1, site2]

                        # check if disentangler lays fully on an interaction term
                        count = 0
                        for interaction in interactions:
                            if all(de_site in interaction for de_site in de_position):
                                count += 1
                        # if not, skip this term
                        if count < 1:
                            continue

                        # append the new disentangler to the disentangler list
                        # and keep it only if it is on a valid position
                        auto_dis.append(de_position)
                        try:
                            _ = self.check_disentangler_position(params, auto_dis)
                        except DisentanglerPositionException:
                            auto_dis.pop()
            sites_in_group = sites_in_group // 2

        return np.array(auto_dis)

    # pylint: disable-next=too-many-statements, too-many-branches
    def check_disentangler_position(self, params, disentangler_pos):
        """
        This function checks if the input disentangler positions are valid
        and returns them. If the input positions are None, returns
        the autoselected ones.

        Arguments
        ---------
        params: dict
            Dictionary with the simulation parameters.
        disentangler_pos : list/array or None
            Disentangler positions. If list/array, each row
            represents one disentangler. If None, the positions are
            autoselected based on the Hamiltonian.

        Return
        ------
        disentangler_pos : list/array
            Disentangler positions - if input was None then
            returns the autoselected positions, if input was list
            then returns the array version which is needed for
            aTTN algorithms. Otherwise returns the input disentangler
            positions.
        """
        if disentangler_pos is None:
            disentangler_pos = self.autoselect_disentangler(params)
            return disentangler_pos

        ll_1d_mapped = self.model.get_number_of_sites(params)
        lattice_size = self.model.eval_lvals(params)

        if not isinstance(disentangler_pos, np.ndarray):
            # if list, convert to array
            if isinstance(disentangler_pos, list):
                disentangler_pos = np.array(disentangler_pos)
            else:
                raise DisentanglerPositionException(
                    "Disentangler positions must be a list or a numpy array, not "
                    f"{type(disentangler_pos)}."
                )

        if len(disentangler_pos.shape) != 2:
            raise DisentanglerPositionException(
                "Disentangler positions must be rank-2, but has a shape "
                f"{disentangler_pos.shape}."
            )

        if disentangler_pos.shape[1] != 2:
            raise DisentanglerPositionException(
                "Disentangler positions must be 2 columns, but has a shape "
                f"{disentangler_pos.shape}."
            )

        if np.min(disentangler_pos) < 0:
            raise DisentanglerPositionException(
                "All disentangler positions must be greater than -1."
            )

        if np.max(disentangler_pos) >= ll_1d_mapped:
            raise DisentanglerPositionException(
                "All disentangler positions must be smaller than system size."
            )

        if any(
            (np.min(dis) % 2 == 0) and (np.max(dis) - np.min(dis) == 1)
            for dis in disentangler_pos
        ):
            raise DisentanglerPositionException(
                "Disentangler cannot be attached to only one tensor."
            )

        if any(dis[0] == dis[1] for dis in disentangler_pos):
            raise DisentanglerPositionException(
                "Disentangler cannot be placed on only one site."
            )

        # Check if MPO is connected to different disentanglers:

        # Create array with num_sites elements, assign each disentangler a value
        # and put these values to the corresponding disentangler positions.
        # The values are 1,2,3, ..., num_disentangler
        lattice_array = np.zeros(ll_1d_mapped, dtype=int)
        ind_count = 1
        for dis in disentangler_pos:
            if any(lattice_array[dis] > 0):
                raise DisentanglerPositionException(
                    "A single physical link cannot have more than one"
                    " disentangler attached to it."
                )
            lattice_array[dis] += ind_count
            ind_count += 1

        # Iterate through interaction terms within Hamiltonian and check if
        # two-body interaction MPO is connected to two different disentanglers.
        # We check if MPO is connected to different disentanglers by checking
        # the values on lattice_array on these sites - from the definition of
        # lattice_array above, there are two different disentanglers if the
        # lattice sites have a different value>0

        # pylint: disable-next=too-many-nested-blocks
        for term in self.model.hterms:
            if not isinstance(term, LocalTerm):
                all_interactions = term.get_interactions(lattice_size, params)
                for single_interaction in all_interactions:
                    # single_interaction[1] contains the 1d coordinates of each
                    # two-body term on the lattice
                    one_term = lattice_array[single_interaction[1]]
                    if len(np.unique(one_term[one_term > 0])) > 1:
                        raise DisentanglerPositionException(
                            f"MPO on sites {single_interaction[1]} connected to "
                            "different disentanglers."
                        )

                    # If there are no multiple disentanglers on a single interaction
                    # term, check also for the cases when disentangler position yields
                    # a 4-link MPO, which creates an error on fortran side. No
                    # further loop over the disentanglers is necessary due to this
                    # fact!
                    # disentanglers on 4-body terms are the candidates
                    if len(one_term) > 3 and np.count_nonzero(one_term) >= 1:
                        # reorder the sites in interaction term
                        order = np.argsort(single_interaction[1])
                        one_term = one_term[order]
                        single_int = np.array(single_interaction[1])[order]

                        # index of disentangler in `one_term`
                        term_dis_ind = np.nonzero(one_term)[0]
                        # index of the disentangler in `disentangler_pos`
                        ind = np.unique(one_term[term_dis_ind])[0] - 1
                        # access the position of that disentangler in TTN
                        dis = disentangler_pos[ind]

                        # One can show that the 4-link MPO will appear if MPO sites
                        # on one side of the disentangler are in both L and R environment.

                        # We check this by defining the array `env` of size of the 1D mapped lattice
                        # we will fill it with different values according to whether they
                        # belong to the left or right environment: if the site
                        # belongs to left environment, the value is 2 and if it belongs to
                        # right environment, the value is 3.

                        # this part of the code finds the position of L and R
                        # environment
                        div = int(ll_1d_mapped / 2)
                        while dis[0] // div == dis[1] // div:
                            div = int(div / 2)
                        # cut is the most left site in the right environment area
                        cut = (dis[1] // div) * div

                        # mark the regions of different environments with
                        # different values
                        env = (
                            np.ones(ll_1d_mapped, dtype=int) * 2
                        )  # first initialize all as L
                        env[cut : cut + div] = 3  # the section of R
                        # (the reason for such separation is the positioning of the anchor
                        # point in the algorithm)

                        # The disentangler is on a valid position only if it does
                        # not divide the left or right environment into two pieces.

                        # In terms of this check, the above criterion is satisfied
                        # only if the sites in the `env`` array on the left and
                        # right of the disentangler surely belong to L and R, i.e.
                        # when abs(env[left site] - env[right site]) = 1 [from the values
                        # of `env` array in the code above].

                        # take only the part of `env` where the interaction term is, i.e.,
                        # convert something like 00022330000 for the whole lattice to
                        # 0223 for the site of the MPO.
                        env_term = env[single_int]

                        # iterate over the disentangler sites of one disentangler which are
                        # on this term.
                        for de_ind in term_dis_ind:
                            # flag if in bulk with respect to whole MPO (not left /
                            # right environment).
                            disentangler_in_bulk = de_ind not in (0, len(env_term) - 1)

                            # If not in bulk with respect to the whole MPO, it must
                            # be valid (also on the edge of left/right environment)
                            if not disentangler_in_bulk:
                                continue

                            # Now we have for sure a disentangler site in the bulk
                            # Does it cut any possible left/right environment into two?
                            # The sequences like 0223 are only one iff we are at the
                            # boundary between 2 and 3 which is a valid position.
                            if abs(env_term[de_ind - 1] - env_term[de_ind + 1]) != 1:
                                raise DisentanglerPositionException(
                                    "Disentangler configuration resulting in a 4-linkID MPO"
                                )

        return disentangler_pos


class ATTNSimulation(QuantumGreenTeaSimulation):
    """
    For backwards compatibility.
    """

    def __init__(self, *args, **kwargs):
        warn("Deprecated ATTNSimulation; switch to QuantumGreenTeaSimulation.")

        version_input_processor = kwargs.get("version_input_processor", None)
        if version_input_processor is not None:
            warn("Deprecated argument input processor.")
            del kwargs["version_input_processor"]

        super().__init__(*args, **kwargs)

        if version_input_processor is not None:
            self.version_input_processor = version_input_processor


def _run_single_thread(obj, params, delete_existing_folder):
    """
    Internal function to launch a single thread of a threaded simulation.

    **Arguments**

    obj : instance of :class:``ATTNSimulation``.
        Simulation class to be run.

    params : dict
        The parameter dictionary, which is required to obtain
        the output folder.

    delete_existing_folder : bool, optional
        If flag is True, existing folder with potential results
        will be overwritten without warning. If False, an error
        is raised if the folders already exist.
        If `True`, `store_checkpoints` must be `False`.
        Default to False
    """
    obj.run_single(params, delete_existing_folder=delete_existing_folder)
    return


class DynamicsQuench(dict):
    """
    Describing a quench of parameters for the dynamics part of
    a TN simulation. The parameters must be defined as a function
    taking the time and the simulation dictionary as arguments.

    **Arguments**

    dt_grid : numpy.ndarray, str, callable
        Contains the list of time steps, which can differ. Moreover,
        it can be parameterized and be a callable or string.

    time_evolution_mode : int, optional
        Defines the time evolution mode.
        0 : automatic selector
            (Defaults to 1 for tensor networks.
            For exact diagonalization,
            defaults to 10 for systems smaller than 10 sites and 11 for others.)
        1 : one-tensor TDVP
        2 : two-tensor TDVP
        3 : two-tensor TDVP (2nd order)
        4 : single-tensor TDVP (2nd order)
        5 : 9 steps of one-site and one step of two-site TDVP
        10 : exact diagonalization with full Hamiltonian matrix generated
        11 : exact diagonalization with Krylov
        Not every network type might support all time evolution modes.
        Default to 0.

    measurement_period : int, str, callable, optional
        Allows to define a measurement period every n time steps. It
        considers only the time steps, not the time passed. There
        is always a measurement at the end of the quench.
        Default to 1.

    oqs_mode : int, optional
        Controls the open quantum system evolution, where no open
        quantum is 0, quantum trajectories with jumps is 1,
        quantum trajectories with norm only is 2, and density matrix
        evolution (Lindblad master eq.) is 3.
        Default to 0.

    check_superfluous : bool, optional
        If ``True``, a warning is raised whenever a dictionary key is
        not in the required parameters.
        Default to True

    **Details**

    Open systems implement the Lindblad equation as

    .. math::

        \\frac{d}{dt} \\rho = -i [H, \\rho]
             + \\sum \\gamma (L \\rho L^{\\dagger}
             - \\frac{1}{2} \\{ L^{\\dagger} L, \\rho \\})

    Complex time evolution is enabled if you pass the time step as complex dt
    in the native python data `complex` to the dt-grid. Negative imaginary part
    will lead to cooling, positive imaginary part results in heating and raises
    a warning. Complex time evolution cannot be combined with open quantum systems.
    The state will be automatically renormalized.
    """

    # pylint: disable-next=too-many-arguments
    def __init__(
        self,
        dt_grid,
        time_evolution_mode=0,
        measurement_period=1,
        oqs_mode=0,
        check_superfluous=True,
    ):
        super().__init__()
        self.dt_grid = dt_grid
        self.time_evolution_mode = time_evolution_mode
        self.measurement_period = measurement_period
        self.oqs_mode = oqs_mode
        self.check_superfluous = check_superfluous

    def __len__(self):
        """
        Overload length, now defined via number of time steps.
        """
        if isinstance(self.dt_grid, str) or hasattr(self.dt_grid, "__call__"):
            raise QTeaLeavesError("Cannot support length for non-ndarray.")

        return len(self.dt_grid)

    def get_length(self, params):
        """
        Calculate the length of the time grid even for parameterized
        grids.

        **Arguments**

        params : dict
            The parameter dictionary, which will be passed to callables
            and used to evaluate string parameters.
        """
        dt_grid = self.eval_numeric_param(self.dt_grid, params)
        return len(dt_grid)

    def get_dt_grid(self, params):
        """
        Evaluate the dt grid and return it.

        **Arguments**

        params : dict
            The parameter dictionary, which will be passed to callables
            and used to evaluate string parameters.
        """
        return self.eval_numeric_param(self.dt_grid, params)

    def eval_numeric_param(self, elem, params):
        """
        Evaluate a numeric parameter which might be defined via the
        parameter dictionary.

        **Arguments**

        elem : callable, string, or int/float
            Defines the parameter either via a function which return
            the value, a string being an entry in the parameter
            dictionary, or directly as the numeric value.

        params : dict
            The parameter dictionary, which will be passed to callables
            and used to evaluate string parameters.
        """
        if isinstance(elem, list):
            return [self.eval_numeric_param(subelem, params) for subelem in elem]

        if hasattr(elem, "__call__"):
            val = elem(params)
        elif isinstance(elem, str):
            val = params[elem]
        else:
            val = elem

        return val

    def iter_params(self, required_params, params, time_at_start=0.0):
        """
        Iterate over the all time steps and the required parameters
        within. Function returns the time-dependent parameters
        evaluated at mid-timestep. Moreover, we return the
        time-dependent parameters at the end of each time step
        to allow for measurements.

        **Arguments**

        required_params : OrderedDict
            Keys are the required parameters, values are the
            default values if no function is present.

        params : dict
            Simulation parameter dictionary.

        time_at_start : float, optional
            Time at the beginning of the quench, which allows
            to take into account previous quenches.
            Default to 0.0
        """
        dt_grid = self.eval_numeric_param(self.dt_grid, params)
        tnow = time_at_start

        if self.check_superfluous:
            for key in self:
                if key not in required_params:
                    warn("Detected superfluous function `%s` in quench." % (key))

        for dt_ii in dt_grid:
            tmid = tnow + 0.5 * dt_ii

            for key in required_params.keys():
                if key in self:
                    yield self[key](tmid, params)
                else:
                    yield required_params[key]

            tnow += dt_ii

            for key in required_params.keys():
                if key in self:
                    yield self[key](tnow, params)
                else:
                    yield required_params[key]

    def iter_params_dts(self, params):
        """
        Iterate over parameters's time steps. Coupling with a time-step dt
        greater than zero, are intended for the time evolution. Every second
        parameter is 0 or -99 and indicating the values are at the end point
        for the measurements, i.e., doing measurements (zero) or doing
        no measurement (-99), respectively. Up to now, no other values
        less or equal to zero are associated with some special meaning.

        **Arguments**

        params : dict
            Simulation parameter dictionary.
        """
        dt_grid = self.eval_numeric_param(self.dt_grid, params)
        meas_period = self.eval_numeric_param(self.measurement_period, params)

        for ii, dt in enumerate(dt_grid[:-1]):
            yield dt

            if ((ii + 1) % meas_period) == 0:
                yield 0.0
            else:
                yield -99.0

        yield dt_grid[-1]
        yield 0.0

    def iter_dts(self):
        """
        Generator yielding all the time steps dt within
        this quench. It returns the delta, not the current
        time in total.
        """
        if isinstance(self.dt_grid, str) or hasattr(self.dt_grid, "__call__"):
            raise QTeaLeavesError("Cannot support iter_dts for non-ndarray.")

        yield from self.dt_grid
