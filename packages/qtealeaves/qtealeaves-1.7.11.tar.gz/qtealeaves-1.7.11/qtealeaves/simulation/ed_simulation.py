# This code is part of qtealeaves.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

# pylint: disable=too-many-branches
# pylint: disable=too-many-statements

"""
The module contains a light-weight execution of an exact state simulation.
"""
import os

# pylint: disable-next=no-member, no-name-in-module
import os.path
from copy import deepcopy

import numpy as np
import scipy.linalg as sla

from qtealeaves.tensors import TensorBackend
from qtealeaves.tooling import QTeaLeavesError

from ..emulator.state_simulator import StateVector
from ..emulator.ttn_simulator import TTN
from ..solvers.krylovexp_solver import KrylovSolverH

__all__ = ["run_ed_simulation"]


# pylint: disable-next=too-many-locals
def run_ed_simulation(simulation, params):
    """
    Run a full simulation with the exact state vector.

    **Arguments**

    simulation : instance of ``ATTNSimulation``
        Represents all the information on the simulation.

    params : dict
        Dictionary containing the current parameters for the
        simulation.
    """

    # Statics
    # -------

    # Collect some information
    lvals = simulation.model.eval_lvals(params)
    num_sites = np.prod(lvals)
    local_dim = simulation.operators.get_local_links(num_sites, params)

    # Get Hamiltonian
    ham = simulation.model.build_ham(simulation.operators, params)

    # If `continue_file` is present, use it to initialize the state
    if params.get("continue_file", "") != "":
        extension = params["continue_file"][-4:]
        if extension != ".npy":
            raise TypeError(
                "The initial state for ED must be in .npy array form. "
                f"Current form is {extension}."
            )
        state = np.load(params["continue_file"])
        if len(state) != int(np.prod(local_dim)):
            raise ValueError(
                f"The number of entries in the inital state array "
                f"({len(state)}) does not correspond "
                "to the Hilbert space size ."
            )
        state = StateVector(num_sites, local_dim, state)
    else:
        state = StateVector.from_groundstate(ham, num_sites, local_dim)

    # Measurements
    folder_name_output = simulation.observables.get_folder_trajectories(
        simulation.folder_name_output, params
    )
    # pylint: disable-next=no-member
    full_file_path = os.path.join(folder_name_output, "static_obs.dat")

    observables = run_ed_measurements(state, ham, simulation, params)
    observables.write_results(full_file_path, params, state_ansatz="STATE")

    # Dynamics
    # --------

    quench_list = params["Quenches"] if ("Quenches" in params) else []

    # convert the dtype of the initial state to complex
    if len(quench_list) > 0:
        state.state = state.state.astype(np.complex128)

    time_now = 0.0
    idx = 0
    for ii, quench in enumerate(quench_list):
        time_evolution_mode = quench.time_evolution_mode
        if time_evolution_mode not in [0, 10, 11]:
            raise QTeaLeavesError(
                f"""Exact diagonalisation requires
                time_evolution_mode 0, 10 or 11, got {time_evolution_mode}."""
            )
        # automatic time_evolution_mode selection depending on the system size
        if time_evolution_mode == 0:
            if num_sites < 10:
                time_evolution_mode = 10
            else:
                time_evolution_mode = 11

        for dt in quench.iter_params_dts(params):
            if dt > 0.0:
                # Time step
                time_mid = time_now + 0.5 * dt

                params_tt = deepcopy(params)
                for key, func in quench.items():
                    params_tt[key] = func(time_mid, params)

                # by default construct the full H matrix
                if time_evolution_mode == 10:
                    ham = simulation.model.build_ham(simulation.operators, params_tt)

                    propagator = sla.expm(-1j * dt * ham)
                    state.apply_global_operator(propagator)

                # or do the Krylov expansion
                elif time_evolution_mode == 11:
                    # update the state
                    state = KrylovSolverH(
                        vec0=state,
                        prefactor=-1j * dt,
                        matvec_func=simulation.model.apply_ham_to_state,
                        conv_params=simulation.convergence,
                        args_func=[simulation.operators, params_tt],
                    ).solve()

                # Increase evolution time and index
                time_now += dt
                idx += 1

            elif np.isclose(dt, 0.0):
                # Measurement
                params_tt = deepcopy(params)
                for key, func in quench.items():
                    params_tt[key] = func(time_now, params)

                ham = simulation.model.build_ham(simulation.operators, params_tt)

                postfix = "_%08d_%08d" % (ii, idx)
                observables = run_ed_measurements(
                    state, ham, simulation, params, postfix=postfix, time=time_now
                )

                file_name = "dyn_obs%08d_%08d.dat" % (1, idx)
                # pylint: disable-next=no-member
                full_file_path = os.path.join(folder_name_output, file_name)
                observables.write_results(full_file_path, params, state_ansatz="STATE")

            else:
                # Skipped measurement
                pass

    return


