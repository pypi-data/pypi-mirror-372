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
Module defining the convergence parameters for tensor network simulations.
"""

# pylint: disable=too-many-branches
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

import logging
from copy import deepcopy

from qtealeaves.tooling import QTeaLeavesError
from qtealeaves.tooling.parameterized import _ParameterizedClass

__all__ = [
    "TNConvergenceParameters",
]

logger = logging.getLogger(__name__)


# pylint: disable-next=dangerous-default-value
def logger_warning(*args, storage=[]):
    """Workaround to display warnings only once in logger."""
    if args in storage:
        return

    storage.append(args)
    logger.warning(*args)


# pylint: disable-next=too-many-instance-attributes
class TNConvergenceParameters(_ParameterizedClass):
    """
    Handling of the convergence parameters for the tensor network
    simulations.

    How-to
    ------

    The arguments can be parameterized for a set of simulations, so any
    of the types should read as follow:

    * (X, str, callable): expecting type X, but if str is passed, we check the
      simulation parameter dictionary's keys or if callable we call the
      function with the simulation parameter dictionary.
    * (X, str, callable, list): expection type X or List[X] as the parameter
      can be modified from sweep to sweep. If list, it has to have (at least)
      `max_iter` entries. Again, str as dictionary key or callable is allowed
      to generate values.
    * (str, callable) and (str, callable, list) : expecting type str, if you
      plan to use a dictionary key, do not use one of the allowed values.

    Arguments
    ---------

    max_bond_dimension : int | str | callable | list, optional
        Maximal bond dimension, e.g., number of singular values in the ansatz.
        The default of 5 is meant for sketching simulations and has to be
        adapted according to the entanglement in the system.
        Default to 5.

    cut_ratio : float, optional (python side only)
        Control which singular values are truncated during splitting tensors.
        Either relative values or truncated norm can be considered. This fine
        tuning can be set via `trunc_method`.
        Default to 1e-9

    Arguments: ansatz (advanced settings)
    -------------------------------------

    ini_bond_dimension : int | str | callable, optional
        The initial bond dimension used during the simulations when the
        initialization is random. The main target is statics simulations. Using
        subspace expansion or two-site updates the bond dimension can grow.
        Default to max_bond_dimension (via `None`).

    min_bond_dimension : int | str | callable, optional
        Set the minimum bond dimension. It is one value independent of
        the sweeps. It will be active during statics and dynamics and especially
        targets simulation which use single tensor updates.
        Default to 1.

    data_type : str | callable | list, optional
        Data type of the TN, which targets static simulations and can be varied
        for each sweep.
        "A" : automatic (results currently in "Z")
        "Z" : double precision complex
        "C" : single precision complex
        "D" : double precision real
        "S" : single precision real
        Default to "A"

    device : str | callable | list, optional
        "cpu" : run on cpu
        "gpu" : run on gpu
        "cpu+gpu" : mixed-memory mode
        "cgpu" : mixed-memory mode (deprecated)
        Fortran: no mixed-device mode available.
        Default to "cpu"

    Arguments: statics
    ------------------

    max_iter : int | str | callable, optional
        Maximum number of sweeps in the ground state search.
        Default to 20.

    statics_method : integer | str | callable, optional
        Method to run ground state search for this/all iteration.
        0 : default/auto (internally e.g., to 2 for ground state search)
        1 : sweep
        2 : sweep with space expansion (can still be reduced to sweep
            during the simulation based on a energy condition)
        3 : imaginary time evolution with two-tensor TDVP
        4 : imaginary time evolution with TDVP space expansion
        5 : imaginary time evolution with TDVP single-tensor
        Fortran: no mode 4 and 5, but additional mode 33 for nearest-neighbor
        imginary time evolution via TEBD.
        Default to 0.

    abs_deviation : float | str | callable, optional
        Exit criterion for ground state search if the energy of the
        current sweep has an absolute per-sweep deviation from the
        previous data points below this threshold:
        :math:`max(|E - E_{last}|) / n_points_conv_check
        < abs_deviation`
        Default to 4e-12.

    rel_deviation : float, optional
        Exit criterion for ground state search if the energy of the
        current sweep has a relative per-sweep deviation from the
        previous data points below this threshold.
        :math:`max(|E - E_{last}|) / n_points_conv_check
        < rel_deviation * |E_{last}|`
        Default to 1e-12.

    target_energy : float | None, optional
        Exit criterion for ground state search if a target
        energy is below this threshold.
        Default to None (criterion ignored).

    noise : float | list | callable, optional
        Noise is added to each tensor before local optimization.
        Useful for escaping local minima.
        Default to 0.

    n_points_conv_check : int, optional
        Number of data points used when checking convergence, e.g.,
        for the ground state search. Exit criteria are not checked
        until this many sweeps have been performed, and are never
        checked if `n_points_conv_check > max_iter`.
        Default to 4. It must be >= 2.

    measure_obs_every_n_iter : int | str | callable, optional
        Modulo for measuring statics every n iterations. If -1,
        no additional measurements. It can be activated, but
        intermediate measurements are only read automatically
        for finite temperature.
        Default to -1 (ignored)

    max_kraus_dimension : int, optional
        The maximal Kraus dimension used during the simulations.
        The default value is purely a starting point for testing
        simulations. For the TTO, for example, the Kraus dimension
        is the dimension of the top link.
        Default to 25.

    target_energy : float | str | callable | None, optional
        Exit criterion for ground state search if a target
        energy is below this threshold.
        Default to None (criterion ignored).

    imag_evo_dt : float | str | callable, optional
        Time-step size for the imaginary time evolution.
        Default to 0.1.

    random_sweep : bool | str | callable | list, optional
        Use random sweep scheme instead of default scheme.
        Default to False.
        Fortran: isometrization is still done, only considered if working with
        space-link expansion.

    skip_exact_rgtensors : logical | str | callable | list, optional
        Allows to skip space expansion if the tensors has already
        reached the maximal bond dimension, see details below.
        Fortran: only considered in sweeps with space-link expansion.
        Default to False.

    Arguments: statics (advanced settings: space-link expansion)
    ------------------------------------------------------------

    min_expansion : int | str | callable | list, optional
        Amount by which the bond dimension is increased at
        every expansion cycle when doing link expansion.
        Default to 20.

    expansion_cycles : int | str | callable | list, optional
        For space link expansion, the link between a tensor and its predefined
        partner tensor are expanded. Then, each tensor and partner tensors
        are optimized `expansion_cycles` times.
        Default to 1.

    expansion_drop : str out of ["f", "o", "d"] | callable | list, optional
        Specifies what to do if space link expansion leads to worse energy
        than before with options expansion_drop="f" for false (accept
        worse energies to escape local minima), "o" for optimize single
        tensor (reinstall original tensors, but optimize as in a single
        tensor update), and "d" for discarding step (reinstall original
        tensors and skip optimization).
        Default to "f".

    Arguments: statics (advanced settings: disentangler)
    ----------------------------------------------------

    de_opt_strategy : str, optional
        The strategy to optimize disentanglers.
        Can be 'mera' or 'backpropagation'.
        Defaults to 'mera'.

    de_opt_start_after_sweeps : int | str | callable, optional
        Start the disentangler optimization only after performing
        this many sweeps without them.
        Default to 1.

    de_opt_max_iter : int | str | callable, optional
        Maximum number of iterations for the optimization of a disentangler.
        Default to 10.

    de_opt_rel_deviation : float | str | callable, optional
        Relative exit criterion for the disentangler optimization.
        Default to 1e-12.

    de_opt_learning_rate_strategy : callable | None, optional
        The function controlling the learning rate per each step for
        the optimization of disentanglers with backpropagation.
        Should have only one argument, the step counter.
        The default option: 20 learning steps (increasing lr exponentially
        from 1e-6 to 0.1), and de_opt_max_iter - 10 steps
        with exponential decrease of the lr to 1e-6.
        Only applies to the 'backpropagation' strategy.
        Default to None.

    de_opt_grad_clipping_value : float, optional
        Clipping the gradients in the backpropagation for disentanglers.
        Passed directly to torch.nn.utils.clip_grad_value_().
        Only for de_opt_strategy = 'backpropagation'.
        Default to 1e10.

    Arguments: decompositions (advanced settings)
    ---------------------------------------------

    trunc_method : str | callable, optional
        Method use to truncate the singular values.
        Available:
        - "R": use cut_ratio
            Cut ratio :math:`\\epsilon` after which the singular values are
            neglected, i.e. if :math:`\\lambda_1` is the bigger singular values
            then after an SVD we neglect all the singular values such that
            :math:`\\lambda_i/\\lambda_1\\leq\\epsilon`.
        - "N": use maximum norm
            Maximum value of the norm neglected for the singular values during
            the trunctation.
        Default to "R"

    trunc_tracking_mode : str | callable, optional
        Modus for storing truncation, 'M' for maximum, 'C' for
        cumulated of the singvals squared (Norm truncated, default).
        Default to "C"

    svd_ctrl : character | callable, optional
        Control for the SVD algorithm. Available:
        - "A" : automatic. Some heuristic is run to choose the best mode for the algorithm.
                The heuristic can be seen in tensors/tensors.py in the function _process_svd_ctrl.
        - "V" : gesvd. Safe but slow method. Recommended in Fortran simulation
        - "D" : gesdd. Fast iterative method. It might fail. Resort to gesvd if it fails
        - "E" : eigenvalue decomposition method. Faster on GPU. Available only when
                contracting the singular value to left or right
        - "X" : sparse eigenvalue decomposition method. Used when you reach the maximum
                bond dimension. Only python.
        - "R" : random SVD method. Used when you reach the maximum bond dimension.
                Only python.
        Fortran: method "R" and "X" are not available.
        Default to "V"

    min_expansion_qrte: int | float, optional
        Number of expansions for QRTE decomposition. The QRTE decomposition is an
        alternative to the QR/SVD and a bit experimental, probably tested in
        qmatchatea before. For the expanding QR, in which case the value is the
        percentage increase (for int, value / 100; float used as is).
        Default to 20.

    Arguments: Krylov solvers for statics and dynamics (advanced settings)
    ----------------------------------------------------------------------

    Note: the statics sets internally `arnoldi_tolerance` passed to the solvers,
    which cannot be modified directly and is set to machine precision inside the
    sweeps.

    arnoldi_maxiter : int | str | callable | list, optional
        Maximum number of iterations in the arnoldi method.
        Default to 32.

    arnoldi_tolerance_fallback : float | str | callable | list, optional
        Tolerance to use if the convergence with the arnoldi_tolerance fails.
        Fortran: TBA
        Default to 1e-2.

    arnoldi_tolerance_default : float | str | callable | list, optional,
        Default tolerance for the Arnoldi method for the single tensor if
        `arnoldi_tolerance` itself is not set. `arnoldi_tolerance` is set
        inside algorithms, but can be missing if we run eigensolver outside
        a ground state search or similar.
        Fortran: TBA
        optimization. Default to 1e-15.

    krylov_maxiter : int | str | callable, optional
        For time evolution and used in the KrylovSolver.
        Default to 32.

    krylov_tol : float
        Evaluated in KrylovSolver, time evolution only.
        Default to 1e-7.

    solver_reorthogonalize : int | None
        In each iteration of the eigen/exponentiation solver, the resulting vector is explicitly
        reorthogonalized with respect to last `solver_reorthogonalize` vectors in
        the Krylov basis. This refers to re-orthogonalization on top of the standard
        orthogonalization with respect to the last two vectors. Such additional reorthogonalization
        can be neccessary in some cases for numerical stability (or when input matrix is not
        Hermitian). If None, re-orthogonalization is done with respect to every vector in a basis
        (safest, but slowest option).
        Default to None.
        Remark: not propagated through non-Hermitian Krylov solver and DenseTensorEigenSolverH

    Deprecated
    ----------

    min_expansion : see expansion_min

    arnoldi_max_tolerance : see arnoldi_tolerance_fallback

    arnoldi_min_tolerance : see arnoldi_tolerance_default


    Details
    -------

    Skip exact renormalization group tensors

    Allows to skip space expansion if the tensors has already
    reached the maximal bond dimension of the underlying
    local Hilbert spaces, i.e., full Hilbert space is captured
    without truncation of entanglement. It does not introduce
    errors itself as the tensor represents a unitary transformation
    with a complete orthogonal set of vector; the idea originates in
    the renormalization group (RG) where combining two sites is a
    unitary transformation as long as the new link dimension is
    as big as the underlying Hilbert space of all local Hilbert
    spaces combined. As it mostly skips operators on
    tensors much below the bond dimension, the benefit lies
    in avoiding to move the isometry (see TTN and moving through higher
    layers), communication overhead for sending small tensors, and
    in the future jit-compilation for many different bond dimensions.
    We aim to filter before the sweep applied; avoids even isometrizing
    towards the skipped tensors.

    Lanczos/Krylov solvers

    The Lanczos/Arnoldi solver (statics) on the qtealeaves side will interally
    set the tolerance to `max(tolerance, eps)` if the tolerance is bigger than
    zero and with eps being the machine precision.
    """

    # pylint: disable-next=too-many-locals, too-many-arguments
    def __init__(
        self,
        *,  # keyword-only arguments follow
        max_bond_dimension=5,
        max_kraus_dimension=25,
        cut_ratio=1e-9,
        ini_bond_dimension=None,
        min_bond_dimension=1,
        data_type="A",
        device="cpu",
        max_iter=20,
        statics_method=2,
        abs_deviation=4e-12,
        rel_deviation=1e-12,
        noise=0.0,
        n_points_conv_check=4,
        measure_obs_every_n_iter=-1,
        target_energy=None,
        imag_evo_dt=0.1,
        random_sweep=False,
        skip_exact_rgtensors=False,
        expansion_min=20,
        expansion_cycles=1,
        expansion_drop="f",
        de_opt_strategy="mera",
        de_opt_start_after_sweeps=1,
        de_opt_max_iter=10,
        de_opt_rel_deviation=1e-12,
        de_opt_learning_rate_strategy=None,
        de_opt_grad_clipping_value=1e-10,
        trunc_method="R",
        trunc_tracking_mode="C",
        svd_ctrl="V",
        min_expansion_qrte=20,
        arnoldi_maxiter=32,
        arnoldi_tolerance_fallback=1e-2,
        arnoldi_tolerance_default=1e-15,
        krylov_maxiter=32,
        krylov_tol=1e-7,
        solver_reorthogonalize=None,
        min_expansion=None,
        arnoldi_min_tolerance=None,
        arnoldi_max_tolerance=None,
    ):
        # Handle deprecated arguments
        # ...........................

        if min_expansion is None:
            min_expansion = expansion_min
        else:
            logger_warning(
                "Deprecated: Passing min_expansion instead of expansion_min."
            )
            if expansion_min != 20:
                raise QTeaLeavesError(
                    "Passed argument and deprecated argument for expansion_min."
                )
            expansion_min = min_expansion

        if arnoldi_min_tolerance is None:
            arnoldi_min_tolerance = arnoldi_tolerance_default
        elif arnoldi_tolerance_default != 1e-15:
            raise QTeaLeavesError(
                "Passed argument and deprecated argument for arnoldi_tolerance_default."
            )
        else:
            logger_warning(
                "Deprecated: Passing arnoldi_min_tolerance instead of arnoldi_tolerance_default."
            )

        if arnoldi_max_tolerance is None:
            arnoldi_max_tolerance = arnoldi_tolerance_fallback
        elif arnoldi_tolerance_fallback != 1e-2:
            raise QTeaLeavesError(
                "Passed argument and deprecated argument for arnoldi_tolerance_fallback."
            )
        else:
            logger_warning(
                "Deprecated: Passing arnoldi_max_tolerance instead of arnoldi_tolerance_fallback."
            )

        # Convergence parameters for statics / decision on convergence
        self.max_kraus_dimension = max_kraus_dimension
        self.max_iter = max_iter
        self.abs_deviation = abs_deviation
        self.rel_deviation = rel_deviation

        # The disentangler optimization stuff
        self.de_opt_strategy = de_opt_strategy
        self.noise = noise
        self.de_opt_max_iter = de_opt_max_iter
        self.de_opt_rel_deviation = de_opt_rel_deviation
        self.de_opt_start_after_sweeps = de_opt_start_after_sweeps
        self.de_opt_learning_rate_strategy = de_opt_learning_rate_strategy
        self.de_opt_grad_clipping_value = de_opt_grad_clipping_value

        self.target_energy = target_energy
        if n_points_conv_check < 2:
            raise ValueError("Minimum number of points for convergence is 2")
        self.n_points_conv_check = n_points_conv_check
        self.measure_obs_every_n_iter = measure_obs_every_n_iter
        self.svd_ctrl = svd_ctrl
        self.min_bond_dimension = min_bond_dimension
        if ini_bond_dimension is None:
            self.ini_bond_dimension = max_bond_dimension
        else:
            self.ini_bond_dimension = ini_bond_dimension
        self.min_expansion_qrte = min_expansion_qrte

        # Consumed in python
        self.trunc_method = (
            trunc_method.upper() if trunc_method in ["r", "n"] else trunc_method
        )
        self.cut_ratio = cut_ratio
        self.arnoldi_maxiter = arnoldi_maxiter
        self.krylov_maxiter = krylov_maxiter
        self.krylov_tol = krylov_tol
        self.solver_reorthogonalize = solver_reorthogonalize
        self.trunc_tracking_mode = trunc_tracking_mode
        if self.trunc_tracking_mode in ["m", "c"]:
            self.trunc_tracking_mode = trunc_tracking_mode.upper()

        # Settings for one or all iterations
        self.sim_params = {}
        self.sim_params["max_bond_dimension"] = max_bond_dimension
        self.sim_params["random_sweep"] = random_sweep
        self.sim_params["skip_exact_rgtensors"] = skip_exact_rgtensors
        self.sim_params["min_expansion"] = min_expansion
        self.sim_params["expansion_cycles"] = expansion_cycles
        self.sim_params["expansion_drop"] = expansion_drop
        self.sim_params["noise"] = noise
        self.sim_params["arnoldi_min_tolerance"] = arnoldi_min_tolerance
        self.sim_params["arnoldi_max_tolerance"] = arnoldi_max_tolerance
        self.sim_params["statics_method"] = statics_method
        self.sim_params["imag_evo_dt"] = imag_evo_dt
        self.sim_params["data_type"] = data_type
        self.sim_params["device"] = device
        self.sim_params["solver_reorthogonalize"] = solver_reorthogonalize

        # For python side, consumed in qtealeaves-solver, can be set
        # by algorithm, but not by user so far. The reason is that
        # we want to be able to set this dynamically based on the target
        # precision in the current sweep in a ground state search or
        # similar use-cases.
        self.sim_params["arnoldi_tolerance"] = None

        # internal flag for data type conversion and delay for renormalizing
        self.data_type_switch = False

    def resolve_params(self, params, idx=None):
        """Resolve parameterized values (inplace-update)."""

        attr_numeric = [
            "max_iter",
            "abs_deviation",
            "rel_deviation",
            "n_points_conv_check",
            "measure_obs_every_n_iter",
            "cut_ratio",
            "krylov_maxiter",
            "arnoldi_maxiter",
            "min_bond_dimension",
            "max_kraus_dimension",
            "ini_bond_dimension",
            "de_opt_start_after_sweeps",
            "target_energy",
            "noise",
            "solver_reorthogonalize",
        ]
        attr_str = ["svd_ctrl", "trunc_method", "trunc_tracking_mode"]
        self._resolve_params_attr(params, attr_numeric, attr_str, idx=idx)

        # Settings for one or all iterations in dictionary
        str_params = ["data_type", "expansion_drop", "device"]

        new_dict = {}
        for key, value in self.sim_params.items():
            if key not in str_params:
                value = self.eval_numeric_param(value, params)
                if hasattr(value, "__len__") and idx is not None:
                    value = value[idx]
            else:
                value = self.eval_str_param(value, params)
                if not isinstance(value, str):
                    if hasattr(value, "__len__") and idx is not None:
                        value = value[idx]

            new_dict[key] = value

        self.sim_params = new_dict

    def resolve_params_copy(self, params, idx=None):
        """
        Return a copy of the convergence parameters with all parameterized
        values resolved.
        """
        resolved = deepcopy(self)
        resolved.resolve_params(params, idx=idx)

        return resolved

    def prepare_parameters_for_iteration(self, params):
        """
        Preparation to write parameters for each iteration. It checks
        if a list of convergence settings has to be written and builds
        a dictionary with the resolved entries for each parameters,
        which is either a value or a list of values.

        **Arguments**

        params : dict
            Dictionary with the simulation parameters.

        **Results**

        has_vector_of_settings : bool
            True if settings change over the iterations and
            the parameters have to be written for each iteration.

        sim_param_all : dict
            Contains the resolved convergence parameters, i.e.,
            strings and functions are resolved with the actual values.
        """
        max_iter = self.eval_numeric_param(self.max_iter, params)

        sim_params_all = {}
        has_vector_of_settings = False

        str_params = ["data_type", "expansion_drop", "device"]

        for key, value in self.sim_params.items():
            if isinstance(value, str):
                # Have to catch strings first as they have a length
                # attribute
                if key in str_params:
                    # String parameters
                    entry = self.eval_str_param(value, params)
                else:
                    # Numeric parameters
                    entry = self.eval_numeric_param(value, params)
            elif hasattr(value, "__len__"):
                # List of any kind
                if key in str_params:
                    # String parameters
                    entry = [
                        self.eval_str_param(value[ii], params)
                        for ii in range(len(value))
                    ]
                else:
                    # Numeric parameters
                    entry = [
                        self.eval_numeric_param(value[ii], params)
                        for ii in range(len(value))
                    ]
            else:
                # Scalar values (cannot be a str parameter, which
                # would go into the first if)
                entry = self.eval_numeric_param(value, params)

            if isinstance(entry, str):
                # String never activates list
                pass
            elif hasattr(entry, "__len__"):
                has_vector_of_settings = True
                if len(entry) != max_iter:
                    raise QTeaLeavesError(
                        "Length of convergence parameter list for "
                        + "%s must match " % (key)
                        + "max_iter=%d." % (max_iter)
                    )

            sim_params_all[key] = entry

        return has_vector_of_settings, sim_params_all

    @property
    def max_bond_dimension(self):
        """
        Provide the getter method for this property important to
        the MPS emulator. It allows to get values without a
        dictionary, but prevents doing it if the values is not
        an integer.
        """
        value = self.sim_params["max_bond_dimension"]
        if hasattr(value, "__len__"):
            value = value[0]

        if isinstance(value, int):
            return value

        raise QTeaLeavesError("Try to use getter on non-int bond dimension.")

    @property
    def data_type(self):
        """
        Provide the getter method for this property important to
        the MPS emulator. It allows to get values without a
        dictionary, but prevents doing it if the values is not
        an integer. (Not queried from the MPS for now).
        """
        value = self.sim_params["data_type"]
        if isinstance(value, str):
            # Value is string itself, return first
            return value

        if hasattr(value, "__len__"):
            value = value[0]
            return value

        raise QTeaLeavesError("Try to use getter on non-str data type.")

    @property
    def min_expansion_qr(self):
        """
        Provide the getter method for this property important to
        the python emulator. It is the percentage of the bond dimension
        increase in the qr
        """
        value = self.min_expansion_qrte
        if hasattr(value, "__len__"):
            value = value[0]

        if isinstance(value, int):
            return value / 100

        raise QTeaLeavesError("Try to use getter on non-valid min_expansion")

    def get_chi(self, params):
        """
        Shortcut to evaluate the bond dimension as numeric parameter.

        **Arguments**

        params : dict
            The parameter dictionary for the simulation.
        """
        return self.eval_numeric_param(self.sim_params["max_bond_dimension"], params)
