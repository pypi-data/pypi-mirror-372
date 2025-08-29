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
The module contains an abstract tensor network, from which other tensor
networks can be derived.
"""

# pylint: disable=too-many-lines, too-many-statements, too-many-branches, too-many-locals, too-many-arguments

import abc
import inspect
import json
import logging
import os
import pickle
from copy import deepcopy
from functools import partial
from time import time as tictoc

import mpmath as mp
import numpy as np
from joblib import Parallel, delayed

from qtealeaves.convergence_parameters import TNConvergenceParameters
from qtealeaves.tensors import TensorBackend
from qtealeaves.tensors.abstracttensor import _AbstractQteaTensor
from qtealeaves.tooling import (
    QTeaBackendError,
    QteaJsonEncoder,
    QTeaLeavesError,
    QTeaOPESError,
)
from qtealeaves.tooling.mpisupport import MPI, TN_MPI_TYPES

__all__ = [
    "postprocess_statedict",
    "MPI",
    "TN_MPI_TYPES",
]

logger = logging.getLogger(__name__)


# pylint: disable-next=dangerous-default-value
def logger_warning(*args, storage=[]):
    """Workaround to display warnings only once in logger."""
    if args in storage:
        return

    storage.append(args)
    logger.warning(*args)


# pylint: disable-next=too-many-public-methods, too-many-instance-attributes
class _AbstractTN(abc.ABC):
    """
    Abstract tensor network class with methods applicable to any
    tensor network.

    Parameters
    ----------

    num_sites: int
        Number of sites

    convergence_parameters: :py:class:`TNConvergenceParameters`
        Class for handling convergence parameters. In particular,
        in the python TN simulator, we are interested in:
        - the *maximum bond dimension* :math:`\\chi`;
        - the *cut ratio* :math:`\\epsilon` after which the singular
            values are neglected, i.e. if :math:`\\lamda_1` is the
            bigger singular values then after an SVD we neglect all the
            singular values such that
            :math:`\\frac{\\lambda_i}{\\lambda_1}\\leq\\epsilon`

    local_dim: int, optional
        Local dimension of the degrees of freedom. Default to 2.

    requires_singvals : boolean, optional
        Allows to enforce SVD to have singular values on each link available
        which might be useful for measurements, e.g., bond entropy (the
        alternative is traversing the whole TN again to get the bond entropy
        on each link with an SVD).

    tensor_backend : `None` or instance of :class:`TensorBackend`
        Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.
    """

    extension = "tn"
    has_de = False
    skip_tto = False

    def __init__(
        self,
        num_sites,
        convergence_parameters,
        local_dim=2,
        requires_singvals=False,
        tensor_backend=None,
    ):
        # Class attributes by arguments
        self._num_sites = num_sites
        self._local_dim = (
            [local_dim] * num_sites if np.isscalar(local_dim) else local_dim
        )
        self._convergence_parameters = convergence_parameters
        self._tensor_backend = (
            TensorBackend() if tensor_backend is None else tensor_backend
        )

        # Other class attributes
        self._iso_center = None
        self.eff_op = None
        self.eff_proj = []

        # internal storage for last energy measurement for algorithms which
        # need an estimate where it is sufficient to rely that this number
        # is not too outdated
        self._prev_energy = None

        # Selection of QR vs SVD
        self._requires_singvals = requires_singvals
        # store solver to be used
        self._solver = None

        # Attributes for MPI
        self.comm = None

        # ML wants to use iso_towards without QR/SVD (which is one super-special
        # use case of a binary label (or rounding approach) + single-tensor update.
        self._tn_ml_mode = None
        self._decomposition_free_iso_towards = False

        # Run checks on input
        # -------------------

        if not isinstance(convergence_parameters, TNConvergenceParameters):
            raise TypeError(
                "Convergence parameters must be TNConvergenceParameters class."
            )

        if not isinstance(self._tensor_backend, TensorBackend):
            raise TypeError(
                f"Passed wrong type {type(self._tensor_backend)} to backend."
            )

        if self._convergence_parameters.max_bond_dimension < 1:
            raise ValueError("The minimum bond dimension for a product state is 1.")

        if self._convergence_parameters.cut_ratio < 0:
            raise ValueError("The cut_ratio value must be positive.")

        if len(self.local_dim) != num_sites:
            raise ValueError(
                f"Length of local_dim {len(local_dim)} differs "
                f"from num_sites {num_sites}."
            )

        if np.min(self.local_dim) < 2:
            raise ValueError("Local dimension cannot be smaller than 2.")

        # internal variable for flex-TDVP
        self._timestep_mode_5_counter = 0

        # cache for local density matrices
        self._cache_rho = {}

        # MPI initialization
        self._initialize_mpi()

    # --------------------------------------------------------------------------
    #                               Properties
    # --------------------------------------------------------------------------

    @property
    def convergence_parameters(self):
        """Get the convergence settings from the TN."""
        return self._convergence_parameters

    @convergence_parameters.setter
    def convergence_parameters(self, value):
        """
        Set the convergence settings from the TN. (no immediate effect, only
        in next steps).
        """
        self._convergence_parameters = value

    @property
    def data_mover(self):
        """Get the data mover od the tensor."""
        return self._tensor_backend.datamover

    @property
    @abc.abstractmethod
    def default_iso_pos(self):
        """
        Returns default isometry center position, e.g., for initialization
        of effective operators.
        """

    @property
    def device(self):
        """Device where the tensor is stored."""
        return self._tensor_backend.device

    @property
    def memory_device(self):
        """Return the memory device stored in the tensor backend."""
        return self.tensor_backend.memory_device

    @property
    def computational_device(self):
        """Return the computational device stored in the tensor backend."""
        return self.tensor_backend.computational_device

    @property
    def dtype(self):
        """Data type of the underlying arrays."""
        for tensor in self._iter_tensors():
            return tensor.dtype

        return None

    def dtype_to_char(self):
        """
        Translate current data type of the tensor back to char C, D, S, Z, H, or I.
        """
        for tensor in self._iter_tensors():
            return tensor.dtype_to_char()

        raise QTeaLeavesError("Empty tensor network.")

    @property
    def dtype_eps(self):
        """Data type's machine precision of the underlying arrays."""
        for tensor in self._iter_tensors():
            return tensor.dtype_eps

        return None

    @property
    def iso_center(self):
        """Isometry center of the tensor network (int|tuple|None)"""
        return self._iso_center

    @iso_center.setter
    def iso_center(self, value):
        """Change the value of the iso center"""
        if isinstance(value, (int, tuple)):
            self._iso_center = value
        elif value is None:
            self._iso_center = None
        else:
            self._iso_center = tuple(value)

    @property
    def has_symmetry(self):
        """Check if TN is built out of symmetric tensors."""
        for tensor in self._iter_tensors():
            return tensor.has_symmetry

        return None

    @property
    def num_sites(self):
        """Number of sites property."""
        return self._num_sites

    @property
    def local_dim(self):
        """Local dimension property"""
        if isinstance(self._local_dim, int):
            # Constant Hilbert space
            return self._local_dim
        if isinstance(self._local_dim, np.ndarray):
            # Potentially different Hilbert spaces via numpy array
            return self._local_dim
        if isinstance(self._local_dim[0], (int, np.int64, np.int32)):
            # Potentially different Hilbert spaces via list, detect
            # cases without symmetry by checking first entry for int
            return self._local_dim
        # Case for symmetries
        return [elem.shape for elem in self._local_dim]

    @property
    def local_links(self):
        """Return information on local link (for symmetries more than integer)."""
        return self._local_dim

    @property
    def solver(self):
        """Return current solver for the TN."""
        return self._solver

    @solver.setter
    def solver(self, value):
        """Set the solver, e.g., currently used for exp(-i H dt) |psi>."""
        self._solver = value

    @property
    def tensor_backend(self):
        """Return tensor backend stored for this TN-ansatz."""
        return self._tensor_backend

    @property
    def tn_ml_mode(self):
        """
        Returning the tensor network machine learning mode used in
        machine learning.
        """
        return self._tn_ml_mode

    @tn_ml_mode.setter
    def tn_ml_mode(self, mode):
        valid_modes = [
            "linkfree",
            "linkfree_isofree",
            "labellink",
            "labellink_back",
            "labellink_conj",
            "linkfree_conj",
        ]
        future_modes = [
            "labelenv_back",
            "labelenv_back_isofree",
            "labelenv_back_fulltn",
        ]

        if mode in future_modes:
            raise NotImplementedError("TN-ML mode {mode=} is not yet enabled.")

        if mode not in valid_modes:
            raise ValueError(f"The TN-ML {mode=} is not available.")

        self._tn_ml_mode = mode

    @staticmethod
    def tn_mpi_types():
        """Provide convenient access to the `TN_MPI_TYPES` for TN ansaetze."""
        return TN_MPI_TYPES

    # --------------------------------------------------------------------------
    #                          Overwritten operators
    # --------------------------------------------------------------------------

    def __repr__(self):
        """
        Return the class name as representation.
        """
        return self.__class__.__name__

    def __len__(self):
        """
        Provide number of sites in the TN.
        """
        return self.num_sites

    # --------------------------------------------------------------------------
    #                       classmethod, classmethod like
    # --------------------------------------------------------------------------

    @classmethod
    @abc.abstractmethod
    def from_statevector(
        cls, statevector, local_dim=2, conv_params=None, tensor_backend=None
    ):
        """Decompose statevector to tensor network of chosen type."""

    @classmethod
    @abc.abstractmethod
    def from_density_matrix(
        cls, rho, n_sites, dim, conv_params, tensor_backend=None, prob=False
    ):
        """Decompose density matrix to tensor network of chosen type."""

    @classmethod
    @abc.abstractmethod
    def from_lptn(cls, lptn, conv_params=None, **kwargs):
        """Converts LPTN to tensor network of chosen type."""

    @classmethod
    @abc.abstractmethod
    def from_mps(cls, mps, conv_params=None, **kwargs):
        """Converts MPS to tensor network of chosen type."""

    @classmethod
    @abc.abstractmethod
    def from_ttn(cls, ttn, conv_params=None, **kwargs):
        """Converts TTN to tensor network of chosen type."""

    @classmethod
    @abc.abstractmethod
    def from_tto(cls, tto, conv_params=None, **kwargs):
        """Converts TTO to tensor network of chosen type."""

    # pylint: disable=inconsistent-return-statements
    @classmethod
    def from_x(cls, obj, conv_params=None, **kwargs):
        """
        Converts tensor network of type `x` to chosen type.

        Parameters
        ----------

        obj: :py:class:`_AbstractTN`
            object to convert to chosen type.

        conv_params: :py:class:`TNConvergenceParameters`, optional
            Input for handling convergence parameters
            Default is None.

        Return
        ------

        new_obj: chosen type decomposition of obj.
            If truncations are part of the underlying result, they
            are skipped.
        """
        if not isinstance(obj, _AbstractTN):
            raise TypeError(
                f"The input is not an abstract TN, but got type {type(obj)}."
            )
        from_x_dict = {
            "mps": cls.from_mps,
            "lptn": cls.from_lptn,
            "ttn": cls.from_ttn,
            "tto": cls.from_tto,
        }
        if obj.extension not in from_x_dict:
            raise TypeError(
                f"Input is of {type(obj)} and cannot be converted to {cls}."
            )

        result = from_x_dict[obj.extension](obj, conv_params, **kwargs)

        if isinstance(result, _AbstractTN):
            return result

        for elem in result:
            if isinstance(elem, _AbstractTN):
                return elem

    # pylint: enable=inconsistent-return-statements

    @classmethod
    @abc.abstractmethod
    def product_state_from_local_states(
        cls,
        mat,
        padding=None,
        convergence_parameters=None,
        tensor_backend=None,
    ):
        """Construct a product (separable) state in a suitable tensor network form, given the local
        states of each of the sites."""

    @classmethod
    def read_pickle(cls, filename, tensor_backend=None):
        """
        Read via pickle-module.

        filename : str, path-like
            Filename including path where to find the tensor network.

        tensor_backend : :class:`TensorBackend` | None, optional
            If not `None`, attribute `_tensor_backend` is set and
            data type and device are converted.
            Default to `None` (no conversion)
        """
        ext = "pkl" + cls.extension
        if not filename.endswith(ext):
            raise QTeaLeavesError(
                f"Filename {filename} not valid, extension should be {ext}."
            )

        with open(filename, "rb") as fh:
            obj = pickle.load(fh)

        if not isinstance(obj, cls):
            raise TypeError(
                f"Loading wrong tensor network ansatz: {type(obj)} vs {cls}."
            )

        if tensor_backend is not None:
            obj.convert(dtype=tensor_backend.dtype, device=tensor_backend.memory_device)
            # pylint: disable-next=protected-access
            obj._tensor_backend = tensor_backend

        return obj

    @classmethod
    @abc.abstractmethod
    def ml_initial_guess(
        cls, convergence_parameters, tensor_backend, initialize, ml_data_mpo, dataset
    ):
        """
        Generate an initial guess for a tensor network machine learning approach.

        Arguments
        ---------

        convergence_parameters : :py:class:`TNConvergenceParameters`
            Class for handling convergence parameters. In particular, the parameter
            `ini_bond_dimension` is of interest when aiming to tune the bond dimension
            of the initial guess.

        tensor_backend : :class:`TensorBackend`
            Selecting the tensor backend to run the simulations with.

        initialize : str
            The string ``superposition-data`` will trigger the superposition of the
            data set. All other strings will be forwarded to the init method of the
            underlying ansatz.

        ml_data_mpo : :class:`MLDataMPO`
            MPO of the labeled data set to be learned including the labels.

        dataset : List[:class:`MPS`]
            Data set represented as list of MPS states. Same order as in
            `ml_data_mpo`.

        Returns
        -------

        ansatz : :class:`_AbstractTN`
            Standard initialization of TN ansatz or Weighted superposition of the
            data set, wehere the weight is the label-value plus an offset of 0.1.
        """

    @classmethod
    @abc.abstractmethod
    def mpi_bcast(cls, state, comm, tensor_backend, root=0):
        """
        Broadcast a whole tensor network.
        """

    def copy(self, dtype=None, device=None):
        """
        Make a copy of a TN.

        **Details**

        The following attributes have a special treatment and are not present
        in the copied object.

        * convergence_parameters
        * log file (filehandle)
        * MPI communicator

        """
        # Store attributes which cannot be pickled, so also potential problems
        # with deepcopy
        storage = self._store_attr_for_pickle()
        obj = deepcopy(self)
        self._restore_attr_for_pickle(storage)

        obj.convert(dtype, device)
        return obj

    @abc.abstractmethod
    def to_dense(self, true_copy=False):
        """Convert into a TN with dense tensors (without symmetries)."""

    @classmethod
    @abc.abstractmethod
    def read(cls, filename, tensor_backend, cmplx=True, order="F"):
        """Read a TN from a formatted file."""

    # --------------------------------------------------------------------------
    #                            Checks and asserts
    # --------------------------------------------------------------------------

    def is_dtype_complex(self):
        """Check if data type is complex based on one example tensor.."""
        for tensor in self._iter_tensors():
            return tensor.is_dtype_complex()

    @staticmethod
    def assert_extension(obj, extension):
        """
        Asserts that `obj.extension` is equal to `extension`.

        Parameters
        ----------

        obj : any
            Will raise error if obj is not an instance of :class:`_AbstractTN`

        extension : str
            Will check if the extension of the TN ansatz matches the extionsion
            of the argument. If not, a type error is raised.
        """
        if not isinstance(obj, _AbstractTN):
            raise TypeError(f"Expected _AbstractTN, but got type {type(obj)}.")
        if obj.extension != extension:
            raise TypeError(f"Expected {extension}, but got type {type(obj)}.")

    def sanity_check(self):
        """
        By default, we provide an empty sanity check method which can be
        overwritten by each class to check properties of the network.
        """
        # by default, no checks and no need to overwrite method in class

    # --------------------------------------------------------------------------
    #                     Abstract methods to be implemented
    # --------------------------------------------------------------------------

    @abc.abstractmethod
    def apply_projective_operator(self, site, selected_output=None, remove=False):
        """
        Apply a projective operator to the site **site**, and give the measurement as output.
        You can also decide to select a given output for the measurement, if the probability is
        non-zero. Finally, you have the possibility of removing the site after the measurement.

        .. warning::

            Applying projective measurements/removing sites is ALWAYS dangerous. The information
            of the projective measurement should be in principle carried over the entire mps,
            by iteratively applying SVDs across all sites. However, this procedure is highly
            suboptimal, since it is not always necessary and will be processed by the
            following two-sites operators. Thus, the procedure IS NOT applied here. Take care
            that entanglement measures through :class:`TNObsBondEntropy` may give incorrect
            results right after a projective operator application. Furthermore, if working
            with parallel approaches, projective operators should be treated with even more
            caution, since they CANNOT be applied in parallel.

        Parameters
        ----------
        site: int
            Index of the site you want to measure
        selected_output: int, optional
            If provided, the selected state is measured. Throw an error if the probability of the
            state is 0
        remove: bool, optional
            If True, the measured index is traced away after the measurement. Default to False.

        Returns
        -------
        meas_state: int
            Measured state
        state_prob : float
            Probability of measuring the output state
        """

    @abc.abstractmethod
    def build_effective_operators(self, measurement_mode=False):
        """
        Build the complete effective operator on each
        of the links. Now assumes `self.eff_op` is set.
        """

    @abc.abstractmethod
    def _convert_singvals(self, dtype, device):
        """Convert the singular values of the tensor network to dtype/device."""

    @abc.abstractmethod
    def _iter_physical_links(self):
        """
        Gives an iterator through the physical links.
        In the MPS, the physical links are connected to nothing,
        i.e. we assign the tensor index -2

        Return
        ------
        Tuple[int]
            The identifier from_tensor, to_tensor
        """

    @abc.abstractmethod
    def get_bipartition_link(self, pos_src, pos_dst):
        """
        Returns two sets of sites forming the bipartition of the system for
        a loopless tensor network. The link is specified via two positions
        in the tensor network.
        """

    @abc.abstractmethod
    def get_pos_links(self, pos):
        """
        Return a list of positions where all links are leading to. Number
        of entries is equal to number of links. Each entry contains the position
        as accessible in the actual tensor network.
        """

    @abc.abstractmethod
    def get_rho_i(self, idx):
        """
        Get the reduced density matrix of the site at index idx

        Parameters
        ----------
        idx : int
            Index of the site
        """

    @abc.abstractmethod
    def get_tensor_of_site(self, idx):
        """
        Generic function to retrieve the tensor for a specific site. Compatible
        across different tensor network geometries.

        Parameters
        ----------
        idx : int
            Return tensor containing the link of the local
            Hilbert space of the idx-th site.
        """

    @abc.abstractmethod
    def iso_towards(
        self,
        new_iso,
        keep_singvals=False,
        trunc=False,
        conv_params=None,
        move_to_memory_device=True,
    ):
        """
        Shift the isometry center to the tensor at the
        corresponding position, i.e., move the isometry to a
        specific tensor, that might not be a physical.

        Parameters
        ----------
        new_iso :
            Position in the TN of the tensor which should be isometrized.
        keep_singvals : bool, optional
            If True, keep the singular values even if shifting the iso with a
            QR decomposition. Default to False.
        trunc : Boolean, optional
            If `True`, the shifting is done via truncated SVD.
            If `False`, the shifting is done via QR.
            Default to `False`.
        conv_params : :py:class:`TNConvergenceParameters`, optional
            Convergence parameters to use for the SVD. If `None`, convergence
            parameters are taken from the TTN.
            Default to `None`.
        move_to_memory_device : bool, optional
            If True, when a mixed device is used, move the tensors that are not the
            isometry center back to the memory device. Default to True.

        Details
        -------
        The tensors used in the computation will always be moved on the computational device.
        For example, the isometry movement keeps the isometry center end the effective operators
        around the center (if present) always on the computational device. If move_to_memory_device
        is False, then all the tensors (effective operators) on the path from the old iso to the new
        iso will be kept in the computational device. This is very useful when you iterate some
        protocol between two tensors, or in general when two tensors are involved.

        """

    @abc.abstractmethod
    def isometrize_all(self):
        """
        Isometrize towards the default isometry position with no previous
        isometry center, e.g., works as well on random states.

        Returns
        -------

        None
        """

    @abc.abstractmethod
    def _iter_tensors(self):
        """Iterate over all tensors forming the tensor network (for convert etc)."""

    @abc.abstractmethod
    def norm(self):
        """
        Calculate the norm of the state.
        """

    @abc.abstractmethod
    def scale(self, factor):
        """
        Multiply the tensor network state by a scalar factor.

        Parameters
        ----------
        factor : float
            Factor for multiplication of current tensor network state.
        """

    @abc.abstractmethod
    def scale_inverse(self, factor):
        """
        Multiply the tensor network state by the inverse of a scalar factor.

        Parameters
        ----------
        factor : float
            Factor for multiplication of current tensor network state.
        """
        # self.scale(1.0 / factor) # Division will be excuted on device

    @abc.abstractmethod
    def set_singvals_on_link(self, pos_a, pos_b, s_vals):
        """Update or set singvals on link via two positions."""

    @abc.abstractmethod
    def site_canonize(self, idx, keep_singvals=False):
        """
        Shift the isometry center to the tensor containing the
        corresponding site, i.e., move the isometry to a specific
        Hilbert space. This method can be implemented independent
        of the tensor network structure.

        Parameters
        ----------
        idx : int
            Index of the physical site which should be isometrized.
        keep_singvals : bool, optional
            If True, keep the singular values even if shifting the iso with a
            QR decomposition. Default to False.
        """

    @abc.abstractmethod
    def _update_eff_ops(self, id_step):
        """
        Update the effective operators after the iso shift

        Parameters
        ----------
        id_step : List[int]
            List with information of the iso moving path

        Returns
        -------
        None
            Updates the effective operators in place
        """

    @abc.abstractmethod
    def _partial_iso_towards_for_timestep(self, pos, next_pos, no_rtens=False):
        """
        Move by hand the iso for the evolution backwards in time

        Parameters
        ----------
        pos : Tuple[int] | int
            Position of the tensor evolved
        next_pos : Tuple[int] | int
            Position of the next tensor to evolve

        Returns
        -------
        QTeaTensor
            The R tensor of the iso movement
        Tuple[int]
            The position of the partner (the parent in TTNs)
        int
            The link of the partner pointing towards pos
        List[int]
            The update path to pass to _update_eff_ops
        """

    @abc.abstractmethod
    def default_sweep_order(self, skip_exact_rgtensors=False):
        """
        Default sweep order to be used in the ground state search/time evolution.

        Arguments
        ---------

        skip_exact_rgtensors : bool, optional
            Allows to exclude tensors from the sweep which are at
            full bond dimension and represent just a unitary
            transformation. Usually set via the convergence
            parameters and then passed here.
            Default to `False`.

        Returns
        -------
        List[int] | List[Tuple[int]]
            The generator that you can sweep through
        """
        raise NotImplementedError("This method is ansatz-specific")

    def default_sweep_order_back(self, skip_exact_rgtensors=False):
        """Default sweep order backwards, e.g., for second-order methods."""
        return self.default_sweep_order(skip_exact_rgtensors=skip_exact_rgtensors)[::-1]

    # pylint: disable-next=unused-argument
    def ml_default_sweep_order(self, num_tensor_rule):
        """
        Default sweep order for a machine learning optimization, where we potentially
        want to allow differences to the ground state sweep.

        Arguments
        ---------

        num_tensor_rule: int
            Specify if it is a one-tensor or two-tensor update.

        Returns
        -------

        sweep_order : List
            List of tensor positions compatible with the corresponding
            ansatz. If not overwritten by ansatz, the `default_sweep_order`
            is returned.
        """

        logger_warning(
            "DeprecationWarning: The machine learning methods in qtealeaves classes are deprecated."
            + " For machine learning tasks, please utilize the qchaitea classes instead."
        )

        return self.default_sweep_order()

    def ml_reorder_pos_pair(self, pos, pos_partner, link_pos, link_partner):
        """
        By default, no re-ordering is done and arguments are returned as is.

        Arguments
        ---------

        pos : int | tuple[int]
            Position of the first tensor in the network.

        pos_partner : int | tuple[int]
            Position of the partner tensor in the network.

        link_pos : int
            Link in tensor connecting to partner tensor.

        link_partner : int
            Link in partner tensor connecting to tensor.

        Returns
        -------

        pos, pos_partner, link_pos, link_partner
            Re-ordering of tensor and partner tensor if beneficial.
        """

        logger_warning(
            "DeprecationWarning: The machine learning methods in qtealeaves classes are deprecated."
            + " For machine learning tasks, please utilize the qchaitea classes instead."
        )

        return pos, pos_partner, link_pos, link_partner

    def filter_sweep_order(self, sweep_order, skip_exact_rgtensors):
        """Filter a sweep order with respect to exact rg tensors if flag active."""
        if not skip_exact_rgtensors:
            return sweep_order

        default_order = self.default_sweep_order(skip_exact_rgtensors=True)
        filtered_sweep_order = []
        for elem in sweep_order:
            if elem in default_order:
                filtered_sweep_order.append(elem)

        return filtered_sweep_order

    @abc.abstractmethod
    def get_pos_partner_link_expansion(self, pos):
        """
        Get the position of the partner tensor to use in the link expansion
        subroutine

        Parameters
        ----------
        pos : int | Tuple[int]
            Position w.r.t. which you want to compute the partner

        Returns
        -------
        int | Tuple[int]
            Position of the partner
        int
            Link of pos pointing towards the partner
        int
            Link of the partner pointing towards pos
        """

    def get_projector_function(self, pos, pos_links):
        """
        Generates a function which locally projects out the effective projectors.
        Used in the excited state search.

        **Arguments**
        pos : tuple[int]
            The position of the tensor from which to project.
        pos_links : list[tuple]
                Position of neighboring tensors where the links in `tensor` lead to.

        **Returns**
        Callable : the function.
        """

        # partial should return a pointer to the function with arguments applied, so it
        # should not create a whole new function object
        return partial(
            self._project_out_projectors,
            projectors=self.eff_proj,
            pos=pos,
            pos_links=pos_links,
        )

    @staticmethod
    def _project_out_projectors(tensor, projectors, pos, pos_links):
        """
        Takes the tensor and projects out all eff_projectors at the given position.
        Used for the excited state search.
        Does not renormalize the tensor to the initial norm! This seems to work better for the
        excited state search (it produces lower overlaps).

        **Arguments**
        tensor : :class:`_AbstractQteaTensor`
            The tensor from which to subtract the projection.
        projectors : list
            A list of projectors as effective operators.
        position : tuple | int
            The position of the tensor.
        pos_links : list[tuple]
            Position of neighboring tensors where the links in `tensor` lead to.

        **Returns**
        :class:`_AbstractQteaTensor`
        """

        tabs = tensor.get_attr("abs")

        # calculate all overlaps first, sort them, and first orthogonalize
        # the ones with the biggest overlap
        overlaps = []
        abs_overlaps = []
        local_projectors = []
        for projector in projectors:
            local_projector = projector.contract_to_projector(
                tensor=None, pos=pos, pos_links=pos_links
            )
            # move to the same device
            local_projector.convert(device=tensor.device)

            overlap = local_projector.dot(tensor)
            overlaps.append(overlap)
            abs_overlaps.append(tabs(overlap))
            local_projectors.append(local_projector)

        # and now orthogonalize starting with the largest overlap
        sorted_ndx = sorted(enumerate(abs_overlaps), key=lambda x: x[1], reverse=True)
        for ii, _ in sorted_ndx:
            overlap = overlaps[ii]
            local_projector = local_projectors[ii]
            tensor.add_update(other=local_projector, factor_other=-1 * overlap)

        # WARNING: I know you want to renormalize here, but it is wrong!
        # You will get wrong results. Luka Feb 2024

        return tensor

    @abc.abstractmethod
    def to_statevector(self, qiskit_order=False, max_qubit_equivalent=20):
        """
        Decompose a given TN into statevector form if pure.

        Parameters
        ----------
        qiskit_order : bool, optional
            If true, the order is right-to-left. Otherwise left-to-right
            (which is the usual order in physics). Default to False.
        max_qubit_equivalent : int, optional
            Maximum number of qubits for which the statevector is computed.
            i.e. for a maximum hilbert space of 2**max_qubit_equivalent.
            Default to 20.

        Returns
        -------

        psi : instance of :class:`_AbstractQteaTensor`
            The statevector of the system

        Raises
        ------

        Mixed state: if mixed-state representations are not pure, an
            error will be raised.
        """

    @abc.abstractmethod
    def write(self, filename, cmplx=True):
        """Write the TN in python format into a FORTRAN compatible format."""

    @abc.abstractmethod
    def apply_local_kraus_channel(self, kraus_ops):
        """
        Apply local Kraus channels to tensor network
        -------
        Parameters
        -------
        kraus_ops : dict of :py:class:`QTeaTensor`
            Dictionary, keys are site indices and elements the corresponding 3-leg Kraus tensors

        Returns
        -------
        singvals_cut: float
            Sum of singular values discarded due to truncation.

        """

    def get_substate(self, first_site, last_site, truncate=False):
        """
        Returns the smaller TN built of tensors from `first_site` to `last_site`,
        where sites refer to physical sites.

        Parameters
        ----------

        first_site : int
            First (physical) site defining a range of tensors which will compose the new TN.
            Python indexing assumed, i.e. counting starts from 0.
        last_site : int
            Last (physical) site of a range of tensors which will compose the new TN.
            Python indexing assumed, i.e. counting starts from 0.
        truncate : Bool
            If False, tensors are returned as is, possibly with non-dummy links
            on edge tensors. If True, the edges of will be truncated to dummy links.
            Default to False.
        """

    @abc.abstractmethod
    def kron(self, other):
        """
        Concatenate two TN, taking the kronecker/outer product
        of the two states. The bond dimension assumed is the maximum
        between the two bond dimensions.

        Parameters
        ----------
        other : :py:class:`_AbstractTN`
            TN to concatenate with self.
        Returns
        -------
        :py:class:`_AbstractTN`
            Concatenation of the first TTN with the second in order
        """

    # --------------------------------------------------------------------------
    #                        Methods that can be inherited
    # --------------------------------------------------------------------------

    def _apply_projective_operator_common(self, site, selected_output):
        """
        Execute common steps across different ansätze.

        Returns
        -------

        rho_i : _AbstractQteaTensor

        meas_state: integer

        old_norm : norm before calculating rho_i and renormalizing
        """
        if selected_output is not None and selected_output > self._local_dim[site] - 1:
            raise ValueError("The seleted output must be at most local_dim-1")

        # Set the orthogonality center
        self.site_canonize(site, keep_singvals=True)

        # Normalize
        old_norm = self.norm()
        self.scale_inverse(old_norm)

        rho_i = self.get_rho_i(site)
        probabilities = rho_i.diag(real_part_only=True, do_get=True)
        cumul_probs = np.cumsum(probabilities)

        random_u = np.random.rand()
        meas_state = None
        for ii, cprob_ii in enumerate(cumul_probs):
            if selected_output is not None and ii != selected_output:
                continue

            if cprob_ii >= random_u or selected_output == ii:
                meas_state = ii
                # state_prob = probabilities[ii]
                break

        if meas_state is None:
            raise QTeaLeavesError("Did not run into measurement.")

        return rho_i, meas_state, old_norm

    def checkpoint_copy_simulation_attr(self, src):
        """Copy attributes linked to the simulation, like convergence parameters."""
        self.convergence_parameters = src.convergence_parameters
        self.solver = src.solver

        if src.comm is not None:
            raise ValueError("Checkpoints and MPI are not yet enabled.")

    def checkpoint_store(
        self,
        folder_name_output,
        dyn_checkpoint_file,
        int_str,
        checkpoint_indicator_file,
        is_dyn=False,
        jdic=None,
    ):
        """
        Store the tensor network as checkpoint.

        **Arguments**

        folder_name_output : str
            Name of the output folder, where we store checkpoints.

        dyn_checkpoint_file : str or `None`
            Name of the previous checkpoint file, which can be deleted after
            creating the new checkpoint.

        int_str : str
            Identifier containing integers as string to identify the checkpoint
            when loading in a potential future run.

        checkpoint_indicator_file: str
            Path to file which indicates whether checkpoints exists.

        is_dyn : bool, optional
            Flag to indicate if checkpoint is for statics (False) or
            dynamics (True).
            Default to `False`.

        jdic : json-compatible structure or `None`, optional
            Store additional information as json.
            Default to `None` (store nothing).
        """

        prev_checkpoint_file = dyn_checkpoint_file
        dyn_stat_switch = "dyn" if is_dyn else "stat"
        dyn_checkpoint_file = os.path.join(
            folder_name_output, f"TTN_{dyn_stat_switch}_{int_str}"
        )
        self.save_pickle(dyn_checkpoint_file)

        if jdic is not None:
            with open(dyn_checkpoint_file + ".json", "w+") as fh:
                json.dump(jdic, fh, cls=QteaJsonEncoder)

        # Delete previous checkpoint
        if prev_checkpoint_file is not None:
            ext = ".pkl" + self.extension
            os.remove(prev_checkpoint_file + ext)

            if os.path.isfile(prev_checkpoint_file + ".json"):
                os.remove(prev_checkpoint_file + ".json")

        if not os.path.isfile(checkpoint_indicator_file):
            with open(checkpoint_indicator_file, "w+") as fh:
                pass

        return dyn_checkpoint_file

    def clear_cache_rho(self):
        """Clear cache of reduced density matrices."""
        self._cache_rho = {}

    def convert(self, dtype, device):
        """Convert the data type and device of a tensor network inplace."""
        if isinstance(dtype, str):
            dtype = self.dtype_from_char(dtype)

        # Converting singular values relies on tensor backend of tensors,
        # thus do it before converting the tensors
        self._convert_singvals(dtype, device)

        # convert all tensors in a tensor network
        if (self.dtype != dtype) or (self.device != device):
            for tensor in self._iter_tensors():
                tensor.convert(dtype, device)

        # convert all effective operators
        if self.eff_op is not None:
            self.eff_op.convert(dtype, device)
        # convert all effective projectors
        for proj in self.eff_proj:
            proj.convert(dtype, device)
        # convert all reduced density matrices
        for idx, rho in self._cache_rho.items():
            self._cache_rho[idx] = rho.convert(dtype, device)

    def move_pos(self, pos, device=None, stream=False):
        """
        Move just the tensor in position `pos` with the effective
        operators insisting on links of `pos` on another device.
        Other objects like effective projectors will be moved as
        well. Acts in place.

        Note: the implementation of the tensor backend can fallback
        to synchronous moves only depending on its implementation.

        Parameters
        ----------
        pos : int | Tuple[int]
            Integers identifying a tensor in a tensor network.
        device : str, optional
            Device where you want to send the QteaTensor. If None, no
            conversion. Default to None.
        stream : bool | stream | None, optional
            If True, use a new stream for memory communication given
            by the data mover. If False, use synchronous communication
            with GPU. If not a boolean (and not None), we assume it
            is a stream object compatible with the backend.
            None is deprecated and equals to False.
            Default to False (Use null stream).
        """
        if device is None:
            # Quick return as pointed out in the docstring.
            return

        if stream is None:
            logger_warning("stream=None is deprecated, use False instead.")
            stream = False

        # Boolean logic for stream and sync are opposite
        if isinstance(stream, bool):
            sync = not stream
        else:
            sync = stream

        _ = stream
        # Convert the tensor
        self.data_mover.move(self[pos], device=device, sync=sync)
        pos_links = self.get_pos_links(pos)
        # Convert the effective operators if present
        if self.eff_op is not None:
            for pos_link in pos_links:
                if (pos_link, pos) in self.eff_op.eff_ops:
                    for tensor in self.eff_op.eff_ops[(pos_link, pos)]:
                        self.data_mover.move(tensor, device=device, sync=sync)

        # Convert the effective projectors if present.
        for proj in self.eff_proj:
            for pos_link in pos_links:
                # Also move the tensor of psi0 (tensor at pos must exist)
                # Here, we just need the tensor and use move of the data_mover
                # instead of move_pos
                self.data_mover.move(proj.psi0[pos], device=device, sync=sync)

                # pylint: disable-next=protected-access
                if (pos_link, pos) in proj._eff_ops:
                    self.data_mover.move(
                        # pylint: disable-next=protected-access
                        proj._eff_ops[(pos_link, pos)],
                        device=device,
                        sync=sync,
                    )

        self._tensor_backend.tensor_cls.free_device_memory(device=device)

    def dtype_from_char(self, dtype):
        """Resolve data type from chars C, D, S, Z and optionally H."""
        for tensor in self._iter_tensors():
            return tensor.dtype_from_char(dtype)

        raise QTeaLeavesError("Querying on empty tensor network.")

    def normalize(self):
        """
        Normalize the state depending on its current norm.
        """
        self.scale_inverse(self.norm())

    def pre_timeevo_checks(self, raise_error=False):
        """Check if a TN ansatz is ready for time-evolution."""
        is_check_okay = True
        if not self.is_dtype_complex() and raise_error:
            raise QTeaLeavesError("Trying time evolution with real state.")

        if not self.is_dtype_complex():
            is_check_okay = False
            logger.warning("Trying to run time evolution with real state.")

        return is_check_okay

    def set_cache_rho(self):
        """Cache the reduced density matrices for faster access."""
        for ii in range(self.num_sites):
            self._cache_rho[ii] = self.get_rho_i(ii)

    def _store_attr_for_pickle(self):
        """Return dictionary with attributes that cannot be pickled and unset them."""
        storage = {
            "conv_params": self._convergence_parameters,
            "comm": self.comm,
            "solver": self._solver,
            "cache_rho": self._cache_rho,
        }

        self._convergence_parameters = None
        self.comm = None
        self._solver = None
        self.clear_cache_rho()

        return storage

    def _restore_attr_for_pickle(self, storage):
        """Restore attributed removed for pickle from dictionary."""
        # Reset temporary removed attributes
        self._convergence_parameters = storage["conv_params"]
        self.comm = storage["comm"]
        self._solver = storage["solver"]
        self._cache_rho = storage["cache_rho"]

    def save_pickle(self, filename):
        """
        Save class via pickle-module. A state is always saved on a host CPU
        with tensor_backend.device set to "cpu". After saving, the state and the
        tensor_backend are converted back to the original device.

        **Details**

        The following attributes have a special treatment and are not present
        in the copied object.

        * convergence_parameters
        * log file (filehandle)
        * MPI communicator
        """
        # otherwise (TTN) run into exception
        # "Need to isometrize to [0, 0], but at {self.iso_center}."
        # in ttn_simulator.build_effective_operators
        self.iso_towards(self.default_iso_pos)

        # Temporary remove objects which cannot be pickled which
        # included convergence parameters for lambda function and
        # parameterized variables, the log file as file handle and
        # the MPI communicator
        storage = self._store_attr_for_pickle()

        memory_device = self.tensor_backend.memory_device
        computational_device = self.tensor_backend.computational_device

        # Assume pickle needs to be on host.
        # Internally an empty call if everything is already on cpu.
        self.convert(None, "cpu")

        ext = "pkl" + self.extension
        if not filename.endswith(ext):
            filename += "." + ext

        with open(filename, "wb") as fh:
            pickle.dump(self, fh)

        # If mixed device, move back only the iso_center,
        # otherwise everythig.
        if computational_device != memory_device:
            self.move_pos(pos=self.iso_center, device=computational_device)
        else:
            self.convert(dtype=None, device=memory_device)

        self._restore_attr_for_pickle(storage)

    # pylint: disable-next=unused-argument
    def permute_spo_for_two_tensors(self, spo_list, theta, link_partner):
        """Returns permuted SPO list, permuted theta, and the inverse permutation."""
        return spo_list, theta, None

    def randomize(self, noise=None, mpo_to_recalculate_eff_ops=None):
        """
        Randomize all tensors in the tensor network.
        Removes eff_ops and eff_proj.
        If an mpo is passed as mpo_to_recalculate_eff_ops,
        the effective operators are recalculated with it.

        Parameters
        ----------
        noise : float | None
            The amount of noise added. None randomizes completely.

        reset_eff_ops_mpo : mpo
            Used to recalculate effective operator.
        """
        for tens in self._iter_tensors():
            old_norm = tens.norm_sqrt()
            tens.randomize(noise=noise)
            new_norm = tens.norm_sqrt()

            tens *= old_norm / new_norm

        # Also reset the effective operators and projectors.
        self.eff_op = None
        self.eff_proj = []

        # reset the iso position
        self.iso_center = None
        self.isometrize_all()
        self.normalize()

        # recalculate the effective operators
        if mpo_to_recalculate_eff_ops is not None:
            mpo_to_recalculate_eff_ops.setup_as_eff_ops(self)

    # --------------------------------------------------------------------------
    #                                  Unsorted
    # --------------------------------------------------------------------------

    def _postprocess_singvals_cut(self, singvals_cut, conv_params=None):
        """
        Postprocess the singular values cut after the application of a
        tSVD based on the convergence parameters. Either take the sum of
        the squared singvals (if `conv_params.trunc_tracking_mode` is `"C"`) or the maximum
        (if `conv_params.trunc_tracking_mode` is `"M"`).

        Parameters
        ----------
        singvals_cut : np.ndarray
            Singular values cut in a tSVD
        conv_params : TNConvergenceParameters, optional
            Convergence parameters. If None, the convergence parameters
            of the tensor network class is used, by default None

        Returns
        -------
        float
            The processed singvals
        """
        if conv_params is None:
            conv_params = self._convergence_parameters
        # If no singvals was cut append a 0 to avoid problems
        if len(singvals_cut) == 0:
            return 0

        if conv_params.trunc_tracking_mode == "M":
            singvals_cut = singvals_cut.max()
        elif conv_params.trunc_tracking_mode == "C":
            if hasattr(singvals_cut, "sum"):
                # Works for numpy, cupy, pytorch ...
                singvals_cut = (singvals_cut**2).sum()
            else:
                # Tensorflow handling (example tensor to get attribute)
                tensor = None
                for tensor in self._iter_tensors():
                    break
                func_sum = tensor.get_attr("sum")
                singvals_cut = func_sum(singvals_cut**2)
        else:
            raise QTeaLeavesError(
                f"Unknown trunc_tracking_mode {conv_params.trunc_method}"
            )

        return singvals_cut

    #########################################
    ########## MEASUREMENT METHODS ##########
    #########################################

    def meas_local(self, op_list):
        """
        Measure a local observable along all sites of the MPS

        Parameters
        ----------
        op_list : list of :class:`_AbstractQteaTensor`
            local operator to measure on each site

        Return
        ------
        measures : ndarray, shape (num_sites)
            Measures of the local operator along each site
        """
        if isinstance(op_list, _AbstractQteaTensor):
            if len(set(self.local_dim)) != 1:
                raise QTeaLeavesError(
                    "Trying to use single operator for non-unique Hilbert spaces."
                )
            op_list = [op_list for _ in range(self.num_sites)]

        # Move all operators to the computational device.
        # Assume self.get_rho(ii) is always on the computational device.
        device_list = []
        for ii, op in enumerate(op_list):
            # The if check because the user could pass a numpy array as the op_list.
            # In that case, we assume everything is on the same device.
            if isinstance(op, _AbstractQteaTensor):
                device_list.append(op.device)
                op.convert(device=self.tensor_backend.computational_device)
            else:
                device_list.append(None)

        # Always store on host
        measures = np.zeros(self.num_sites)

        # This subroutine can be parallelized if the singvals are stored using
        # joblib
        for ii in range(self.num_sites):
            rho_i = self.get_rho_i(ii)
            op = op_list[ii]
            if op.ndim != 2:
                # Need copy, otherwise input tensor is modified ("passed-by-pointer")
                op = op.copy()
                op.trace_one_dim_pair([0, 3])

            # Ensure that numpy/cupy operators are on the computational device.
            # tensordot() should already check this, but it prints a warning
            # "Converting tensor on the fly" that can be avoided by converting
            # explicitly the array here.
            # Note: op in the op_list is not overwritten
            if not isinstance(op, _AbstractQteaTensor):
                # NOTE: maybe there is a better place to make this conversion
                op = self._tensor_backend.from_elem_array(
                    op,
                    dtype=rho_i.dtype,
                    device=self.tensor_backend.computational_device,
                )

            expectation = rho_i.tensordot(op, ([0, 1], [1, 0]))
            measures[ii] = np.real(expectation.get_entry())

        # Move the operators back.
        for ii, op in enumerate(op_list):
            if isinstance(op, _AbstractQteaTensor):
                op.convert(device=device_list[ii])

        return measures

    def meas_magic(
        self, renyi_idx=2, num_samples=1000, return_probabilities=False, precision=14
    ):
        """
        Measure the magic of the state as defined
        in https://arxiv.org/pdf/2303.05536.pdf, with a given number of samples.
        To see how the procedure works see meas_unbiased_probabilities.

        Parameters
        ----------
        renyi_idx : int, optional
            Index of the Rényi entropy you want to measure.
            If 1, measure the Von Neumann entropy. Default to 2.
        num_samples : int | List[int], optional
            Number of random number sampled for the unbiased probability measurement.
            If a List is passed, then the algorithm is run over several superiterations
            and each entry on num_samples is the number of samples of a superiteration.
            Default to 1000.
        return_probabilities : bool, optional
            If True, return the probability dict. Default to False.
        precision: int, optional
            Precision for the probability interval computation. Default to 14.
            For precision>15 mpmath is used, so a slow-down is expected.

        Returns
        -------
        float
            The magic of the state
        """
        if np.isscalar(num_samples):
            num_samples = [num_samples]

        # Sample the state probabilities
        opes_bound_probs = {}
        opes_probs = np.array([])
        for num_samp in num_samples:
            # Sample the numbers
            samples = np.random.rand(int(num_samp))
            # Do not perform the computation for the already sampled numbers
            probs, new_samples = _check_samples_in_bound_probs(
                samples, opes_bound_probs
            )
            opes_probs = np.hstack((opes_probs, probs))
            # Perform the sampling for the unseen samples
            bound_probs = self.meas_unbiased_probabilities(
                new_samples, mode="magic", precision=precision
            )
            opes_bound_probs.update(bound_probs)
            # Add the sampled probability to the numpy array
            probs, _ = _check_samples_in_bound_probs(new_samples, bound_probs)
            opes_probs = np.hstack((opes_probs, probs))

        # Compute the magic with the samples
        magic = -self.num_sites * np.log(2)
        # Pass from probability intervals to probability values
        if renyi_idx > 1:
            magic += np.log((opes_probs ** (renyi_idx - 1)).mean()) / (1 - renyi_idx)
        else:
            magic += -(np.log(opes_probs)).mean()

        if return_probabilities:
            return magic, opes_bound_probs
        return magic

    def meas_projective(
        self,
        nmeas=1024,
        qiskit_convention=False,
        seed=None,
        unitary_setup=None,
        do_return_probabilities=False,
    ):
        """
        Perform projective measurements along the computational basis state

        Parameters
        ----------
        nmeas : int, optional
            Number of projective measurements. Default to 1024.
        qiskit_convention : bool, optional
            If the sites during the measure are represented such that
            |201> has site 0 with value one (True, mimicks bits ordering) or
            with value 2 (False usually used in theoretical computations).
            Default to False.
        seed : int, optional
            If provided it sets the numpy seed for the random number generation.
            Default to None
        unitary_setup : `None` or :class:`UnitarySetupProjMeas`, optional
            If `None`, no local unitaries are applied during the projective
            measurements. Otherwise, the unitary_setup provides local
            unitaries to be applied before the projective measurement on
            each site.
            Default to `None`.
        do_return_probabilities : bool, optional
            If `False`, only the measurements are returned. If `True`,
            two arguments are returned where the first are the
            measurements and the second are their probabilities.
            Default to `False`

        Return
        ------
        measures : dict
            Dictionary where the keys are the states while the values the number of
            occurrences. The keys are separated by a comma if local_dim > 9.
        """
        if nmeas == 0:
            return {}

        if seed is not None and isinstance(seed, int):
            np.random.seed(seed)

        # Put in canonic form
        self.site_canonize(0)

        measures = []
        probabilities = []
        # Loop over number of measurements
        for _ in range(nmeas):
            state = np.zeros(self.num_sites, dtype=int)
            temp_tens = deepcopy(self.get_tensor_of_site(0))
            # Loop over tensors
            cumulative_prob = 1.0
            for ii in range(self.num_sites):
                target_prob = np.random.rand()
                measured_idx, temp_tens, prob_ii = self._get_child_prob(
                    temp_tens, ii, target_prob, unitary_setup, state, qiskit_convention
                )
                cumulative_prob *= prob_ii

                # Save the measured state either with qiskit or
                # theoretical convention
                if qiskit_convention:
                    state[self.num_sites - 1 - ii] = measured_idx
                else:
                    state[ii] = measured_idx

            if isinstance(self._local_dim, list):
                max_local_dim = np.max(self._local_dim)
            else:
                max_local_dim = self._local_dim.max()

            if max_local_dim < 10:
                measure_ii = np.array2string(
                    state, separator="", max_line_width=2 * self.num_sites
                )[1:-1]
            else:
                measure_ii = np.array2string(
                    state, separator=",", max_line_width=2 * self.num_sites
                )[1:-1]

            probabilities.append(cumulative_prob)

            # Come back to CPU if on GPU for list in measures (not needed since it is string)
            measures.append(measure_ii)

        measures = np.array(measures)
        states, counts = np.unique(measures, return_counts=True)
        probabilities = dict(zip(measures, probabilities))
        measures = dict(zip(states, counts))

        if do_return_probabilities:
            return measures, probabilities
        return measures

    def meas_unbiased_probabilities(
        self,
        num_samples,
        qiskit_convention=False,
        bound_probabilities=None,
        do_return_samples=False,
        precision=15,
        mode="projection_z",
    ):
        """
        Compute the probabilities of measuring a given state if its probability
        falls into the explored in num_samples values.
        The functions divide the probability space in small rectangles, draw
        num_samples random numbers and then follow the path until the end.
        The number of states in output is between 1 and num_samples.

        For a different way of computing the probability tree see the
        function :py:func:`meas_even_probabilities` or
        :py:func:`meas_greedy_probabilities`

        Parameters
        ----------
        num_samples : int
            Maximum number of states that could be measured.
        qiskit_convention : bool, optional
            If the sites during the measure are represented such that
            |201> has site 0 with value one (True, mimics bits ordering) or
            with value 2 (False usually used in theoretical computations).
            Default to False.
        probability_bounds : dict, optional
            Bounds on the probability computed previously with this function,
            i.e. if a uniform random number has value
            `left_bound< value< right_bound` then you measure the state.
            The dict structure is `{'state' : (left_bound, right_bound)}`.
            If provided, it speed up the computations since the function will
            skip values in the intervals already known. By default None.
        do_return_samples : bool, optional
            Enables, if `True`, to return the random number used for sampling
            in addition to the `bound_probabilities`. If `False`, only the
            `bound_probabilities` are returned.
            Default to `False`
        precision : int, optional
            Decimal place precision for the mpmath package. It is only
            used inside the function, and setted back to the original after
            the computations. Default to 15.
            If it is 15 or smaller, it just uses numpy.
        mode : str, optional
            Mode of the unbiased sampling. Default is "projection_z", equivalent
            to sampling the basis states on the Z direction.
            Possibilities:
            - "projection_z"
            - "magic"

        Return
        ------
        bound_probabilities : dict
            Dictionary analogous to the `probability_bounds` parameter.
            The keys are separated by a comma if local_dim > 9.
        samples : np.ndarray
            Random numbers from sampling, only returned if activated
            by optional argument.
        """

        # Use mpmath if precision is larger than 15
        has_mp = precision > 15

        # Handle internal cache; keep if possible: if bound probabilities
        # are passed, it must be the same state and we can keep the
        # cache.
        do_clear_cache = bound_probabilities is None

        # Always set gauge to site=0; even if cache is not cleared,
        # the actual isometry center did not move
        self.site_canonize(0)

        # Normalize for quantum trajectories
        old_norm = self.norm()
        self.normalize()

        if mode == "projection_z":
            local_dim = self.local_dim
            get_children_prob = self._get_children_prob
            initial_tensor = self.get_tensor_of_site(0)
        elif mode == "magic":
            local_dim = [
                4,
            ] * self.num_sites
            get_children_prob = self._get_children_magic
            tmp = self.get_tensor_of_site(0)
            initial_tensor = tmp.eye_like(tmp.links[0])
        else:
            raise ValueError(f"mode {mode} not available for unbiased sampling")

        # ==== Initialize variables ====
        # all_probs is a structure to keep track of already-visited nodes in
        # the probability tree. The i-th dictionary of the list correspond to
        # a state measured up to the i-th site. Each dictionary has the states
        # as keys and as value the list [state_prob, state_tens]
        all_probs = [{} for _ in range(self.num_sites)]
        # Initialize precision
        old_precision = mp.mp.dps
        mp.mp.dps = precision
        # This precision is pretty much independent of the numpy-datatype as
        # it comes from multiplication. However, it is important when we sum
        # for the intervals
        mpf_wrapper, almost_equal = _mp_precision_check(precision)
        # Sample uniformly in 0,1 the samples, taking into account the already
        # sampled regions given by bound_probabilities
        if np.isscalar(num_samples):
            samples, bound_probabilities = _resample_for_unbiased_prob(
                num_samples, bound_probabilities
            )
        else:
            samples = num_samples
            bound_probabilities = (
                {} if bound_probabilities is None else bound_probabilities
            )
        # ==== Routine ====
        cum_prob = None
        cum_probs = None
        zero_probs_counter = 0

        for idx, sample in enumerate(samples):
            # If the sample is in an already sampled area continue
            if idx > 0:
                if cum_prob is None:
                    logger.warning(
                        "Error information QTeaOPESError at idx=%d with samples %s.",
                        idx,
                        str(samples[: idx + 1]),
                    )
                    raise QTeaOPESError("cum_prob not defined.")
                if left_prob_bound < sample < left_prob_bound + cum_prob:
                    continue
            # Set the current state to no state
            curr_state = ""
            # Set the current tensor to be measured to the first one
            tensor = deepcopy(initial_tensor)
            # Initialize the probability to 1
            curr_prob = 1
            # Initialize left bound of the probability interval. Arbitrary precision
            left_prob_bound = mpf_wrapper(0.0)
            # Loop over the sites
            for site_idx in range(0, self.num_sites):
                # Initialize new possible states, adding the digits of the local basis to
                # the state measured up to now
                if site_idx > 0:
                    states = [
                        curr_state + f",{ii}" for ii in range(local_dim[site_idx])
                    ]
                else:
                    states = [curr_state + f"{ii}" for ii in range(local_dim[site_idx])]

                # Compute the children if we didn't already follow the branch
                if not np.all([ss in all_probs[site_idx] for ss in states]):
                    # Remove useless information after the first cycle. This operation is
                    # reasonable since the samples are ascending, i.e. if we switch path
                    # we will never follow again the old paths.
                    if idx > 0:
                        all_probs[site_idx:] = [
                            {} for _ in range(len(all_probs[site_idx:]))
                        ]

                    # Compute new probabilities
                    probs, tensor_list = get_children_prob(
                        tensor, site_idx, curr_state, do_clear_cache
                    )

                    # Clear cache only upon first iteration
                    do_clear_cache = False

                    # get probs to arbitrary precision
                    # if precision > 15:
                    #    probs = mp.matrix(probs)
                    # Multiply by the probability of being in the parent state
                    # Multiplication is safe from the precision point of view
                    probs = curr_prob * probs

                    # Update probability tracker for next branch, avoiding
                    # useless additional computations
                    for ss, prob, tens in zip(states, probs, tensor_list):
                        all_probs[site_idx][ss] = [prob, tens]

                # Retrieve values if already went down the path
                else:
                    probs = []
                    tensor_list = []
                    for prob, tens in all_probs[site_idx].values():
                        probs.append(prob)
                        tensor_list.append(tens)
                # Select the next branch if we didn't reach the leaves
                # according to the random number sampled
                if site_idx < self.num_sites - 1:
                    cum_probs = np.cumsum(probs)  # Compute cumulative
                    # Select first index where the sample is lower than the cumulative
                    try:
                        meas_idx = [
                            sample < float(cum_prob) for cum_prob in cum_probs
                        ].index(True)
                    except ValueError as exc:
                        # If the sample is not smaller than any of the cum_probs,
                        # it must be the last sample (probably within machine precision)
                        eps = abs(sample - cum_probs[-1])
                        if eps > 10 * tensor_list[0].dtype_eps:
                            info_str = " with eps, dtype_eps, sample, cum_probs: "
                            info_values = ", ".join(
                                [
                                    str(eps),
                                    str(tensor_list[0].dtype_eps),
                                    str(sample),
                                    str(cum_probs),
                                ]
                            )
                            # pylint: disable-next=logging-not-lazy
                            logger.warning(
                                "Error information QTeaOPESError"
                                + info_str
                                + info_values
                            )
                            raise QTeaOPESError(
                                "IndexError in OPES sampling not within machine precision."
                            ) from exc
                        if eps > 0:
                            # Testing against exact zero on purpose, to warn if we are close
                            # to machine precision here
                            logger_warning(
                                "Sampling with OPES close to machine precision."
                            )

                        meas_idx = len(cum_probs) - 1

                    # Update run-time values based on measured index
                    tensor = deepcopy(tensor_list[meas_idx])
                    curr_state = states[meas_idx]
                    curr_prob = probs[meas_idx]
                    # Update value of the sample based on the followed path
                    cum_probs_idx = 0.0 if meas_idx == 0 else cum_probs[meas_idx - 1]
                    sample -= float(cum_probs_idx)
                    # Update left-boundary value with probability remaining on the left
                    # of the measured index
                    if meas_idx > 0:
                        if has_mp:
                            left_prob_bound += float(cum_probs[meas_idx - 1])
                        else:
                            left_prob_bound += cum_probs[meas_idx - 1]
                # Save values if we reached the leaves
                else:
                    cum_prob = mpf_wrapper(0.0)
                    for ss, prob in zip(states, probs):
                        if prob < 0:
                            msg = (
                                "Probably you need an higher precision.",
                                "Measured negative probability of %s, set to 0.",
                            )
                            logger.warning(msg, prob)
                            prob = 0
                        tmp = float(prob) if has_mp else prob
                        if not almost_equal((tmp, 0)):
                            bound_probabilities[ss] = (
                                left_prob_bound + cum_prob,
                                left_prob_bound + cum_prob + tmp,
                            )
                        else:
                            zero_probs_counter += 1
                        cum_prob += tmp

            # For TTN with caching strategy (empty interface implemented
            # also for any abstract tensor network)
            all_probs = self.clear_cache(all_probs=all_probs, current_key=curr_state)

        if zero_probs_counter > 0:
            msg = (
                f"The probability of {zero_probs_counter} samples was "
                + "smaller than the precision. No bounds will be associated."
            )
            logger.warning(msg)

        # Rewrite with qiskit convention and remove commas if needed
        bound_probabilities = postprocess_statedict(
            bound_probabilities,
            local_dim=self.local_dim,
            qiskit_convention=qiskit_convention,
        )

        self.scale(old_norm)
        mp.mp.dps = old_precision

        if do_return_samples:
            return bound_probabilities, samples

        return bound_probabilities

    def sample_n_unique_states(
        self, num_unique, exit_coverage=0.9999, ignore_opes_errors=False, **kwargs
    ):
        """
        Sample a given number of unique target states. This is the target number of
        states, the actual number of states can differ.

        **Arguments**

        num_unique : int
            Number of unique states to be sampled. This is a target number;
            the actual number of sampled states might differ in the end.

        exit_coverage : float, optional
            Coverage at which sampling can stop even without reaching the
            target number of unique states.
            Default to 0.9999

        ignore_opes_errors : bool, optional
            Allows to ignore `QTeaOpesError` to return at least the samples
            that have been sampled so far.
            Default to False

        kwargs : keyword arguments
            Passed through to unbiased sampling, e.g., `qiskit_convention`,
            `precision`, and `mode`. `bound_probabilities` is accepted if
            called from MPI sampling (identified by left-right keys).

        **Details**

        The target number of unique states will not be reached if the probability of
        the sampled states reaches the `exit_coverage`.

        The target number of unique states will be overfulfilled in most other cases
        as the last superiteration might generate slightly more states than needed.
        """
        sampling_result = None
        for key in kwargs:
            if key not in [
                "qiskit_convention",
                "precision",
                "mode",
                "bound_probabilities",
            ]:
                raise ValueError(f"Keyword argument `{key}` not allowed.")

            # We want to reuse this function for sampling from MPI, but not necessarily
            # other calls should be able to pass kwargs bound_probabilities. For MPI
            # calls, we know either left or right must be set as key.
            if key == "bound_probabilities":
                sampling_result = kwargs["bound_probabilities"]
                if ("left" not in sampling_result) and ("right" not in sampling_result):
                    raise QTeaLeavesError(
                        "Only MPI sampling allowed for bound_probailities."
                    )

        if sampling_result is not None:
            kwargs = deepcopy(kwargs)
            del kwargs["bound_probabilities"]

        # initial data set
        try:
            sampling_result = self.meas_unbiased_probabilities(
                num_samples=num_unique, bound_probabilities=sampling_result, **kwargs
            )
        except QTeaOPESError:
            if not ignore_opes_errors:
                # Trigger exception anyway
                raise

            # User requests to ignore them, print to logger, and return empty dict
            logger.warning("Initial OPES sampling failed.")
            return {}

        covered_probability = sum(
            interval[1] - interval[0] for interval in sampling_result.values()
        )

        while (len(sampling_result) < num_unique) and (
            covered_probability < exit_coverage
        ):
            delta = num_unique - len(sampling_result)
            num_samples = max(10, 2 * delta)

            try:
                sampling_result = self.meas_unbiased_probabilities(
                    num_samples=num_samples,
                    bound_probabilities=sampling_result,
                    **kwargs,
                )
            except QTeaOPESError:
                if not ignore_opes_errors:
                    # Trigger exception anyway
                    raise

                # User requests to ignore them, print to logger, and return what
                # we have so far
                logger.warning(
                    "OPES sampling failed in loop; returning most recent results."
                )
                return sampling_result

            covered_probability = sum(
                interval[1] - interval[0] for interval in sampling_result.values()
            )

        return sampling_result

    @staticmethod
    def mpi_sample_n_unique_states(
        state,
        num_unique,
        comm,
        tensor_backend,
        cache_size=None,
        cache_clearing_strategy=None,
        filter_func=None,
        mpi_final_op=None,
        root=0,
        **kwargs,
    ):
        """
        Sample a target number of unique states. This is the target number of
        states, the actual number of states can differ.

        **Arguments**

        state : instance of :class:`_AbstractTN`
            State to be sampled from; needs to exist only on root and will
            be broadcasted via MPI to all other threads.

        num_unique : int
            Number of unique states to be sampled. This is a target number;
            the actual number of sampled states might differ in the end.

        comm : MPI-communicator from mpi4py
            Communicator of threads to be used for sampling.

        tensor_backend : :class:`TensorBackend`
            Tensor backend used for state, which will be needed to build
            up the state during bcast.

        cache_size : int, optional
            Cache size limit for the sampling (bytes) per MPI-thread.
            Default to 1,000,000,000 (1GB).

        cache_clearing_strategy : str, optional
            The strategy to be used to clear the cache
            within the sampling routine for TTN simulation.
            The possibilities are "num_qubits" or "state".
            Default to "num_qubits".

        filter_func : callable or `None`, optional
            Takes state string and probability boundaries as the two
            arguments in this order and returns `True` / `False.
            Filtering can reduce the workload before MPI-communication
            of states.
            Default to `None` (no filtering)

        mpi_final_op : str or `None`
            Either `None` or `mpi_gather` (root will contain all states)
            or `mpi_all_gather` (all threads will contain all states)
            Default to `None`.

        root : int, optional
            Thread-index of the MPI-thread holding the TN ansatz.
            Default to 0.

        ansatz : _AbstractTN (inside kwargs)
            Ansatz is needed to broadcast the TN state to the other processes.

        kwargs : keyword arguments
            Passed through to unbiased sampling, e.g., `qiskit_convention`,
            `precision`, and `mode`.
        """
        for key in kwargs:
            if key not in ["qiskit_convention", "precision", "mode", "ansatz"]:
                raise ValueError(f"Keyword argument `{key}` not allowed.")

        if mpi_final_op not in [None, "mpi_gather", "mpi_all_gather"]:
            raise ValueError(f"Argument for mpi_final_op {mpi_final_op} not allowed.")

        if MPI is None:
            raise ImportError(
                "Trying to call sampling with MPI, but MPI was not imported."
            )

        # We need a deepcopy of the keywork arguments here as we delete the key
        # "ansatz". Deleting this key "ansatz" is necessary as
        # ``sample_n_unique_states`` will check for superfluous keyword arguments.
        # This choice is a bit peculiar, but allows to hide the keyword argument
        # "ansatz" filled by the TN implementation (and not provided by the user).
        kwargs = deepcopy(kwargs)
        ansatz = kwargs["ansatz"]
        exit_coverage = kwargs.get("exit_coverage", 0.9999)
        del kwargs["ansatz"]

        size = comm.Get_size()
        rank = comm.Get_rank()

        psi = ansatz.mpi_bcast(state, comm, tensor_backend, root=root)

        if cache_size is not None:
            psi.set_cache_limit_sampling(cache_size)
        if cache_clearing_strategy is not None:
            psi.set_cache_clearing_strategy_sampling(strategy=cache_clearing_strategy)

        ranges = np.linspace(0, 1, size + 1)

        # We divide the workload of sampling by dividing the interval into size
        # subintervals evenly distributed. We use the sampling feature of defining
        # an already sampled interval to block for each MPI-process the intervals
        # of the other MPI processes. To identify the "special" intervals, they have
        # keys "left" and "right".
        sampling_result = {}
        if rank > 0:
            sampling_result["left"] = (0.0, ranges[rank])
        if rank + 1 < size:
            sampling_result["right"] = (ranges[rank + 1], 1.0)

        total_num_unique_states = 0
        total_covered_probability = 0
        total_num_active = size
        ii_active = 1

        while (
            total_num_unique_states < num_unique
            and total_covered_probability < exit_coverage
            and total_num_active > 0
        ):
            if ii_active == 1:
                num_unique_rank = int(
                    np.ceil((num_unique - total_num_unique_states) / total_num_active)
                )
                sampling_result = psi.sample_n_unique_states(
                    num_unique_rank, bound_probabilities=sampling_result, **kwargs
                )

            # Ignore left/right boundary, account for double counting states
            # at boundary
            ii_num_unique_states = len(sampling_result) - 3

            ii_covered_probability = sum(
                interval[1] - interval[0] for interval in sampling_result.values()
            )

            if ii_covered_probability >= exit_coverage:
                ii_active = 0

            ii_covered_probability -= sampling_result.get("left", [0.0, 0.0])[1]
            ii_covered_probability -= 1.0 - sampling_result.get("right", [1.0, 1.0])[0]

            # pylint: disable=c-extension-no-member
            # Gather results
            total_num_unique_states = comm.allreduce(ii_num_unique_states, op=MPI.SUM)
            total_covered_probability = comm.allreduce(
                ii_covered_probability, op=MPI.SUM
            )
            total_num_active = comm.allreduce(ii_active, op=MPI.SUM)
            # pylint: enable=c-extension-no-member

        if rank > 0:
            del sampling_result["left"]
        if rank + 1 < size:
            del sampling_result["right"]

        if filter_func is not None:
            # Apply filter passed by user
            keys_to_delete = []
            for key, value in sampling_result.items():
                if filter_func(key, value):
                    keys_to_delete.append(key)
                    sampling_result[key] = None

            for key in keys_to_delete:
                del sampling_result[key]

        if mpi_final_op in ["mpi_gather", "mpi_all_gather"]:
            # Collect everything on root
            if comm.Get_rank() == root:
                for ii in range(comm.Get_size()):
                    if ii == root:
                        continue

                    dict_ii = comm.recv(source=ii)
                    sampling_result.update(dict_ii)

            else:
                comm.send(sampling_result, root)

        if mpi_final_op == "mpi_all_gather":
            sampling_result = comm.bcast(sampling_result, root=root)

        return sampling_result

    def _get_children_prob(self, tensor, site_idx, curr_state, do_clear_cache):
        """
        Compute the probability and the relative tensor state of all the
        children of site `site_idx` in the probability tree

        Parameters
        ----------

        tensor : np.ndarray
            Parent tensor, with respect to which we compute the children

        site_idx : int
            Index of the parent tensor

        curr_state : str
            Comma-separated string tracking the current state of all
            sites already done with their projective measurements.

        do_clear_cache : bool
            Flag if the cache should be cleared. Only read for first
            site when a new meausrement begins.

        Returns
        -------

        probabilities : list of floats
            Probabilities of the children

        tensor_list : list of ndarray
            Child tensors, already contracted with the next site
            if not last site.
        """
        # Cannot implement it here, it highly depends on the TN
        # geometry
        raise NotImplementedError("This function has to be overwritten.")

    def _get_children_magic(
        self, transfer_matrix, site_idx, curr_state, do_clear_cache
    ):
        """
        Compute the magic probability and the relative tensor state of all the
        children of site `site_idx` in the probability tree, conditioned on
        the transfer matrix

        Parameters
        ----------

        transfer_matrix : np.ndarray
            Parent transfer matrix, with respect to which we compute the children

        site_idx : int
            Index of the parent tensor

        curr_state : str
            Comma-separated string tracking the current state of all
            sites already done with their projective measurements.

        do_clear_cache : bool
            Flag if the cache should be cleared. Only read for first
            site when a new measurement begins.

        Returns
        -------

        probabilities : list of floats
            Probabilities of the children

        tensor_list : list of ndarray
            Child tensors, already contracted with the next site
            if not last site.
        """
        # Cannot implement it here, it highly depends on the TN
        # geometry
        raise NotImplementedError("This function has to be overwritten.")

    def clear_cache(self, num_qubits_keep=None, all_probs=None, current_key=None):
        """
        Clear cache until cache size is below cache limit again. This function
        is empty and works for any tensor network without cache. If the inheriting
        tensor network has a cache, it has to be overwritten.

        **Arguments**

        all_probs : list of dicts
            Contains already calculated branches of probability tree. Each
            TTN has to decide if they need to be cleaned up as well.
        """
        if self is None:
            # Never true, but prevent linter warning (needs self when
            # cache is actually defined) and unused arguments
            print("Args", num_qubits_keep, all_probs, current_key)
            return None

        return all_probs

    def _get_child_prob(
        self,
        tensor,
        site_idx,
        target_prob,
        unitary_setup,
        curr_state,
        qiskit_convention,
    ):
        """
        Compute which child has to be selected for a given target probability
        and return the index and the tensor of the next site to be measured.

        Parameters
        ----------

        tensor : np.ndarray
            Tensor representing the site to be measured with a projective
            measurement.

        site_idx : int
            Index of the site to be measured and index of `tensor`.

        target_prob : scalar
            Scalar drawn from U(0, 1) and deciding on the which projective
            measurement outcome will be picked. The decision is based on
            the site `site_idx` only.

        unitary_setup : instance of :class:`UnitarySetupProjMeas` or `None`
            If `None`, no local unitaries are applied. Otherwise,
            unitary for local transformations are provided and applied
            to the local sites.

        curr_state : np.ndarray of rank-1 and type int
            Record of current projective measurements done so far.

        qiskit_convention : bool
            Qiskit convention, i.e., ``True`` stores the projective
            measurement in reverse order, i.e., the first qubit is stored
            in ``curr_state[-1]``. Passing ``False`` means indices are
            equal and not reversed.
        """
        # Cannot implement it here, it highly depends on the TN
        # geometry
        raise NotImplementedError("This function has to be overwritten.")

    def compute_energy(self, pos=None):
        """
        Compute the energy of the TTN through the effective operator
        at position pos.

        Parameters
        ----------
        pos : list, optional
            If a position is provided, the isometry is first shifted to
            that position and then the energy is computed. If None,
            the current isometry center is computed, by default None

        Returns
        -------
        float
            Energy of the TTN
        """

        if self.eff_op is None:
            logger.warning(
                "Tried to compute energy with no effective operators. Returning nan."
            )
            return np.nan
        # Move the iso center if needed
        if pos is not None:
            self.iso_towards(pos)
        else:
            pos = self.iso_center
            if not np.isscalar(pos):
                pos = tuple(pos)

        self.move_pos(pos, device=self._tensor_backend.computational_device)

        # Retrieve the tensor at the isometry
        tens = self[self.iso_center]

        # Get the list of operators to contract
        pos_links = self.get_pos_links(pos)

        # Contract the tensor with the effective operators around
        vec = self.eff_op.contract_tensor_lists(tens, pos, pos_links)

        # force a standard python float
        energy = float(np.real(tens.get_of(tens.dot(vec))))

        # Update internal storage
        self._prev_energy = energy

        # Force to return standard python float
        return float(np.real(np.array(tens.get_of(energy))))

    #########################################################################
    ######################### Optimization methods ##########################
    #########################################################################

    def optimize_single_tensor(self, pos):
        """
        Optimize the tensor at position `pos` based on the
        effective operators loaded in the TTN

        Parameters
        ----------
        pos : list of ints or int
            Position of the tensor in the TN

        Returns
        -------
        float
            Computed energy
        """
        tic = tictoc()

        # Isometrise towards the desired tensor
        self.iso_towards(pos)
        pos_links = self.get_pos_links(pos)

        dim_problem = np.prod(self[pos].shape)
        if dim_problem == 1:
            # Nothing to do - ARPACK will fail
            eigenvalue = self.compute_energy()
            return eigenvalue

        # If we have effective projectors, get the function to project them out.
        # This is passed to the eig_api() as kwargs.
        # The projectors act directly on the Lanczos vectors.
        if len(self.eff_proj) > 0:
            project_out_projectors = self.get_projector_function(
                pos=pos, pos_links=pos_links
            )

            # orthogonalize the initial tensor and normalize
            self[pos] = project_out_projectors(self[pos])
            self[pos].normalize()

        else:
            project_out_projectors = None

        # If noise is added, randomize the tensor
        if self.convergence_parameters.noise != 0:
            self[pos].randomize(noise=self.convergence_parameters.noise)
            self[pos].normalize()

        # solve with solver
        eigenvalues, tensor = self[pos].eig_api(
            self.eff_op.contract_tensor_lists,
            self[pos].shape,
            self._convergence_parameters,
            args_func=(pos, pos_links),
            kwargs_func={"pre_return_hook": project_out_projectors},
        )

        logger.info(
            "Optimized tensor %-8s  max chi: %-4d  energy: %-19.14g  time: %.1f",
            pos,
            max(tensor.shape),
            eigenvalues[0],
            tictoc() - tic,
        )

        self[pos] = tensor

        # Update internal storage
        self._prev_energy = eigenvalues[0]

        return np.real(tensor.get_of(eigenvalues[0]))

    def optimize_link_expansion(
        self,
        pos,
        pos_partner,
        link_self,
        link_partner,
    ):
        """
        Optimize a tensor pair via a space-link expansion.

        **Arguments**

        pos : int, tuple of ints (depending on TN)
            position of tensor to be optimized

        pos_partner : int, tuple of ints (depending on TN)
            position of partner tensor, where link between
            tensor and partner tensor will be randomly
            expanded.

        link_self : int
            Link connecting to partner tensor (in tensor at `pos`)

        link_partner : int
            Link connecting to optimized tensors (in partner tensor).

        requires_singvals : bool
            Flag if calling methods upstream need singular values, i.e.,
            want to replace QR with SVDs

        Returns
        -------
        float
            Computed energy
        """
        if isinstance(pos, list):
            raise QTeaLeavesError("Passing list as position")
        if isinstance(pos_partner, list):
            raise QTeaLeavesError("Passing list as partner position")

        # Here it would be beneficial to implement the skip_exact_rgtensors, but
        # we would need to add a data structure to flag which tensors are converged.
        # After that, when moving the iso with svd we can easily understand if there
        # is truncation
        # _ = self._convergence_parameters.sim_params["skip_exact_rgtensors"]
        self.iso_towards(pos_partner)

        tensor = self[pos].copy()
        tensor_partner = self[pos_partner].copy()

        # If energy goes up and we want to reinstall original tensor
        expansion_drop = self._convergence_parameters.sim_params["expansion_drop"]
        if not expansion_drop == "f":
            if self._prev_energy is None:
                self._prev_energy = self.compute_energy()
            prev_tensor = tensor.copy()
            prev_tensor_partner = tensor_partner.copy()

        link_dim = tensor.shape[link_self]
        max_dim = link_dim + self._convergence_parameters.sim_params["min_expansion"]

        links_copy_self = list(tensor.links).copy()
        links_copy_self[link_self] = None
        links_copy_self = tensor.set_missing_link(
            links_copy_self, max_dim, are_links_outgoing=tensor.are_links_outgoing
        )

        links_copy_other = list(tensor_partner.links).copy()
        links_copy_other[link_partner] = None
        links_copy_other = tensor_partner.set_missing_link(
            links_copy_other,
            max_dim,
            are_links_outgoing=tensor_partner.are_links_outgoing,
        )

        new_dim = min(
            int(links_copy_self[link_self]),
            int(links_copy_other[link_partner]),
            max_dim,
        )

        if new_dim <= link_dim:
            # cannot expand anything here
            logger.debug("Saturated expansion, optimizing individually.")

            # Have to do isostep and norm as well
            self.iso_towards(pos, move_to_memory_device=False)

            energy = self.optimize_single_tensor(pos)
            return energy

        self[pos], self[pos_partner] = tensor.expand_link_tensorpair(
            tensor_partner,
            link_self,
            link_partner,
            new_dim,
        )

        # Ideal implementation would be ...
        # First iso_towards to pos_partner, as well as pos_partner
        # after decision.

        # Update of eff operators (internal iso_towards in space link
        # expansion cannot truncate or update singvals)
        # By move_to_memory_device=False we also keep the other
        # tensor in device memory
        self.iso_towards(pos, move_to_memory_device=False)

        # Random entries destroyed normalization, to get valid
        # eigenvalue in these intermediate steps, need to renormalize
        self.normalize()

        # Expansion cycles
        # ----------------

        # Same here, use QR as otherwise truncation kicks in potentially]
        # undoing the expansion. Final iso_towards with QR or SVD follows
        # after expansion cycles.
        requires_singvals = self._requires_singvals
        self._requires_singvals = False

        for _ in range(self._convergence_parameters.sim_params["expansion_cycles"]):
            self.iso_towards(pos, move_to_memory_device=False)
            energy = self.optimize_single_tensor(pos)

            self.iso_towards(pos_partner, move_to_memory_device=False)
            energy = self.optimize_single_tensor(pos_partner)

        # Reset value
        self._requires_singvals = requires_singvals

        # Decision on accepting update
        # ----------------------------

        if expansion_drop in ["f"] or energy <= self._prev_energy:
            # We improved in energy or accept higher energies to escape local
            # minima in this sweep
            self.iso_towards(
                pos,
                keep_singvals=requires_singvals,
                trunc=True,
                conv_params=self._convergence_parameters,
            )
            # should we compute this? yes, the difference can be large ...
            self.normalize()
            energy = self.compute_energy(pos)
        elif expansion_drop in ["o"]:
            # Energy did not improve, but optimize locally

            # pylint: disable-next=possibly-used-before-assignment
            self[pos] = prev_tensor
            # pylint: disable-next=possibly-used-before-assignment
            self[pos_partner] = prev_tensor_partner

            # Iso center before copy was at pos_partner
            self.iso_center = pos_partner
            self.iso_towards(
                pos,
                trunc=requires_singvals,
                keep_singvals=requires_singvals,
            )
            energy = self.optimize_single_tensor(pos)

        elif expansion_drop in ["d"]:
            # Energy did not improve, reinstall previous tensors, discard
            # step and do not optimize even locally

            # pylint: disable-next=possibly-used-before-assignment
            self[pos] = prev_tensor
            # pylint: disable-next=possibly-used-before-assignment
            self[pos_partner] = prev_tensor_partner

            # Iso center before copy was at pos_partner
            self.iso_center = pos_partner
            self.iso_towards(
                pos,
                trunc=requires_singvals,
                keep_singvals=requires_singvals,
            )
        else:
            # There should be no other case
            raise QTeaLeavesError(f"Unknown {expansion_drop=} scenario.")

        # iso_towards does not normalize (maybe it does inside the truncate methods ...)
        # but not normalization should be necessary if eigensolver returns
        # basisvectors which should be normalized by default

        return energy

    def optimize_two_tensors(self, pos, pos_partner, link_self, link_partner):
        """
        Local ground-state search on two tensors simultaneously.

        Parameters
        ----------
        pos : Tuple[int] | int
            Position in the TN of the tensor to time-evolve
        pos_partner : int, tuple of ints (depending on TN)
            position of partner tensor, where link between
            tensor and partner tensor will be randomly
            expandend.
        link_self : int
            Link connecting to partner tensor (in tensor at `pos`)
        link_partner : int
            Link connecting to optimized tensors (in partner tensor).

        Returns
        -------
        float
            Computed energy
        """
        # Isometrize towards the desired tensor.
        # We do this additional step to ensure they are both
        # on the computational device
        self.iso_towards(pos_partner)
        self.iso_towards(pos, move_to_memory_device=False)

        tens_a = self[pos]
        tens_b = self[pos_partner]
        is_a_outgoing = tens_a.are_links_outgoing[link_self]

        theta = tens_a.tensordot(tens_b, ([link_self], [link_partner]))

        # Build custom eff ops list
        custom_ops = []
        for ii, elem in enumerate(self.get_pos_links(pos)):
            if ii == link_self:
                continue

            if elem is None:
                custom_ops.append(None)
            else:
                custom_ops.append(self.eff_op[(elem, pos)])

        for ii, elem in enumerate(self.get_pos_links(pos_partner)):
            if ii == link_partner:
                continue

            if elem is None:
                custom_ops.append(None)
            else:
                custom_ops.append(self.eff_op[(elem, pos_partner)])

        custom_ops, theta, inv_perm = self.permute_spo_for_two_tensors(
            custom_ops, theta, link_partner
        )

        if len(self.eff_proj) > 0:
            raise NotImplementedError(
                """The effective projectors are not
                                       implemented for two tensor optimization."""
            )

        eigenvalues, theta = theta.eig_api(
            self.eff_op.contract_tensor_lists,
            theta.shape,
            self._convergence_parameters,
            args_func=(None, None),
            kwargs_func={"custom_ops": custom_ops},
        )

        if inv_perm is not None:
            theta.transpose_update(inv_perm)

        links_a = list(range(tens_a.ndim - 1))
        links_b = list(range(tens_a.ndim - 1, theta.ndim))

        tens_a, tens_b, svals, svals_cut = theta.split_svd(
            links_a,
            links_b,
            contract_singvals="R",
            conv_params=self._convergence_parameters,
            is_link_outgoing_left=is_a_outgoing,
        )

        svals_cut = self._postprocess_singvals_cut(
            singvals_cut=svals_cut, conv_params=self._convergence_parameters
        )
        svals_cut = theta.get_of(svals_cut)

        self.set_singvals_on_link(pos, pos_partner, svals)

        nn = tens_a.ndim
        perm_a = list(range(link_self)) + [nn - 1] + list(range(link_self, nn - 1))
        self[pos] = tens_a.transpose(perm_a)

        nn = tens_b.ndim
        perm_b = (
            list(range(1, link_partner + 1)) + [0] + list(range(link_partner + 1, nn))
        )
        self[pos_partner] = tens_b.transpose(perm_b)

        self.iso_towards(pos_partner, keep_singvals=True)

        return np.real(tens_a.get_of(eigenvalues[0]))

    #########################################################################
    ######################## Time evolution methods #########################
    #########################################################################

    def timestep_single_tensor(self, pos, next_pos, sc):
        """
        Time step for a single-tensor update on a single tensor `exp(sc*Heff*dt)`.

        Parameters
        ----------
        pos : Tuple[int] | int
            Position in the TN of the tensor to time-evolve
        next_pos: Tuple[int] | int
            Position in the TN of the next tensor to time-evolve
        sc : complex
            Multiplicative factor in the exponent `exp(sc*Heff*dt)`

        Return
        ------
        List[qtealeaves.solvers.krylovexp_solver.KrylovInfo]
            Information about the convergence of each Krylov update.

        """
        logger.info("Time-step at tensor %s-%s", pos, next_pos)
        logger.debug("Time-step at tensor's norm %f, scalar %s", self.norm(), sc)

        timestep_info = []

        # Isometrize towards the desired tensor
        self.iso_towards(pos)
        pos_links = self.get_pos_links(pos)

        if sc.imag == 0:
            sc = sc.real

        krylov_solver = self._solver(
            self[pos],
            sc,
            self.eff_op.contract_tensor_lists,
            self._convergence_parameters,
            args_func=(pos, pos_links),
        )

        self[pos], conv = krylov_solver.solve()
        timestep_info.append(conv)

        if next_pos is not None:
            # Have to evolve backwards
            # ------------------------
            #
            # This is a bit inconvenient, because we have to shift the isometry
            # center by hand as the r-tensor has to be evolved backwards in time.
            (
                rtens,
                pos_partner,
                link_partner,
                path_elem,
            ) = self._partial_iso_towards_for_timestep(pos, next_pos)

            # Retrieve operator from partner to iso center
            ops_a = self.eff_op[(pos_partner, pos)]

            # Path elem src layer-tensor-link, dst layer-tensor-link
            self._update_eff_ops(path_elem)

            # Needing just one operators, no idxs needed
            ops_b = self.eff_op[(pos, pos_partner)]

            # Assumed to be in the order of links
            ops_list_reverse = [ops_b, ops_a]

            krylov_solver = self._solver(
                rtens,
                -sc,
                self.eff_op.contract_tensor_lists,
                self._convergence_parameters,
                args_func=(None, None),
                kwargs_func={"custom_ops": ops_list_reverse},
            )

            rtens, conv = krylov_solver.solve()
            timestep_info.append(conv)

            tmp = rtens.tensordot(self[pos_partner], ([1], [link_partner]))
            if link_partner == 0:
                self[pos_partner] = tmp
            else:
                nn = self[pos_partner].ndim
                perm = (
                    list(range(1, link_partner + 1))
                    + [0]
                    + list(range(link_partner + 1, nn))
                )
                self[pos_partner] = tmp.transpose(perm)

            self.iso_center = pos_partner
            # Move pos to the memory device
            self.move_pos(pos, device=self._tensor_backend.memory_device, stream=True)

        return timestep_info

    def timestep_two_tensors(self, pos, next_pos, sc, skip_back):
        """
        Time step for a single-tensor update on two tensors `exp(sc*Heff*dt)`.

        Parameters
        ----------
        pos : Tuple[int] | int
            Position in the TN of the tensor to time-evolve
        next_pos: Tuple[int] | int
            Position in the TN of the next tensor to time-evolve
        sc : complex
            Multiplicative factor in the exponent `exp(sc*Heff*dt)`
        skip_back : bool
            Flag if backwards propagation of partner tensor can be skipped;
            used for last two tensors, partner tensor must be next position
            as well.

        Return
        ------
        List[qtealeaves.solvers.krylovexp_solver.KrylovInfo]
            Information about the convergence of each Krylov update.

        """
        logger.debug("Time-step at tensor %s", pos)

        timestep_info = []

        if len(self.eff_proj) > 0:
            # the effective projectors should not be here, as they are ignored.
            raise QTeaLeavesError(
                "Doing time evolution with self.eff_proj set."
                + "Remove eff_proj before starting the dynamics."
            )

        # Isometrize towards the desired tensor
        self.iso_towards(pos)

        # pos_partner, link_pos, link_partner = self.get_pos_partner_link_expansion(pos)
        (
            link_pos,
            pos_partner,
            link_partner,
            path_elem,
        ) = self._partial_iso_towards_for_timestep(pos, next_pos, no_rtens=True)

        tens_a = self[pos]
        tens_b = self[pos_partner]
        is_a_outgoing = tens_a.are_links_outgoing[link_pos]

        theta = tens_a.tensordot(tens_b, ([link_pos], [link_partner]))

        # Build custom eff ops list
        custom_ops = []
        for ii, elem in enumerate(self.get_pos_links(pos)):
            if ii == link_pos:
                continue

            if elem is None:
                custom_ops.append(None)
            else:
                custom_ops.append(self.eff_op[(elem, pos)])

        for ii, elem in enumerate(self.get_pos_links(pos_partner)):
            if ii == link_partner:
                continue

            if elem is None:
                custom_ops.append(None)
            else:
                custom_ops.append(self.eff_op[(elem, pos_partner)])

        custom_ops, theta, inv_perm = self.permute_spo_for_two_tensors(
            custom_ops, theta, link_partner
        )
        krylov_solver = self._solver(
            theta,
            sc,
            self.eff_op.contract_tensor_lists,
            self._convergence_parameters,
            args_func=(None, None),
            kwargs_func={"custom_ops": custom_ops},
        )

        theta, conv = krylov_solver.solve()
        timestep_info.append(conv)

        if inv_perm is not None:
            theta.transpose_update(inv_perm)

        links_a = list(range(tens_a.ndim - 1))
        links_b = list(range(tens_a.ndim - 1, theta.ndim))

        tens_a, tens_b, svals, svals_cut = theta.split_svd(
            links_a,
            links_b,
            contract_singvals="R",
            conv_params=self._convergence_parameters,
            is_link_outgoing_left=is_a_outgoing,
        )

        svals_cut = self._postprocess_singvals_cut(
            singvals_cut=svals_cut, conv_params=self._convergence_parameters
        )
        svals_cut = theta.get_of(svals_cut)

        self.set_singvals_on_link(pos, pos_partner, svals)

        nn = tens_a.ndim
        perm_a = list(range(link_pos)) + [nn - 1] + list(range(link_pos, nn - 1))
        self[pos] = tens_a.transpose(perm_a)

        nn = tens_b.ndim
        perm_b = (
            list(range(1, link_partner + 1)) + [0] + list(range(link_partner + 1, nn))
        )
        self[pos_partner] = tens_b.transpose(perm_b)

        self._update_eff_ops(path_elem)
        self.iso_center = pos_partner

        # Move back to memory tensor at pos
        self.move_pos(pos, device=self._tensor_backend.memory_device, stream=True)

        if not skip_back:
            # Have to evolve backwards
            # ------------------------

            pos_links = self.get_pos_links(pos_partner)

            krylov_solver = self._solver(
                self[pos_partner],
                -sc,
                self.eff_op.contract_tensor_lists,
                self._convergence_parameters,
                args_func=(pos_partner, pos_links),
            )

            self[pos_partner], conv = krylov_solver.solve()
            timestep_info.append(conv)

        elif pos_partner != next_pos:
            raise QTeaLeavesError("Sweep order incompatible with two-tensor update.")

        return timestep_info

    def timestep_single_tensor_link_expansion(self, pos, next_pos, sc):
        """
        Time step for a single-tensor update on two tensors `exp(sc*Heff*dt)`.

        Parameters
        ----------
        pos : Tuple[int] | int
            Position in the TN of the tensor to time-evolve
        next_pos: Tuple[int] | int
            Position in the TN of the next tensor to time-evolve
        sc : complex
            Multiplicative factor in the exponent `exp(sc*Heff*dt)`

        Return
        ------
        List[qtealeaves.solvers.krylovexp_solver.KrylovInfo]
            Information about the convergence of each Krylov update.

        """
        logger.debug("Time-step with link expansion at tensor %s", pos)

        timestep_info = []
        requires_singvals = True

        if next_pos is None:
            return self.timestep_single_tensor(pos, next_pos, sc)

        self.iso_towards(
            pos,
            trunc=requires_singvals,
            keep_singvals=requires_singvals,
            move_to_memory_device=True,
        )
        self.iso_towards(
            next_pos,
            trunc=requires_singvals,
            keep_singvals=requires_singvals,
            move_to_memory_device=False,
        )

        (
            link_self,
            pos_partner,
            link_partner,
            _,
        ) = self._partial_iso_towards_for_timestep(pos, next_pos, no_rtens=True)

        tensor = self[pos].copy()
        tensor_partner = self[pos_partner].copy()

        # Expand the tensors
        option_a = (
            tensor.shape[link_self]
            + self._convergence_parameters.sim_params["min_expansion"]
        )
        option_b = 2 * tensor.shape[link_self]
        option_c = np.delete(list(tensor.shape), link_self).prod()

        # pylint: disable-next=nested-min-max
        new_dim = min(option_a, min(option_b, option_c))

        self[pos], self[pos_partner] = tensor.expand_link_tensorpair(
            tensor_partner, link_self, link_partner, new_dim, ctrl="Z"
        )
        # Update of eff operators (internal iso_towards in space link
        # expansion cannot truncate or update singvals)
        self.iso_towards(pos, move_to_memory_device=False)

        # Expansion cycles
        # ----------------

        # Same here, use QR as otherwise truncation kicks in potentially]
        # undoing the expansion. Final iso_towards with QR or SVD follows
        # after expansion cycles.
        exp_cycles = self._convergence_parameters.sim_params["expansion_cycles"]

        sc_e = sc / exp_cycles
        for ii in range(exp_cycles):
            self.iso_towards(pos, move_to_memory_device=False)
            conv = self.timestep_single_tensor(pos, pos_partner, sc_e)
            timestep_info.extend(conv)

            if exp_cycles > 1:
                next_pos_partner = pos if ii < exp_cycles - 1 else None
                conv = self.timestep_single_tensor(pos_partner, next_pos_partner, sc_e)
                timestep_info.extend(conv)

        # Evolve back the tensor at pos_partner
        if exp_cycles > 1:
            conv = self.timestep_single_tensor(pos_partner, None, -sc)
            timestep_info.extend(conv)
            self.iso_towards(
                pos,
                trunc=requires_singvals,
                keep_singvals=requires_singvals,
                move_to_memory_device=False,
            )
            self.iso_towards(
                pos_partner,
                trunc=requires_singvals,
                keep_singvals=requires_singvals,
                move_to_memory_device=True,
            )

        return timestep_info

    # pylint: disable-next=too-many-return-statements
    def timestep(self, dt, mode, sweep_order=None, sweep_order_back=None):
        """
        Evolve the Tensor network for one timestep.

        Parameters
        ----------
        mode : int
            Currently encoded are single-tensor TDVP first order (1), two-tensor
            TDVP first order (2), two-tensor TDVP second order (3), and single-tensor
            TDVP second order (4). A flex-TDVP as (5) is pending. The "_kraus" extension
            for modes 1-4 includes dissipative evolution.
        sweep_order : List[int] | None
            Order in which we iterate through the network for the timestep.
            If None, use the default in `self.default_sweep_order()`
        sweep_order_back : List[int] | None
            Order in which we iterate backwards through the network for the timestep.
            If None, use the default in `self.default_sweep_order()[::-1]`
        dt : float
            Timestep

        Returns
        -------
        List[qtealeaves.solvers.krylovexp_solver.KrylovInfo]
            Information about the convergence of each Krylov update.

        Details
        -------

        Flex-TDVP in the fortran implementation was using two-tensor updates
        as long as the maximal bond dimension is not reached and then a ratio
        of 9 single-tensor updates to 1 two-tensor update step.
        """

        if len(self.eff_proj) > 0:
            # the effective projectors should not be here, as they are ignored.
            raise QTeaLeavesError(
                "Doing time evolution with self.eff_proj set."
                + "Remove eff_proj before starting the dynamics."
            )

        if mode == 1:
            return self.timestep_mode_1(dt, sweep_order=sweep_order)
        if mode == 2:
            return self.timestep_mode_2(dt, sweep_order=sweep_order)
        if mode == 3:
            return self.timestep_mode_3(
                dt,
                sweep_order=sweep_order,
                sweep_order_back=sweep_order_back,
            )
        if mode == 4:
            return self.timestep_mode_4(
                dt,
                sweep_order=sweep_order,
                sweep_order_back=sweep_order_back,
            )
        if mode == 5:
            return self.timestep_mode_5(dt, sweep_order=sweep_order)
        if mode == "1_kraus":
            return self.timestep_mode_1_kraus(dt, sweep_order=sweep_order)
        if mode == "2_kraus":
            return self.timestep_mode_2_kraus(dt, sweep_order=sweep_order)
        if mode == "3_kraus":
            return self.timestep_mode_3_kraus(
                dt, sweep_order=sweep_order, sweep_order_back=sweep_order_back
            )
        if mode == "4_kraus":
            return self.timestep_mode_4_kraus(
                dt, sweep_order=sweep_order, sweep_order_back=sweep_order_back
            )
        raise ValueError(f"Time evolution mode {mode} not available.")

    def timestep_mode_1(self, dt, sweep_order=None, normalize=False):
        """
        Evolve the Tensor network for one timestep (single-tensor update
        1st order).

        Parameters
        ----------
        dt : float
            Timestep
        sweep_order : List[int] | None
            Order in which we iterate through the network for the timestep.
            If None, use the default in `self.default_sweep_order()`

        Returns
        -------
        List[qtealeaves.solvers.krylovexp_solver.KrylovInfo]
            Information about the convergence of each Krylov update.
        """
        convergence_info = []

        if sweep_order is None:
            sweep_order = self.default_sweep_order()

        for ii, pos in enumerate(sweep_order):
            # 1st order update
            next_pos = None if (ii + 1 == len(sweep_order)) else sweep_order[ii + 1]
            convergence_info.extend(
                self.timestep_single_tensor(pos, next_pos, -1j * dt)
            )
            if normalize:
                self.normalize()

        return convergence_info

    def timestep_mode_2(self, dt, sweep_order=None):
        """
        Evolve the Tensor network for one timestep (two-tensor update
        1st order).

        Parameters
        ----------
        dt : float
            Timestep
        sweep_order : List[int] | None
            Order in which we iterate through the network for the timestep.
            If None, use the default in `self.default_sweep_order()`

        Returns
        -------
        List[qtealeaves.solvers.krylovexp_solver.KrylovInfo]
            Information about the convergence of each Krylov update.
        """
        timestep_info = []

        if sweep_order is None:
            sweep_order = self.default_sweep_order()

        for ii, pos in enumerate(sweep_order):
            # 1st order update
            next_pos = None if (ii + 1 == len(sweep_order)) else sweep_order[ii + 1]
            skip_back = ii + 2 == len(sweep_order)
            timestep_info.extend(
                self.timestep_two_tensors(pos, next_pos, -1j * dt, skip_back)
            )

            if skip_back:
                break

        return timestep_info

    def timestep_mode_3(self, dt, sweep_order=None, sweep_order_back=None):
        """
        Evolve the Tensor network for one timestep (two-tensor update
        2nd order).

        Parameters
        ----------
        dt : float
            Timestep
        sweep_order : List[int] | None
            Order in which we iterate through the network for the timestep.
            If None, use the default in `self.default_sweep_order()`
        sweep_order_back : List[int] | None
            Order in which we iterate backwards through the network for the timestep.
            If None, use the default in `self.default_sweep_order()[::-1]`

        Returns
        -------
        List[qtealeaves.solvers.krylovexp_solver.KrylovInfo]
            Information about the convergence of each Krylov update.
        """
        conv = self.timestep_mode_2(0.5 * dt, sweep_order=sweep_order)

        if sweep_order_back is None:
            sweep_order_back = self.default_sweep_order_back()

        conv_back = self.timestep_mode_2(0.5 * dt, sweep_order=sweep_order_back)

        return conv + conv_back

    def timestep_mode_4(
        self, dt, sweep_order=None, sweep_order_back=None, normalize=False
    ):
        """
        Evolve the Tensor network for one timestep (single-tensor update
        2nd order).

        Parameters
        ----------
        dt : float
            Timestep
        sweep_order : List[int] | None
            Order in which we iterate through the network for the timestep.
            If None, use the default in `self.default_sweep_order()`
        sweep_order_back : List[int] | None
            Order in which we iterate backwards through the network for the timestep.
            If None, use the default in `self.default_sweep_order()[::-1]`

        Returns
        -------
        List[qtealeaves.solvers.krylovexp_solver.KrylovInfo]
            Information about the convergence of each Krylov update.
        """
        conv = self.timestep_mode_1(
            0.5 * dt, sweep_order=sweep_order, normalize=normalize
        )

        if sweep_order_back is None:
            sweep_order_back = self.default_sweep_order_back()

        conv_back = self.timestep_mode_1(
            0.5 * dt, sweep_order=sweep_order_back, normalize=normalize
        )

        return conv + conv_back

    def timestep_mode_5(self, dt, sweep_order=None, stride_two_tensor=10):
        """
        Evolve the Tensor network for one timestep (mixed two-tensor and
        one-tensor update, first order).

        Parameters
        ----------
        dt : float
            Timestep
        sweep_order : List[int] | None
            Order in which we iterate through the network for the timestep.
            If None, use the default in `self.default_sweep_order()`
        stride_two_tensor: int
            If maximum bond dimension is reached, do a two-tensor update
            every `stride_two_tensor` steps.

        Returns
        -------
        List[qtealeaves.solvers.krylovexp_solver.KrylovInfo]
            Information about the convergence of each Krylov update.
        """
        timestep_info = []

        if sweep_order is None:
            sweep_order = self.default_sweep_order()

        idx = self._timestep_mode_5_counter
        self._timestep_mode_5_counter += 1

        # For the main loop, we always evolve the R-tensor back in time
        skip_back = False

        for ii, pos in enumerate(sweep_order[:-2]):
            # Everything but the last two
            next_pos = sweep_order[ii + 1]

            link_pos, _, _, _ = self._partial_iso_towards_for_timestep(
                pos, next_pos, no_rtens=True
            )

            is_link_full = self[pos].is_link_full(link_pos)
            enforce_two_tensor = idx % stride_two_tensor == 0
            do_two_tensor = (not is_link_full) or enforce_two_tensor

            if do_two_tensor:
                timestep_info.extend(
                    self.timestep_two_tensors(pos, next_pos, -1j * dt, skip_back)
                )
            else:
                timestep_info.extend(
                    self.timestep_single_tensor(pos, next_pos, -1j * dt)
                )

        # Treat the last two tensors (cannot decide individually on update-scheme)
        pos = sweep_order[-2]
        next_pos = sweep_order[-1]
        link_pos, pos_partner, link_partner, _ = self._partial_iso_towards_for_timestep(
            pos, next_pos, no_rtens=True
        )

        is_link_full_a = self[pos].is_link_full(link_pos)
        is_link_full_b = self[pos_partner].is_link_full(link_partner)
        is_link_full = is_link_full_a or is_link_full_b
        enforce_two_tensor = idx % stride_two_tensor == 0
        do_two_tensor = (not is_link_full) or enforce_two_tensor

        if do_two_tensor:
            skip_back = True
            timestep_info.extend(
                self.timestep_two_tensors(pos, next_pos, -1j * dt, True)
            )
        else:
            timestep_info.extend(self.timestep_single_tensor(pos, next_pos, -1j * dt))
            timestep_info.extend(self.timestep_single_tensor(next_pos, None, -1j * dt))

        return timestep_info

    def timestep_mode_1_kraus(self, dt, sweep_order=None, normalize=False):
        """
        Evolve the Tensor network for one timestep of the Lindblad master equation
        (single-tensor update1st order) + Local dissipation.

        Parameters
        ----------
        dt : float
            Timestep
        sweep_order : List[int] | None
            Order in which we iterate through the network for the timestep.
            If None, use the default in `self.default_sweep_order()`
        sweep_order_back : List[int] | None
            Order in which we iterate backwards through the network for the timestep.
            If None, use the default in `self.default_sweep_order()[::-1]`

        Returns
        -------
        conv : List[qtealeaves.solvers.krylovexp_solver.KrylovInfo]
            Information about the convergence of each Krylov update.
        """

        kraus_ops = self.eff_op.get_local_kraus_operators(dt)

        conv1 = self.timestep_mode_1(
            0.5 * dt, sweep_order=sweep_order, normalize=normalize
        )
        singvals_cut = self.apply_local_kraus_channel(kraus_ops=kraus_ops)
        conv2 = self.timestep_mode_1(
            0.5 * dt, sweep_order=sweep_order, normalize=normalize
        )

        conv = conv1 + conv2

        return conv, singvals_cut

    def timestep_mode_2_kraus(self, dt, sweep_order=None):
        """
        Evolve the Tensor network for one timestep of the Lindblad master equation
        (two-tensor update 1st order) + Local dissipation.

        Parameters
        ----------
        dt : float
            Timestep
        sweep_order : List[int] | None
            Order in which we iterate through the network for the timestep.
            If None, use the default in `self.default_sweep_order()`
        sweep_order_back : List[int] | None
            Order in which we iterate backwards through the network for the timestep.
            If None, use the default in `self.default_sweep_order()[::-1]`

        Returns
        -------
        conv : List[qtealeaves.solvers.krylovexp_solver.KrylovInfo]
            Information about the convergence of each Krylov update.
        """

        kraus_ops = self.eff_op.get_local_kraus_operators(dt)

        conv1 = self.timestep_mode_2(0.5 * dt, sweep_order=sweep_order)
        singvals_cut = self.apply_local_kraus_channel(kraus_ops=kraus_ops)
        conv2 = self.timestep_mode_2(0.5 * dt, sweep_order=sweep_order)

        conv = conv1 + conv2

        return conv, singvals_cut

    def timestep_mode_3_kraus(self, dt, sweep_order=None, sweep_order_back=None):
        """
        Evolve the Tensor network for one timestep of the Lindblad master equation
        (two-tensor update 2nd order) + Local dissipation.

        Parameters
        ----------
        dt : float
            Timestep
        sweep_order : List[int] | None
            Order in which we iterate through the network for the timestep.
            If None, use the default in `self.default_sweep_order()`
        sweep_order_back : List[int] | None
            Order in which we iterate backwards through the network for the timestep.
            If None, use the default in `self.default_sweep_order()[::-1]`

        Returns
        -------
        conv : List[qtealeaves.solvers.krylovexp_solver.KrylovInfo]
            Information about the convergence of each Krylov update.
        """

        kraus_ops = self.eff_op.get_local_kraus_operators(dt)

        conv1 = self.timestep_mode_3(
            0.5 * dt,
            sweep_order=sweep_order,
            sweep_order_back=sweep_order_back,
        )
        singvals_cut = self.apply_local_kraus_channel(kraus_ops=kraus_ops)
        conv2 = self.timestep_mode_3(
            0.5 * dt, sweep_order=sweep_order, sweep_order_back=sweep_order_back
        )

        conv = conv1 + conv2

        return conv, singvals_cut

    def timestep_mode_4_kraus(
        self, dt, sweep_order=None, sweep_order_back=None, normalize=False
    ):
        """
        Evolve the Tensor network for one timestep of the Lindblad master equation
        (single-tensor update 2nd order) + Local dissipation.

        Parameters
        ----------
        dt : float
            Timestep
        sweep_order : List[int] | None
            Order in which we iterate through the network for the timestep.
            If None, use the default in `self.default_sweep_order()`
        sweep_order_back : List[int] | None
            Order in which we iterate backwards through the network for the timestep.
            If None, use the default in `self.default_sweep_order()[::-1]`

        Returns
        -------
        conv : List[qtealeaves.solvers.krylovexp_solver.KrylovInfo]
            Information about the convergence of each Krylov update.
        """

        kraus_ops = self.eff_op.get_local_kraus_operators(dt)

        conv1 = self.timestep_mode_4(
            0.5 * dt,
            sweep_order=sweep_order,
            sweep_order_back=sweep_order_back,
            normalize=normalize,
        )
        singvals_cut = self.apply_local_kraus_channel(kraus_ops=kraus_ops)
        conv2 = self.timestep_mode_4(
            0.5 * dt,
            sweep_order=sweep_order,
            sweep_order_back=sweep_order_back,
            normalize=normalize,
        )

        conv = conv1 + conv2

        return conv, singvals_cut

    #########################################################################
    ########################## Observables methods ##########################
    #########################################################################
    def check_obs_input(self, ops, idxs=None):
        """
        Check if the observables are in the right
        format

        Parameters
        ----------
        ops : list of np.ndarray or np.ndarray
            Observables to measure
        idxs: list of ints, optional
            If has len>0 we expect a list of operators, otherwise just one.

        Return
        ------
        None
        """
        if np.isscalar(self.local_dim):
            local_dim = [
                self.local_dim,
            ] * self.num_sites
        else:
            local_dim = self.local_dim
        if not np.all(np.array(local_dim) == local_dim[0]):
            raise RuntimeError("Measurement not defined for non-constant local_dim")

        if idxs is None:
            ops = [ops]

        # for op in ops:
        #    if list(op.shape) != [local_dim[0]] * 2:
        #        raise ValueError(
        #            "Input operator should be of shape (local_dim, local_dim)"
        #        )

        if idxs is not None:
            if len(idxs) != len(ops):
                raise ValueError(
                    "The number of indexes must match the number of operators"
                )

    #########################################################################
    ############################## MPI methods ##############################
    #########################################################################
    # pylint: disable=c-extension-no-member
    def _initialize_mpi(self):
        if (MPI is not None) and (MPI.COMM_WORLD.Get_size() > 1):
            self.comm = MPI.COMM_WORLD

    # pylint: enable=c-extension-no-member

    def mpi_send_tensor(self, tensor, to_):
        """
        Send the tensor in position `tidx` to the process
        `to_`.

        Parameters
        ----------
        tensor : xp.ndarray
            Tensor to send
        to_ : int
            Index of the process where to send the tensor

        Returns
        -------
        None
        """
        tensor.mpi_send(to_, self.comm, TN_MPI_TYPES)

    def mpi_receive_tensor(self, from_):
        """
        Receive the tensor from the process `from_`.


        Parameters
        ----------
        from_ : int
            Index of the process that sent the tensor

        Returns
        -------
        xp.ndarray
            Received tensor
        """
        return self._tensor_backend.tensor_cls.mpi_recv(
            from_, self.comm, TN_MPI_TYPES, self._tensor_backend
        )

    def reinstall_isometry_parallel(self, *args, **kwargs):
        """
        Reinstall the isometry in a parallel TN parallely
        """
        # Empty on purpose: depends on TN ansatz and
        # it is used ONLY for MPI-distributed ansatzes

    def reinstall_isometry_serial(self, *args, **kwargs):
        """
        Reinstall the isometry in a parallel TN serially
        """
        # Empty on purpose: depends on TN ansatz and
        # it is used ONLY for MPI-distributed ansatzes

    @staticmethod
    def matrix_to_tensorlist(
        matrix, n_sites, dim, conv_params, tensor_backend=TensorBackend()
    ):
        """
        For a given matrix returns dense MPO form decomposing with SVDs

        Parameters
        ----------
        matrix : ndarray
            Matrix to write in LPTN(MPO) format
        n_sites : int
            Number of sites
        dim : int
            Local Hilbert space dimension
        conv_params : :py:class:`TNConvergenceParameters`
            Input for handling convergence parameters.
            In particular, in the LPTN simulator we
            are interested in:
            - the maximum bond dimension (max_bond_dimension)
            - the cut ratio (cut_ratio) after which the
            singular values in SVD are neglected, all
            singular values such that
            :math:`\\lambda` /:math:`\\lambda_max`
            <= :math:`\\epsilon` are truncated
        tensor_backend : instance of :class:`TensorBackend`
            Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.

        Return
        ------
        List[QteaTensor]
            List of tensor, the MPO decomposition of the matrix
        """

        if not isinstance(matrix, tensor_backend.tensor_cls):
            matrix = tensor_backend.tensor_cls.from_elem_array(matrix)

        bond_dim = 1
        tensorlist = []
        work = matrix
        for ii in range(0, n_sites - 1):
            #                dim  dim**(n_sites-1)
            #  |                 ||
            #  O  --[unfuse]-->  O   --[fuse upper and lower legs]-->
            #  |                 ||
            #
            # ==O==  --[SVD, truncating]-->  ==O-o-O==
            #
            #                 | |
            #  --[unfuse]-->  O-O           ---iterate
            #                 | |
            #             dim   dim**(n_sites-1)
            work = np.reshape(
                work,
                (
                    bond_dim,
                    dim,
                    dim ** (n_sites - 1 - ii),
                    dim,
                    dim ** (n_sites - 1 - ii),
                ),
            )
            tens_left, work, _, _ = work.split_svd(
                [0, 1, 3], [2, 4], contract_singvals="R", conv_params=conv_params
            )
            tensorlist.append(tens_left)
            bond_dim = deepcopy(work.shape[0])
        work = work.reshape((work.shape[0], dim, dim, 1))
        tensorlist.append(work)

        return tensorlist

    def debug_device_memory(self):
        """
        Write informations about the memory usage in each device,
        and how many tensors are stored in each device.
        This should not be used in performance simulations but only in debugging.
        """

        # First we do this for tensors in the Tensor network
        tensors_in_device = {}
        memory_in_device = {}
        for tens in self._iter_tensors():
            if tens.device in tensors_in_device:
                tensors_in_device[tens.device] += 1
                memory_in_device[tens.device] += tens.getsizeof()
            else:
                tensors_in_device[tens.device] = 1
                memory_in_device[tens.device] = tens.getsizeof()
        nt_tot = np.array(list(tensors_in_device.values()), dtype=int).sum()

        for (
            device,
            ntens,
        ) in tensors_in_device.items():
            mem = memory_in_device[device]
            logger.debug(
                "TN tensors in %s are %d/%d for %d bytes",
                device,
                ntens,
                nt_tot,
                mem,
            )

        # Then we do the same for tensors in the effective operators
        if self.eff_op is not None:
            tensors_in_device = {}
            memory_in_device = {}
            for eff_ops_link in self.eff_op.eff_ops.values():
                for tens in eff_ops_link:
                    if tens.device in tensors_in_device:
                        tensors_in_device[tens.device] += 1
                        memory_in_device[tens.device] += tens.getsizeof()
                    else:
                        tensors_in_device[tens.device] = 1
                        memory_in_device[tens.device] = tens.getsizeof()
            nt_tot = np.array(list(tensors_in_device.values()), dtype=int).sum()

            for (
                device,
                ntens,
            ) in tensors_in_device.items():
                mem = memory_in_device[device]
                logger.debug(
                    "Effective operators tensors in %s are %d/%d for %d bytes",
                    device,
                    ntens,
                    nt_tot,
                    mem,
                )

        # Count the memory for effective projectors
        for proj in self.eff_proj:
            tensors_in_device = {}
            memory_in_device = {}
            for tens in proj.values():
                if tens.device in tensors_in_device:
                    tensors_in_device[tens.device] += 1
                    memory_in_device[tens.device] += tens.getsizeof()
                else:
                    tensors_in_device[tens.device] = 1
                    memory_in_device[tens.device] = tens.getsizeof()
            nt_tot = np.array(list(tensors_in_device.values()), dtype=int).sum()

            for (
                device,
                ntens,
            ) in tensors_in_device.items():
                mem = memory_in_device[device]
                logger.debug(
                    "Effective operators tensors in %s are %d/%d for %d bytes",
                    device,
                    ntens,
                    nt_tot,
                    mem,
                )

        logger.debug(
            "Used bytes in device memory: %d/%d",
            self.data_mover.device_memory,
            self.data_mover.mempool.total_bytes(),
        )

    # ------------------------
    # ---- ML Operations -----
    # ------------------------

    def ml_to_id_step(self, pos, pos_p):
        """
        Construct the id_step variables to shift effective operators given two
        positions in the tensor network.

        Arguments
        ---------

        pos : tuple[int] | int
            First position in the :class:`_AbstractTN`.

        pos_p : tuple[int] | int
            Second position in the :class:`_AbstractTN`.

        Returns
        -------

        id_step
            Compatible step with ansatz
        """

        logger_warning(
            "DeprecationWarning: The machine learning methods in qtealeaves classes are deprecated."
            + " For machine learning tasks, please utilize the qchaitea classes instead."
        )

        return [pos, pos_p]

    @abc.abstractmethod
    def ml_get_gradient_single_tensor(self, pos):
        """
        Get the gradient w.r.t. to the tensor at ``pos`` similar to the
        two-tensor version.

        Parameters
        ----------

        pos : int
            Index of the tensor to work with.

        Returns
        -------

        grad : :class:`_AbstractQteaTensor`
            Gradient tensor

        loss : float
            The loss function.
        """

    @abc.abstractmethod
    def ml_get_gradient_two_tensors(self, pos, pos_p=None):
        """
        Get the gradient w.r.t. the tensors at position `pos`, `pos_p`
        of the MPS following the procedure explained in
        https://arxiv.org/pdf/1605.05775.pdf for the
        data_sample given

        Parameters
        ----------

        pos : int
            Index of the tensor to optimize

        pos_p : int | None
            Index of partner tensor. If `None`, partner
            tensor will be queried.

        Returns
        -------
        grad : :class:`_AbstractQteaTensor`
            Gradient tensor

        loss : float
            The loss function.

        """

    # pylint: disable-next=dangerous-default-value
    def ml_optimize_single_tensor(self, pos, learning_rate, tracker={}):
        """
        Optimize a single tensors using a batch of data damples

        Parameters
        ----------
        pos : int
            Position of the tensor to optimize
        learning_rate : float
            Learining rate for the tensor update
        tracker : dict, optional
            Counts how often loss decreases and increases.

        Returns
        -------
        xp.ndarray
            Singular values cut in the optimization
        float
            Value of the loss function
        tracker : dict
            Counts how often loss decreases and increases.
        """

        logger_warning(
            "DeprecationWarning: The machine learning methods in qtealeaves classes are deprecated."
            + " For machine learning tasks, please utilize the qchaitea classes instead."
        )

        if "+" not in tracker:
            tracker["+"] = 0
            tracker["-"] = 0

        self.iso_towards(pos, True, trunc=True)
        tensor = self[self.iso_center]
        orig_tensor = tensor.copy()

        # Fix learning rate on the fly following the argument of the two-tensor update
        num_attempts = 4
        decrease_factor = 8
        accept_update = True

        # Get the gradient
        tgrad, loss = self.ml_get_gradient_single_tensor(pos)

        for jj in range(num_attempts):
            tensor += learning_rate * tgrad
            self[self.iso_center] = tensor

            _, new_loss = self.ml_get_gradient_single_tensor(pos)

            if jj == 0:
                if new_loss <= loss:
                    tracker["-"] += 1
                else:
                    tracker["+"] += 1

            if new_loss < loss:
                break

            if jj + 1 == num_attempts:
                accept_update = False
                break

            tensor = orig_tensor.copy()
            tgrad /= decrease_factor

        if not accept_update:
            self[self.iso_center] = orig_tensor

        singv_cut = []
        return singv_cut, loss, tracker

    def ml_one_tensor_step(self, pos, num_grad_steps=1):
        """
        Do a gradient descent step via backpropagation with one tensor
        and the label link in the environment.

        Parameters
        ----------

        pos : int | tuple(int)
            Position of the tensor to be optimized in the network.

        num_grad_steps : int
            Number of steps as loop in the gradient descent.

        Returns
        -------

        loss : float (as native data type of the backend on the CPU)
            Value of the loss function.
        """

        logger_warning(
            "DeprecationWarning: The machine learning methods in qtealeaves classes are deprecated."
            + " For machine learning tasks, please utilize the qchaitea classes instead."
        )

        self.iso_towards(pos, True, trunc=True)
        pos_links = self.get_pos_links(pos)

        tensor = self[self.iso_center]
        eff_op_0 = self.eff_op[(pos_links[0], pos)].tensor
        eff_op_1 = self.eff_op[(pos_links[1], pos)].tensor
        eff_op_2 = self.eff_op[(pos_links[2], pos)].tensor

        tensor.elem.requires_grad_(True)

        optim, nn = tensor.get_attr("optim", "nn")
        optimizer = optim.AdamW([tensor.elem])  # *args, **kwargs)
        gradient_clipper = nn.utils.clip_grad_value_

        # pylint: disable-next=protected-access
        true_labels = self.eff_op._current_labels
        test_idx = np.arange(true_labels.shape[0], dtype=int)

        # Actually do the iteration
        for _ in range(num_grad_steps):

            # Call the optimization function:
            # pylint: disable-next=protected-access
            loss = self._cost_func_one_tensor(
                tensor,
                eff_op_0,
                eff_op_1,
                eff_op_2,
                true_labels,
                test_idx,
                self.tn_ml_mode,
                self.extension,
            )

            optimizer.zero_grad()
            loss.backward(retain_graph=False)

            # If the gradients are too large, this clips their value.
            gradient_clipper([tensor.elem], 1e10)

            # iterate the optimizer
            optimizer.step()

        # turn of the requires_grad() and detach
        tensor.elem.requires_grad_(False)
        tensor = tensor.from_elem_array(tensor.elem.detach().clone())

        self[self.iso_center] = tensor

        loss = tensor.get_of(loss)
        loss = loss.detach().clone()

        return loss

    @abc.abstractmethod
    def ml_two_tensor_step(self, pos, num_grad_steps=1):
        """
        Do a gradient descent step via backpropagation with two tensors
        and the label link in the environment.

        Parameters
        ----------

        pos : int | tuple(int)
            Position of the tensor to be optimized in the network.

        num_grad_steps : int
            Number of steps as loop in the gradient descent.

        Returns
        -------

        loss : float (as native data type of the backend on the CPU)
            Value of the loss function.
        """

    def ml_full_tn_step(self, num_grad_steps=1):
        """
        Do a gradient descent backpropagation step on the whole TN.

        Parameters
        ----------

        num_grad_steps : int
            Number of steps as loop in the gradient descent.

        Returns
        -------

        loss : float (as native data type of the backend on the CPU)
            Value of the loss function.

        """

        logger_warning(
            "DeprecationWarning: The machine learning methods in qtealeaves classes are deprecated."
            + " For machine learning tasks, please utilize the qchaitea classes instead."
        )

        tensor_list = []
        tensor = None
        for tensor in self._iter_tensors():
            tensor.elem.requires_grad_(True)
            tensor_list.append(tensor)

        if tensor is None:
            raise QTeaLeavesError("Running on empty TN ansatz.")

        optim, nn = tensor.get_attr("optim", "nn")
        optimizer = optim.AdamW([tensor.elem])  # *args, **kwargs)
        gradient_clipper = nn.utils.clip_grad_value_

        # pylint: disable-next=protected-access
        true_labels = self.eff_op._current_labels
        test_idx = np.arange(true_labels.shape[0], dtype=int)

        # Actually do the iteration
        for _ in range(num_grad_steps):

            # Call the optimization function:
            # pylint: disable-next=protected-access
            loss = self._cost_func_full_tn(
                self,
                true_labels,
                test_idx,
                self.tn_ml_mode,
            )

            optimizer.zero_grad()
            loss.backward(retain_graph=False)

            # If the gradients are too large, this clips their value.
            gradient_clipper([tensor.elem], 1e10)

            # iterate the optimizer
            optimizer.step()

        # turn of the requires_grad() and detach
        for tensor in self._iter_tensors():
            # pylint: disable=protected-access
            tensor.elem.requires_grad_(False)
            tensor._elem = tensor.elem.detach().clone()
            # pylint: enable=protected-access

        loss = tensor.get_of(loss)
        loss = loss.detach().clone()

        return loss

    @staticmethod
    def _cost_func_one_tensor(
        tensor,
        eff_op_0,
        eff_op_1,
        eff_op_2,
        true_labels,
        test_idx,
        tn_ml_mode,
        extension,
    ):
        """
        Calculate the forward function for the loss for one-tensor updates.

        Arguments
        ---------

        tensor : :class:`_AbstractQteaBaseTensor`
            The tensor in the ansatz to be optimized right now inside a sweep.

        eff_op_0 : :class:`_AbstractQteaBaseTensor`
            Effective operator, connected to the first link of tensor.

        eff_op_1 : :class:`_AbstractQteaBaseTensor`
            Effective operator, connected to the second link of tensor.

        eff_op_2 : :class:`_AbstractQteaBaseTensor`
            Effective operator, connected to the third link of tensor.

        true_labels : :class:`_AbstractQteaTensor`
            The actual labels of the training data.

        test_idx : np.ndarray of ints
            Indices from 0 to `num_samples - 1` to subtract true label 1
            for loss function.

        tn_ml_mode : str
            Tensor network machine learning mode to be used for this
            ansatz / loss calculation.

        extension : str
            File extension of ansatz to distinguish between MPS, TTO, etc.

        Returns
        -------

        loss : float
            The loss function.
        """
        if true_labels.has_symmetry:
            # Access to elem would fail for symmetric tensors in this function
            raise ValueError("How can labels be a symmetric tensor?")

        has_label_link = tensor.ndim == 4
        (
            treal,
            my_sum,
        ) = tensor.get_attr("real", "sum")

        if not has_label_link:
            estr_labels = "abc,xmayi,ynbzi,zlcxi->mnli"
        elif extension == "mps":
            estr_labels = "abtc,xmayi,ynbzi,zlcxi->ti"
        elif extension == "tto":
            estr_labels = "abct,xmayi,ynbzi,zlcxi->ti"
        else:
            raise QTeaLeavesError(f"Undefined TN-ML case for einsum with {extension=}.")

        labels = tensor.einsum(
            estr_labels,
            eff_op_0,
            eff_op_1,
            eff_op_2,
        )

        if "labelenv" in tn_ml_mode:
            # Covering: labelenv_back, labelenv_back_isofree,
            # and labelenv_back_fulltn
            labels.fuse_links_update(0, 2)

        if "back" in tn_ml_mode:
            # Covering: labellink_back, labelenv_back,
            # labelenv_back_isofree, labelenv_back_fulltn,

            dtype_int = true_labels.dtype_from_char("I")
            axis0_idx = true_labels.copy().convert(dtype=dtype_int).elem

            # prediction = targmax(labels.elem, axis=0)
            # print(
            #     "Acc training in loop",
            #     my_sum(prediction == true_labels.elem) / true_labels.shape[0],
            # )

            labels.elem[axis0_idx, test_idx] -= 1
            diff = my_sum(labels.elem**2)
        else:
            raise ValueError(f"The mode {tn_ml_mode=} is not valid.")

        # Calculate loss and move to CPU / host
        loss = treal(diff)
        loss /= true_labels.shape[0]

        return loss

    @staticmethod
    def _cost_func_two_tensor(
        tensor1,
        tensor2,
        eff_op_0,
        eff_op_1,
        eff_op_2,
        eff_op_3,
        einsum_str,
        true_labels,
        test_idx,
        tn_ml_mode,
    ):
        """
        Calculate the forward function for the loss.

        Arguments
        ---------

        tensor1 : :class:`_AbstractQteaBaseTensor`
            One tensor in the ansatz.

        tensor2 : :class:`_AbstractQteaBaseTensor`
            Second tensor in the ansatz.

        eff_op_0 : :class:`_AbstractQteaBaseTensor`
            Effective operator, usually connected to `tensor1`.

        eff_op_1 : :class:`_AbstractQteaBaseTensor`
            Effective operator, usually connected to `tensor1`.

        eff_op_2 : :class:`_AbstractQteaBaseTensor`
            Effective operator, usually connected to `tensor2`.

        eff_op_3 : :class:`_AbstractQteaBaseTensor`
            Effective operator, usually connected to `tensor2`.

        einsum_str : str
            String for contractin the six tensors via einsum.

        true_labels : :class:`_AbstractQteaTensor`
            The actual labels of the training data.

        test_idx : np.ndarray of ints
            Indices from 0 to `num_samples - 1` to subtract true label 1
            for loss function.

        tn_ml_mode : str
            Tensor network machine learning mode to be used for this
            ansatz / loss calculation.

        Returns
        -------

        loss : float
            The loss function.
        """
        if true_labels.has_symmetry:
            # Access to elem would fail for symmetric tensors in this function
            raise ValueError("How can labels be a symmetric tensor?")

        treal, my_sum = tensor1.get_attr("real", "sum")
        labels = tensor1.einsum(
            einsum_str,
            tensor2,
            eff_op_0,
            eff_op_1,
            eff_op_2,
            eff_op_3,
        )

        if tn_ml_mode in ["labelenv_back", "labelenv_back_isofree"]:
            labels.fuse_links_update(0, 3)

        if tn_ml_mode in ["labellink_back", "labelenv_back", "labelenv_back_isofree"]:

            dtype_int = true_labels.dtype_from_char("I")
            axis0_idx = true_labels.copy().convert(dtype=dtype_int).elem

            # prediction = targmax(labels.elem, axis=0)
            # print(
            #    "CP prediction",
            #    my_sum(labels.elem < 0.0),
            #    my_sum(prediction == true_labels.elem),
            # )

            labels.elem[axis0_idx, test_idx] -= 1
            diff = my_sum(labels.elem**2)

        else:
            raise ValueError(f"The mode {tn_ml_mode=} is not valid.")

        # Calculate loss and move to CPU / host
        loss = treal(diff)
        loss /= true_labels.shape[0]

        return loss

    @staticmethod
    def _cost_func_full_tn(tn_ansatz, true_labels, test_idx, tn_ml_mode):
        """
        Optize all tensors of an ansatz with gradient descent for supervised-learning.

        Parameters
        ----------

        tn_ansatz : :class:`_AbstractTN`
           Tensor network ansatz used as predictor for a supervised ML task.

        true_labels : :class:`_AbstractQteaTensor`
            The actual labels of the training data.

        test_idx : np.ndarray of ints
            Indices from 0 to `num_samples - 1` to subtract true label 1
            for loss function.

        tn_ml_mode : str
            Tensor network machine learning mode to be used for this
            ansatz / loss calculation.

        Returns
        -------

        loss : float
            The loss function.
        """
        ml_data_mpo = tn_ansatz.eff_op
        ml_data_mpo.setup_as_eff_ops(tn_ansatz)
        pos = tn_ansatz.iso_center
        pos_links = tn_ansatz.get_pos_links(pos)

        tensor = tn_ansatz[pos]
        eff_op_0 = tn_ansatz.eff_op[(pos_links[0], pos)].tensor
        eff_op_1 = tn_ansatz.eff_op[(pos_links[1], pos)].tensor
        eff_op_2 = tn_ansatz.eff_op[(pos_links[2], pos)].tensor

        # pylint: disable-next=protected-access
        return tn_ansatz._cost_func_one_tensor(
            tensor,
            eff_op_0,
            eff_op_1,
            eff_op_2,
            true_labels,
            test_idx,
            tn_ml_mode,
            tn_ansatz.extension,
        )

    # pylint: disable-next=dangerous-default-value
    def ml_optimize_two_tensors(
        self,
        pos,
        learning_rate,
        direction=1,
        tracker={},
    ):
        """
        Optimize two tensors using a batch of data damples

        Parameters
        ----------
        pos : int
            Position of the tensor to optimize
        learning_rate : float
            Learining rate for the tensor update
        direction : int, optional
            Direction either left to right (>0) or right to left (< 0).
            Default to 1.
        tracker : dict, optional
            Counts how often loss decreases and increases.

        Returns
        -------
        xp.ndarray
            Singular values cut in the optimization
        float
            Value of the loss function
        tracker : dict
            Counts how often loss decreases and increases.
        """

        logger_warning(
            "DeprecationWarning: The machine learning methods in qtealeaves classes are deprecated."
            + " For machine learning tasks, please utilize the qchaitea classes instead."
        )

        self.sanity_check()

        if "+" not in tracker:
            tracker["+"] = 0
            tracker["-"] = 0

        # Information on partner tensor
        pos_p, link_self, link_p = self.get_pos_partner_link_expansion(pos)
        pos, pos_p, link_self, link_p = self.ml_reorder_pos_pair(
            pos, pos_p, link_self, link_p
        )

        # Canonize to pos
        self.iso_towards(pos, True, trunc=True)

        # Have to re-run as link_self or link_p can require a change with label link
        pos, pos_p, link_self, link_p = self.ml_reorder_pos_pair(
            pos, pos_p, link_self, link_p
        )

        # Get the gradient
        tgrad, loss = self.ml_get_gradient_two_tensors(pos, pos_p=pos_p)

        # Compute the two_tensor of site pos, pos+1 for the update
        two_tensors = self[pos].tensordot(self[pos_p], ([link_self], [link_p]))
        if self[pos_p].ndim == 4:
            # Partner position in MPS and TTO should always be rank-3 now
            raise QTeaLeavesError("Label link should now always be on `pos`.")

        orig_left = self[pos]
        orig_right = self[pos_p]
        orig_two_tensors = two_tensors.copy()

        direction = "R" if direction > 0 else "L"
        if self.extension == "tto":
            # Keep iso center in lower tensor (left-moving)
            direction = "L"

        # Hard-coded parameter four in case learning rate is too high and we go past
        # the minimum. Learning rate will decrease between each iteration by a factor
        # of eight
        num_attempts = 4
        decrease_factor = 8
        accept_update = True

        for jj in range(num_attempts):
            two_tensors += learning_rate * tgrad

            tmp = list(range(two_tensors.ndim))

            perm_l = None
            if two_tensors.ndim == 4:
                # No label link
                split_links_self = tmp[:2]
                split_links_p = tmp[2:]
                perm_r = None
            elif direction == "R":
                split_links_self = tmp[:2]
                split_links_p = tmp[2:]
                if self.extension == "mps":
                    perm_r = [0, 2, 1, 3]
                elif link_p == 0:
                    perm_r = [0, 2, 3, 1]
                elif link_p == 1:
                    perm_r = [2, 0, 3, 1]
                else:
                    raise QTeaLeavesError("Case not covered yet. Open a ticket.")
            else:
                # direction == "L"
                split_links_self = tmp[:3]
                split_links_p = tmp[3:]
                if self.extension == "mps":
                    perm_r = None
                elif link_p == 0:
                    perm_r = None
                elif link_p == 1:
                    perm_r = [1, 0, 2]
                else:
                    raise QTeaLeavesError("Case not covered yet. Open a ticket.")

                if self.extension == "tto":
                    # This is the only case with a permutation on the left tensor
                    perm_l = [0, 1, 3, 2]

            # Split the tensor back and update the MPS
            left, right, singvals, singval_cut = two_tensors.split_svd(
                split_links_self,
                split_links_p,
                contract_singvals=direction,
                conv_params=self._convergence_parameters,
                perm_left=perm_l,
                perm_right=perm_r,
            )

            # We have to permute legs back eventually
            switch_tn = 1 if self.extension == "tto" else 0
            switch_4 = 4 if orig_left.ndim == 4 else 3
            switch = switch_tn * switch_4
            if switch == 3 and (link_self + 1 != self[pos].ndim):
                # Scalar label detection, TTO
                nn = left.ndim
                perm_a = (
                    list(range(link_self)) + [nn - 1] + list(range(link_self, nn - 1))
                )
                left = left.transpose(perm_a)

            if switch == 3 and (link_p != 0):
                # Scalar label detection, TTO
                nn = right.ndim
                perm_b = list(range(1, link_p + 1)) + [0] + list(range(link_p + 1, nn))
                right = right.transpose(perm_b)

            self[pos] = left
            self[pos_p] = right
            _, new_loss = self.ml_get_gradient_two_tensors(pos, pos_p=pos_p)

            if jj == 0:
                if new_loss <= loss:
                    tracker["-"] += 1
                else:
                    tracker["+"] += 1

            if new_loss < loss:
                break

            if jj + 1 == num_attempts:
                accept_update = False
                break

            two_tensors = orig_two_tensors.copy()
            tgrad /= decrease_factor

        if accept_update:
            self.set_singvals_on_link(pos, pos_p, singvals)

            # Have to manually update effective operators as we shift
            # the iso center
            if self.eff_op is None:
                # Well, nothing to do, but simplifies the next elifs
                pass
            elif direction == "R":
                self._update_eff_ops(self.ml_to_id_step(pos, pos_p))
                self.iso_center = pos_p
            elif direction == "L":
                if self.extension == "tto":
                    self.iso_center = pos_p
                # pylint: disable-next=arguments-out-of-order
                self._update_eff_ops(self.ml_to_id_step(pos_p, pos))
                self.iso_center = pos

        else:
            self[pos] = orig_left
            self[pos_p] = orig_right

        self.sanity_check()

        return singval_cut, loss, tracker

    @abc.abstractmethod
    def ml_update_conjugate_gradient_two_tensors(
        self, pos: int, pos_p: int | None = None
    ):
        """
        Get the optimized "two_tensors" at position `pos`, `pos_p` through
        Conjugate gradient descent strategy following a procedure based upon
        https://arxiv.org/pdf/1605.05775.pdf for the
        data_sample given.

        the name of the variables in the following is chosen upon Conj. Grad. Algor. in
        https://en.wikipedia.org/wiki/Conjugate_gradient_method

        Parameters
        ----------

        pos : int
            Index of the tensor to optimize

        pos_p : int | None
            Index of partner tensor. If `None`, partner
            tensor will be queried.

        Returns
        -------
        grad : :class:`_AbstractQteaTensor`
            Gradient tensor

        loss : float
            The loss function.

        """

    # note: adapt to have check on steps.

    # pylint: disable-next=dangerous-default-value
    def ml_optimize_two_tensors_conj(
        self,
        pos,
        direction=1,
        tracker={},
    ):
        """
        Optimize two tensors through Conjugate Gradient Descent Algorithm
        using a batch of data damples.

        Parameters
        ----------
        pos : int
            Position of the tensor to optimize
        learning_rate : float
            Learining rate for the tensor update
        direction : int, optional
            Direction either left to right (>0) or right to left (< 0).
            Default to 1.
        tracker : dict, optional
            Counts how often loss decreases and increases.

        Returns
        -------
        xp.ndarray
            Singular values cut in the optimization
        float
            Value of the loss function
        tracker : dict
            Counts how often loss decreases and increases.
        """
        self.sanity_check()

        if "+" not in tracker:
            tracker["+"] = 0
            tracker["-"] = 0

        # Information on partner tensor
        pos_p, link_self, link_p = self.get_pos_partner_link_expansion(pos)
        pos, pos_p, link_self, link_p = self.ml_reorder_pos_pair(
            pos, pos_p, link_self, link_p
        )

        # Canonize to pos
        self.iso_towards(pos, True, trunc=True)

        # Have to re-run as link_self or link_p can require a change with label link
        pos, pos_p, link_self, link_p = self.ml_reorder_pos_pair(
            pos, pos_p, link_self, link_p
        )

        # Get the update of the contraction tn[pos] and tn[pos_p]
        optimized_two_tensors, loss = self.ml_update_conjugate_gradient_two_tensors(
            pos, pos_p
        )

        # Compute the two_tensor of site pos, pos+1 for the update
        two_tensors = self[pos].tensordot(self[pos_p], ([link_self], [link_p]))
        if self[pos_p].ndim == 4:
            # Partner position in MPS and TTO should always be rank-3 now
            raise QTeaLeavesError("Label link should now always be on `pos`.")

        direction = "R" if direction > 0 else "L"
        if self.extension == "tto":
            # Keep iso center in lower tensor (left-moving)
            direction = "L"

        tmp = list(range(two_tensors.ndim))

        perm_l = None
        if two_tensors.ndim == 4:
            # No label link
            split_links_self = tmp[:2]
            split_links_p = tmp[2:]
            perm_r = None
        elif direction == "R":
            split_links_self = tmp[:2]
            split_links_p = tmp[2:]
            if self.extension == "mps":
                perm_r = [0, 2, 1, 3]
            elif link_p == 0:
                perm_r = [0, 2, 3, 1]
            elif link_p == 1:
                perm_r = [2, 0, 3, 1]
            else:
                raise QTeaLeavesError("Case not covered yet. Open a ticket.")
        else:
            # direction == "L"
            split_links_self = tmp[:3]
            split_links_p = tmp[3:]
            if self.extension == "mps":
                perm_r = None
            elif link_p == 0:
                perm_r = None
            elif link_p == 1:
                perm_r = [1, 0, 2]
            else:
                raise QTeaLeavesError("Case not covered yet. Open a ticket.")

            if self.extension == "tto":
                # This is the only case with a permutation on the left tensor
                perm_l = [0, 1, 3, 2]

        # Split the tensor back and update the MPS (isnt this general for all ansatz?)
        left, right, singvals, singval_cut = optimized_two_tensors.split_svd(
            split_links_self,
            split_links_p,
            contract_singvals=direction,
            conv_params=self._convergence_parameters,
            perm_left=perm_l,
            perm_right=perm_r,
        )

        # We have to permute legs back eventually
        switch_tn = 1 if self.extension == "tto" else 0
        switch_4 = 4 if self[pos].ndim == 4 else 3
        switch = switch_tn * switch_4
        if switch == 3 and (link_self + 1 != self[pos].ndim):
            # Scalar label detection, TTO
            nn = left.ndim
            perm_a = list(range(link_self)) + [nn - 1] + list(range(link_self, nn - 1))
            left = left.transpose(perm_a)

        if switch == 3 and (link_p != 0):
            # Scalar label detection, TTO
            nn = right.ndim
            perm_b = list(range(1, link_p + 1)) + [0] + list(range(link_p + 1, nn))
            right = right.transpose(perm_b)

        self[pos] = left
        self[pos_p] = right

        self.set_singvals_on_link(pos, pos_p, singvals)

        # Have to manually update effective operators as we shift
        # the iso center
        if self.eff_op is None:
            # Well, nothing to do, but simplifies the next elifs
            pass
        elif direction == "R":
            self._update_eff_ops(self.ml_to_id_step(pos, pos_p))
            self.iso_center = pos_p
        elif direction == "L":
            if self.extension == "tto":
                self.iso_center = pos_p
            # pylint: disable-next=arguments-out-of-order
            self._update_eff_ops(self.ml_to_id_step(pos_p, pos))
            self.iso_center = pos

        self.sanity_check()

        return singval_cut, loss, tracker

    # pylint: enable=unused-argument

    def ml_optimize(
        self,
        ml_data_mpo,
        learning_rate,
        tn_ml_mode,
    ):
        """
        Optimize the TN using the algorithm of Stoudenmire

        Parameters
        ----------
        ml_data_mpo : py:class:`MLDataMPO`
            Feature dataset
        learning_rate : float or callable
            Learning rate for the tensor update. If callable, it can depend on the sweep.
        tn_ml_mode :  str
            Defines the mode how to execute the machine learning. Must be
            compatible with the initial guess and the MPO, which will be
            checked. Available values are ``linkfree``, ``linkfree_isofree``, ``linkfree_conj``,
            ``labellink``, ``labellink_conj``, ``labellink_back``, ``labelenv_back``,
            and ``labelenv_back_isofree``.

        Previous arguments
        ------------------

        * num_sweeps: from convergence parameters `max_iter`
          Number of optimization sweeps (epochs)
        * no_impovement_criterion: from convergence parameters `n_points_conv_check`
          Exit criterion if consecutive iterations do not lead
          to an improvement, we exit.
        * decomposition_free_iso_towards : from `tn_ml_mode`
          Allow to skip QR/SVD decompositions when shifting isometry center.
          TN-ML does not require unitary gauged tensors if we have
          no label link and single-tensor updates.
        * use_backwards : from `tn_ml_mode`
          Use gradient descent with back propagation.

        Returns
        -------
        xp.ndarray
            Singular values cut in the optimization
        dict:
            Simulation log as dictionary with entries
            ``loss_pre_sweep`` (list), ``loss_post_sweep`` (list),
            ``sweep_time`` (list), ``total_time`` (float).

        Details
        -------

        The machine learning modes are

        * ``linkfree`` : using overlap, mostly binary problems
        * ``linkfree_isofree`` : using overlap, single-site without decomposition,
          mostly binary problems.
        * ``linkfree_conj`` : using overlap, mostly binary problems,
          loss function minimized via conjugate gradient descent.
        * ``labellink`` : standard TN-ML shifting label-link with the iso-center,
          gradient is calculated as tensor contraction.
        * ``labellink_back`` : standard TN-ML shiftling label-link with the iso-center,
          but using loss function, gradient descent, and back propagation.
        * ``labellink_conj`` : standard TN-ML shifting label-link with the iso-center,
          loss function minimized via conjugate gradient descent.

        Future methods are (but unittest fail here)

        * ``labelenv_back`` : label-link in environment, loss function minimized
          via gradient descent and back propagation.
        * ``labelenv_back_isofree`` : label-link in environment, loss function minimized
          via gradient descent and back propagation, no iso-shift.
        * ``labelenv_back_fulltn``: optimize all tensors at the same time.
        """

        logger_warning(
            "DeprecationWarning: The machine learning methods in qtealeaves classes are deprecated."
            + " For machine learning tasks, please utilize the qchaitea classes instead."
        )

        self.tn_ml_mode = tn_ml_mode
        if self.tn_ml_mode is None:
            raise QTeaLeavesError("tn_ml_mode has to be set before calling optimize.")

        num_sweeps = self.convergence_parameters.max_iter
        no_improvement_criterion = self.convergence_parameters.n_points_conv_check
        decomposition_free_iso_towards = "isofree" in tn_ml_mode
        use_backwards = "back" in tn_ml_mode
        use_conjugate = "conj" in tn_ml_mode

        if use_backwards and use_conjugate:
            raise NotImplementedError(
                "Conjugate gradient + back propagation is Not Implemented."
            )

        # Hard-coded for now
        num_grad_steps = 1

        backend_lib = self[self.iso_center].linear_algebra_library
        if use_backwards and (backend_lib not in ["torch"]):
            raise QTeaBackendError(f"Backpropagation not supported for {backend_lib=}.")

        if self.extension not in ["mps", "tto"]:
            raise NotImplementedError(
                f"Ansatz `{self.extension}` has no support for machine learning."
            )

        if self[self.iso_center].dtype_to_char() not in ["D", "S", "H"]:
            # conj() calls are most likely not completely in the right places, so
            # we have to raise the error here.
            val = self[self.iso_center].dtype_to_char()
            raise ValueError(f"Can only use real data types for TN-ML, but got {val}.")

        num_site_rule = self.convergence_parameters.sim_params["statics_method"]
        if num_site_rule not in [1, 2]:
            raise ValueError(f"Got a statics methods {num_site_rule} for TN-ML.")
        # avoid possibly-used-before-assignment
        loss_ii, singv_cut = None, None

        if (num_site_rule != 1) and decomposition_free_iso_towards:
            if "back" not in self.tn_ml_mode:
                raise ValueError(
                    f"Two tensor update and {tn_ml_mode=} does not allow "
                    "skipping QR/SVD for TN-ML"
                )

        has_label_link = self[self.iso_center].ndim == 4
        if (not has_label_link) and (ml_data_mpo.num_labels > 2):
            logger.warning("No label link, but more than 2 labels (not recommended).")

        self._decomposition_free_iso_towards = decomposition_free_iso_towards

        has_label_link = self[self.iso_center].ndim == 4
        if (not has_label_link) and (ml_data_mpo.num_labels > 2):
            logger.warning("No label link, but more than 2 labels (not recommended).")

        self._decomposition_free_iso_towards = decomposition_free_iso_towards

        simulation_log = {
            "loss_pre_sweep": [],
            "loss_post_sweep": [],
            "loss_full_history": [],
            "sweep_time": [],
            "total_time": None,
        }
        time_0 = tictoc()

        sweep = self.ml_default_sweep_order(num_site_rule)
        singvals_cut = np.zeros(len(sweep) * num_sweeps)

        # If learning rate is not callable do a constant function
        if not callable(learning_rate):
            learning_rate_f = lambda x: learning_rate
        else:
            learning_rate_f = learning_rate

        max_chi = self.convergence_parameters.max_bond_dimension
        self.convergence_parameters.sim_params["max_bond_dimension"] = (
            self.convergence_parameters.ini_bond_dimension
        )

        no_improvement_counter = 0
        for nswp in range(num_sweeps):
            tic = tictoc()
            logger.debug("%s Sweep %s started %s", "=" * 20, nswp, "=" * 20)

            # Select the training batch
            loss_i0 = None
            if tn_ml_mode == "labelenv_back_fulltn":
                if nswp == 0:
                    ml_data_mpo.setup_as_eff_ops(self)

                loss_ii = self.ml_full_tn_step()
                sweep = []
                if nswp == 0:
                    loss_i0 = 2 * loss_ii
            elif (nswp == 0) or (ml_data_mpo.batch_size != ml_data_mpo.num_samples):
                ml_data_mpo.setup_as_eff_ops(self)

            for ii, pos in enumerate(sweep):
                iso_dir = 1

                singv_cut = []

                if num_site_rule == 1:
                    if use_backwards:
                        loss_ii = self.ml_one_tensor_step(
                            pos, num_grad_steps=num_grad_steps
                        )
                    elif use_conjugate:
                        raise NotImplementedError(
                            "Conjugate gradient for 1 site optimization Not Implemented yet."
                        )
                    else:
                        for _ in range(num_grad_steps):
                            singv_cut, loss_ii, _ = self.ml_optimize_single_tensor(
                                pos, learning_rate_f(nswp)
                            )
                elif num_site_rule == 2:
                    if use_backwards:
                        loss_ii = self.ml_two_tensor_step(
                            pos, num_grad_steps=num_grad_steps
                        )
                    elif use_conjugate:
                        for _ in range(num_grad_steps):
                            singv_cut, loss_ii, _ = self.ml_optimize_two_tensors_conj(
                                pos,
                                direction=iso_dir,
                            )
                    else:
                        for _ in range(num_grad_steps):
                            singv_cut, loss_ii, _ = self.ml_optimize_two_tensors(
                                pos,
                                learning_rate_f(nswp),
                                direction=iso_dir,
                            )
                else:
                    # So far cannot be encountered as long as num_site_rule either
                    # 1 or 2. But better be safe than sorry.
                    raise QTeaLeavesError("TN-ML case not covered.")

                simulation_log["loss_full_history"].append(float(loss_ii))
                if ii == 0:
                    loss_i0 = loss_ii

                # Postprocess the singvals as prescribed in the convergence parameters
                singvals_cut[nswp * len(sweep) + ii] = self._postprocess_singvals_cut(
                    singv_cut
                )

            if loss_i0 > loss_ii:
                no_improvement_counter = 0
            else:
                no_improvement_counter += 1

            toc = tictoc()
            sweep_time = toc - tic
            simulation_log["loss_pre_sweep"].append(float(loss_i0))
            simulation_log["loss_post_sweep"].append(float(loss_ii))
            simulation_log["sweep_time"].append(sweep_time)

            logger.debug(
                "Sweep in %f seconds with loss: %f -> %f", sweep_time, loss_i0, loss_ii
            )

            self.convergence_parameters.sim_params["max_bond_dimension"] = min(
                self.convergence_parameters.sim_params["max_bond_dimension"] + 1,
                max_chi,
            )

            if no_improvement_counter == no_improvement_criterion:
                logger.debug(
                    "Exit loop, no imrovement since %d sweeps.",
                    no_improvement_criterion,
                )
                break

        toc = tictoc()
        simulation_log["total_time"] = toc - time_0

        return singvals_cut, simulation_log

    def ml_predict(self, data_samples, n_jobs=1, do_round=True):
        """
        Predict the labels of the data samples passed

        Parameters
        ----------
        data_samples : List[py:class:`MPS`] | :class:`MLDataMPO`
            Feature dataset
        true_labels : List[int]
            Labels of the dataset
        n_jobs : int, optional
            Number of parallel jobs for the optimization, by default 1
        do_round : bool, optional
            If true, labels will be rounded to integers, otherwise
            returned as float.
            Default to True

        Returns
        -------
        List | np.ndarray of rank 1
            Predicted labels
        """

        logger_warning(
            "DeprecationWarning: The machine learning methods in qtealeaves classes are deprecated."
            + " For machine learning tasks, please utilize the qchaitea classes instead."
        )

        if (self[self.iso_center].ndim == 4) and isinstance(data_samples, list):
            # ML-TN has label link and we have a list of MPSs
            return self._ml_predict_label_link(
                data_samples, n_jobs=n_jobs, do_round=do_round
            )

        if ("labellink" in self.tn_ml_mode) or ("labelenv" in self.tn_ml_mode):
            # ML-TN has label link and we got a MLDataMPO
            return self._ml_predict_label_link_via_mpo(data_samples, do_round=do_round)

        return self._ml_predict_scalar(data_samples, n_jobs=n_jobs, do_round=do_round)

    def _ml_predict_scalar(self, data_samples, n_jobs=1, do_round=True):
        """
        Predict ML-TN for approach without label link (using norm, e.g., binary problem).
        For arguments, see :func:`ml_predict`.
        """
        if not isinstance(data_samples, list):
            # Most likely a MLDataMPO
            return self._ml_predict_label_link_via_mpo(data_samples, do_round=do_round)

        if n_jobs == 1:
            # Avoid joblib level for serial jobs
            # pylint: disable-next=no-member
            labels = [self.contract(sample) for sample in data_samples]
        else:
            labels = Parallel(n_jobs=n_jobs)(
                # pylint: disable-next=no-member
                delayed(self.contract)(sample)
                for sample in data_samples
            )

        if do_round:
            labels = np.real(np.round(labels)).astype(int)

        return labels

    # pylint: disable-next=unused-argument
    def _ml_predict_label_link_via_mpo(self, ml_data_mpo, do_round=True):
        """
        Predict the labels of the data samples passed

        Parameters
        ----------
        data_samples : :class:`MLDataMPO`
            Feature dataset

        For other arguments, see :func:`ml_predict`.
        """
        if "labellink" in self.tn_ml_mode:
            self.iso_towards(self.default_iso_pos, trunc=True)
        else:
            # QR is okay, we cannot go up in bond dimension
            self.iso_towards(self.default_iso_pos, trunc=False)

        tensor = self[self.iso_center]

        orig_eff_op = self.eff_op
        self.eff_op = None
        # pylint: disable-next=protected-access
        _batch_size = ml_data_mpo.batch_size
        # pylint: disable-next=protected-access
        ml_data_mpo._batch_size = ml_data_mpo.num_samples
        ml_data_mpo.setup_as_eff_ops(self)

        if self.extension == "tto":
            einsum_str = "abct,xmayi,ynbzi,zlcxi->ti"
            eff_0 = self.eff_op[((1, 0), (0, 0))].tensor
            eff_1 = self.eff_op[((1, 1), (0, 0))].tensor
            eff_2 = self.eff_op[(None, (0, 0))].tensor
        else:
            # MPS keeps label link at kraus link position of LPTN
            einsum_str = "abtd,xmayi,ynbzi,zldxi->mnlti"
            nn = self.num_sites
            eff_0 = self.eff_op[(nn - 2, nn - 1)].tensor
            eff_1 = self.eff_op[(-nn - 1, nn - 1)].tensor
            eff_2 = self.eff_op[(None, nn - 1)].tensor

        if "linkfree" in self.tn_ml_mode:
            einsum_str = einsum_str.replace("t", "").replace("mnl", "")
        elif "labelenv" in self.tn_ml_mode:
            einsum_str = einsum_str.replace("t", "")
        elif "labellink" in self.tn_ml_mode:
            einsum_str = einsum_str.replace("mnl", "")

        labels = tensor.einsum(
            einsum_str,
            eff_0,
            eff_1,
            eff_2,
        )

        if "labelenv" in self.tn_ml_mode:
            labels.fuse_links_update(0, 2)

        labels = np.array(tensor.get_of(labels.elem))
        if ("linkfree" in self.tn_ml_mode) and do_round:
            labels = np.round(labels)
        else:
            if do_round:
                labels = np.argmax(np.abs(labels), axis=0)
            else:
                labels = np.transpose(labels, (1, 0))

        # pylint: disable-next=protected-access
        ml_data_mpo._batch_size = _batch_size
        self.eff_op = orig_eff_op

        return labels

    # pylint: disable-next=unused-argument
    def _ml_predict_label_link(self, data_samples, n_jobs=1, do_round=True):
        """
        Predict ML-TN for approach with label link (vec and argmax).

        Arguments
        ---------

        data_samples : List[py:class:`MPS`]
            Feature dataset

        For other arguments, see :func:`ml_predict`.
        """
        self.iso_towards(0, trunc=True)

        boundaries = (self.num_sites - 1, 0)
        labels = []
        for sample in data_samples:
            # pylint: disable-next=no-member
            transfer_mat = self.contract(sample, boundaries=boundaries)

            sample_conj = sample[0].conj().convert(device=self.computational_device)
            overlap = transfer_mat.einsum(
                "abc,ijka,xjb->k",
                self[0],
                sample_conj,
            )

            overlap.convert(device="cpu")
            labels.append(np.array(overlap.elem))

        if do_round:
            labels = [np.argmax(elem) for elem in labels]

        return labels

    #########################################################################
    ############################## Measurement methods ######################
    #########################################################################

    def meas_exp_value(self, mpo):
        """
        Measures the expectation value of a given MPO for a
        TN state.

        Arguments
        ---------
        mpo : :py:class:`ITPO` or iterator
            The MPO whose expectation value we want to measure.
            The measurement has two modes. The first mode is passing the ITPO MPO,
            in which case the entire mpo is measured at once.
            The second mode is to pass an iterator which yields ITPO terms of the MPO
            batch by batch, in which case the output will be the sum of expectation values
            performed on each batch. The second mode is useful when the MPO to measure
            contains a large number of ITPO terms, therefore measuring it in batches
            escapes the memory issues.

        Return
        ------
        exp_value : float
            Expectation value of the MPO.
        """
        # save this info for later
        iso_center = deepcopy(self.iso_center)
        state_eff_op = self.eff_op

        # Check if mpo is an iterator, if not then measure entire mpo at once
        if not inspect.isgeneratorfunction(mpo):
            # check tensor backend
            mpo_tensor_backend = mpo.site_terms.construct_tensor_backend()
            if mpo_tensor_backend.device != self.tensor_backend.device:
                raise ValueError(
                    "MPO and state devices don't match: "
                    f"{mpo_tensor_backend.device} and {self.tensor_backend.device}."
                )
            if mpo_tensor_backend.tensor_cls != self.tensor_backend.tensor_cls:
                raise ValueError(
                    "MPO and state tensor classes don't match: "
                    f"{mpo_tensor_backend.tensor_cls} and {self.tensor_backend.tensor_cls}."
                )

            if hasattr(self, "de_layer"):
                # include the disentanglers into the itpo
                mpo = self.de_layer.contract_de_layer(
                    mpo, self.tensor_backend, params=None
                )

            # Carry out the measurement of this sub-MPO
            self.eff_op = None
            # compute eff ops
            mpo.setup_as_eff_ops(self)
            # measure
            exp_value = self.compute_energy()

        # otherwise measure in batches
        else:
            # measuring iteratively batch by batch
            exp_value = 0.0
            for sub_mpo in mpo():
                if np.abs(exp_value) < 1e-8:
                    # check tensor backend on the first entry
                    mpo_tensor_backend = sub_mpo.site_terms.construct_tensor_backend()
                    if mpo_tensor_backend.device != self.tensor_backend.device:
                        raise ValueError(
                            "MPO and state devices don't match: "
                            f"{mpo_tensor_backend.device} and {self.tensor_backend.device}."
                        )
                    if mpo_tensor_backend.tensor_cls != self.tensor_backend.tensor_cls:
                        raise ValueError(
                            "MPO and state tensor classes don't match: "
                            f"{mpo_tensor_backend.tensor_cls} and {self.tensor_backend.tensor_cls}."
                        )

                if hasattr(self, "de_layer"):
                    # include the disentanglers into the itpo
                    sub_mpo = self.de_layer.contract_de_layer(
                        sub_mpo, self.tensor_backend, params=None
                    )

                # Carry out the measurement of this sub-MPO
                self.eff_op = None
                # compute eff ops
                sub_mpo.setup_as_eff_ops(self)
                # measure
                exp_value += self.compute_energy()

        # restore effective operators and iso center to get state into
        # previous form
        self.eff_op = state_eff_op
        _ = self.compute_energy()
        if iso_center is not None:
            self.iso_towards(iso_center)

        return exp_value