# pylint: disable-next=too-many-locals, too-many-arguments
def run_ed_measurements(state, ham, simulation, params, postfix=None, time=None):
    """
    Run all the measurements for a state.

    **Arguments**

    state : instance of StateVector
        State to be measured.

    ham : numpy ndarray
        Contains the Hamiltonian defined on the full Hilbert space.

    simulation : instance of ``ATTNSimulation``
        Represents all the information on the simulation.

    params : dict
        Dictionary containing the current parameters for the
        simulation.

    postfix : str or ``None``, optional
        Postfix to be attached to filename etc. If ``None``, no
        postfix is attached.
        Default to empty string via ``None``.

    time : float or ``None``, optional
        The current time during the evolution if float. If a
        time cannot be specified, e.g., for statics, pass
        ``None`` or do not pass argument.
        Default to ``None``.

    **Returns**

    Instance of ``TNObservables``. If we run in parallel, we better
    make a copy before using the buffer of the TNObservables.
    """
    # We probably need params in the future - avoid unused argument error
    _ = len(params)

    if postfix is None:
        postfix = ""

    observables = deepcopy(simulation.observables)

    observables.results_buffer["energy"] = state.meas_global_operator(ham)
    observables.results_buffer["norm"] = state.norm()
    if time is not None:
        observables.results_buffer["time"] = time

    # Local observables
    # -----------------

    local_obs = observables.obs_list["TNObsLocal"]

    for jj, name_jj in enumerate(local_obs.name):
        site_vector = []

        for ii in range(state.num_sites):
            operator = simulation.operators[(ii, local_obs.operator[jj])]
            rho_i = state.reduced_rho_i(ii)
            site_vector.append(np.real(np.trace(rho_i.dot(operator))))

        local_obs.results_buffer[name_jj] = site_vector

    # Correlation measurements
    # ------------------------

    corr_obs = observables.obs_list["TNObsCorr"]

    for kk, name_kk in enumerate(corr_obs.name):
        corr_mat = np.zeros((state.num_sites, state.num_sites), dtype=np.complex128)

        for ii in range(state.num_sites):
            op_ai = simulation.operators[(ii, corr_obs.operators[kk][0])]
            op_bi = simulation.operators[(ii, corr_obs.operators[kk][1])]
            op_ab = np.dot(op_ai, op_bi)

            rho_i = state.reduced_rho_i(ii)
            corr_mat[ii, ii] = np.trace(np.dot(op_ab, rho_i))

            for jj in range(ii + 1, state.num_sites):
                op_aj = simulation.operators[(jj, corr_obs.operators[kk][0])]
                op_bj = simulation.operators[(jj, corr_obs.operators[kk][1])]
                op_axb = np.kron(op_ai, op_bj)
                op_bxa = np.kron(op_bi, op_aj)

                rho_ij = state.reduced_rho_ij(ii, jj)

                corr_mat[ii, jj] = np.trace(np.dot(op_axb, rho_ij))
                corr_mat[jj, ii] = np.trace(np.dot(op_bxa, rho_ij))

        corr_obs.results_buffer[name_kk] = corr_mat

    # Distance measurement (TNDistance2Pure)
    # --------------------

    dist_obs = observables.obs_list["TNDistance2Pure"]

    for jj, name_jj in enumerate(dist_obs.name):
        path_jj = dist_obs.path_to_state[jj]

        psi_ttn = TTN.read(path_jj, TensorBackend())
        psi_vec = psi_ttn.to_statevector()

        dist_obs.results_buffer[name_jj] = state.dot(psi_vec)

    # State2File measurement
    # ----------------------
    #
    # we will store numpy arrays now independent of the flag

    file_obs = observables.obs_list["TNState2File"]

    for jj, name_jj in enumerate(file_obs.name):
        full_name = name_jj + postfix + ".npy"
        np.save(full_name, state.state)

        file_obs.results_buffer[name_jj] = full_name

    return observables
