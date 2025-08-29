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
The module contains a light-weight execution of a tensor network simulations for:

- MPS
- TTN
- aTTN

"""

# pylint: disable=too-many-locals
# pylint: disable=too-many-lines
# pylint: disable=too-many-arguments
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements

import json

# pylint: disable-next=no-member, no-name-in-module
import logging
import os
import os.path
from copy import deepcopy
from time import time as tictoc
from warnings import warn

import numpy as np

import qtealeaves.mpos
from qtealeaves.abstracttns.abstract_tn import _AbstractTN
from qtealeaves.convergence_parameters import TNConvergenceParametersFiniteT
from qtealeaves.emulator.attn_simulator import ATTN
from qtealeaves.emulator.lptn_simulator import LPTN
from qtealeaves.emulator.mps_simulator import MPS
from qtealeaves.emulator.ttn_simulator import TTN
from qtealeaves.emulator.tto_simulator import TTO
from qtealeaves.mpos import ITPO, DenseMPO, DenseMPOList, MPOSite, SparseMPO
from qtealeaves.solvers import KrylovSolverH, KrylovSolverNH
from qtealeaves.tensors import TensorBackend
from qtealeaves.tooling import QTeaLeavesError

__all__ = ["run_tn_simulation", "update_time_dependent_terms", "optimize"]

logger = logging.getLogger(__name__)

TN_TYPE = {1: TTN, 2: ATTN, 3: LPTN, 4: MPS, 5: TTN, 6: MPS, 7: ATTN, 8: TTO, 9: LPTN}
TN_TYPE_LABEL = {
    1: "TTN",
    2: "ATTN",
    3: "LPTN",
    4: "MPS",
    5: "TTN",
    6: "MPS",
    7: "ATTN",
    8: "TTO",
    9: "LPTN",
}

AVAIL_DTYPES = {
    "A": np.complex128,
    "Z": np.complex128,
    "C": np.complex64,
    "D": np.float64,
    "S": np.float32,
    "H": np.float16,  # Problems with eigensolver, mixed-precision for linalg
}

# Store intrasweep checkpoints beyond 24 h / sweep (time in sec)
QTEA_TIMELIMIT_INTRASWEEP_CHECKPOINTS = int(
    os.environ.get("QTEA_TIMELIMIT_INTRASWEEP_CHECKPOINTS", 3600 * 24)
)


# pylint: disable-next=dangerous-default-value
def logger_warning(*args, storage=[]):
    """Workaround to display warnings only once in logger."""
    if args in storage:
        return

    storage.append(args)
    logger.warning(*args)


def run_tn_simulation(simulation, params):
    """
    Run a full simulation with the python tensor network.

    **Arguments**

    simulation : instance of ``ATTNSimulation``
        Represents all the information on the simulation.

    params : dict
        Dictionary containing the current parameters for the
        simulation.
    """
    tic = tictoc()
    seed = params.get("seed", [11, 13, 17, 19])
    sim_hash = simulation.checkpoint_params_hash(params)

    # Collect some information
    lvals = simulation.model.eval_lvals(params)
    num_sites = np.prod(lvals)
    folder_name_input = simulation.observables.get_folder_trajectories(
        simulation.folder_name_input, params
    )
    folder_name_output = simulation.observables.get_folder_trajectories(
        simulation.folder_name_output, params
    )

    # This is the only one going actually to standard out
    logger.info("Starting simulation %s", folder_name_input)

    # Tensor types for simulation
    if not isinstance(simulation.py_tensor_backend, TensorBackend):
        # tensor backend class has call attribute which conflicts with eval_numeric_param
        tensor_backend = deepcopy(
            simulation.eval_numeric_param(simulation.py_tensor_backend, params)
        )
    else:
        tensor_backend = simulation.py_tensor_backend
    tensor_backend.set_seed(seed)

    tensor_cls = tensor_backend.tensor_cls
    base_tensor_cls = tensor_backend.base_tensor_cls

    conv_params_init = simulation.convergence.resolve_params_copy(params, idx=0)
    # remove learning rate to avoid problems with pickling state
    conv_params_init.de_opt_learning_rate_strategy = None

    device = conv_params_init.sim_params["device"]
    if ("+" in device) or (device == "cgpu"):
        if device == "cgpu":
            logger_warning("Deprecation mixed-device `cgpu`, use `cpu+gpu` instead.")

        # Must be actual device, choose memory device
        device = tensor_backend.memory_device
    example_tensor = tensor_backend([1], device=device, create_base_tensor_cls=True)
    dtype = example_tensor.dtype_from_char(conv_params_init.data_type)
    if device != tensor_backend.device:
        warn(
            "Mismatch in device from TensorBackend vs convergence parameters. "
            + "Potentially more conversions are required and watch out for errors."
        )
    if dtype != tensor_backend.dtype:
        warn(
            "Mismatch in dtype from TensorBackend vs convergence parameters. "
            + "Potentially more conversions are required and watch out for errors. "
            + "We automatically select the higher precision to generate operators."
        )

        # This is a problem because we need to generate operators in the higher
        # precision
        init_tensor = example_tensor.copy().convert(dtype=dtype)
        if init_tensor.dtype_eps > example_tensor.dtype_eps:
            dtype = example_tensor.dtype

    if "SymmetryGenerators" in params:
        new_generators = []
        for elem in params["SymmetryGenerators"]:
            if isinstance(elem, str):
                new_generators.append(elem)
                continue

            # User passed matrix / tensor, we have to convert it on the fly
            # to a string key. Since user passed a matrix / tensor, it cannot
            # be a simulation with different Hilbert spaces (okay, it should
            # not be ...)
            if len(simulation.operators.set_names) > 1:
                raise QTeaLeavesError("Single generator matrix for set of operators.")

            # id() must be unique, so we can set it across different simulations
            # again, it will be the same matrix
            key = "_auto_generator" + str(id(elem))
            if key not in simulation.operators:
                simulation.operators[key] = elem
            new_generators.append(key)

    else:
        new_generators = []

    if not simulation.py_tensor_backend.tensor_cls.has_symmetry:
        sectors = {}
        sym = []
    else:
        if ("SymmetryTypes" in params) or ("Symmetries" in params):
            sym = tensor_backend.parse_symmetries(params)
        elif "SymmetryGenerators" in params:
            raise QTeaLeavesError("Generators were passed, but no symmetries.")
        else:
            # Defines a default symmetry
            sym = []

        if (not new_generators) and (not sym):
            # Trivial symmetry and not generator
            for name in simulation.operators.set_names:
                simulation.operators[(name, "_trivial_gen_u1")] = (
                    0.0 * simulation.operators.get_operator(name, "id", params)
                )
            new_generators = ["_trivial_gen_u1"]

        sym, sectors = tensor_backend.parse_sectors(params, sym)

    if len(sym) > 1:
        # Raise warning for now, multiple symmetries did not pass unittests
        warn(
            "Two and more symmetries are an experimental feature. "
            + "Use only for testing features."
        )

    # Select the desired ansatz. Either TTN (5), MPS (6), ATTN (7) or TTO (8)
    tn_type = simulation.eval_numeric_param(simulation.tn_type, params)
    if tn_type in TN_TYPE:
        # TTN, MPS, ATTN or TTO simulation
        ansatz = TN_TYPE[tn_type]
    else:
        raise QTeaLeavesError(f"The tn_type {tn_type} is not available.")

    # Prepare operators
    # -----------------

    operators = base_tensor_cls.convert_operator_dict(
        simulation.operators,
        params=params,
        symmetries=[],
        generators=[],
        base_tensor_cls=base_tensor_cls,
        dtype=dtype,
        device=tensor_backend.memory_device,
    )

    if base_tensor_cls != tensor_cls:
        operators = tensor_cls.convert_operator_dict(
            operators,
            symmetries=sym,
            generators=new_generators,
            base_tensor_cls=base_tensor_cls,
        )

    # Prepare state
    # -------------

    requires_singvals = False
    if (
        len(simulation.observables.obs_list["TNObsCorr"]) > 0
        or len(simulation.observables.obs_list["TNObsCustom"]) > 0
    ):
        requires_singvals = True
    elif ansatz.has_de and len(simulation.observables.obs_list["TNObsLocal"]) > 0:
        # aTTNs need singvals also for local meas
        requires_singvals = True
    elif tn_type in [8] and "TNObsBondEntropy" in simulation.observables.obs_list:
        requires_singvals = True

    # If `continue_file` is present, use it to initialize the state
    if "continue_file" in params:
        if isinstance(params["continue_file"], ansatz):
            # state is passed directly from python
            state = params["continue_file"]

        else:
            # state is passed as a file
            ext = params["continue_file"].split(".")[-1]

            if ext == "pkl" + ansatz.extension:
                state = ansatz.read_pickle(params["continue_file"], tensor_backend)
            elif ext == ansatz.extension:
                state = ansatz.read(params["continue_file"], tensor_backend)
            else:
                msg = f"""No approach available to read `{params["continue_file"]}`."""
                msg += f" Default extension / ansatz is `{ansatz.extension}`."
                raise QTeaLeavesError(msg)

            state.convert(dtype, device)

        state.convergence_parameters = simulation.convergence
        # Set flag for QR vs SVD here
        # pylint: disable-next=protected-access
        state._requires_singvals = requires_singvals
        if state.iso_center is None:
            state.iso_towards(state.default_iso_pos)

        de_sites_sim = simulation.disentangler
        if ansatz.has_de and de_sites_sim is not None:
            logger.warning(
                "Ignoring disentangler position from QuantumGreenTeaSimulation "
                " and taking the positions from continue_file."
            )

    else:
        # if aTTN, set disentangler positions
        if ansatz.has_de:
            de_sites = simulation.check_disentangler_position(
                params, simulation.disentangler
            )
            logger.info("Disentanglers at %s", de_sites.tolist())
            de_initialize = "identity"
        else:
            de_initialize = None
            de_sites = None

        initialize = "random"
        if (ansatz == LPTN) and isinstance(
            simulation.convergence, TNConvergenceParametersFiniteT
        ):
            initialize = "infinite_t"

        # initialize a random state
        local_dims = operators.get_local_links(num_sites, params)
        state = ansatz(
            num_sites,
            conv_params_init,
            local_dim=local_dims,
            requires_singvals=requires_singvals,
            initialize=initialize,
            tensor_backend=tensor_backend,
            sectors=sectors,
            de_sites=de_sites,
            de_initialize=de_initialize,
        )

        # Set parameterized convergence parameters now, but
        # ansatz has no way to resolve parameterization
        state.convergence_parameters = simulation.convergence

    iso_pos = state.default_iso_pos

    # Prepare system Hamiltonian
    # --------------------------

    dense_mpo_list = DenseMPOList.from_model(
        simulation.model, params, tensor_backend=tensor_backend
    )
    dense_mpo_list.initialize(operators, params)

    mpo_mode = simulation.eval_numeric_param(simulation.mpo_mode, params)
    if tensor_backend.tensor_cls.has_symmetry and (mpo_mode in [1, 2, 3, 4, 11]):
        # Bug with eigensolver and symmetries and iTPO ... ticket is open:
        # https://baltig.infn.it/quantum_tea_leaves_internal/py_api_quantum_tea_leaves/-/issues/101
        raise QTeaLeavesError(
            "Currently symmetries and MPO modes which are not iTPO have problems. "
            f"Current mpo_type={mpo_mode}"
        )

    if params.get("use_mpo_from_continue_file", False):
        if "continue_file" not in params:
            raise QTeaLeavesError("No continue file was used.")
        mpo = state.eff_op
    elif mpo_mode == 0:
        mpo = ITPO(num_sites, do_indexing=False)
        mpo.add_dense_mpo_list(dense_mpo_list)
    elif mpo_mode in [-1, 1]:
        # Auto-select goes to iTPO
        mpo = ITPO(num_sites)
        mpo.add_dense_mpo_list(dense_mpo_list)
    elif mpo_mode in [2]:
        mpo = ITPO(num_sites, enable_update=True)
        mpo.add_dense_mpo_list(dense_mpo_list)
    elif mpo_mode in [3]:
        mpo = ITPO(num_sites, do_compress=True)
        mpo.add_dense_mpo_list(dense_mpo_list)
    elif mpo_mode in [4]:
        mpo = ITPO(num_sites, do_compress=True, enable_update=True)
        mpo.add_dense_mpo_list(dense_mpo_list)
    elif mpo_mode == 10:
        if isinstance(params.get("_sparse_mpo", None), SparseMPO):
            # Allow user defined SparseMPO as not many rules are supported
            # Then, delete from dictionary otherwise deepcopy is prevented
            mpo = params["_sparse_mpo"]
            del params["_sparse_mpo"]
        else:
            mpo = SparseMPO(num_sites, operators, do_vecs=True)
            mpo.add_dense_mpo_list(dense_mpo_list, params, indexed_spo=False)
    elif mpo_mode == 11:
        if isinstance(params.get("_sparse_mpo", None), SparseMPO):
            # Allow user defined SparseMPO as not many rules are supported
            mpo = params["_sparse_mpo"]
            del params["_sparse_mpo"]
        else:
            mpo = SparseMPO(num_sites, operators, do_vecs=True)
            mpo.add_dense_mpo_list(dense_mpo_list, params)

    else:
        raise QTeaLeavesError(f"The mpo_mode {mpo_mode} is not available.")

    # Statics
    # -------

    # If dynamics checkpoints are available, call to statics is not necessary
    checkpoint_indicator_file = os.path.join(
        folder_name_output, "has_dyn_checkpoints.txt"
    )
    load_dyn_from_checkpoint = os.path.isfile(checkpoint_indicator_file)

    # pylint: disable-next=protected-access
    state._requires_singvals = requires_singvals

    # Initialize effective operators
    if not params.get("use_mpo_from_continue_file", False):
        mpo.setup_as_eff_ops(state)

    # We loop the statics search for the ground state + all excited states.

    # We save all states intermediately, and load them only when we measure the overlaps.
    # This reduces memory requirements, and allows us to measure overlaps with checkpoints.
    def intermediate_state_fname(excited_ii):
        return os.path.join(
            folder_name_output, f"saved_state_{excited_ii:03}.pkl" + state.extension
        )

    num_excited_states = params.get("num_excited_states", 0)
    if num_excited_states > 0 and state.extension not in [
        "ttn",
        "mps",
    ]:
        raise NotImplementedError(
            f"Found {num_excited_states=}. Excited state search is not"
            + f"implemented for {state.extension}."
        )

    for excited_ii in range(num_excited_states + 1):
        if excited_ii > 0:
            # Reinitialize a random state.
            # pylint: disable=protected-access
            state = ansatz(
                state._num_sites,
                state.convergence_parameters,
                local_dim=state._local_dim,
                requires_singvals=state._requires_singvals,
                initialize="random",
                tensor_backend=state.tensor_backend,
                sectors=sectors,
                de_sites=state.de_layer.de_sites if state.has_de else None,
                de_initialize=de_initialize if state.has_de else None,
            )
            mpo.setup_as_eff_ops(state)
            # pylint: enable=protected-access

            # Load the excited states, set them up as projectors, and delete.
            for kk in range(excited_ii):
                previous_state = ansatz.read_pickle(intermediate_state_fname(kk))
                if previous_state.tensor_backend.dtype != state.tensor_backend.dtype:
                    # pylint: disable-next=logging-not-lazy
                    logger.warning(
                        f"The {kk}-th loaded projectors have "
                        + f"dtype: {previous_state.tensor_backend.dtype}, but the state has "
                        + f"dtype: {state.tensor_backend.dtype}. Precision might be lost."
                    )

                eff_proj = getattr(
                    qtealeaves.mpos, f"{ansatz.extension.upper()}Projector"
                )(psi0=previous_state)
                eff_proj.setup_as_eff_ops(state)
                state.eff_proj.append(eff_proj)

                # remove state from memory
                del previous_state

        # In the spirit of functools.partial, we wrap two (!) calls
        # here setting some arguments by default
        def partial_tn_measurements(
            state,
            postfix,
            time,
            observables=simulation.observables,
            operators=operators,
            params=params,
            tensor_backend=tensor_backend,
            tn_type=tn_type,
        ):
            observables_tmp = deepcopy(observables)
            observables_tmp = run_tn_measurements(
                state,
                observables_tmp,
                operators,
                params,
                tensor_backend,
                tn_type,
                postfix=postfix,
                time=time,
            )

            # pylint: disable-next=cell-var-from-loop
            if excited_ii == 0:
                # keep backwards compatability
                full_file_path = os.path.join(
                    folder_name_output, f"static_obs_{postfix}.dat"
                )
            else:
                full_file_path = os.path.join(
                    folder_name_output,
                    # pylint: disable-next=cell-var-from-loop
                    f"static_obs_excited{excited_ii:03}_{postfix}.dat",
                )

            observables_tmp.write_results(
                full_file_path,
                params,
                state_ansatz=TN_TYPE_LABEL[tn_type],
            )
            return

        if not load_dyn_from_checkpoint:
            # Minimization of the energy
            sweep_order = params.get("sweep_order", None)
            state, energy_list, needs_measurement = optimize(
                state,
                params,
                folder_name_output,
                simulation.store_checkpoints,
                excited_ii,
                partial_tn_measurements,
                sweep_order=sweep_order,
            )

            convergence_name = (
                "convergence.log"
                if excited_ii == 0
                else f"convergence_excited{excited_ii:03d}.log"
            )
            np.savetxt(
                os.path.join(folder_name_output, convergence_name),
                energy_list,
                header="Time\t Energy",
            )

            if needs_measurement:
                # Measurements
                # pylint: disable-next=no-member

                if excited_ii == 0:
                    # keep backwards compatability
                    full_file_path = os.path.join(folder_name_output, "static_obs.dat")
                else:
                    full_file_path = os.path.join(
                        folder_name_output, f"static_obs_excited{excited_ii:03}.dat"
                    )

                observables = deepcopy(simulation.observables)
                observables = run_tn_measurements(
                    state,
                    observables,
                    operators,
                    params,
                    tensor_backend,
                    tn_type,
                )
                observables.write_results(
                    full_file_path, params, state_ansatz=TN_TYPE_LABEL[tn_type]
                )

        # Compute the overlaps with all previous states and print them to the log.
        if excited_ii > 0:
            write_overlaps(
                excited_ii, state, ansatz, intermediate_state_fname, folder_name_output
            )

        # Remove projectors. They might be large,
        # and are not necessary for dynamics.
        state.eff_proj = []

        # save the state, unless we are in the last iteration
        if excited_ii < num_excited_states:
            state.save_pickle(intermediate_state_fname(excited_ii))

    # read the state for dynamics
    start_dynamics_from = params.get("start_dynamics_from", 0)

    # If we continue from the last state we found, no reading is necessary,
    # because the state is already loaded.
    # Otherwise, load it.
    if start_dynamics_from != num_excited_states:
        state_fname = intermediate_state_fname(start_dynamics_from)
        state = ansatz.read_pickle(state_fname)
        logger.info("Starting dynamics with excited state %i.", start_dynamics_from)

    # Remove all saved intermediate states. The loop ends at num_excited_states
    # (and not at num_excited_states + 1), because the last state is not written.
    for ii in range(num_excited_states):
        os.remove(intermediate_state_fname(ii))

    # Dynamics
    # --------
    if "Quenches" in params:
        dynamics_info = []  # convergence info of each quench
        state.pre_timeevo_checks()

        dyn_checkpoint_file = None
        params_ii = None

        # pylint: disable-next=no-member
        qtrand = np.random.RandomState()
        qtrand.seed(params.get("seed", [11, 13, 17, 19]))
        _ = qtrand.random(1000)
        qtjump_threshold = qtrand.random()

        time = 0
        kk = 0
        for _, quench in enumerate(params["Quenches"]):
            quench_info = []  # convergence info of each timestep
            dynamics_info.append(quench_info)
            dt_grid = quench.get_dt_grid(params)
            tevo_mode = quench.time_evolution_mode
            oqs_mode = quench.oqs_mode
            if oqs_mode in [0, 3]:
                state.solver = KrylovSolverH
            elif oqs_mode in [1, 2]:
                state.solver = KrylovSolverNH
                if ("seed" not in params) and (oqs_mode == 1):
                    raise QTeaLeavesError("No seed, but quantum trajectory.")
                if tn_type in [8]:
                    raise QTeaLeavesError(
                        "Trying to use quantum trajectories on a density matrix!"
                        "For open system dynamics with density matrices use oqs_mode=3."
                    )
            else:
                raise QTeaLeavesError("OQS mode unknown")

            # By convention, coupling parameters in the Hamiltonian which
            # do not appear in the quench, are taken from the ground state.
            # The following line will enforce this by passing params_ii=None
            # and force_rebuild_mpo=True.
            state, params_ii = update_time_dependent_terms(
                state,
                time,
                params,
                None,
                quench,
                mpo_mode,
                iso_pos,
                force_rebuild_mpo=True,
            )

            for jj, dt in enumerate(dt_grid):
                kk += 1

                if isinstance(dt, complex):
                    # Running complex time evolution ... do some checks here.
                    if oqs_mode != 0:
                        raise ValueError(
                            "Complex time evolution with open quantum system."
                        )
                    if dt.imag > 0:
                        logger_warning(
                            "Complex time evolution, but no cooling, i.e., Im(dt) > 0."
                        )

                # Target implementation would be `"%08d_%08d" % (ii, jj)`, but for
                # compatibility with current postprocessing
                int_str_ij = f"{1:08}_{kk:08}"

                if load_dyn_from_checkpoint:
                    dyn_checkpoint_file = os.path.join(
                        folder_name_output, f"TTN_dyn_{int_str_ij}"
                    )
                    dyn_checkpoint_file_pkl = (
                        dyn_checkpoint_file + ".pkl" + ansatz.extension
                    )
                    if os.path.isfile(dyn_checkpoint_file_pkl):
                        # Found checkpoint
                        logger.info("Loading checkpoint from time step %d.", kk)
                        old_state = state
                        state = ansatz.read_pickle(
                            dyn_checkpoint_file_pkl,
                            tensor_backend=old_state.tensor_backend,
                        )
                        state.checkpoint_copy_simulation_attr(old_state)
                        load_dyn_from_checkpoint = False

                    time += dt
                    continue

                # Time-step (evaluate mid-time-step)
                time += 0.5 * dt
                state.iso_towards(iso_pos, keep_singvals=requires_singvals, trunc=True)
                state, params_ii = update_time_dependent_terms(
                    state, time, params, params_ii, quench, mpo_mode, iso_pos
                )
                if oqs_mode not in [3]:
                    timestep_info = state.timestep(dt, tevo_mode)
                else:
                    timestep_info, _tot_singvals_cut_kraus = state.timestep(
                        dt, str(tevo_mode) + "_kraus"
                    )
                quench_info.append(timestep_info)

                if (oqs_mode in [1]) and (state.norm() ** 2 < qtjump_threshold):
                    # Apply quantum jumps
                    apply_quantum_jump(
                        state,
                        simulation.model,
                        operators,
                        quench,
                        time,
                        params_ii,
                        qtrand,
                    )

                    qtjump_threshold = qtrand.random()

                if isinstance(dt, complex):
                    # For complex time evolution, we have to re-normalize
                    state.normalize()

                # Measurement
                time += 0.5 * dt
                if ((jj + 1) % quench.measurement_period == 0) or (
                    jj + 1 == len(dt_grid)
                ):
                    state.iso_towards(
                        iso_pos, keep_singvals=requires_singvals, trunc=True
                    )
                    state, params_ii = update_time_dependent_terms(
                        state,
                        time,
                        params,
                        params_ii,
                        quench,
                        mpo_mode,
                        iso_pos,
                    )

                    observables = deepcopy(simulation.observables)
                    observables = run_tn_measurements(
                        state,
                        observables,
                        operators,
                        params,
                        tensor_backend,
                        tn_type,
                        int_str_ij,
                        time=time,
                    )

                    filename = f"dyn_obs{1:08}_{kk:08}.dat"
                    # pylint: disable-next=no-member
                    full_file_path = os.path.join(folder_name_output, filename)

                    observables.write_results(
                        full_file_path,
                        params,
                        state_ansatz=TN_TYPE_LABEL[tn_type],
                    )
                if simulation.store_checkpoints:
                    dyn_checkpoint_file = state.checkpoint_store(
                        folder_name_output,
                        dyn_checkpoint_file,
                        int_str_ij,
                        checkpoint_indicator_file,
                        is_dyn=True,
                    )

                _timestep_summary = np.asarray(timestep_info).T

                if oqs_mode not in [3]:
                    logger.info(
                        "Finished time-step %-5d"
                        "  tot err: %-7.1e"
                        "  avg iters: %-4.1f"
                        "  freq converged: %-4.2f",
                        kk,
                        _timestep_summary[2].sum(),
                        _timestep_summary[1].mean(),
                        _timestep_summary[0].mean(),
                    )
                else:
                    logger.info(
                        "Finished time-step %-5d"
                        "  tot err: %-7.1e"
                        "  tot singvals cut in Kraus step: %-7.1e"
                        "  avg iters: %-4.1f"
                        "  freq converged: %-4.2f",
                        kk,
                        _timestep_summary[2].sum(),
                        _tot_singvals_cut_kraus,
                        _timestep_summary[1].mean(),
                        _timestep_summary[0].mean(),
                    )

        if load_dyn_from_checkpoint:
            msg = "No checkpoint found, although checkpoint indicator file exists."
            raise QTeaLeavesError(msg)

    mpo.print_summary()

    toc = tictoc()
    logger.info("Simulation time is %2.4f.", toc - tic)

    # Create indicator file for finished simulation
    finished_jdic = {"cpu_time": toc - tic, "sim_hash": sim_hash}
    finished_json = os.path.join(folder_name_output, "has_finished.json")
    with open(finished_json, "w+", encoding="utf-8") as fh:
        json.dump(finished_jdic, fh)
    return


def optimize(
    state,
    params,
    folder_name_output,
    store_checkpoints,
    excited_ii,
    partial_tn_measurements,
    sweep_order=None,
):
    """
    Optimize the tensor network by optimizing each tensor
    in the TN a number of times equal to num_sweeps.
    If not specified in sweep_order,
    the optimization is defined by `state.default_sweep_order` method.
    The number of sweeps and the other details
    are controlled in :py:class:`TNConvergenceParameters`

    Parameters
    ----------

    state : instance of :class:`_AbstractTN`
        State to be optimized.
    params : dict
        Contains parameters for simulation to resolve parameterization.
    folder_name_input : str
        Folder path for output and storing checkpoints.
    store_checkpoints : bool
        Flag if checkpoints should be stored (`True`) or not (`False`).
    excited_ii : int
        Integer counter for excited states. Needed for storing checkpoints.
        If only ground state search, set to 0.
    sweep_order : List[int] | List[Tuple[int]] | None, optional
        PATH for the optimization, passed as the
        integer index of the tensor.
        Default to `None`.

    Returns
    -------

    :class:`_AbstractTN`
        State after optimization (in-place update not posisble for checkpoints).

    np.ndarray[float], shape [n, 2]
        Computational time and energy after each sweep

    bool
        Status if measurement is required (True) because the state
        was updated. In case of a loaded checkpoint which returns without
        additional optimizations, `False` is returned.
    """
    needs_measurement = True
    energies = []
    sweep_times = []

    if sweep_order is None:
        sweep_order = state.default_sweep_order()

    # Retrieve the convergence parameters to keep parameterization
    conv_params_parameterized = state.convergence_parameters
    conv_params = conv_params_parameterized.resolve_params_copy(params)

    # We will need setting about last setting for skip_exact_rgtensors
    last_skip_exact_rgtensors = False

    # For checkpointing
    ansatz = type(state)
    intra_sweep_last = False
    stat_checkpoint_file = None
    if folder_name_output is None:
        # Some unittests run without output folder
        checkpoint_indicator_file = None
        load_stat_from_checkpoint = False
    else:
        has_checkpoint_name = (
            "has_stat_checkpoints.txt"
            if excited_ii == 0
            else f"has_stat_checkpoints_{excited_ii:03}.txt"
        )
        checkpoint_indicator_file = os.path.join(
            folder_name_output, has_checkpoint_name
        )
        load_stat_from_checkpoint = os.path.isfile(checkpoint_indicator_file)

    # Set solver for imaginary time evolution via TDVP
    state.solver = KrylovSolverH

    if state.has_de:
        # save the unperturbed hamiltonian here

        # remove de_opt_learning_rate_strategy because of problems with pickling state
        learning_strategy = deepcopy(
            conv_params_parameterized.de_opt_learning_rate_strategy
        )
        conv_params_parameterized.de_opt_learning_rate_strategy = None
        state.eff_op_no_disentanglers = deepcopy(state.eff_op)
        # restore de_opt_learning_rate
        conv_params_parameterized.de_opt_learning_rate_strategy = learning_strategy

    tmp = state.compute_energy(state.iso_center)
    logger.info(
        "Starting sweeps with energy: %-19.14g",
        tmp,
    )

    # Cycle over sweeps
    exit_criterion = "d"
    for ii in range(conv_params.max_iter):
        initial_sweep_time = tictoc()
        int_str_i = f"{ii:08}" if excited_ii == 0 else f"{excited_ii:03}_{ii:08}"
        outer_loop_continue = False

        # Resolve convergence parameters
        state.convergence_parameters = conv_params_parameterized.resolve_params_copy(
            params, idx=ii
        )

        sim_params = state.convergence_parameters.sim_params
        update_method = state.convergence_parameters.sim_params["statics_method"]

        # Logic for convert
        # .................

        device = sim_params["device"]
        if device == "auto":
            # Automatic converts to cpu for now, later choose based on
            # devices present and bond dimension (?).
            device = "cpu"
            state.tensor_backend.device = device

        dtype = sim_params["data_type"]
        if dtype == "A":
            # Automatic converts to double complex for now, later choose
            # based on H being real or complex and tolerance for this iteration
            dtype = "Z"
        if isinstance(dtype, str):
            state.convergence_parameters.data_type_switch = (
                dtype != state.dtype_to_char()
            )
            dtype = state.dtype_from_char(dtype)
        else:
            state.convergence_parameters.data_type_switch = dtype != state.dtype
        state.tensor_backend.dtype = dtype

        # skipped internally if not necessary
        state.convert(dtype, state.tensor_backend.memory_device)

        state.convergence_parameters.sim_params["arnoldi_tolerance"] = (
            10 * state.dtype_eps
        )

        if sim_params["random_sweep"]:
            # Shuffle works in place
            np.random.shuffle(sweep_order)

        update_method = sim_params["statics_method"]
        last_skip_exact_rgtensors = sim_params["skip_exact_rgtensors"]
        if ii + 1 == conv_params.max_iter:
            # In the last sweep, we never skip as it saves doing the
            # isometrization after the sweeps for the measurements
            last_skip_exact_rgtensors = False
        elif state.convergence_parameters.data_type_switch:
            # When switching data types, we cannot get stuck with tensor
            # with potentially lower precision, visit them all to update
            # unitary tensors to potentially higher precision
            last_skip_exact_rgtensors = False
        elif load_stat_from_checkpoint:
            # If loading from checkpoint, we cannot be sure about precision
            # either, revisit all tensors. Data could have switched, allow
            # higher norm errors ...
            last_skip_exact_rgtensors = False
            state.convergence_parameters.data_type_switch = True

        if update_method in (4, 5) and last_skip_exact_rgtensors:
            # It might work, but we would need to figure out the theory if
            # the local term in the eff MPO does the job or if we are missing
            # something.
            raise QTeaLeavesError(
                "Cannot combine skipping RG tensors for imag time evo."
            )

        if load_stat_from_checkpoint:
            # Potentially, we will look for too many intra-sweep checkpoints, but
            # we cannot find anything which is wrong. As we do not have the state
            # at the beginning of the last started sweep, finding out the sweep
            # order with skipped rg tensors is not possible.
            sweep_order_ii = sweep_order
        else:
            sweep_order_ii = state.filter_sweep_order(
                sweep_order, last_skip_exact_rgtensors
            )

        if (
            state.has_de
            and ii >= state.convergence_parameters.de_opt_start_after_sweeps
            and not (
                load_stat_from_checkpoint
            )  # do not optimize DE if there is a checkpoint in future sweeps
        ):
            # if aTTN, optimize disentanglers and incorporate them into the TTN

            energy_before = state.compute_energy(state.iso_center)

            # reset the hamiltonian back to the one without the disentanglers
            state.eff_op_no_disentanglers.setup_as_eff_ops(state)
            state.optimize_disentanglers()
            state.apply_des_to_hamiltonian(params=params)

            energy_after = state.compute_energy(state.iso_center)
            logger.info(
                "Optimized disentanglers. Energy: %-19.14g, Time: %.1f, energy gain: %-19.14g",
                energy_after,
                tictoc() - initial_sweep_time,
                energy_before - energy_after,
            )
            if energy_before - energy_after < 0:
                logger.warning("Disentanglers increased energy!")

        sweep_max_bond_dim = 0
        # Cycle over optimization path
        for jj, pos in enumerate(sweep_order_ii):
            int_str_ij = (
                f"{ii:08}_{jj:08}"
                if excited_ii == 0
                else f"{excited_ii:03}_{ii:08}_{jj:08}"
            )
            tic = tictoc()

            if load_stat_from_checkpoint and (jj == 0):
                # Check for end of sweep with int_str_i
                state, energies, sweep_times, _, cp_status = _query_if_checkpoint(
                    state, folder_name_output, ansatz, int_str_i, state.tensor_backend
                )

                if (cp_status == 2) or (ii + 1 == conv_params.max_iter):
                    # Direct return, converged or reached max_iter
                    energies_and_times = np.array([sweep_times, energies]).T
                    return state, energies_and_times, False

                if cp_status == 1:
                    # do not continue loop over j, found checkpoint at end
                    logger.info(
                        "Loading checkpoint for excited state %i, sweep %i",
                        excited_ii,
                        (ii + 1),
                    )
                    outer_loop_continue = True
                    load_stat_from_checkpoint = False
                    break

                continue

            if load_stat_from_checkpoint:
                # Check for intra-sweep checkpoint
                (
                    state,
                    energies,
                    sweep_times,
                    sweep_order_tmp,
                    cp_status,
                ) = _query_if_checkpoint(
                    state, folder_name_output, ansatz, int_str_ij, state.tensor_backend
                )

                if cp_status == 1:
                    # found checkpoint
                    logger.info(
                        "Loading checkpoint at sweep %d, tensor %d.", ii + 1, jj + 1
                    )
                    load_stat_from_checkpoint = False

                    if sweep_order_tmp is None:
                        # Intra-sweep checkpoints needs a sweep-order
                        msg = "Intra-sweep checkpoint seems to be a post-sweep "
                        msg += "checkpoint because no sweep order is stored "
                        msg += "in the corresponding json."
                        raise QTeaLeavesError(msg)

                    sweep_order_ii = sweep_order_tmp

                    if jj + 1 == len(sweep_order_ii):
                        # Was the last one in the sweep ... and still not
                        # saved as checkpoint after sweep? (dj)
                        outer_loop_continue = True

                continue

            # Energy minimization with single tensor update
            if update_method == 1:
                energy = state.optimize_single_tensor(pos)

            # Energy minimization with single tensor update and subspace expansion
            elif update_method in (0, 2):
                (
                    pos_partner,
                    link_state,
                    link_partner,
                ) = state.get_pos_partner_link_expansion(pos)
                energy = state.optimize_link_expansion(
                    pos,
                    pos_partner,
                    link_state,
                    link_partner,
                )

            # Energy minimization with imaginary time evolution single-site TDVP
            elif update_method in (4, 5):
                if update_method == 5:
                    upd_fun = state.timestep_single_tensor
                else:
                    upd_fun = state.timestep_single_tensor_link_expansion
                next_pos = (
                    None if (jj + 1 == len(sweep_order_ii)) else sweep_order_ii[jj + 1]
                )
                upd_fun(
                    pos,
                    next_pos,
                    -sim_params["imag_evo_dt"],
                )
                state.normalize()
            elif update_method == 3:
                # Two-tensor TDVP
                if jj + 1 == len(sweep_order_ii):
                    pass
                elif jj + 2 == len(sweep_order_ii):
                    state.timestep_two_tensors(
                        pos,
                        sweep_order_ii[jj + 1],
                        -sim_params["imag_evo_dt"],
                        True,
                    )
                else:
                    state.timestep_two_tensors(
                        pos,
                        sweep_order_ii[jj + 1],
                        -sim_params["imag_evo_dt"],
                        False,
                    )
                state.normalize()
            else:
                raise ValueError(f"Unknown statics method {update_method}.")

            sweep_max_bond_dim = max(sweep_max_bond_dim, *state[pos].shape)

            # Checkpoints inside the sweep are only enabled for optimization
            # taking longer than 24h per sweep
            toc = tictoc()
            opt_time = toc - tic
            predicted_sweep_time = opt_time * len(sweep_order_ii)
            intrasweep_checkpoint = (
                predicted_sweep_time > QTEA_TIMELIMIT_INTRASWEEP_CHECKPOINTS
            )

            intra_sweep_last = jj + 1 == len(sweep_order_ii)
            if store_checkpoints and intrasweep_checkpoint and (not intra_sweep_last):
                # Long computation time, store intra-sweep checkpoint. By default,
                # mid-sweep checkpoints are not converged states (always False)
                stat_checkpoint_file = state.checkpoint_store(
                    folder_name_output,
                    stat_checkpoint_file,
                    int_str_ij,
                    checkpoint_indicator_file,
                    jdic={
                        "energies": energies,
                        "sweep_times": sweep_times,
                        "sweep_order_ii": sweep_order_ii,
                        "converged": False,
                    },
                )

        if state.convergence_parameters.data_type_switch:
            state.convergence_parameters.data_type_switch = False
            state.normalize()

        if outer_loop_continue or load_stat_from_checkpoint:
            continue

        # Save energy and checkpoint at the end of the sweep
        # with link expasion compute and save energy after truncation
        if update_method != 1:
            energy = state.compute_energy(state.iso_center)
        sweep_time = tictoc() - initial_sweep_time

        # pylint: disable-next=possibly-used-before-assignment
        energies.append(energy)
        sweep_times.append(sweep_time)
        logger.info(
            "Finished sweep %-3d  max chi: %-4d  energy: %-19.14g  time: %.1f",
            ii + 1,
            sweep_max_bond_dim,
            energy,  # pylint: disable=possibly-used-before-assignment
            sweep_time,
        )

        every_n = state.convergence_parameters.measure_obs_every_n_iter
        if ((ii + 1) % every_n == 0) and (every_n != -1):
            # Extra measurements
            partial_tn_measurements(
                state,
                postfix=f"{(ii+1):08}",
                time=None,
            )

        # Stopping criterion
        exit_criterion = check_exit_criterion(
            state.convergence_parameters, energies, ii
        )
        exit_by_criterion = exit_criterion != "d"

        # Save energy and checkpoint at the end of the sweep (last intrasweep
        # is never stored)
        if store_checkpoints:
            stat_checkpoint_file = state.checkpoint_store(
                folder_name_output,
                stat_checkpoint_file,
                int_str_i,
                checkpoint_indicator_file,
                jdic={
                    "energies": energies,
                    "sweep_times": sweep_times,
                    "sweep_order_ii": None,
                    "converged": exit_by_criterion,
                },
            )
        intra_sweep_last = False

        # Stopping criterion
        if exit_by_criterion:
            break

    if load_stat_from_checkpoint:
        msg = "No checkpoint found, although checkpoint indicator file exists."
        raise QTeaLeavesError(msg)

    if last_skip_exact_rgtensors:
        # Variables like the singular values in the skipped tensors might
        # still be from the initialization and have to updated (up to the
        # current understanding).
        #
        # A parallel version could be possible if singular values at the
        # boundary to the skipped tensors are stored, but depends highly
        # on the ansatz
        restore_iso_center = state.iso_center

        # There were problems on the pytorch side with mixed precision
        # caused by different complex data types, resolve them here
        state.convert(state.dtype, None)

        for ii in range(state.num_sites):
            state.site_canonize(ii)

        state.iso_towards(restore_iso_center)

    exit_criterion_str = {
        "d": "max_iter reached",
        "a": "abs_deviation convergence",
        "r": "rel_deviation convergence",
        "e": "target energy reached",
    }.get(exit_criterion, "not assessed")
    logger.info("Simulation finished due to %s.", exit_criterion_str)

    # Set as numpy arrays energies and times for the same result of fortran
    energies_and_times = np.array([sweep_times, energies]).T
    return state, energies_and_times, needs_measurement


def apply_quantum_jump(state, model, operators, quench, time, params, qtrand):
    """Apply a quantum jump."""
    state.normalize()
    terms_oqs = []
    weights = []

    # To keep import order clean, we provide Lindblad terms with necessary
    # classes as kwargs
    kwargs = {
        "MPOSite": MPOSite,
        "DenseMPO": DenseMPO,
        "DenseMPOList": DenseMPOList,
        "ITPO": ITPO,
        "dim": model.dim,
        "lvals": model.eval_numeric_param(model.lvals, params),
    }

    for term in model:
        if not term.is_oqs:
            continue

        weight = term.quantum_jump_weight(
            state, operators, quench, time, params, **kwargs
        )
        terms_oqs.append(term)
        weights.append(weight)

    weights = np.cumsum(np.array(weights))
    weights /= weights[-1]

    # throw a random number to decide which term in the
    # list of lindblad terms will jump
    rand = qtrand.random()
    idx = weights.shape[0] - 1
    for ii in range(idx):
        if rand < weights[ii]:
            idx = ii
            break

    # Needed for kraus jumps
    kwargs["quench"] = quench
    kwargs["time"] = time
    # Apply jump
    terms_oqs[idx].quantum_jump_apply(state, operators, params, qtrand, **kwargs)


def update_time_dependent_terms(
    state, time, params, params_ii, quench, mpo_mode, pos, force_rebuild_mpo=False
):
    """
    Update the MPO layer according to the time-dependent couplings.

    **Arguments**

    state : :class:`_AbtractTN`

    time : float
        Time of the current step.

    params : dict
        Used as initial starting point if params_ii is None

    params_ii : dict
        Parameters of the system in the last call.

    quench :
        Quench instance contains the time-dependent functions.

    mpo_mode : int
        MPO mode required to decide on how to update the
        effective operators.

    pos : int | tuple of ints
        Default position of isometry center.

    force_rebuild_mpo : bool, optional
        Force method to re-calculate the MPO

    **Returns**

    state : state itself (updated inplace anyway)

    params_ii : updated params dict (to check for time evolution
        with constant checks)
    """
    # Default value should come from ground state search, which is solved
    # with a call to this method upfront starting every quench with params_ii=None

    # If not time dependent and not forced to rebuild, skip updating MPOs
    # as in sudden quench scenarios
    is_time_dependent = force_rebuild_mpo

    if (params_ii is None) and state.eff_op.has_oqs:
        # First call to OQS must be flagged as time-dependent as Lindblad
        # couplings are always zero in statics for MPS, TTN even if
        # the params dictionary has a non-zero value
        params_ii = deepcopy(params)
        is_time_dependent = True
    elif params_ii is None:
        params_ii = deepcopy(params)

    for key in quench.keys():
        coupl = quench[key](time, params)

        is_time_dependent = is_time_dependent or (coupl != params_ii[key])
        params_ii[key] = coupl

    if not is_time_dependent:
        return state, params_ii

    if mpo_mode in [2, 4]:
        # Update scheme without recalculating
        state.iso_towards(pos)
        state.eff_op.do_update = True
        state.eff_op.update_couplings(params_ii)
        state.build_effective_operators()
        state.eff_op.do_update = False
    else:
        mpo = state.eff_op
        mpo.update_couplings(params_ii)
        state.eff_op = None
        mpo.setup_as_eff_ops(state)

    return state, params_ii


def run_tn_measurements(
    state,
    observables,
    operators,
    params,
    tensor_backend,
    tn_type,
    postfix=None,
    time=None,
):
    """
    Run all the measurements for a tensor network.

    **Arguments**

    state : instance of _AbstractTN
        Tensor network to be measured.

    observables : instance of TNObservables
        Observables.

    operators : instance of TNOperators
        Operators.

    params : dict
        Dictionary containing the current parameters for the
        simulation.

    tensor_backend; instance of `TensorBackend`
        Tensor backend of the simulation

    tn_type: int
        Identifier for the TN ansatz (MPS, TTN, ATTN, TTO)

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
    tn_type_label = TN_TYPE_LABEL[tn_type]

    # save the initial iso position
    initial_iso_pos = state.iso_center

    if initial_iso_pos is None:
        state.iso_towards(state.default_iso_pos)
        initial_iso_pos = state.default_iso_pos

    # Need iso center at default position (trunc=True to be safe
    # for close-to-degeneracies)
    iso_pos = state.default_iso_pos

    if postfix is None:
        postfix = ""
    if not isinstance(state, _AbstractTN):
        raise TypeError(f"state must be an instance of _AbstractTN, not {type(state)}.")

    observables.results_buffer["energy"] = state.compute_energy()

    # We need the square norm (not implemented on TTN level as own function)
    # `get_norm` returns the value required for a renormalization, i.e.,
    # sqrt(<psi|psi>), while we expect <psi|psi>
    # Force to convert to python-float (even for torch scalars in torch.Tensor)

    # pylint: disable-next=protected-access
    for example_tensor in state._iter_tensors():
        break
    norm_backend = state.norm()
    # pylint: disable-next=undefined-loop-variable
    norm = example_tensor.get_of(norm_backend)
    norm = float(np.array(norm)) ** 2
    # pylint: disable-next=undefined-loop-variable
    tabs = example_tensor.get_attr("abs")
    # pylint: disable-next=undefined-loop-variable
    do_renorm = tabs(norm_backend - 1.0) > 10 * example_tensor.dtype_eps
    if do_renorm:
        state.scale_inverse(norm_backend)
        logger.warning(
            "State was renormalized during measurement with norm %2.15f", norm
        )

    observables.results_buffer["norm"] = norm
    if time is not None:
        observables.results_buffer["time"] = time

    # Set the cache for reduced density matrices: local measurements have
    # fast loop over sites and slow loop over operators and we avoid
    # looping twice or more through it. Further, singular values will
    # be updated.
    _local_obs = observables.obs_list["TNObsLocal"]
    condition_local = (
        tn_type_label in _local_obs.measurable_ansaetze and len(_local_obs) > 0
    )

    # pylint: disable-next=protected-access
    if condition_local or state._requires_singvals:
        state.set_cache_rho()
        state.iso_towards(state.default_iso_pos)

    # Copy the effective projectors and remove them from the state.
    # They are reinstated after the measurements.
    tmp_eff_proj = state.eff_proj
    state.eff_proj = []

    # figure out which excited state we are at from the length of the projector list
    num_excited = len(tmp_eff_proj)
    excited_index = f"_excited{num_excited:03}" if num_excited > 0 else ""

    # Local observables
    # -----------------
    local_obs = observables.obs_list["TNObsLocal"]
    if tn_type_label in local_obs.measurable_ansaetze and len(local_obs.name) > 0:
        if state.has_de:
            # if aTTN, then local entries on sites with disentanglers are not
            # local anymore
            state.iso_towards(iso_pos, keep_singvals=True, trunc=True)

            h_iso_center = deepcopy(state.iso_center)
            hmpo = state.eff_op

            # get the iTPO of these non-local terms and contract with DE layer
            itpo = local_obs.to_itpo(
                operators, tensor_backend, state.num_sites, de_layer=state.de_layer
            )
            itpo = state.de_layer.contract_de_layer(itpo, tensor_backend, params)

            # measure iTPO
            itpo.set_meas_status(do_measurement=True)
            state.eff_op = None
            itpo.setup_as_eff_ops(state, measurement_mode=True)

            dict_by_tpo_id = itpo.collect_measurements()
            idx = -1

            # restore back the original hamiltonian as effective operator
            state.eff_op = hmpo

        for jj, name_jj in enumerate(local_obs.name):
            operator_list = [
                operators[(kk, local_obs.operator[jj])] for kk in range(state.num_sites)
            ]
            local_meas = state.meas_local(operator_list)

            # if aTTN, rewrite the values for sites with disentanglers
            if state.has_de:
                for kk in range(state.num_sites):
                    if kk in state.de_layer.de_sites:
                        # disentangler on a site
                        idx += 1
                        local_meas[kk] = np.real(dict_by_tpo_id[idx])

            local_obs.results_buffer[name_jj] = local_meas

    # Correlation measurements
    # ------------------------
    # Optimize correlators with either get_rho_ij or a better meas_tensor_product
    corr_obs = observables.obs_list["TNObsCorr"]

    # pylint: disable-next=too-many-nested-blocks
    if tn_type_label in corr_obs.measurable_ansaetze and len(corr_obs.name) > 0:
        # Measure diagonal entries first (otherwise overwriting results
        # in measurement mode error/warning)
        corr_diag = []
        for kk, name_kk in enumerate(corr_obs.name):
            ops_list = []
            for jj in range(state.num_sites):
                op_a = operators[(jj, corr_obs.operators[kk][0])]
                op_b = operators[(jj, corr_obs.operators[kk][1])]

                if op_a.ndim == 2:
                    op_ab = op_a @ op_b
                else:
                    # Assume rank-4 (but delta charge both times to the right
                    op_ab = op_a.tensordot(op_b, ([2], [1]))
                    op_ab.flip_links_update([0, 2])
                    op_ab.trace_one_dim_pair([0, 3])
                    op_ab.trace_one_dim_pair([1, 3])

                ops_list.append(op_ab)

            corr_diag_ii = np.zeros(state.num_sites, dtype=np.complex128)

            for ii, elem in enumerate(state.meas_local(ops_list)):
                # if aTTN, then diagonal entries on sites
                # with disentanglers are not local anymore, so skip
                if hasattr(state, "de_layer") and (ii in state.de_layer.de_sites):
                    continue
                corr_diag_ii[ii] = elem

            corr_diag.append(corr_diag_ii)

        state.iso_towards(iso_pos, keep_singvals=True, trunc=True)

        h_iso_center = deepcopy(state.iso_center)
        hmpo = state.eff_op

        # convert the correlation matrix to iTPOS for measurement
        de_layer = state.de_layer if state.has_de else None
        kk = 0
        name_kk = corr_obs.name[kk]
        corr_kk = np.zeros((state.num_sites, state.num_sites), dtype=np.complex128)
        ii = 0
        jj = 0
        for itpo in corr_obs.to_itpo(
            operators, tensor_backend, state.num_sites, de_layer=de_layer
        ):
            if state.has_de:
                itpo = state.de_layer.contract_de_layer(itpo, tensor_backend, params)

            itpo.set_meas_status(do_measurement=True)
            state.eff_op = None
            itpo.setup_as_eff_ops(state, measurement_mode=True)

            # Retrieve results from itpo measurement
            dict_by_tpo_id = itpo.collect_measurements()
            itpo_batch_size = len(dict_by_tpo_id)
            idx = 0
            while idx < itpo_batch_size:
                # skip the diag terms (for aTTN diag terms without the disentangler)
                if ii == jj and not (
                    hasattr(state, "de_layer") and (ii in state.de_layer.de_sites)
                ):
                    pass
                else:
                    corr_kk[ii, jj] = dict_by_tpo_id[idx]
                    idx += 1

                jj += 1
                if jj == state.num_sites:
                    jj = 0
                    ii += 1
                if ii == state.num_sites:
                    # get the diagonal terms from local measurements
                    for xx in range(state.num_sites):
                        if hasattr(state, "de_layer") and (
                            xx in state.de_layer.de_sites
                        ):
                            continue
                        corr_kk[xx, xx] = corr_diag[kk][xx]

                    corr_obs.results_buffer[name_kk] = corr_kk
                    ii = 0
                    kk += 1
                    if kk < len(corr_obs.name[kk]):
                        name_kk = corr_obs.name[kk]
                        corr_kk = np.zeros(
                            (state.num_sites, state.num_sites), dtype=np.complex128
                        )
                    else:
                        name_kk = None
                        corr_kk = None

            if name_kk is not None:
                # The last term has not been stored yet, which is usually the case
                # as it is a diagonal terms and has only an iTPO measurement for
                # aTTNs and similar: get the diagonal terms from local measurements
                for xx in range(state.num_sites):
                    if hasattr(state, "de_layer") and (xx in state.de_layer.de_sites):
                        continue
                    corr_kk[xx, xx] = corr_diag[kk][xx]

                corr_obs.results_buffer[name_kk] = corr_kk

        # Migrate counter if same MPO type
        if isinstance(hmpo, ITPO):
            hmpo.add_contraction_counters(state.eff_op)

        if (np.array(state.iso_center) != np.array(h_iso_center)).any():
            raise QTeaLeavesError(
                "Iso center moved.! Cannot re-install Hamiltonian MPO."
            )
        state.eff_op = hmpo

    # Distance measurement (TNDistance2Pure)
    # --------------------------------------
    dist_obs = observables.obs_list["TNDistance2Pure"]
    if tn_type_label in dist_obs.measurable_ansaetze:
        for jj, name_jj in enumerate(dist_obs.name):
            path_jj = dist_obs.path_to_state[jj]

            psi_tn = TN_TYPE[tn_type].read(path_jj, tensor_backend=state.tensor_backend)

            dist_obs.results_buffer[name_jj] = state.dot(psi_tn)

    # State2File measurement
    # ----------------------
    # we will store numpy arrays now independent of the flag
    file_obs = observables.obs_list["TNState2File"]
    if tn_type_label in file_obs.measurable_ansaetze:

        for jj, name_jj in enumerate(file_obs.name):
            filename_tmp = observables.eval_str_param(name_jj, params)
            filename_tmp += postfix + excited_index + ".pkl" + state.extension

            if file_obs.formatting[jj] == "U":
                state.save_pickle(filename_tmp)
            elif file_obs.formatting[jj] == "F":
                filename_tmp = filename_tmp.replace(".pkl", ".")
                state.write(filename_tmp)
            elif file_obs.formatting[jj] == "D":
                state_dense = state.to_dense()
                state_dense.save_pickle(filename_tmp)

            file_obs.results_buffer[name_jj] = filename_tmp

    # TNObsTensorProduct measurement
    # ----------------------------
    tp_obs = observables.obs_list["TNObsTensorProduct"]
    if tn_type_label in tp_obs.measurable_ansaetze:

        for name, ops, sites in zip(tp_obs.name, tp_obs.operators, tp_obs.sites):
            sites = [site[0] for site in sites]
            tp_operators = [operators[(sites[jj], ii)] for jj, ii in enumerate(ops)]
            tp_obs.results_buffer[name] = np.complex128(
                state.meas_tensor_product(tp_operators, sites)
            )

    # TNObsWeightedSum measurement
    # ----------------------------
    ws_obs = observables.obs_list["TNObsWeightedSum"]
    if tn_type_label in ws_obs.measurable_ansaetze:
        if ws_obs.use_itpo and len(ws_obs.name) > 0:
            state.iso_towards(iso_pos, keep_singvals=True, trunc=True)
            h_iso_center = deepcopy(state.iso_center)
            hmpo = state.eff_op

            itpo = ws_obs.to_itpo(operators, tensor_backend, state.num_sites)

            state.eff_op = None
            itpo.setup_as_eff_ops(state, measurement_mode=True)

            # Retrieve the results
            dict_by_tpo_id = itpo.collect_measurements()
            cnt = 0
            for name, coeffs in zip(ws_obs.name, ws_obs.coeffs):
                values = np.array(
                    [dict_by_tpo_id[ii] for ii in range(cnt, cnt + len(coeffs))]
                )
                ws_obs.results_buffer[name] = np.complex128(values.sum())
                cnt += len(coeffs)

            if (np.array(state.iso_center) != np.array(h_iso_center)).any():
                raise QTeaLeavesError(
                    "Iso center moved.! Cannot re-install Hamiltonian MPO."
                )
            state.eff_op = hmpo
        else:
            # Cycle over weighted sum observables
            for name, coef, tp_ops in zip(
                ws_obs.name, ws_obs.coeffs, ws_obs.tp_operators
            ):
                op_string = []
                idxs_string = []
                if isinstance(tp_ops, list):
                    tp_op = tp_ops[0]
                else:
                    tp_op = tp_ops
                # Cycle over the TPO of a single weighted sum
                for ops, sites in zip(tp_op.operators, tp_op.sites):
                    sites = [site[0] for site in sites]
                    tp_operators = [
                        operators[(sites[jj], ii)] for jj, ii in enumerate(ops)
                    ]
                    idxs_string.append(sites)
                    op_string.append(tp_operators)

                ws_obs.results_buffer[name] = np.complex128(
                    state.meas_weighted_sum(op_string, idxs_string, coef)
                )

    # TNObsProjective measurement
    # ---------------------------
    pj_obs = observables.obs_list["TNObsProjective"]
    if tn_type_label in pj_obs.measurable_ansaetze:
        for name, qk_conv in zip(pj_obs.name, pj_obs.qiskit_convention):
            pj_obs.results_buffer[name] = state.meas_projective(
                nmeas=pj_obs.num_shots, qiskit_convention=qk_conv
            )

    # TNObsProbabilities measurement
    # ------------------------------
    prob_obs = observables.obs_list["TNObsProbabilities"]
    if tn_type_label in prob_obs.measurable_ansaetze:
        for name, prob_type, prob_param, qk_conv, precision in zip(
            prob_obs.name,
            prob_obs.prob_type,
            prob_obs.prob_param,
            prob_obs.qiskit_convention,
            prob_obs.precision,
        ):
            if isinstance(name, list):
                name = name[0]
            if prob_type == "U":
                if np.isscalar(prob_param):
                    prob_param = [prob_param]
                prob_obs.results_buffer[name] = {}
                for prob_p in prob_param:
                    prob_obs.results_buffer[name] = state.meas_unbiased_probabilities(
                        prob_p,
                        qiskit_convention=qk_conv,
                        precision=precision,
                        bound_probabilities=prob_obs.results_buffer[name],
                        do_return_samples=True,
                    )
            elif prob_type == "E":
                prob_obs.results_buffer[name] = state.meas_even_probabilities(
                    prob_param, qiskit_convention=qk_conv
                )
            elif prob_type == "G":
                prob_obs.results_buffer[name] = state.meas_greedy_probabilities(
                    prob_param, qiskit_convention=qk_conv
                )

    # TNObsBondEntropy measurement
    # ----------------------------
    be_obs = observables.obs_list["TNObsBondEntropy"]
    if tn_type_label in be_obs.measurable_ansaetze:
        if len(be_obs.name) == 1:
            bond_entropy = state.meas_bond_entropy()
            be_obs.results_buffer[be_obs.name[0]] = bond_entropy

    # TNObsTZeroCorr measurement
    # --------------------------
    tzcorr_obs = observables.obs_list["TNObsTZeroCorr"]
    if tn_type_label in tzcorr_obs.measurable_ansaetze:
        pass

    # TNObsCorr4 measurement
    # ----------------------
    corr4_obs = observables.obs_list["TNObsCorr4"]
    if tn_type_label in corr4_obs.measurable_ansaetze:
        pass

    # Custom correlation measurements
    # -------------------------------
    custom_obs = observables.obs_list["TNObsCustom"]
    if tn_type_label in custom_obs.measurable_ansaetze and len(custom_obs.name) > 0:
        state.iso_towards(iso_pos, keep_singvals=True, trunc=True)
        h_iso_center = deepcopy(state.iso_center)
        hmpo = state.eff_op

        # Custom_results is the container for the results.
        # It is a list of np arrays, whose shapes match the length of each measurement.
        custom_results = [
            np.zeros(len(sites), dtype=np.complex128)
            for sites in custom_obs.site_indices
        ]

        # convert the correlators to itpo for measurement
        # See below for meaning of ndx_site and ndx_meas.
        ndx_site = 0
        ndx_meas = 0

        for itpo in custom_obs.to_itpo(operators, tensor_backend, state.num_sites):

            if hasattr(state, "de_layer"):
                # include the disentanglers into the itpo
                itpo = state.de_layer.contract_de_layer(itpo, tensor_backend, params)

            itpo.set_meas_status(do_measurement=True)
            state.eff_op = None
            itpo.setup_as_eff_ops(state, measurement_mode=True)

            # Retrieve results from itpo measurement
            dict_by_tpo_id = itpo.collect_measurements()
            # Sort the entries of the dictionary according to the key.
            # This makes the loop below easier.
            list_by_tpo_id = [dict_by_tpo_id[key] for key in sorted(dict_by_tpo_id)]

            # The results are filled in one-by-one to support batches

            # dict_by_tpo_id is a dictionary with all resuts.
            # This loop accumulates the results into the proper
            # arrays in the custom_results list.
            # ndx_meas counts the different correlation measurements
            # ndx_site counts the entries for each measurement
            for result in list_by_tpo_id:
                custom_results[ndx_meas][ndx_site] = result

                ndx_site += 1
                # When you get to the end of one observable,
                # reset ndx_site and increase kk to the next one.
                if ndx_site == len(custom_obs.site_indices[ndx_meas]):
                    name_obs = custom_obs.name[ndx_meas]
                    custom_obs.results_buffer[name_obs] = custom_results[ndx_meas]

                    ndx_site = 0
                    ndx_meas += 1

        # Migrate counter if same MPO type
        if isinstance(hmpo, ITPO):
            hmpo.add_contraction_counters(state.eff_op)

        if (np.array(state.iso_center) != np.array(h_iso_center)).any():
            raise QTeaLeavesError(
                "Iso center moved! Cannot re-install Hamiltonian MPO."
            )
        state.eff_op = hmpo

    # MPO measurements
    # ----------------

    mpo_meas = observables.obs_list["TNObsDenseMPOList"]
    if tn_type_label in mpo_meas.measurable_ansaetze and len(mpo_meas.name) > 0:
        # initial setup
        state.iso_towards(iso_pos, keep_singvals=True, trunc=True)
        h_iso_center = state.iso_center
        hmpo = state.eff_op

        # get energy (in case of variance of energy measurement)
        energy = observables.results_buffer["energy"]

        for kk, mpo_name in enumerate(mpo_meas.name):
            value = 0.0
            for sub_mpo in mpo_meas.iterators[kk](params, operators):
                itpo_sub_mpo = ITPO(state.num_sites)
                itpo_sub_mpo.add_dense_mpo_list(sub_mpo)
                if hasattr(state, "de_layer"):
                    # include the disentanglers into the itpo
                    itpo_sub_mpo = state.de_layer.contract_de_layer(
                        itpo_sub_mpo, tensor_backend, params
                    )

                # Carry out the measurement of this sub-MPO
                state.eff_op = None
                itpo_sub_mpo.setup_as_eff_ops(state)
                value += state.compute_energy()

            if mpo_meas.is_energy_var[kk]:
                # Treat the special and common case of calculating the
                # variance of the energy.
                value -= energy**2

            # Set the value in the results
            mpo_meas.results_buffer[mpo_name] = value

        # retrieve the hamiltonian eff ops and reset energy
        state.eff_op = hmpo
        _ = state.compute_energy

    # TNObsLogNegativity measurement
    # ----------------------------
    ln_obs = observables.obs_list["TNObsLogNegativity"]
    if tn_type_label in ln_obs.measurable_ansaetze:
        if len(ln_obs.name) == 1:
            mode = ln_obs.mode[0]
            log_neg = state.meas_log_negativity(mode=mode)
            ln_obs.results_buffer[ln_obs.name[0]] = log_neg

    # Custom Json observables measurement
    # ----------------
    customfunction_obs = observables.obs_list["TNCustomFunctionObs"]
    if (
        tn_type_label in customfunction_obs.measurable_ansaetze
        and len(customfunction_obs.name) > 0
    ):
        for name, func, func_kwargs in zip(
            customfunction_obs.name,
            customfunction_obs.function,
            customfunction_obs.func_kwargs,
        ):
            # Measure the observable with custom function
            customfunction_obs.results_buffer[name] = func(
                state, func_kwargs=func_kwargs
            )

    # Actually, just reset the iso_center.
    # The iso center changes, even with only local measurements. Bug?
    state.iso_towards(initial_iso_pos)

    # Check that the iso_pos is the same as at the begining and reset the projectors.
    if initial_iso_pos == state.iso_center:
        state.eff_proj = tmp_eff_proj
    else:
        raise QTeaLeavesError(
            f"""The iso_position changed from {initial_iso_pos} to {state.iso_center}
                during the measurement. Cannot reinstate the effective projectors!"""
        )

    state.clear_cache_rho()

    if do_renorm:
        state.scale(norm_backend)

    return observables