def postprocess_statedict(state_dict, local_dim=2, qiskit_convention=False):
    """
    Remove commas from the states defined as keys of statedict
    and, if `qiskit_convention=True` invert the order of the
    digits following the qiskit convention

    Parameters
    ----------
    state_dict : dict
        State dictionary, which keys should be of the format
        'd,d,d,d,d,...,d' with d from 0 to local dimension
    local_dim : int or array-like of ints, optional
        Local dimension of the sites. Default to 2
    qiskit_convention : bool, optional
        If True, invert the digit ordering to follow qiskit
        convention

    Return
    ------
    dict
        The postprocessed state dictionary
    """
    # Check on parameter
    if np.isscalar(local_dim):
        local_dim = [local_dim]

    postprocecessed_state_dict = {}
    for key, val in state_dict.items():
        # If the maximum of the local_dim is <10
        # remove the comma, since the definition
        # is not confusing
        if np.max(local_dim) < 10:
            key = key.replace(",", "")
        # Invert the values if qiskit_convention == True
        if qiskit_convention:
            postprocecessed_state_dict[key[::-1]] = val
        else:
            postprocecessed_state_dict[key] = val

    return postprocecessed_state_dict


def _resample_for_unbiased_prob(num_samples, bound_probabilities):
    """
    Sample the `num_samples` samples in U(0,1) to use in the function
    :py:func:`meas_unbiased_probabilities`. If `bound_probabilities`
    is not None, then the function checks that the number of samples
    outside the ranges already computed in bound_probabilities are
    not in total num_samples. The array returned is sorted ascendingly

    Parameters
    ----------
    num_samples : int
        Number of samples to be drawn for :py:func:`meas_unbiased_probabilities`
    bound_probabilities : dict or None
        See :py:func:`meas_unbiased_probabilities`.

    Return
    ------
    np.ndarray
        Sorted samples in (0,1)
    dict
        Empty dictionary if bound_probabilities is None, otherwise the
        bound_probabilities input parameter.
    """
    if (bound_probabilities is None) or (len(bound_probabilities) == 0):
        # Contains the boundary probability of measuring the state, i.e. if a uniform
        # random number has value left_bound< value< right_bound then you measure the
        # state. The dict structure is {'state' : [left_bound, right_bound]}
        bound_probabilities = {}
        samples = _random_uniform(0, 1, num_samples)
    else:
        # Prepare the functions to be used later on based on precision
        mpf_wrapper, almost_equal = _mp_precision_check(mp.mp.dps)
        # Go on and sample until you reach an effective number of num_samples,
        # withouth taking into account those already sampled in the given
        # bound_probabilities
        bounds_array = np.zeros((len(bound_probabilities), 2))
        for idx, bound in enumerate(bound_probabilities.values()):
            bounds_array[idx, :] = bound
        bounds_array = bounds_array[bounds_array[:, 0].argsort()]

        if "left" in bound_probabilities and len(bound_probabilities) > 1:
            bounds_array[0, 1] = min(bounds_array[0, 1], bounds_array[1, 0])

        if "right" in bound_probabilities and len(bound_probabilities) > 1:
            bounds_array[-1, 0] = max(bounds_array[-1, 0], bounds_array[-2, 1])

        # Immediatly return if almost all the space has been measured
        if almost_equal(
            (np.sum(bounds_array[:, 1] - bounds_array[:, 0]), mpf_wrapper(1.0))
        ):
            return np.random.uniform(0, 1, 1), bound_probabilities

        if mp.mp.dps > 15:
            logger_warning(
                "Resampling is performed at standard precision 16 digits"
                + "at least in np.random.choice."
            )

        # Sample unsampled areas. First, prepare array for sampling
        array_for_sampling = []
        last_bound = 0
        last_idx = 0
        while not almost_equal((last_bound, mpf_wrapper(1.0))):
            # Skip if interval already measured
            if last_idx < len(bounds_array) and almost_equal(
                (last_bound, bounds_array[last_idx, 0])
            ):
                last_bound = bounds_array[last_idx, 1]
                last_idx += 1
            # Save interval
            else:
                if 0 < last_idx < len(bounds_array):
                    array_for_sampling.append(
                        [bounds_array[last_idx - 1, 1], bounds_array[last_idx, 0]]
                    )
                    last_bound = bounds_array[last_idx, 0]
                elif last_idx == len(bounds_array):
                    array_for_sampling.append([bounds_array[last_idx - 1, 1], 1])
                    last_bound = 1
                else:  # Initial case
                    array_for_sampling.append([0, bounds_array[last_idx, 0]])
                    last_bound = bounds_array[last_idx, 0]

        nparray_for_sampling = np.array(array_for_sampling)
        # Sample from which intervals you will sample
        sample_prob = nparray_for_sampling[:, 1] - nparray_for_sampling[:, 0]
        sample_prob[sample_prob < 0] = 0.0
        sample_prob /= np.sum(sample_prob)
        intervals_idxs = np.random.choice(
            np.arange(len(array_for_sampling)),
            size=num_samples,
            replace=True,
            p=sample_prob,
        )
        intervals_idxs, num_samples_per_interval = np.unique(
            intervals_idxs, return_counts=True
        )

        # Finally perform uniform sampling
        samples = np.zeros(1)
        for int_idx, num_samples_int in zip(intervals_idxs, num_samples_per_interval):
            interval = nparray_for_sampling[int_idx, :]
            samples = np.hstack(
                (samples, np.random.uniform(*interval, size=num_samples_int))
            )
        samples = samples[1:]

    # Sort the array
    samples = np.sort(samples)

    return samples, bound_probabilities


