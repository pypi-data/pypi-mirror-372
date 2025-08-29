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
The module contains tools for the QUBO solvers in :mod:`qubo_solver`.
"""

# pylint: disable=too-many-locals
# pylint: disable=too-many-arguments

# Modules
# -----------------------------------------------
## Utils
from os import makedirs

## Maths and linear algebra
import numpy as np
import scipy.sparse as ssp
from scipy.sparse import csr_matrix as spmatrix

from qtealeaves.convergence_parameters import TNConvergenceParameters

## Quantum Green TEA
from qtealeaves.emulator import MPS, TTN
from qtealeaves.modeling import LocalTerm, QuantumModel
from qtealeaves.observables import TNObservables, TNState2File
from qtealeaves.operators import TNSpin12Operators
from qtealeaves.simulation import QuantumGreenTeaSimulation
from qtealeaves.tensors import TensorBackend

__all__ = [
    "create_exact_observables",
    "create_exact_spinglass_hamiltonian",
    "compute_exact_spectrum",
    "measure_exact_observables",
    "generate_perturbation_transverse_fields",
    "get_exact_driver_product_state",
    "get_driver_product_state_via_tn_gss",
]
# -----------------------------------------------
# -----------------------------------------------


## ==================================================
## Spin glass Hamiltonians: exact ground-state search
## ==================================================
def create_exact_observables(number_of_spins):
    """
    Construct the observables as many-body
    operators represented as sparse matrices.

    **Arguments**

    number_of_spins : int
        The number of spins in the system.

    **Returns**

    observables : Dict
        A dictionary containing the
        observables as 2D sparse scipy
        matrices.
        The name of the observable is
        the key, the operator matrix
        representing the observable is
        the value.
    """

    # Constructing single-site spin glass operators
    zpauli = spmatrix([[1, 0], [0, -1]])

    # Constructing the full (tensor product) operators
    # acting on the whole system
    # Z_site = I \otimes I \otimes ... \otimes Z_site \otimes ... \otimes I
    full_zpauli_operators = [
        ssp.kron(
            A=ssp.kron(A=ssp.identity(2**site, format="csr"), B=zpauli, format="csr"),
            B=ssp.identity(2 ** (number_of_spins - site - 1), format="csr"),
            format="csr",
        )
        for site in range(number_of_spins)
    ]

    # Output
    return {"sz": full_zpauli_operators}


def create_exact_spinglass_hamiltonian(
    spinglass_couplings, one_body_terms_prefactor=1.0, two_body_terms_prefactor=1.0
):
    """
    Construct the exact 2D matrix representation
    of a spin glass Hamiltonian operator characterized
    by ``spinglass_couplings``.

    **Arguments**

    spinglass_couplings : Dict
        The set of couplings defining the spin
        glass Hamiltonian, specifically
            - 'offset': the constant term proportional
                        to the identity.
                        This energy offset does not influence
                        the spectrum of the spin glass system,
                        but it is necessary to reconstruct the
                        exact energy values of the eigenstates
                        encoding spin configurations,
            - 'one-body': the set of single-body couplings,
                          i.e., the set of local longitudinal
                          magnetic fields (biases), one for each
                          spin-1/2 in the spin glass system;
            - 'two-body': the set of two-body (in general all-to-all)
                          couplings describing the interactions
                          between pairs of spin-1/2.
    one_body_terms_prefactor : float, optional
        The multiplicative prefactor of the spin glass
        local biases terms.
        Default to 1.0.
    two_body_terms_prefactor : float, optional
        The multiplicative prefactor of the spin-spin
        interaction-strength terms.
        Default to 1.0.

    **Returns**

    ham_matrix : csr_matrix[float]
        The 2D scipy sparse matrix representing
        the spin glass Hamiltonian matrix as a
        many-body operator.
    """

    # Initialization
    n_spins = spinglass_couplings["one-body"].size
    zpauli = spmatrix([[1, 0], [0, -1]])

    # Building the Hamiltonian matrix
    ham_matrix = spmatrix((2**n_spins, 2**n_spins))

    # Adding one-body terms
    for site, bias in enumerate(spinglass_couplings["one-body"]):
        ham_matrix += (
            one_body_terms_prefactor
            * bias
            * ssp.kron(
                A=ssp.kron(
                    A=ssp.identity(2**site, format="csr"), B=zpauli, format="csr"
                ),
                B=ssp.identity(2 ** (n_spins - site - 1), format="csr"),
                format="csr",
            )
        )

    # Adding long-range two-spin interactions
    jmat = two_body_terms_prefactor * spinglass_couplings["two-body"]
    for site1 in range(n_spins - 1):
        for site2 in range(site1 + 1, n_spins):
            mel = jmat[site1, site2]
            if mel != 0:
                ham_matrix += mel * ssp.kron(
                    A=ssp.kron(
                        A=ssp.kron(
                            A=ssp.kron(
                                A=ssp.identity(2**site1, format="csr"),
                                B=zpauli,
                                format="csr",
                            ),
                            B=ssp.identity(n=2 ** (site2 - site1 - 1), format="csr"),
                            format="csr",
                        ),
                        B=zpauli,
                        format="csr",
                    ),
                    B=ssp.identity(2 ** (n_spins - site2 - 1), format="csr"),
                    format="csr",
                )

    # Output
    return ham_matrix


def compute_exact_spectrum(ham_matrix, number_of_eigenstates=1):
    """
    Compute the exact spectrum of a many-body
    classical Hamiltonian.
    The following implementation stems directly
    from the classical nature of the Hamiltonian,
    indicating that the matrix representing the
    Hamiltonian operator is diagonal in the chosen
    (computational) basis.

    **Arguments**

    ham_matrix : csr_matrix[float]
        The 2D scipy sparse matrix representing
        the Hamiltonian operator.
    number_of_eigenstates : int, optional
        The fist ``number_of_eigenstate`` states
        to be computed.
        Default to 1, i.e., only the ground state.

    **Returns**

    spectrum : List[List[float, np.ndarray[float]]]
        The target number of eigenstates
        and associated exact energies in
        the Hamiltonian spectrum.
        The output is a list of exact
        [energy, eigenstate] sorted in
        ascending order w.r.t. the energy
        values.
    """

    # Getting the diagonal elements of the Hamiltonian matrix
    energies = ham_matrix.diagonal()
    hilbert_space_dim = energies.size

    # Checking the required number of eigenstates
    if not 0 < number_of_eigenstates <= hilbert_space_dim:
        raise ValueError(
            "The number of eigenstates "
            "must be between 1 and the "
            "dimension of the Hilbert space."
        )

    # Constructing the required spectrum
    if number_of_eigenstates == hilbert_space_dim:  ### Full spectrum
        eigs_idxs = np.arange(hilbert_space_dim)
    else:  ### Partial spectrum
        eigs_idxs = np.argpartition(energies, number_of_eigenstates)[
            :number_of_eigenstates
        ]
        eigs_idxs = eigs_idxs[np.argsort(energies[eigs_idxs])]
    spectrum = [
        [energies[ii], np.bincount([ii], minlength=hilbert_space_dim)]
        for ii in eigs_idxs
    ]

    # Output
    return spectrum


def measure_exact_observables(observables, exact_spectrum):
    r"""
    Measure observables on the exact eigenstates
    of a classical many-body Hamiltonian.

    **Arguments**

    observables: Dict
        The dictionary that holds information
        on the observables to be measured as
        many-body operators.
        See for example :func:`create_exact_observables`
    exact_spectrum : List[List[float, np.ndarray[float]]]
        The set of lists [energy, eigenvector]
        obtained via the exact computation of
        a classical many-body Hamiltonian.
        See for example :func:`compute_exact_spectrum`.

    **Returns**

    expectation_values : Dict
        The dictionary that contains the quantum
        average of each observable to be measured
        on the exact eigenstates of the many-body
        Hamiltonian, i.e.,

        .. math::

            \left\langle \psi
            \left\vert \mathcal{O} \right\vert
            \psi \right\rangle

        where :math:`\mathcal{O}` is the quantum
        operrator representing the desired observables.
    """

    # Measuring the one-body Z-Pauli matrix on each site
    bitstrings = [
        [
            round((np.conj(level[1]).T).dot(operator.dot(level[1])).item())
            for operator in observables["sz"]
        ]
        for level in exact_spectrum
    ]

    # Output
    return {"sz": bitstrings}


## =========================================
## Tensor network ground-state search: utils
## =========================================
def generate_perturbation_transverse_fields(
    model_local_hfields, ratio, sign_mode="random"
):
    """
    Generate a set of local random inhomogeneous
    transverse fields to add a quantum X-Pauli term
    at each site to the classical spin glass Hamiltonian.
    This could improve the ground-state search via
    tensor network optimization, helping to escape local
    minima of the glassy energy landscape.
    These transverse fields are randomly drawn, with their
    magnitude determined by the average value of the local
    longitudinal magnetic fields, i.e., the spin glass local
    biases of the classical Hamiltonian.

    **Arguments**

    model_local_hfields : np.ndarray[float]
        The set of local longitudinal magnetic
        fields, i.e., the local spin glass biases,
        related to the classical Z-Pauli terms in
        the classical spin glass Hamiltonian.
    ratio : float
        The ratio of the magnitude of the strength
        of the classical longitudinal terms (Z-Pauli)
        to the quantum off-diagonal transverse field
        terms (X-Pauli) to be added.
        This ratio controls the magnitude of the
        transverse field perturbation relative to
        the classical Hamiltonian, whose ground state
        must be determined.
    sign_mode : str, optional
        The sign of the local random transverse fields.
        Three possible choices are available for this
        argument:
            - "same": use the same sign w.r.t. the
                      mean direction of the classical
                      longitudinal fields;
            - "opposite": using the opposite sign w.r.t.
                          the mean direction of the
                          classical longitudinal fields;
            - "random": using random signs w.r.t. the
                        mean direction of the classical
                        longitudinal fields;
        Default to ``random``.

    **Returns**

    transverse_hfields : np.ndarray[float]
        The set of random local transverse fields
        to be added as X-Pauli couplings to the
        classical spin glass Hamiltonian.
    """

    # Computing the mean value of the spin glass local biases
    sign_of_sg_biases = np.sign(np.mean(model_local_hfields))
    abs_model_local_hfields = np.abs(model_local_hfields)
    mean_model_local_hfields = np.mean(abs_model_local_hfields)
    order_of_magnitude = mean_model_local_hfields / ratio

    # Generating local random transverse fields
    size = model_local_hfields.size
    if sign_mode == "random":
        transverse_hfields = np.random.uniform(
            low=-order_of_magnitude, high=order_of_magnitude, size=size
        )
    elif sign_mode in {"same", "opposite"}:
        sign_multiplier = 1 if sign_mode == "same" else -1
        transverse_hfields = sign_of_sg_biases * np.random.uniform(
            low=order_of_magnitude, high=2 * order_of_magnitude, size=size
        )
        transverse_hfields *= sign_multiplier
    else:
        raise NotImplementedError(
            f"Sign mode '{sign_mode}' of transverse fields not available."
        )

    # Output
    return transverse_hfields


def get_exact_driver_product_state(
    n_sites,
    bond_dimension=1,
    numerical_noise=1e-7,
    tn_type=5,
    tn_backend=TensorBackend(),
):
    r"""
    Construct the product state

    .. math::

        {\left\vert+\right\rangle}^{\otimes n}

    to be used as an initial state for a tensor
    network ground-state search. Here, :math:`n`
    is the number of sites.
    This product state is exactly constructed by hand
    but it can be represented as a tensor network state
    at a given bond dimension by padding properly
    the tensors.

    **Arguments**

    n_sites : int
        The number of physical sites of the
        tensor network.
    bond_dimension : int, optional
        The bond dimension of the created
        product state.
        Default to 1.
    numerical_noise : float, optional
        Numerical noise for creating a
        product state with bond dimension
        greater than 1.
    tn_type : int, optional
        The ansatz to be used for approximating the
        wave function of the mapped spin glass system.
        Available topologies are ``TTN`` (use 5) for
        Tree Tensor Networks and ``MPS`` (use 6) for
        Matrix Product States.
        Default to ``TTN`` (5).
    tn_backend : :class:`qtealeaves..tensors.TensorBackend`, optional
        The backend for the tensors in the the
        initial tensor network state.
        Default to `TensorBackend()`.

    **Returns**

    psi : :class:`qtealeaves.emulator.TTN` | :class:`qtealeaves.emulator.MPS`
        The created TTN product state.
        When the tensor network ansatz for the
        initial state is MPS, the TTN is converted
        to the corresponding MPS.
    """

    # Creating the local state |+>
    local_plus_state = np.full((n_sites, 2), 1 / np.sqrt(2))

    # Creating the product state as a tree tensor network
    psi = TTN.product_state_from_local_states(
        mat=local_plus_state,
        padding=[bond_dimension, numerical_noise],
        convergence_parameters=TNConvergenceParameters(
            max_bond_dimension=bond_dimension
        ),
        tensor_backend=tn_backend,
    )

    if tn_type == 6:
        psi = MPS.from_tensor_list(psi.to_mps_tensor_list())

    # Output
    return psi


def get_driver_product_state_via_tn_gss(
    n_sites,
    path_to_file,
    bond_dimension,
    input_folder=None,
    output_folder=None,
    tn_type=5,
    tn_backend=TensorBackend(),
):
    r"""
    Construct the product state

    .. math::

        {\left\vert+\right\rangle}^{\otimes n}

    to be used as an initial state for a tensor
    network ground-state search. Here, :math:`n`
    is the number of sites.
    This product state is obtained by performing
    the ground-state search of the driver Hamiltonian
    using a bond dimension of ``bond_dimension``.

    **Arguments**

    n_sites : int
        The number of physical sites of the
        tensor network.
    filename : str
        The full path of the file where the
        generated product state is stored.
    bond_dimension : int, optional
        The bond dimension of the created
        product state.
        Default to 1.
    input_folder : str, optional
        The full path to the folder where
        input data for this ground-state
        search are stored.
        Default to None, i.e., a default
        path will be used.
    output_folder : str, optional
        The full path to the folder where
        output data for this ground-state
        search are stored.
        Default to None, i.e., a default
        path will be used.
    tn_type : int, optional
        The ansatz to be used for approximating the
        wave function of the mapped spin glass system.
        Available topologies are ``TTN`` (use 5) for
        Tree Tensor Networks and ``MPS`` (use 6) for
        Matrix Product States.
        Default to ``TTN`` (5).
    tn_backend : :class:`qtealeaves..tensors.TensorBackend`, optional
        The backend for the tensors in the the
        initial tensor network state.
        Default to `TensorBackend()`.

    **Returns**

    The full path to the file where the
    initial tensor-network product state
    is stored. This file path can be used
    as a starting point to solve the QUBO
    problem within the tensor network solver.
    """

    # Building the driver Hamiltonian
    hdriver = QuantumModel(1, "L", name="Driver Hamiltonian")
    hdriver += LocalTerm("sx")

    # Preparing the ground-state search
    makedirs(path_to_file, exist_ok=True)
    state_filename = f"{path_to_file}psi0_{n_sites}"
    tn_obs = TNObservables()
    tn_obs += TNState2File(name=state_filename, formatting="U")
    tn_ops = TNSpin12Operators()
    tn_params = {"L": n_sites}
    tn_conv_params = TNConvergenceParameters(
        max_bond_dimension=bond_dimension, data_type="C"
    )
    tn_input_folder = input_folder or f"./tn_driver_product_state_input_{n_sites}"
    tn_output_folder = output_folder or f"./tn_driver_product_state_output_{n_sites}"
    simulator = QuantumGreenTeaSimulation(
        model=hdriver,
        operators=tn_ops,
        convergence=tn_conv_params,
        observables=tn_obs,
        folder_name_input=tn_input_folder,
        folder_name_output=tn_output_folder,
        tn_type=tn_type,
        tensor_backend=2,
        has_log_file=True,
        store_checkpoints=False,
        py_tensor_backend=tn_backend,
    )

    # Running the ground-state search
    simulator.run(params=tn_params, delete_existing_folder=True, nthreads=1)
    sim_res = simulator.get_static_obs(tn_params)

    # Output
    return sim_res[state_filename]
