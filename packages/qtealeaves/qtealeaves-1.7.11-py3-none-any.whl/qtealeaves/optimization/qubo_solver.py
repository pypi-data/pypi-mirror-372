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
The module contains both exact and tensor-network based solvers
for a generic QUBO problem in a standard format.
"""

# pylint: disable=invalid-name
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=too-many-arguments
# pylint: disable=too-many-statements
# pylint: disable=too-many-instance-attributes

import codecs
import json

# Modules
# -----------------------------------------------
## Utils
import re
from os import makedirs, path
from time import time

## Maths and linear algebra
import numpy as np

from qtealeaves.convergence_parameters import TNConvergenceParameters
from qtealeaves.emulator import TTN
from qtealeaves.modeling import QuantumModel, RandomizedLocalTerm, TwoBodyAllToAllTerm1D
from qtealeaves.observables import TNObservables, TNObsLocal, TNState2File
from qtealeaves.operators import TNSpin12Operators
from qtealeaves.simulation import QuantumGreenTeaSimulation
from qtealeaves.tensors import TensorBackend

## Quantum Green TEA
from qtealeaves.tooling import QTeaLeavesError

## Classical optimization tools
from .opt_tooling import (
    compute_exact_spectrum,
    create_exact_observables,
    create_exact_spinglass_hamiltonian,
    generate_perturbation_transverse_fields,
    get_driver_product_state_via_tn_gss,
    get_exact_driver_product_state,
    measure_exact_observables,
)

__all__ = ["QUBOSolver", "QUBOConvergenceParameter"]
# -----------------------------------------------
# -----------------------------------------------


class QUBOProblemError(QTeaLeavesError):
    """
    Custom derived exception class
    for errors in the QUBO solver
    instantiation process.
    """


class QUBOSetUpError(QTeaLeavesError):
    """
    Custom derived exception class
    for errors during the set-up of
    the QUBO solver simulation.
    """


class QUBOConvergenceParameter(TNConvergenceParameters):
    # pylint: disable=anomalous-backslash-in-string
    """
    Convergence parameters for the QUBO solver.
    An instance of this class must be created and
    passed to the QUBO solver whenever the QUBO problem
    is to be solved using tensor networks.

    Parameters
    ----------

    max_bond_dimension : int, optional
        The maximum bond dimension of the tensor
        network during the ground-state search.
        The maximum value of the bond dimension is
        upper bounded by
        :math:`2^{n \\mathbin{//} 2}`, where
        :math:`n` is the number of spins in the
        spin glass system.
        Default to 8.
    max_iter : int, optional
        The maximum number of sweeps for the
        ground-state search. After ``max_iter``
        the ground-state search ends.
        Default to 20 sweeps.
    abs_deviation : float, optional
        Exit criterion for the ground-state search.
        If the energy of the current sweep has an
        absolute per-sweep deviation from the previous
        sweeps below this threshold, the tensor network
        optimization ends.
        Default to 4e-12.
    rel_deviation : float, optional
        Exit criterion for ground-state search.
        If the energy of the current sweep has
        a relative per-sweep deviation from the previous
        sweeps below this threshold, the tensor network
        optimization ends.
        Default to 1e-12.
    n_points_conv_check : int, optional
        The number of sweeps used when checking
        convergence for the ground state search.
        Exit criteria are not checked until this
        many sweeps have been performed.
        Default to 6.
    random_sweeps : bool, optional
        If True, perform random sweeps to optimize
        the tensors.
        Default to False.
    enable_spacelink_expansion : bool, optional
        The mode used for sweeping along the tensors
        during the optimization. If False, standard
        sweeps without space link expansion are performed
        to obtain the ground state; if True, the first
        half of the sweeps use space link expansion,
        while in the second half the space link expansion
        is disabled.
        Default to False.
    arnoldi_maxiter : int, optional
        Maximum number of Lanczos vectors to be used in
        the eigensolver.
        Default to 32.
    psi0 : str, optional
        The initial tensor network state from which
        to start the ground-state search for the spin
        glass Hamiltonian representing the QUBO problem.
        The available options are:
            - ``random``: the initial state of the
              tensors is initialized randomly;
              - ``exact_driver_product_state``: the tensors
              are initialized in the product state

                :math:`\\left\vert{+}\right\rangle^{n}`

                .. math::

                  \\left\vert{+}\right\rangle
                  =
                  \\dfrac{1}{\\sqrt{2}}
                  \\left(\\left\vert{0}\right\rangle
                  +
                  \\left\vert{1}\right\rangle\right)

              i.e., in the ground state of the driver Hamiltonian

              .. math::

                \\mathcal{H}_{\\scriptscriptstyle driver}
                =
                \\sum\\limits_{j=1}^n \\sigma_j^x .

              Within this option, the product state is exactly
              constructed with the given initial bond dimension
              :math:`\\chi =` ``init_bond_dimension``;
            - 'tn_driver_product_state': the tensors are initialized
              in the ground state of
              :math:`\\mathcal{H}_{\\scriptscriptstyle driver}` obtained
              via a ground-state search of the corresponding
              driver Hamiltonian with bond dimension
              :math:`\\chi =` ``init_bond_dimension``.
              Default to ``random``.
    ini_bond_dimension : int, optional
        The bond dimension used to construct the initial
        tensor network state. Using subspace expansion
        the bond dimension can grow.
        Default to None, i.e., the initial
        bond dimension is initialized to ``max_bond_dimension``.
    psi0_noise : float, optional
        Numerical noise to construct the
        exact initial product state with a
        given bond dimension. More details
        can be found in the :mod:`opt_tooling`
        submodule.
        Default to 1e-7.
    transverse_field_ratio : float, optional
        The ratio of the magnitude of the strength
        of the classical longitudinal terms (Z-Pauli)
        to the quantum off-diagonal transverse field
        terms (X-Pauli) to be added.
        This ratio controls the magnitude of the
        transverse field perturbation relative to
        the classical Hamiltonian, whose ground state
        must be determined. See the function
        :func:`generate_perturbation_transverse_fields`
        in the :mod:`opt_tooling` submodule.
        Default to 0, i.e., no transverse fields will
        be added to the classical Hamiltonian.
    tn_input_folder_path : str, optional
        The full path where to save the input
        data and parameters for the tensor network
        ground-state search. If the folder does not exist,
        it will be automatically created.
        Default to ``/Tensor_Network_Simulation_Inputs/``.
    tn_output_folder_path : str, optional
        The full path where to save the output data and
        log files for the tensor network ground-state
        search. If the folder does not exist, it will
        be automatically created.
        Default to ``/Tensor_Network_Simulation_Outputs/``.
    tn_sampling_folder_path : str, optional
        The full path where to save the tensor network
        states for the OPES sampling. If the folder does
        not exist, it will be automatically created.
        Default to ``/Tensor_Network_Simulation_States/``.
    tn_io_extra_tag : str, optional
        Extra common tag to be added at the end of
        simulation log files in order to distringuish
        different simulations.
        Default to None.
    data_type : str, optional
        Data type of the tensors in the chosen ansatz.
        Available options are

        - "A": automatic
        - "Z": double precision complex (.complex128)
        - "C": single precision complex (.complex64)
        - "D": double precision real (.float64)
        - "S": single precision real (.float32)

        Default to ``C``.
    tn_type : int, optional
        The ansatz to be used for approximating the
        wave function of the mapped spin glass system.
        Available topologies are ``TTN`` (use 5) for
        Tree Tensor Networks and ``MPS`` (use 6) for
        Matrix Product States.
        Default to ``TTN`` (5).
    optimization_level : int, optional
        Optimization level for the tensor network simulation,
        i.e., the MPO representation inside the tensor network
        simulation. To enforce cache for sampling input 1, or to
        use TPO (iTPO with compression) input 0 (3).
        Default to -1, which enables an auto-selection.
    device : str, optional
        Device where to run the optimization.
        Available options are ``cpu`` to run
        the ground-state search on the CPUs,
        and ``gpu`` to run the ground-state
        search on the GPUs.
        Default to ``cpu``.
    """

    def __init__(
        self,
        max_bond_dimension=8,
        max_iter=20,
        abs_deviation=4e-12,
        rel_deviation=1e-12,
        n_points_conv_check=6,
        random_sweeps=False,
        enable_spacelink_expansion=False,
        arnoldi_maxiter=32,
        psi0="random",
        ini_bond_dimension=None,
        psi0_noise=1e-7,
        transverse_field_ratio=0,
        tn_input_folder_path="./Tensor_Network_Simulation_Inputs/",
        tn_output_folder_path="./Tensor_Network_Simulation_Outputs/",
        tn_sampling_folder_path="./Tensor_Network_Simulation_States/",
        tn_io_extra_tag=None,
        tn_type=5,
        data_type="C",
        optimization_level=-1,
        device="cpu",
        **kwargs,
    ):
        """Constructor."""

        # Choose method for sweeping
        if enable_spacelink_expansion:  ### Space link expansion
            sweep_mode = [0] * (max_iter // 2)
            sweep_mode += [1] * (max_iter - max_iter // 2)
        else:  ### No space link expansion
            sweep_mode = 1

        # Inherited attributes from qtealeaves
        initial_bdim = ini_bond_dimension or max_bond_dimension
        super().__init__(
            max_iter=max_iter,
            abs_deviation=abs_deviation,
            rel_deviation=rel_deviation,
            n_points_conv_check=n_points_conv_check,
            max_bond_dimension=max_bond_dimension,
            svd_ctrl="A",
            random_sweep=random_sweeps,
            arnoldi_maxiter=arnoldi_maxiter,
            statics_method=sweep_mode,
            data_type=data_type,
            ini_bond_dimension=initial_bdim,
            device=device,
            **kwargs,
        )

        # QUBO-params attributes
        if tn_type not in [5, 6]:
            raise QUBOSetUpError(
                f"The {tn_type} ansatz-type is unavailable for the QUBO solver."
            )
        self.tn_type = tn_type

        self.tn_input_folder = tn_input_folder_path
        self.tn_output_folder = tn_output_folder_path
        self.tn_sampling_folder = tn_sampling_folder_path
        self.tn_io_extra_tag = tn_io_extra_tag

        if psi0 not in [
            "random",
            "exact_driver_product_state",
            "tn_driver_product_state",
        ]:
            raise QUBOSetUpError(
                f"Tensor network state initialization option {psi0} not available."
            )

        self.psi0 = psi0
        self.psi0_noise = psi0_noise
        self.transverse_field_ratio = transverse_field_ratio
        self.mpo_mode = optimization_level


class QUBOSolver:
    r"""
    Solver for a generic QUBO problem

    .. math::

        \\min\\limits_{x \in \\left\{0, 1\right\}^n} f(\\boldsymbol{x})

    .. math::

        f(\\boldsymbol{x}) = \\boldsymbol{x}^T \\mathcal{Q} \\boldsymbol{x}

    where :math:`\boldsymbol{x}` is the :math:`n`-dimensional binary
    vector describing the binary configuration of the QUBO decision
    variables. The QUBO problem is uniquely described by the QUBO matrix
    :math:`\\mathcal{Q}`, which must be a symmetric or upper triangular
    real matrix.

    This QUBO solver implements different methods to obtain a solution:
        - ``brute-force`` obtains the exact solution (global optimum)
          but it's limited by the number of binaries (:math:`n \\leq 30`);
        - ``exact ground-state search`` maps the QUBO problem into an
          equivalent spin glass Hamiltonian and encodes the QUBO solution
          into the ground state of this Hamiltonian. The ground state is
          exactly reconstructed by creating the full Hamiltonian matrix
          and sorting its diagonal. This method obtains the exact solution
          (global optimum), but it's limited by the number of binaries
          (:math:`n \\leq 30`, depending on the available RAM);
        - ``tensor-network based ground-state search`` also maps the
          QUBO problem into a corresponding ground-state search of a
          spin glass Hamiltonian, but the solution is found by applying
          tensor-network optimization using tools from qtealeaves.
          This solver is not limited by the number of binaries but by
          the amount of entanglement needed for the computation.

    Parameters
    ----------

    qubo_matrix : np.ndarray[float]
        The input QUBO problem represented by its QUBO matrix.
        The input matrix must be either a symmetric or and
        upper triangular 2D numpy array of real numbers.
        Only the upper triangular part of the input
        matrix will be considered, i.e., if :math:`Q_{ij}`
        are the matrix elements of the input QUBO problem,
        only those for :math:`i \\leq j` will be used by the
        solver.
    """

    # Constructor for a QUBO solver instance
    # -------------------------------------------
    def __init__(self, qubo_matrix):
        if np.iscomplexobj(qubo_matrix):
            raise QUBOProblemError("QUBO matrix must not be a complex matrix!")
        if not (
            np.allclose(qubo_matrix, qubo_matrix.T, rtol=1e-9, atol=1e-12)
            or np.allclose(qubo_matrix, np.triu(qubo_matrix), rtol=1e-9, atol=1e-12)
        ):
            raise QUBOProblemError("The input QUBO matrix is not in standard format!")

        self.qubo_matrix = np.triu(qubo_matrix)
        self.n_binaries = qubo_matrix.shape[0]
        self.n_interactions = np.count_nonzero(self.qubo_matrix)
        self.n_interactions -= np.count_nonzero(np.diagonal(qubo_matrix).copy())
        self.cost = None
        self.solution = None
        self.time_to_solution = None

    # -------------------------------------------
    # -------------------------------------------

    # Instance methods
    # -------------------------------------------
    def evaluate(self, binaries_configuration):
        r"""
        Evaluate the QUBO cost function for a given
        binaries configuration.
        The QUBO cost function is defined as

        .. math::

            f_{\\mathrm{\\scriptscriptstyle QUBO}}
            =
            \\sum\nolimits_{j < j^{\prime} = 1}^n
            Q_{j j^{\prime}} x_j x_{j^{\prime}}
            +
            \\sum\nolimits_{j=1}^n Q_{jj} x_j

        where :math:`n` is the number of binary decision
        variables in the QUBO problem and :math:`\\mathcal{Q}`
        is the QUBO matrix.

        **Arguments**

        binaries_configuration : List[int]
            The :math:`n`-dimensional bitstring
            representing the given decision variables
            in the QUBO configuration.

        **Returns**

        cost : float
            The value of the QUBO cost function
            for the given binaries configuration.
        """

        # Reshaping the input bitstring
        config = np.array(binaries_configuration).reshape(-1, 1)

        # Evaluating the cost function
        cost = (config.T @ self.qubo_matrix @ config).item()

        # Output
        return cost

    def to_spinglass_couplings(self):
        """
        Derive the corresponding spin glass model
        of the QUBO problem.
        The couplings of the spin glass Hamiltonian
        are obtained from the QUBO matrix elements
        by transforming binary variables to spin-1/2
        variables (0 --> -1, 1 --> +1).

        **Arguments**

        None

        **Returns**

        spinglass_couplings : Dict
            The set of couplings defining the corresponding
            spin glass Hamiltonian, specifically:
                - 'offset': the constant term proportional
                            to the identity.
                            This energy offset does not influence
                            the solution of the QUBO problem, but it
                            is necessary to reconstruct the exact
                            value of the QUBO cost function, e.g.,
                            from the ground-state energy;
                - 'one-body': the set of single-body couplings,
                              i.e., the set of local longitudinal
                              magnetic fields (biases), one for each
                              spin-1/2 in the spin glass system;
                - 'two-body': the set of two-body (in general all-to-all)
                              couplings describing the interactions
                              between pairs of spin-1/2.
        """

        qjj = np.diagonal(self.qubo_matrix).copy()
        qij_upper = np.triu(self.qubo_matrix, k=1)

        ## Energy offset
        cte = 0.5 * np.sum(qjj) + 0.25 * np.sum(qij_upper)

        ## One-body couplings, aka, spin glass local magnetic fields
        qij = qij_upper + qij_upper.T
        magnetic_fields = 0.5 * qjj + 0.25 * np.sum(qij, axis=1)

        # Output
        spinglass_couplings = {
            "offset": cte,
            "one-body": magnetic_fields,
            "two-body": 0.25 * qij_upper,
        }
        return spinglass_couplings

    def solve_via_brute_force(self):
        """
        Solve the QUBO problem via brute
        force by generating all the possible
        decision binary configurations.
        This solver is, of course, limited
        to problem sizes less than 30 binaries.
        No mapping to a spin glass is needed
        for this solver.

        **Arguments**

        None

        **Returns**

        None
        """

        if self.n_binaries >= 30:
            raise RuntimeError(
                "\n\n**********************************************************\n"
                "**********************************************************\n"
                "With great power comes great responsibility!\n"
                "The space of all the possible binaries configuration\n"
                "is huge, but sadly, your poor old CLASSICAL computer's\n"
                "memory just ain't up to the task!\n"
                f"Crazy number of binaries --> {self.n_binaries} :O."
                "\n**********************************************************\n"
                "**********************************************************\n"
            )

        # Generating all the possible configuration
        st_to_sol = time()
        opt_cost = float("inf")
        opt_config = None

        for bitstring in range(2**self.n_binaries):
            tmp_config = [(bitstring >> i) & 1 for i in range(self.n_binaries)]
            tmp_cost = self.evaluate(tmp_config)
            if tmp_cost < opt_cost:
                opt_cost = tmp_cost
                opt_config = tmp_config

        self.time_to_solution = time() - st_to_sol
        self.cost = [opt_cost]
        self.solution = [opt_config]

    def solve_via_exact_sorting(self, spinglass_model, n_solutions=1):
        """
        Find the optimal solution(s) to the QUBO problem
        by mapping it onto a spin glass Hamiltonian.
        Then, find the ground-state (or low-energy
        eigenstates) of this Hamiltonian by performing
        an exact sorting of its diagonal.

        **Arguments**

        spinglass_model : Dict
            The set of couplings defining the
            corresponding spin glass Hamiltonian.
            For more details, see
            :meth:`~QUBOSolver.to_spinglass_couplings`.
        n_solutions : int, optional
            The number of optimal solutions to the
            QUBO to be computed, i.e., the number
            of eigenstates to be extracted from the
            ordered spin glass spectrum.

        **Returns**

        None
        """

        if self.n_binaries >= 30:
            raise RuntimeError(
                "\n\n**********************************************************\n"
                "**********************************************************\n"
                "With great power comes great responsibility!\n"
                "The Hilbert space is huge, but sadly, your\n"
                "poor old CLASSICAL computer's memory just\n"
                "ain't up to the task!\n"
                f"Crazy number of qubits --> {self.n_binaries} :O."
                "\n**********************************************************\n"
                "**********************************************************\n"
            )

        # Constructing the spin glass Hamiltonian
        obs = create_exact_observables(self.n_binaries)
        sg_ham = create_exact_spinglass_hamiltonian(spinglass_model)

        # Solving the spectrum
        st_to_sol = time()
        sg_spectrum = compute_exact_spectrum(sg_ham, n_solutions)
        sg_config = measure_exact_observables(obs, sg_spectrum)["sz"]
        self.time_to_solution = time() - st_to_sol

        # Constructing QUBO solution(s)
        self.solution = [self.spin_to_binary_config(config) for config in sg_config]

        # Computing the optimal cost of QUBO configuration(s)
        self.cost = [self.evaluate(sol) for sol in self.solution]

    def solve_via_tn_ground_state_search(
        self,
        spinglass_model,
        convergence_params,
        n_eigenstates=1,
        tensor_backend=TensorBackend(),
    ):
        r"""
        Find the optimal solution(s) to the QUBO problem
        by mapping it onto a spin glass Hamiltonian.
        Then, find the ground-state (or low-energy
        eigenstates) of this Hamiltonian by performing
        a variational optimization via tensor-network methods.
        Specifically, the wave function of the spin glass
        system is represented as a tensor network (TN) with a
        given topology and bond dimension, and the energy is
        optimized using numerical methods from qtealeaves.

        **Arguments**

        spinglass_model : Dict
            The set of couplings defining the
            corresponding spin glass Hamiltonian.
            For more details, see
            :meth:`~QUBOSolver.to_spinglass_couplings`.
        convergence_params : instance of :class:`QUBOConvergenceParameter`
            The convergence parameters for the QUBO solver
            simulation, for example the bond dimension, the
            number of sweeps, and the initial tensor network
            state.
        n_eigenstates : int, optional
            The number of optimal solutions to the
            QUBO problem to be computed, i.e., the
            number of eigenstates to be extracted
            from the spin glass spectrum.
            Default to 1, i.e., only the ground state.
            If greater than 1, excited states are obtained
            via sampling of spin configurations from the
            converged tensor network state. In this case, there
            is no guarantee that the sampled states are exactly
            the first ``n_eigenstates`` eigenvectors in the
            Hamiltonian spectrum (in general, they don't).
        tensor_backend : :class:`qtealeaves.tensors.TensorBackend`, optional
            Setup for tensor backend that defines the complete
            backend to be used for the tensors.
            Default to TensorBackend(), meaning that the underlying
            class for tensors is :class:`qtealeaves.tensors.QteaTensor`,
            the device for both the memory and the computations is
            the CPU and the data type of the tensors is np.complex128,
            i.e., double precision complex.
            You can pass different backend for the tensor class, for
            example pytorch running on GPUs, or use a mixed device
            for memory and computations with CPU + GPU.
            More details can be found both in `qtealeaves` and
            `qredtea`.

        **Returns**

        None
        """

        # Check method arguments type
        if not isinstance(convergence_params, QUBOConvergenceParameter):
            raise TypeError(
                "Expected an instance of QUBOConvergenceParameter, "
                f"but got {type(convergence_params).__name__}"
            )

        # Building the spin glass model to be solved
        # ------------------------------------------
        ## Constructing the spin glass Hamiltonian as a TN operator
        hbiases = spinglass_model["one-body"]
        sg_ints = spinglass_model["two-body"]
        tn_ops = TNSpin12Operators()
        tn_obs = TNObservables()
        tn_obs += TNObsLocal(name="sz", operator="sz")

        sg_ham = QuantumModel(1, "L", name="QUBO-Spin Glass Model")
        sg_ham += RandomizedLocalTerm(operator="sz", coupling_entries=hbiases)
        sg_ham += TwoBodyAllToAllTerm1D(operators=["sz", "sz"], coupling_matrix=sg_ints)

        ## Adding transverse quantum perturbation if requested
        if convergence_params.transverse_field_ratio != 0:
            transverse_hfield = generate_perturbation_transverse_fields(
                model_local_hfields=hbiases,
                ratio=convergence_params.transverse_field_ratio,
            )
            sg_ham += RandomizedLocalTerm(
                operator="sx", coupling_entries=transverse_hfield
            )
        # ------------------------------------------
        # ------------------------------------------

        # The ground-state search starts here
        # -----------------------------------
        ## Creating the initial state
        if convergence_params.psi0 == "random":
            tn_params = {"L": self.n_binaries}
        elif convergence_params.psi0 == "exact_driver_product_state":
            if convergence_params.tn_type == 6:
                raise NotImplementedError(
                    "Starting from the driver product "
                    "state is not yet implemented for MPS."
                )
            psi0_storing_file = convergence_params.tn_input_folder
            psi0_storing_file += "exact_driver_product_states/"
            makedirs(psi0_storing_file, exist_ok=True)
            psi0_storing_file += f"psi0_{self.n_binaries}.pklttn"
            psi0_state = get_exact_driver_product_state(
                n_sites=self.n_binaries,
                bond_dimension=convergence_params.ini_bond_dimension,
                numerical_noise=convergence_params.psi0_noise,
                tn_type=convergence_params.tn_type,
                tn_backend=tensor_backend,
            )
            psi0_state.save_pickle(psi0_storing_file)
            tn_params = {"L": self.n_binaries, "continue_file": psi0_storing_file}
        elif convergence_params.psi0 == "tn_driver_product_state":
            if convergence_params.tn_type == 6:
                raise NotImplementedError(
                    "Starting from the driver product "
                    "state is not yet implemented for MPS."
                )
            psi0_storing_file = get_driver_product_state_via_tn_gss(
                n_sites=self.n_binaries,
                path_to_file="./tn_driver_product_states/",
                bond_dimension=convergence_params.ini_bond_dimension,
                tn_type=convergence_params.tn_type,
                tn_backend=tensor_backend,
            )
            tn_params = {"L": self.n_binaries, "continue_file": psi0_storing_file}
        else:
            # Was checked in another place already, but let's be clear
            # here as well
            raise QUBOSetUpError(
                "Tensor network state initialization option "
                f"{convergence_params.psi0} not available."
            )

        ## Instantiating the simulation
        tn_input_filename = (
            f"{convergence_params.tn_input_folder}input_{self.n_binaries}"
        )
        tn_output_filename = (
            f"{convergence_params.tn_output_folder}output_{self.n_binaries}"
        )
        tn_sampling_filename = (
            f"{convergence_params.tn_sampling_folder}psi_{self.n_binaries}"
        )
        if convergence_params.tn_io_extra_tag:
            tn_input_filename += f"_{convergence_params.tn_io_extra_tag}"
            tn_output_filename += f"_{convergence_params.tn_io_extra_tag}"
            tn_sampling_filename += f"_{convergence_params.tn_io_extra_tag}"
        makedirs(tn_input_filename, exist_ok=True)
        makedirs(tn_output_filename, exist_ok=True)
        makedirs(convergence_params.tn_sampling_folder, exist_ok=True)

        tn_obs += TNState2File(tn_sampling_filename, "U")

        simulator = QuantumGreenTeaSimulation(
            model=sg_ham,
            operators=tn_ops,
            convergence=convergence_params,
            observables=tn_obs,
            folder_name_input=tn_input_filename,
            folder_name_output=tn_output_filename,
            tn_type=convergence_params.tn_type,
            tensor_backend=2,
            mpo_mode=convergence_params.mpo_mode,
            has_log_file=True,
            store_checkpoints=False,
            py_tensor_backend=tensor_backend,
        )

        ## Running the ground-state search
        st_to_sol = time()
        simulator.run(params=tn_params, delete_existing_folder=True)
        self.time_to_solution = time() - st_to_sol

        ## Obtaining QUBO solution(s)
        gss_results = simulator.get_static_obs(tn_params)
        if n_eigenstates == 1:  ### Getting only the ground state
            tn_sg_config = [round(ss) for ss in gss_results["sz"]]
            try:
                self.solution = [self.spin_to_binary_config(tn_sg_config)]
                self.cost = [self.evaluate(sol) for sol in self.solution]
            except ValueError:  ### Get degeneracy in the ground state
                psi_gs = TTN.read(
                    filename=tn_sampling_filename + ".pklttn",
                    tensor_backend=tensor_backend,
                )
                tn_solutions = [
                    (
                        np.array(list(config), dtype=int)
                        ^ (
                            np.array(list(config), dtype=int) & 1
                            == np.array(list(config), dtype=int)
                        )
                    ).tolist()
                    for config in psi_gs.sample_n_unique_states(
                        num_unique=n_eigenstates
                    ).keys()
                ]
                tn_costs = [self.evaluate(sol) for sol in tn_solutions]
                self.cost, self.solution = zip(*sorted(zip(tn_costs, tn_solutions)))
        else:  ### Getting more than one low-energy solutions via sampling
            psi = TTN.read(
                filename=tn_sampling_filename + ".pklttn",
                tensor_backend=tensor_backend,
            )
            tn_solutions = [
                (
                    np.array(list(config), dtype=int)
                    ^ (
                        np.array(list(config), dtype=int) & 1
                        == np.array(list(config), dtype=int)
                    )
                ).tolist()
                for config in psi.sample_n_unique_states(
                    num_unique=n_eigenstates
                ).keys()
            ]
            tn_costs = [self.evaluate(sol) for sol in tn_solutions]
            self.cost, self.solution = zip(*sorted(zip(tn_costs, tn_solutions)))
        # -----------------------------------
        # -----------------------------------

    def solve(
        self,
        solver="tensor-network",
        n_solutions=1,
        rescale_couplings=True,
        tn_convergence_parameters=None,
        tensor_backend=TensorBackend(),
    ):
        """
        Solve the QUBO problem with a specific ``solver``.

        **Arguments**

        solver : str, optional
            The method to be used for performing
            the ground-state search of the mapped
            spin glass Hamiltonian. Options are
            ``tensor-network``, ``exact`` and ``brute-force``.
            Default to ``tensor-network``.
        n_solutions : int, optional
            The number of optimal or near-optimal
            solutions to be computed with the given
            ``solver``.
            Default to 1, i.e., the solver searches
            only for the ground state of the mapped
            spin glass Hamiltonian. This arguments does
            not affect the ``brute-force`` solver.
        rescale_couplings : bool, optional
            If True, the couplings defining the
            corresponding spin glass model are
            rescaled in [-1, 1].
            This arguments does not affect the
            ``brute-force`` solver.
            Default to True.
        tn_convergence_params : instance of :class:`QUBOConvergenceParameter`
            The convergence parameters for the QUBO solver
            simulation based on tensor network methods.
            Default to None, meaning no tensor network method
            is used to solve the QUBO.
        tensor_backend : :class:`qtealeaves.tensors.TensorBackend`, optional
            Setup for tensor backend that defines the complete
            backend to be used for the tensors.
            Default to TensorBackend(), meaning that the underlying
            class for tensors is :class:`qtealeaves.tensors.QteaTensor`,
            the device for both the memory and the computations is
            the CPU and the data type of the tensors is np.complex128,
            i.e., double precision complex.
            You can pass different backend for the tensor class, for
            example pytorch running on GPUs, or use a mixed device
            for memory and computations with CPU + GPU.
            More details can be found both in `qtealeaves` and
            `qredtea`.

        **Returns**

        None
        """

        # Checking method arguments
        if solver not in ["brute-force", "exact", "tensor-network"]:
            raise NotImplementedError(f"QUBO solver {solver} not available.")

        # Solving the QUBO problem
        ## Brute force
        if solver == "brute-force":
            self.solve_via_brute_force()
            return

        ## Mapping into spin glass
        sg_model = self.to_spinglass_couplings()
        if rescale_couplings:
            sg_model = self.renormalize_spinglass_couplings(sg_model)

        # Ground-state search
        if solver == "tensor-network":
            self.solve_via_tn_ground_state_search(
                spinglass_model=sg_model,
                convergence_params=tn_convergence_parameters,
                n_eigenstates=n_solutions,
                tensor_backend=tensor_backend,
            )
        elif solver == "exact":
            self.solve_via_exact_sorting(sg_model, n_solutions)

    def prettyprint(self):
        """
        Pretty print method to visualize
        the QUBO matrix to standard output.

        **Arguments**

        None

        **Returns**

        None
        """

        # Determining the maximum width of each column
        col_widths = [
            max(len(str(item)) for item in col) for col in zip(*self.qubo_matrix)
        ]

        # Constructing the format string for each row
        row_format = "  |  ".join(["{{:{}}}".format(width) for width in col_widths])

        # Printing each row using the format string
        print("QUBO matrix\n-------------")
        for row in self.qubo_matrix:
            print(row_format.format(*row))

    def _save_to_cplex_lp(self, filename):
        """
        Save the QUBO matrix to an LP file.

        **Arguments**

        filename : str
            The full path (with the ".lp" extension)
            to the LP log file where the QUBO matrix
            will be written.

        **Returns**

        None
        """

        # Start writing to the LP file
        with open(filename, "w") as lp_file:
            # Writing the objective function
            lp_file.write("Minimize\n")
            lp_file.write(" obj: ")

            terms = []

            # Adding linear terms (diagonal elements)
            for jj in range(self.n_binaries):
                if self.qubo_matrix[jj, jj] != 0:
                    terms.append(f"{self.qubo_matrix[jj, jj]:+.20f} x{jj}")

            # Adding quadratic terms (off-diagonal elements)
            for jj in range(self.n_binaries):
                for kk in range(jj + 1, self.n_binaries):
                    if self.qubo_matrix[jj, kk] != 0:
                        terms.append(
                            f"{2 * self.qubo_matrix[jj, kk]:+20f} x{jj} * x{kk}"
                        )

            # Writing all terms of the objective function
            lp_file.write(" ".join(terms) + "\n")

            # Binary constraints for each variable
            lp_file.write("\nSubject To\n")
            lp_file.write("\nBounds\n")

            for jj in range(self.n_binaries):
                lp_file.write(f" 0 <= x{jj} <= 1\n")

            # Declaring the variables as binary
            lp_file.write("\nBinary\n")
            for jj in range(self.n_binaries):
                lp_file.write(f" x{jj}\n")

            lp_file.write("\nEnd\n")

    def save_to_file(self, filename, ftype):
        """
        Save the QUBO matrix to a log file.

        **Arguments**

        filename : str
            The full path (without the extension)
            to the log file where the QUBO matrix
            will be written in the specified ``ftype``
            extension.

        ftype : str, optional
            The (allowed) extension of the
            output log file.

        **Returns**

        None
        """

        if ftype not in ["json", "txt", "lp"]:
            raise NotImplementedError(f"Format {ftype} not supported.")
        filename += f".{ftype}"

        if ftype == "json":  ### jsonify the QUBO matrix
            jsonified_qubo = self.qubo_matrix.tolist()
            with codecs.open(filename, "w", encoding="utf-8") as out_file:
                json.dump(
                    obj=jsonified_qubo,
                    fp=out_file,
                    separators=(",", ":"),
                    sort_keys=True,
                    indent=4,
                )
        elif ftype == "txt":  ### textify the QUBO matrix
            with open(filename, "w") as out_file:
                out_file.write("# " + "-" * 79)
                out_file.write(
                    f"\n# [n = {self.n_binaries}] \t n: QUBO problem binaries\n"
                )
                out_file.write("# " + "-" * 79 + "\n#\n")
                out_file.writelines(
                    f"{row_idx}\t{col_idx}\t{value:.20e}\n"
                    for (row_idx, col_idx), value in np.ndenumerate(self.qubo_matrix)
                    if col_idx >= row_idx
                )
                out_file.write("# END\n")
        elif ftype == "lp":  ### save to the standard CPLEX LP format
            self._save_to_cplex_lp(filename)

    # -------------------------------------------
    # -------------------------------------------

    # Static methods
    # -------------------------------------------
    @staticmethod
    def spin_to_binary_config(spin_configuration):
        r"""
        Implement the conversion from spin 1/2
        variables to binary variables to recover
        a QUBO problem bitstring.
        The linear transformation

            - :math:`x = \\dfrac{1 + \\sigma}{2}`
            - :math:`x \in \\left\{0, 1\right\}` (binary variable)
            - :math:`\\sigma \in \\left\{+1, -1\right\}` (qubit variable`

        maps the 0-bit into spin-down and the 1-bit
        into spin-up.

        **Arguments**

        spin_configuration : List[int]
            The configuration of +1 and -1 representing
            the quantum expectation value of the
            Z-Pauli matrix on each site of the spin glass
            model (+1 means spin-up while -1 mean spin-down).

        **Returns**

        bitstring : List[int]
            The converted string of 0s and 1s.
        """

        # Converting qubits to binaries
        bitstring = []
        for spin in spin_configuration:
            if spin in {1, -1}:
                bitstring.append((1 + spin) // 2)
            else:
                raise ValueError("Measurement error: single spin must be up or down.")

        # Output
        return bitstring

    @staticmethod
    def renormalize_spinglass_couplings(spinglass_couplings, max_diff=100):
        """
        Rescale the couplings (local biases and two-spin
        interaction strengths) of the spin glass model
        associated with the QUBO matrix to the range [-1, 1]
        whenever the difference between the largest and the
        smallest value of the couplings exceeds ``max_diff``.

        **Arguments**

        spinglass_couplings : Dict
            The set of couplings defining the corresponding
            spin glass Hamiltonian, specifically:
                - 'offset': the constant term proportional
                            to the identity.
                            This energy offset does not influence
                            the solution of the QUBO problem, but it
                            is necessary to reconstruct the exact
                            value of the QUBO cost function, e.g.,
                            from the ground-state energy;
                - 'one-body': the set of single-body couplings,
                              i.e., the set of local longitudinal
                              magnetic fields (biases), one for each
                              spin-1/2 in the spin glass system;
                - 'two-body': the set of two-body (in general all-to-all)
                              couplings describing the interactions
                              between pairs of spin-1/2.
        max_diff : float, optional
            If the difference between the largest and the smallest
            values of the coupling strengths exceeds this number,
            the spin glass couplings are rescaled to [-1, 1].
            Default to 100.

        **Returns**

        rescaled_couplings : Dict
            The set of rescaled couplings defining the
            corresponding spin glass Hamiltonian, specifically:
                - 'offset': the constant term proportional
                            to the identity.
                            The offset is not affected by the rescaling;
                - 'max': the rescaling factor to get back the original
                         spin glass Hamiltonian couplings;
                - 'one-body': the set of rescaled single-body couplings,
                              i.e., the set of local longitudinal
                              magnetic fields (biases), one for each
                              spin-1/2 in the spin glass system;
                - 'two-body': the set of rescaled two-body (in general
                              all-to-all) couplings describing the
                              interactions between pairs of spin-1/2.
        """

        # Loading couplings
        rescaled_one_body = spinglass_couplings["one-body"]
        rescaled_two_body = spinglass_couplings["two-body"]

        # Ensuring that not all couplings are zero
        assert not (
            np.all(rescaled_one_body == 0) and np.all(rescaled_two_body == 0)
        ), QUBOProblemError(
            "The spin glass Hamiltonian resulting from the "
            "input QUBO is zero. Check-out your input QUBO problem."
        )

        # Computing the absolute values and grouping couplings
        abs_res_one_body = np.abs(rescaled_one_body)
        abs_res_two_body = np.abs(rescaled_two_body)
        abs_res_couplings = np.concatenate(
            (abs_res_one_body.ravel(), abs_res_two_body.ravel())
        )
        abs_res_couplings = abs_res_couplings[abs_res_couplings > 0]

        # Computing max and min of the absolute couplings
        min_abs_coupling = abs_res_couplings.min()
        max_abs_coupling = abs_res_couplings.max()

        # Renormalizing the couplings if needed
        if max_abs_coupling >= max_diff * min_abs_coupling:
            rescaled_couplings = {
                "offset": spinglass_couplings["offset"],
                "max": max_abs_coupling,
                "one-body": rescaled_one_body / max_abs_coupling,
                "two-body": rescaled_two_body / max_abs_coupling,
            }
        else:
            rescaled_couplings = spinglass_couplings.copy()
            rescaled_couplings["max"] = 1

        # Output
        return rescaled_couplings

    @staticmethod
    def _read_from_cplex_lp(filename):
        """
        Read a QUBO problem from a standard CPLEX LP file
        and construct the corresponding QUBO matrix.

        **Arguments**

        filename : str
            The full path (with the ".lp" extension)
            to the LP log file where the QUBO matrix
            will be read.

        **Returns**

        qubo_matrix : np.ndarray[float]
            The QUBO matrix constructed from the QUBO problem.
        """

        linear_terms = {}
        quadratic_terms = {}
        n_vars = 0

        # Defining REGular EXpressions for matching variables and coefficients
        linear_term_regex = re.compile(r"([+-]?\d*\.?\d+)\s*x(\d+)\b(?!\s*\*\s*x)")
        quadratic_term_regex = re.compile(r"([+-]?\d*\.?\d+)\s*x(\d+)\s*\*\s*x(\d+)\b")

        # Start reading the LP file
        with open(filename, "r") as file:
            in_objective = False
            for line in file:
                line = line.strip()

                # Findind the start of the objective function
                if line.startswith("Minimize"):
                    in_objective = True
                    continue

                # Ending objective function section
                if line.startswith("Subject To"):
                    in_objective = False
                    break

                # Parsing the objective function lines
                if in_objective:
                    # Matching linear terms h_j * x_j
                    for match in linear_term_regex.finditer(line):
                        coeff = float(match.group(1))
                        binary_index = int(match.group(2))
                        linear_terms[binary_index] = coeff
                        n_vars = max(n_vars, binary_index + 1)

                    # Matching quadratic terms J_jk * x_j * x_k
                    for match in quadratic_term_regex.finditer(line):
                        coeff = float(match.group(1)) / 2.0
                        binary1_idx = int(match.group(2))
                        binary2_idx = int(match.group(3))
                        quadratic_terms[(binary1_idx, binary2_idx)] = coeff
                        n_vars = max(n_vars, binary1_idx + 1, binary2_idx + 1)

        # Initializing the QUBO matrix
        qubo_matrix = np.zeros((n_vars, n_vars))

        # Populating the diagonal (linear terms)
        for idx, coeff in linear_terms.items():
            qubo_matrix[idx, idx] = coeff

        # Populating the off-diagonal (quadratic terms)
        for (idx1, idx2), coeff in quadratic_terms.items():
            qubo_matrix[idx1, idx2] = coeff
            ## Ensuring the symmetry
            qubo_matrix[idx2, idx1] = coeff

        return qubo_matrix

    # -------------------------------------------
    # -------------------------------------------

    # Class methods
    # -------------------------------------------
    @classmethod
    def read(cls, filename):
        """
        Initialize the QUBO problem from an input file.

        **Arguments**

        filename : str
            The full path to the file containing
            the QUBO problem as a matrix in a given
            (allowed) format.
            A check on file's extension is performed
            before reading.

        **Returns**

        obj : :class:`qtealeaves.optimization.QUBOSolver`
            The created QUBO solver object.
        """

        # Reading qubo from file depending on format
        _, file_ext = path.splitext(filename)
        if file_ext == ".json":
            with codecs.open(filename, "r", encoding="utf-8") as in_file:
                jsonified_data = in_file.read()
                unjsonified_qubo = json.loads(jsonified_data)
            obj = cls(np.array(unjsonified_qubo))
        elif file_ext == ".txt":
            row_idxs, col_idxs, qij = np.loadtxt(
                fname=filename, delimiter="\t", usecols=(0, 1, 2), unpack=True
            )
            qubo_size = int(np.max(col_idxs) + 1)
            qubo_matrix = np.zeros((qubo_size, qubo_size))
            for row_idx, col_idx, mel in zip(row_idxs, col_idxs, qij):
                qubo_matrix[int(row_idx)][int(col_idx)] = mel
            obj = cls(qubo_matrix)
        elif file_ext == ".lp":
            qubo_matrix = cls._read_from_cplex_lp(filename)
            obj = cls(qubo_matrix)
        else:
            raise NotImplementedError(
                f"There is no reader for the given file extension {file_ext}"
            )

        # Output
        return obj

    # -------------------------------------------
    # -------------------------------------------