def _projector(idxs, shape, xp=np):
    """
    Generate a projector of a given shape on the
    subspace identified by the indexes idxs

    Parameters
    ----------
    idxs : int or array-like of ints
        Indexes where the diagonal of the projector is 1,
        i.e. identifying the projector subspace
    shape : int or array-like of ints
        Dimensions of the projector. If an int, it is
        assumed a square matrix
    xp : module handle
        Module handle for the creation of the projector.
        Possible are np (cpu) or cp (cpu). Default to np.
    """
    if np.isscalar(idxs):
        idxs = [idxs]
    if np.isscalar(shape):
        shape = (shape, shape)

    idxs = np.array(idxs, dtype=int)
    projector = xp.zeros(shape)
    projector[idxs, idxs] = 1
    return projector


def _projector_for_rho_i(idxs, rho_i):
    """
    Generate a projector of a given shape on the
    subspace identified by the indexes idxs

    Parameters
    ----------
    idxs : int or array-like of ints
        Indexes where the diagonal of the projector is 1,
        i.e. identifying the projector subspace
    shape : int or array-like of ints
        Dimensions of the projector. If an int, it is
        assumed a square matrix
    xp : module handle
        Module handle for the creation of the projector.
        Possible are np (cpu) or cp (cpu). Default to np.
    """
    if np.isscalar(idxs):
        idxs = [idxs]

    projector = rho_i.zeros_like()
    for ii in idxs:
        projector.set_diagonal_entry(ii, 1.0)

    return projector