def _query_if_checkpoint(
    state, folder_name_output, ansatz, int_str, tensor_backend=None
):
    """
    Queries checkpoint and returns state, energies, and status, where
    status is either 0 (no checkpoint found), 1 (checkpoint found but
    not yet converged), or 2 (checkpoint found and converged).
    """
    energies = []
    sweep_times = []
    sweep_order = None

    stat_checkpoint_file = os.path.join(folder_name_output, f"TTN_stat_{int_str}")
    stat_checkpoint_json = stat_checkpoint_file + ".json"
    stat_checkpoint_file_pkl = stat_checkpoint_file + ".pkl" + ansatz.extension

    cp_status = 0
    if os.path.isfile(stat_checkpoint_file_pkl):
        # Found file for the end of the ii-th sweep
        logger.info("Loading checkpoint for sweeps with id %s.", int_str)

        old_state = state
        state = ansatz.read_pickle(stat_checkpoint_file_pkl, tensor_backend)
        state.checkpoint_copy_simulation_attr(old_state)

        with open(stat_checkpoint_json, "r") as fh:
            jdic = json.load(fh)
            energies = jdic["energies"]
            sweep_times = jdic["sweep_times"]
            sweep_order = jdic["sweep_order_ii"]

            cp_status = 2 if jdic["converged"] else 1

        if cp_status == 1:
            os.remove(stat_checkpoint_file_pkl)

    return state, energies, sweep_times, sweep_order, cp_status


def check_exit_criterion(conv_params, energies, sweep_idx):
    """
    Check the stopping criterion for the optimization.
    You compare the last `n_points_conv_check` to the last
    point, and say a simulation converged if:
    :math:`max(|E - E_{last}|) / n_points_conv_check
    < abs_deviation` or
    :math:`max(|E - E_{last}|) / n_points_conv_check
    < rel_deviation * |E_{last}|`.

    Parameters
    ----------
    conv_params : TNConvergenceParameters
        The convergence parameters of the simulation
    energies : np.ndarray[float]
        The energies of the simulation up to that point
    sweep_idx : int
        Integer of the sweep

    Returns
    -------
    str
        If "d", the optimization did not converge yet
        If "a", the simulation converged due to the absolute deviation criterion
        If "r", the simulation converged due to the relative deviation criterion
    """
    converged = "d"

    if sweep_idx >= conv_params.n_points_conv_check:
        # get last energy
        last_energy = energies[-1]
        # get last self._convergence_parameters.n_points_conv_check energies
        important_energies = energies[-conv_params.n_points_conv_check :]
        # Compute max(|E - E_{last}|)
        dev = (
            np.max(np.abs(np.array(important_energies) - last_energy))
            / conv_params.n_points_conv_check
        )
        if conv_params.target_energy is not None:
            # Target energy check
            if last_energy < conv_params.target_energy:
                converged = "e"
        elif dev < conv_params.abs_deviation:
            # Absolute deviation check
            converged = "a"
        elif dev < conv_params.rel_deviation * abs(last_energy):
            # Relative deviation check
            converged = "r"

    return converged