def _mp_precision_check(precision):
    """
    Based on the precision selected, gives
    a wrapper around the initialization of
    variables and almost equal check.
    In particolar, if `precision>15`,
    use mpmath library

    Parameters
    ----------
    precision : int
        Precision of the computations

    Return
    ------
    callable
        Initializer for variables
    callable
        Almost equal check for variables
    """
    if precision > 15:
        # pylint: disable-next=unnecessary-lambda
        mpf_wrapper = lambda x: mp.mpf(x)
        almost_equal = lambda x: mp.almosteq(
            x[0], x[1], abs_eps=mp.mpf(10 ** (-precision))
        )
    else:
        mpf_wrapper = lambda x: x
        almost_equal = lambda x: np.isclose(x[0], x[1], atol=10 ** (-precision), rtol=0)

    return mpf_wrapper, almost_equal


def _check_samples_in_bound_probs(samples, bound_probabilities):
    """
    Check if the samples are falling in the probability intervals
    defined by the dictionary bound_probabilities, received as
    output by the OPES/unbiased sampling

    Parameters
    ----------
    samples : np.ndarray
        List of samples
    bound_probabilities : dict
        Dictionary of bound probabilities, where the key is the
        measure and the values the intervals of probability

    Returns
    -------
    np.ndarray(float)
        The probability sampled by samples, repeated the correct
        amount of times
    np.ndarray(float)
        The subset of the original samples not falling into the
        already measured intervals
    """
    if len(bound_probabilities) == 0:
        return [], samples

    bound_probs = np.array(list(bound_probabilities.values()))
    left_bound = bound_probs[:, 0]
    right_bound = bound_probs[:, 1]
    probs = bound_probs[:, 1] - bound_probs[:, 0]
    new_samples = []

    def get_probs(sample, new_samples):
        condition = np.logical_and(sample < right_bound, sample > left_bound)

        if not any(condition):
            new_samples.append(sample)
            return -1
        res = probs[condition]
        return res[0]

    # get_probs = np.vectorize(get_probs)
    probablity_sampled = np.array([get_probs(ss, new_samples) for ss in samples])

    probablity_sampled = probablity_sampled[probablity_sampled > 0].astype(float)

    return probablity_sampled, np.array(new_samples)


def _random_uniform(lower, upper, num_samples):
    """
    Return a numpy array of num_samples samples distributed uniformly
    over the interval [lower, upper). If the mpmath precision is greater
    than 15 uses mpmath, otherwise uses numpy.random.uniform.

    Parameters
    ----------
    lower : float
        Lower boundary of the output interval. All values generated will
        be greater than or equal to lower.
    upper : float
        Upper boundary of the output interval. All values generated will
        be less than upper.
    num_samples : int
        Number of sampled values.

    Returns
    -------
    np.ndarray | np.array(mpf)
        Drawn samples.

    """

    if mp.mp.dps <= 15:
        return np.random.uniform(lower, upper, num_samples)

    samples = [
        mp.mpf("0." + "".join([str(np.random.randint(10)) for _ in range(mp.mp.dps)]))
        for _ in range(num_samples)
    ]
    samples = np.array(samples)
    samples = lower + samples * (upper - lower)
    return samples