def write_overlaps(
    excited_ii, state, ansatz, intermediate_state_fname, folder_name_output
):
    """
    Compute and write the overlaps between the current excited state
    and the previously found states.

    **Arguments**
    excited_ii : int
        The index of the excited state.
    state : `Abstract_tn`
        The current state.
    ansatz : class
        The class of the state ansatz. Used for calling the read method.
    intermediate_state_fname : `Callable`
        A callable defining the filenames where the intermediate states are found.
        Takes the index (int) as parameter.
    folder_name_output : str
        The path to the output of the simulation.

    **Returns**
        A list of computed overlaps.
    """

    # the paths to the files are:
    overlaps_fname_json = "overlaps.json"
    overlaps_file_json = os.path.join(folder_name_output, overlaps_fname_json)

    # get the overlaps
    overlaps = []
    for kk in range(excited_ii):
        # load state, measure overlap, delete
        previous_state = ansatz.read_pickle(intermediate_state_fname(kk))
        overlap = np.abs(state.dot(previous_state))
        overlaps.append(overlap)
        del previous_state

    logger.info("Overlaps with the previous states: %s", str(overlaps))

    ##############################
    # write to the .json file
    # read the dictionary if it exists
    overlap_dict = {}
    if os.path.isfile(overlaps_file_json):
        with open(overlaps_file_json, "r") as json_file:
            overlap_dict = json.load(json_file)

    # append the overlaps to the dictionary
    overlap_dict[excited_ii] = overlaps

    # write to json
    with open(overlaps_file_json, "w") as overf:
        json.dump(overlap_dict, overf)

    return
