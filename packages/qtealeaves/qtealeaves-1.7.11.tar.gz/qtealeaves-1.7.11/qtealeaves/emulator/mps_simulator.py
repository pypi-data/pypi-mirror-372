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
The module contains a light-weight MPS emulator.
"""

# pylint: disable=too-many-lines, too-many-statements, too-many-arguments, too-many-locals, too-many-branches

import logging
from copy import deepcopy
from warnings import warn

import matplotlib.cm as cmx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from matplotlib.collections import LineCollection

from qtealeaves.abstracttns import postprocess_statedict
from qtealeaves.abstracttns.abstract_tn import _AbstractTN, _projector_for_rho_i
from qtealeaves.convergence_parameters import TNConvergenceParameters
from qtealeaves.mpos import MPSProjector
from qtealeaves.tensors import TensorBackend
from qtealeaves.tensors.abstracttensor import _AbstractQteaTensor
from qtealeaves.tooling import QTeaLeavesError

__all__ = ["MPS"]

# Sanity checks are diabled by default, but can be enabled for debugging
RUN_SANITY_CHECKS = False

logger = logging.getLogger(__name__)


# pylint: disable-next=dangerous-default-value
def logger_warning(*args, storage=[]):
    """Workaround to display warnings only once in logger."""
    if args in storage:
        return

    storage.append(args)
    logger.warning(*args)


# pylint: disable-next=too-many-public-methods, too-many-instance-attributes
class MPS(_AbstractTN):
    """Matrix product states class

    Parameters
    ----------
    num_sites: int
        Number of sites
    convergence_parameters: :py:class:`TNConvergenceParameters`
        Class for handling convergence parameters. In particular, in the MPS simulator we are
        interested in:
        - the *maximum bond dimension* :math:`\\chi`;
        - the *cut ratio* :math:`\\epsilon` after which the singular
            values are neglected, i.e. if :math:`\\lamda_1` is the
            bigger singular values then after an SVD we neglect all the
            singular values such that :math:`\\frac{\\lambda_i}{\\lambda_1}\\leq\\epsilon`
    local_dim: int or list of ints, optional
        Local dimension of the degrees of freedom. Default to 2.
        If a list is given, then it must have length num_sites.
    initialize: str, optional
        The method for the initialization. Default to "vacuum"
        Available:
        - "vacuum", for the |000...0> state (no symmetric tensors yet)
        - "random", for a random state at given bond dimension
    requires_singvals : boolean, optional
        Allows to enforce SVD to have singular values on each link available
        which might be useful for measurements, e.g., bond entropy (the
        alternative is traversing the whole TN again to get the bond entropy
        on each link with an SVD).
    tensor_backend : `None` or instance of :class:`TensorBackend`
        Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.
    sectors : dict | None, optional
        Can restrict symmetry sector and/or bond dimension in initialization.
        If empty, no restriction. The global symmetry sector is parsed from the
        the key `global`; intermediate sectors can be restricted via integer
        keys specifying the number of sites to the left of the corresponding link.
        Example: Restrict irreps after the second site at python-index=1, the
        key equals to 2 for two sites being on the left of the link.
        Default to `None` resulting in empty dictionary.
    """

    extension = "mps"

    def __init__(
        self,
        num_sites,
        convergence_parameters,
        local_dim=2,
        initialize="vacuum",
        requires_singvals=False,
        tensor_backend=None,
        sectors=None,
        **kwargs,
    ):
        super().__init__(
            num_sites,
            convergence_parameters,
            local_dim=local_dim,
            requires_singvals=requires_singvals,
            tensor_backend=tensor_backend,
        )
        sectors = {} if sectors is None else sectors

        # Set orthogonality tracker for left/right-orthogonal form
        self._first_non_orthogonal_left = 0
        self._first_non_orthogonal_right = num_sites - 1

        # We can set numpy double, will be converted
        self._singvals = [None for _ in range(num_sites + 1)]

        # Initialize the tensors to the |000....0> state
        self._tensors = []
        self._initialize_mps(initialize, sectors=sectors)

        # Attribute used for computing probabilities. See
        # meas_probabilities for further details
        self._temp_for_prob = {}

        # Variable to save the maximum bond dimension reached at any moment
        self.max_bond_dim_reached = 1

        # Each tensor has 3 links, but all tensors share links. So effectively
        # we have 2 links per tensor, plus one at the beginning and one at the end
        self.num_links = 2 + 2 * num_sites
        self.sectors = sectors
        # Contains the index of the neighboring effective operator in
        # a 1-d vector of operators. Each vector op_neighbors(:, ii)
        # contains the index of a link for the ii-th tensor in this layer.
        # 0-o-2-o-4-o-6-o-8  --->   i -o- i+2
        #   |1  |3  |5  |7             | i+1
        self.op_neighbors = np.zeros((3, num_sites), dtype=int)
        self.op_neighbors[0, :] = np.arange(0, 2 * num_sites, 2)
        self.op_neighbors[1, :] = np.arange(1, 2 * num_sites, 2)
        self.op_neighbors[2, :] = np.arange(2, 2 * num_sites + 1, 2)

        # MPS initialization now takes care of device and
        # dtype in `_initialize_mps`

    # --------------------------------------------------------------------------
    #                               Properties
    # --------------------------------------------------------------------------

    @property
    def default_iso_pos(self):
        """
        Returns default isometry center position, e.g., for initialization
        of effective operators.
        """
        return self.num_sites - 1

    @property
    def tensors(self):
        """List of MPS tensors"""
        return self._tensors

    @property
    def singvals(self):
        """List of singular values in the bonds"""
        return self._singvals

    @property
    def first_non_orthogonal_left(self):
        """First non orthogonal tensor starting from the left"""
        return self._first_non_orthogonal_left

    @property
    def first_non_orthogonal_right(self):
        """First non orthogonal tensor starting from the right"""
        return self._first_non_orthogonal_right

    @property
    def iso_center(self):
        """
        Output the gauge center if it is well defined, otherwise None
        """
        if self.first_non_orthogonal_left == self.first_non_orthogonal_right:
            center = self.first_non_orthogonal_right
        else:
            center = None
        return center

    @iso_center.setter
    def iso_center(self, value):
        if value is None:
            self._first_non_orthogonal_left = 0
            self._first_non_orthogonal_right = self.num_sites - 1
            return
        self._first_non_orthogonal_left = value
        self._first_non_orthogonal_right = value

    @property
    def physical_idxs(self):
        """Physical indices property"""
        return self.op_neighbors[1, :].reshape(-1)

    @property
    def current_max_bond_dim(self):
        """Maximum bond dimension of the mps"""
        max_bond_dims = [(tt.shape[0], tt.shape[2]) for tt in self]
        return np.max(max_bond_dims)

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
        Provide number of sites in the MPS
        """
        return self.num_sites

    def __getitem__(self, key):
        """Overwrite the call for lists, you can access tensors in the MPS using

        .. code-block::
            MPS[0]
            >>> [[ [1], [0] ] ]

        Parameters
        ----------
        key : int
            index of the MPS tensor you are interested in

        Returns
        -------
        np.ndarray
            Tensor at position key in the MPS.tensor array
        """
        return self.tensors[key]

    def __setitem__(self, key, value):
        """Modify a tensor in the MPS by using a syntax corresponding to lists.
        It is the only way to modify a tensor

        .. code-block::
            tens = np.ones( (1, 2, 1) )
            MPS[1] = tens


        Parameters
        ----------
        key : int
            index of the array
        value : np.array
            value of the new tensor. Must have the same shape as the old one
        """
        if not isinstance(value, _AbstractQteaTensor):
            raise TypeError("New tensor must be an _AbstractQteaTensor.")
        self._tensors[key] = value

        return None

    def __iter__(self):
        """Iterator protocol"""
        return iter(self.tensors)

    def __add__(self, other):
        """
        Add two MPS states in a "non-physical" way. Notice that this function
        is highly inefficient if the number of sites is very high.
        For example, adding |00> to |11> will result in |00>+|11> not normalized.
        Remember to take care of the normalization yourself.

        Parameters
        ----------
        other : MPS
            MPS to concatenate

        Returns
        -------
        MPS
            Summation of the first MPS with the second
        """
        return self._add(other)

    def __iadd__(self, other):
        """Concatenate the MPS other with self inplace"""
        # pylint: disable-next=invalid-name
        add_mps = self.__add__(other)

        return add_mps

    def __mul__(self, factor):
        """Multiply the mps by a scalar and return the new MPS"""
        if not np.isscalar(factor):
            raise TypeError("Multiplication is only defined with a scalar number")

        other = deepcopy(self)
        if other.iso_center is None:
            other.right_canonize(
                max(0, self.first_non_orthogonal_left), keep_singvals=True
            )
        other._tensors[self.iso_center] *= factor

        return other

    def __imul__(self, factor):
        """Multiply the mps by a scalar in place"""
        if not np.isscalar(factor):
            raise TypeError("Multiplication is only defined with a scalar number")
        mult_mps = self.__mul__(factor)

        return mult_mps

    def __truediv__(self, factor):
        """Divide the mps by a scalar and return the new MPS"""
        if not np.isscalar(factor):
            raise TypeError("Multiplication is only defined with a scalar number")

        other = deepcopy(self)
        if other.iso_center is None:
            other.right_canonize(
                max(0, self.first_non_orthogonal_left), keep_singvals=True
            )
        other._tensors[self.iso_center] /= factor
        return other

    def __itruediv__(self, factor):
        """Divide the mps by a scalar in place"""
        if not np.isscalar(factor):
            raise TypeError("Multiplication is only defined with a scalar number")
        div_mps = self.__truediv__(factor)

        return div_mps

    def __matmul__(self, other):
        """
        Implement the contraction between two MPSs overloading the operator
        @. It is equivalent to doing <self|other>. It already takes into account
        the conjugation of the left-term
        """
        if not isinstance(other, MPS):
            raise TypeError("Only two MPS classes can be contracted")

        return other.contract(self)

    def dot(self, other):
        """
        Calculate the dot-product or overlap between two MPSs, i.e.,
        <self | other>.

        Parameters
        ----------

        other : :class:`MPS`
            Measure the overlap with this other MPS.

        Returns
        -------a

        Scalar representing the overlap.
        """
        return other.contract(self)

    # --------------------------------------------------------------------------
    #                       classmethod, classmethod like
    # --------------------------------------------------------------------------

    @classmethod
    def from_statevector(
        cls,
        statevector,
        local_dim=2,
        conv_params=None,
        tensor_backend=None,
    ):
        """
        Initialize the MPS tensors by decomposing a statevector into MPS form.
        All the degrees of freedom must have the same local dimension

        Parameters
        ----------
        statevector : ndarray of shape( local_dim^num_sites, )
            Statevector describing the interested state for initializing the MPS
        local_dim : int, optional
            Local dimension of the degrees of freedom. Default to 2.
        conv_params : :py:class:`TNConvergenceParameters`, optional
            Convergence parameters for the new MPS. If None, the maximum bond
            bond dimension possible is assumed, and a cut_ratio=1e-9.
            Default to None.
        tensor_backend : `None` or instance of :class:`TensorBackend`
            Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.

        Returns
        -------
        obj : :py:class:`MPS`
            MPS simulator class

        Examples
        --------
        >>> -U1 - U2 - U3 - ... - UN-
        >>>  |    |    |          |
        # For d=2, N=7 and chi=5, the tensor network is as follows:
        >>> -U1 -2- U2 -4- U3 -5- U4 -5- U5 -4- U6 -2- U7-
        >>>  |      |      |      |      |      |      |
        # where -x- denotes the bounds' dimension (all the "bottom-facing" indices
        # are of dimension d=2). Thus, the shapes
        # of the returned tensors are as follows:
        >>>      U1         U2         U3         U4         U5         U6         U7
        >>> [(1, 2, 2), (2, 2, 4), (4, 2, 5), (5, 2, 5), (5, 2, 4), (4, 2, 2), (2, 2, 1)]
        """
        if not isinstance(statevector, np.ndarray):
            raise TypeError("`from_statevector` requires numpy array.")

        # Check if statevector contains all zeros
        if np.all(statevector == 0):
            raise ValueError("State vector contains all zeros.")

        statevector = statevector.reshape(-1)
        num_sites = int(np.log(len(statevector)) / np.log(local_dim))

        max_bond_dim = local_dim ** (num_sites // 2)
        if conv_params is None:
            conv_params = TNConvergenceParameters(max_bond_dimension=int(max_bond_dim))
        obj = cls(num_sites, conv_params, local_dim, tensor_backend=tensor_backend)

        state_tensor = statevector.reshape([1] + [local_dim] * num_sites + [1])
        tensor_cls = obj._tensor_backend.tensor_cls
        state_tensor = tensor_cls.from_elem_array(
            state_tensor,
            dtype=obj._tensor_backend.dtype,
            device=obj._tensor_backend.computational_device,
        )
        for ii in range(num_sites - 1):
            legs = list(range(len(state_tensor.shape)))
            tens_left, tens_right, singvals, _ = state_tensor.split_svd(
                legs[:2], legs[2:], contract_singvals="R", conv_params=conv_params
            )

            obj._tensors[ii] = tens_left
            obj._singvals[ii + 1] = singvals
            state_tensor = tens_right
        obj._tensors[-1] = tens_right

        # After this procedure the state is in left canonical form and
        # overwrite any previous information of the isometry center
        obj._first_non_orthogonal_left = obj.num_sites - 1
        obj._first_non_orthogonal_right = obj.num_sites - 1

        obj.convert(obj._tensor_backend.dtype, obj._tensor_backend.memory_device)

        return obj

    @classmethod
    def from_mps(cls, mps, conv_params=None, **kwargs):
        """Converts MPS to MPS.

        Parameters
        ----------
        mps: :py:class:`MPS`
            object to convert to MPS.
        conv_params: :py:class:`TNConvergenceParameters`, optional
            Input for handling convergence parameters
            Default is None.
        kwargs : additional keyword arguments
            They are accepted, but not passed to calls in this function.

        Return
        ------
        new_mps: :py:class:`MPS`
            Decomposition of mps, here a copy.
        """
        cls.assert_extension(mps, "mps")
        new_mps = mps.copy()
        new_mps.convergence_parameters = conv_params
        return new_mps

    @classmethod
    def from_lptn(cls, lptn, conv_params=None, **kwargs):
        """Converts LPTN to MPS.

        Parameters
        ----------
        lptn: :py:class:`LPTN`
            object to convert to MPS.
        conv_params: :py:class:`TNConvergenceParameters`, optional
            Input for handling convergence parameters.
            If None, the algorithm will try to
            extract conv_params from lptn.convergence_parameters.
            Default is None.
        kwargs : additional keyword arguments
            They are accepted, but not passed to calls in this function.

        Return
        ------

        mps: :py:class:`MPS`
            Decomposition of lptn.
        """
        cls.assert_extension(lptn, "lptn")
        if conv_params is None:
            conv_params = lptn.convergence_parameters
        psi = MPS.from_tensor_list(
            lptn.copy().to_tensor_list_mps(),
            conv_params=conv_params,
            tensor_backend=lptn.tensor_backend,
        )
        return psi

    @classmethod
    def from_ttn(cls, ttn, conv_params=None, **kwargs):
        """Converts TTN to MPS.

        Parameters
        ----------
        ttn: :py:class:`TTN`
            object to convert to MPS.
        conv_params: :py:class:`TNConvergenceParameters`, optional
            Input for handling convergence parameters.
            If None, the algorithm will try to
            extract conv_params from ttn.convergence_parameters.
            Default is None.
        kwargs : additional keyword arguments
            They are accepted, but not passed to calls in this function.

        Return
        ------

        mps: :py:class:`MPS`
             Decomposition of ttn.
        """
        cls.assert_extension(ttn, "ttn")
        if conv_params is None:
            conv_params = ttn.convergence_parameters
        psi = MPS.from_tensor_list(
            ttn.copy().to_mps_tensor_list(conv_params)[0],
            conv_params=conv_params,
            tensor_backend=ttn.tensor_backend,
        )
        return psi

    @classmethod
    def from_tto(cls, tto, conv_params=None, **kwargs):
        """Converts TTO to MPS.

        Parameters
        ----------
        tto: :py:class:`TTO`
            Object to convert to MPS.
        conv_params: :py:class:`TNConvergenceParameters`, optional
            Input for handling convergence parameters
            Default is None.
        kwargs : additional keyword arguments
            They are accepted, but not passed to calls in this function.

        Return
        ------

        mps: :py:class:`MPS`
             Decomposition of tto.
        """
        cls.assert_extension(tto, "tto")
        return cls.from_ttn(tto.copy().to_ttn(), conv_params)

    @classmethod
    def from_density_matrix(
        cls, rho, n_sites, dim, conv_params, tensor_backend=None, prob=False
    ):
        """Converts density matrix to MPS (not implemented yet)."""
        raise NotImplementedError("Feature not yet implemented.")

    def _initialize_mps(self, initialize, sectors=None):
        """
        Initialize the MPS with a given structure. Available are:
        - "vacuum", initializes the MPS in |00...0>
        - "random", initializes the MPS in a random state at fixed bond dimension

        The MPS will have an isometry center for both choices. If one overwrites
        the tensor list, one needs to overwrite as well the isometry center.

        Parameters
        ----------
        initialize : str
            Type of initialization.

        sectors : dict | None, optional
            Can restrict symmetry sector and/or bond dimension in initialization.
            If empty, no restriction.
            Default `None` resulting in empty dictionary.

        Returns
        -------
        None
        """
        sectors = {} if sectors is None else sectors

        kwargs = self._tensor_backend.tensor_cls_kwargs()
        tensor_cls = self._tensor_backend.tensor_cls

        if initialize.lower() == "vacuum":
            if len(sectors) > 0:
                raise ValueError("Sectors not considered for vacuum state.")

            if tensor_cls.has_symmetry:
                # The following calls to tensor_cls have integers as link information
                # and only work for tensors without symmetry.
                raise ValueError(
                    "Initialize MPS if-case does not work with symmetries yet."
                )

            for ii in range(self.num_sites):
                state0 = self.tensor_backend(
                    [1, self._local_dim[ii], 1],
                    ctrl="ground",
                    device=self.tensor_backend.memory_device,
                )
                self._tensors.append(state0)
            self._singvals = [
                tensor_cls([1], ctrl="O", **kwargs).elem
                for _ in range(self.num_sites + 1)
            ]

            self.iso_center = 0
            self.move_pos(0, device=self.tensor_backend.computational_device)
        elif initialize.lower() == "random":
            # Works only for qubits right now
            chi_ini = self._convergence_parameters.ini_bond_dimension

            # Link directions are equal for all tensors in the MPS
            link_dirs = [False, False, True]

            # For first iteration, we need to have a fake-list of links where
            # the third entry is correct, i.e., a dummy link
            links = [
                self._tensor_backend.tensor_cls.dummy_link(self.local_links[0])
            ] * 3

            # initialize all tensors apart from last one
            for ii in range(self.num_sites):
                links = [links[-1], self.local_links[ii], None]
                # if last tensor then set to dummy link
                if ii == self.num_sites - 1:
                    chi_ini = chi_ini if self[0].has_symmetry else 1

                key = ii + 1 if ii + 1 < self.num_sites else "global"
                sector = sectors.get(key, None)
                links = tensor_cls.set_missing_link(
                    links, chi_ini, are_links_outgoing=link_dirs, restrict_irreps=sector
                )

                tensor = self.tensor_backend(
                    links,
                    ctrl="R",
                    are_links_outgoing=link_dirs,
                    device=self.tensor_backend.memory_device,
                )
                self._tensors.append(tensor)

            # isometrize towards the last site
            self.site_canonize(self.num_sites - 1, normalize=True)
            # isometrize towards the first site to truncate back bond dimension
            self.site_canonize(0, normalize=True)
            self.normalize()
        else:
            raise QTeaLeavesError(
                f"Initialziation method `{initialize}` not valid for MPS."
            )

    @classmethod
    def ml_initial_guess(
        cls,
        convergence_parameters,
        tensor_backend,
        initialize,
        ml_data_mpo,
        dataset,
        has_trivial_label_link=True,
        has_env_label_link=False,
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
            `ml_data_mpo`. Only accessed in case of ``superposition-data``.

        has_trivial_link : bool, optional
            With a trivial link (`True`), the ML-MPS learns solely based on the overlap
            of the sample with the ansatz rounded to the closest integer. Instead,
            the typical ML approach with argmax over a vector is used with
            `has_trivial_link=False`.
            Default to True

        has_env_label_link : bool, optional
            Move label link into the environment, which means here having a non-trivial
            link towards the environment in the ansatz.
            Default to False.

        Returns
        -------

        ansatz : :class:`_AbstractTN`
            Standard initialization of TN ansatz or Weighted superposition of the
            data set, wehere the weight is the label-value plus an offset of 0.1.
        """

        logger_warning(
            "DeprecationWarning: The machine learning methods in qtealeaves classes are deprecated."
            + " For machine learning tasks, please utilize the qchaitea classes instead."
        )

        num_sites = ml_data_mpo.num_sites
        local_dim = ml_data_mpo.site_terms[0].shape[2]

        if has_trivial_label_link and has_env_label_link:
            raise ValueError(
                "Trivial label link and env label link cannot be both true."
            )

        stack_first = not has_trivial_label_link

        if initialize != "superposition-data":
            if has_trivial_label_link:
                eff_num_sites = num_sites
                local_dims = local_dim
            else:
                eff_num_sites = num_sites + 1
                local_dims = [local_dim] * num_sites + [ml_data_mpo.num_labels]

            psi = MPS(
                eff_num_sites,
                convergence_parameters,
                local_dim=local_dims,
                initialize=initialize,
                tensor_backend=tensor_backend,
            )

            if num_sites != eff_num_sites:
                # we have to adopt
                if psi.iso_center >= num_sites:
                    psi.iso_towards(num_sites - 1)
                psi = psi.get_substate(0, num_sites)

            if (not has_trivial_label_link) and (not has_env_label_link):
                # we have to adapt even more, label link same position as Kraus link in LPTN
                pos = num_sites - 1
                psi.iso_towards(pos)
                psi[pos].attach_dummy_link(3)

            return psi

        # pylint: disable=protected-access
        unique_labels = np.unique(ml_data_mpo._labels)
        tn_states = []
        ini_convergence_params = deepcopy(convergence_parameters)
        ini_convergence_params.sim_params["max_bond_dimension"] = (
            convergence_parameters.ini_bond_dimension
        )
        for label in unique_labels:
            mask = ml_data_mpo._labels == label

            selected = []
            for ii in range(ml_data_mpo.num_samples):
                if mask[ii]:
                    selected.append(dataset[ii])

            selected[0] = selected[0].copy()
            selected[0].convergence_parameters = ini_convergence_params

            for elem in selected[1:]:
                selected[0] += elem
                selected[0].convergence_parameters = ini_convergence_params
                selected[0].iso_towards(0, trunc=True)
                selected[0].iso_towards(num_sites - 1, trunc=True)
                selected[0].normalize()

            selected[0].scale(0.1 + label)
            tn_states.append(selected[0])

        initial_guess = tn_states[0]
        for elem in tn_states[1:]:
            initial_guess = initial_guess._add(elem, stack_first=stack_first)
            initial_guess.convergence_parameters = ini_convergence_params
            initial_guess.iso_towards(num_sites - 1, trunc=False)
            initial_guess.iso_towards(0, trunc=True)

        if stack_first and (not has_env_label_link):
            # Install order left-local-label-right
            initial_guess.iso_towards(0)
            initial_guess[0].attach_dummy_link(0)
            initial_guess[0].transpose_update([0, 2, 1, 3])

        # pylint: enable=protected-access

        return initial_guess

    @classmethod
    def mpi_bcast(cls, state, comm, tensor_backend, root=0):
        """
        Broadcast a whole tensor network.

        Arguments
        ---------

        state : :class:`MPS` (for MPI-rank root, otherwise None is acceptable)
            State to be broadcasted via MPI.

        comm : MPI communicator
            Send state to this group of MPI processes.

        tensor_backend : :class:`TensorBackend`
            Needed to identity data types and tensor classes on receiving
            MPI threads (plus checks on sending MPI thread).

        root : int, optional
            MPI-rank of sending thread with the state.
            Default to 0.
        """
        raise NotImplementedError("MPS cannot be broadcasted yet.")

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
        """Try sampling a target number of unique states from TN ansatz."""
        ansatz = MPS

        return _AbstractTN.mpi_sample_n_unique_states(
            state,
            num_unique,
            comm,
            tensor_backend,
            cache_size=cache_size,
            cache_clearing_strategy=cache_clearing_strategy,
            filter_func=filter_func,
            mpi_final_op=mpi_final_op,
            root=root,
            ansatz=ansatz,
            **kwargs,
        )

    def to_dense(self, true_copy=False):
        """
        Return MPS without symmetric tensors.

        Parameters
        ----------

        true_copy : bool, optional
            The function can be forced to return an actual copy with
            `true_copy=True`, while otherwise `self` can be returned
            if the MPS is already without symmetries.
            Default to `False`

        Returns
        -------

        dense_mps : :class:`MPS`
            MPS representation without symmetric tensors.
        """
        if self.has_symmetry:
            # Have to convert
            tensor_list = [elem.to_dense() for elem in self]

            tensor_backend = deepcopy(self._tensor_backend)
            tensor_backend.tensor_cls = self._tensor_backend.base_tensor_cls

            obj = self.from_tensor_list(
                tensor_list,
                conv_params=self.convergence_parameters,
                tensor_backend=tensor_backend,
            )

            for ii, s_vals in enumerate(self.singvals):
                if s_vals is None:
                    continue

                # Tensor list is shorter, still choose tensor belonging to singvals.
                # pylint: disable-next=protected-access
                jj = min(ii, len(self) - 1)
                # pylint: disable-next=protected-access
                obj._singvals[ii] = self[jj].to_dense_singvals(
                    s_vals, true_copy=true_copy
                )

            obj.iso_center = self.iso_center

            return obj

        # Cases without symmetry

        if true_copy:
            return self.copy()

        return self

    # --------------------------------------------------------------------------
    #                            Checks and asserts
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    #                     Abstract methods to be implemented
    # --------------------------------------------------------------------------

    def _convert_singvals(self, dtype, device):
        """Convert the singular values of the tensor network to dtype/device."""
        if len(self.tensors) == 0:
            return

        # Take any example tensor
        if self.iso_center is not None:
            tensor = self[self.iso_center]
        else:
            tensor = self[0]

        singvals_list = []
        for elem in self._singvals:
            if elem is None:
                singvals_list.append(None)
            else:
                singvals_ii = tensor.convert_singvals(elem, dtype, device)
                singvals_list.append(singvals_ii)

        self._singvals = singvals_list

    def get_bipartition_link(self, pos_src, pos_dst):
        """
        Returns two sets of sites forming the bipartition of the system for
        a loopless tensor network. The link is specified via two positions
        in the tensor network.

        **Arguments**

        pos_src : tuple of two ints
            Specifies the first tensor and source of the link.

        pos_dst : tuple of two ints
            Specifies the second tensor and destination of the link.

        **Returns**

        sites_src : list of ints
            Hilbert space indices when looking from the link towards
            source tensor and following the links therein.

        sites_dst : list of ints
            Hilbert space indices when looking from the link towards
            destination tensor and following the links therein.
        """
        if pos_src < pos_dst:
            return list(range(pos_src + 1)), list(range(pos_src + 1, self.num_sites))

        # pos_src > pos_dst
        return list(range(pos_dst + 1, self.num_sites)), list(range(pos_dst + 1))

    def get_pos_links(self, pos):
        """
        List of tensor position where links are leading to.

        Parameters
        ----------
        pos : int
            Index of the tensor in the MPS

        Returns
        -------
        Tuple[int]
            Index of the tensor connected through links to pos.
            None if they are open links.
        """
        return [
            pos - 1 if pos > 0 else None,
            -pos - 2,
            pos + 1 if pos < self.num_sites - 1 else None,
        ]

    def get_rho_i(self, idx):
        """
        Get the reduced density matrix of the site at index idx

        Parameters
        ----------
        idx : int
            Index of the site

        Returns
        -------
        :class:`_AbstractQteaTensor`
            Reduced density matrix of the site
        """
        if idx in self._cache_rho:
            return self._cache_rho[idx]

        if self.iso_center is None:
            self.iso_towards(idx, keep_singvals=True)

        s_idx = 1 if self.iso_center > idx else 0
        if self.singvals[idx + s_idx] is None:
            self.iso_towards(idx, keep_singvals=True)
            tensor = self[idx]
        else:
            self.move_pos(idx, device=self._tensor_backend.computational_device)
            tensor = self[idx]
            if self.iso_center > idx:
                tensor = tensor.scale_link(self.singvals[idx + s_idx], 2)
            elif self.iso_center < idx:
                tensor = tensor.scale_link(self.singvals[idx + s_idx], 0)

        rho = tensor.tensordot(tensor.conj(), [[0, 2], [0, 2]])
        if self.iso_center != idx:
            self.move_pos(idx, device=self._tensor_backend.memory_device, stream=True)

        trace = rho.trace(return_real_part=True, do_get=False)
        if abs(1 - trace) > 10 * rho.dtype_eps:
            logger_warning("Renormalizing reduced density matrix.")
            rho /= trace

        return rho

    def get_tensor_of_site(self, idx):
        """
        Generic function to retrieve the tensor for a specific site. Compatible
        across different tensor network geometries. This function does not
        shift the gauge center before returning the tensor.

        Parameters
        ----------
        idx : int
            Return tensor containing the link of the local
            Hilbert space of the idx-th site.
        """
        return self[idx]

    # pylint: disable-next=arguments-differ
    def iso_towards(
        self,
        new_iso,
        keep_singvals=False,
        trunc=False,
        conv_params=None,
        move_to_memory_device=True,
        normalize=False,
    ):
        """
        Apply the gauge transformation to shift the isometry
        center to a specific site `new_iso`.
        The method might be different for
        other TN structure, but for the MPS it is the same.

        Parameters
        ----------
        new_iso : int
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
        normalize : bool, optional
            Flag if intermediate steps should normalize.
            Default to `False`

        Details
        -------
        The tensors used in the computation will always be moved on the computational device.
        For example, the isometry movement keeps the isometry center end the effective operators
        around the center (if present) always on the computational device. If move_to_memory_device
        is False, then all the tensors (effective operators) on the path from the old iso to the new
        iso will be kept in the computational device. This is very useful when you iterate some
        protocol between two tensors, or in general when two tensors are involved.

        """
        self.left_canonize(
            new_iso,
            trunc=trunc,
            keep_singvals=keep_singvals,
            conv_params=conv_params,
            move_to_memory_device=move_to_memory_device,
            normalize=normalize,
        )
        self.right_canonize(
            new_iso,
            trunc=trunc,
            keep_singvals=keep_singvals,
            conv_params=conv_params,
            move_to_memory_device=move_to_memory_device,
            normalize=normalize,
        )

    def isometrize_all(self):
        """
        Isometrize towards the default isometry position with no previous
        isometry center, e.g., works as well on random states.

        Returns
        -------

        None
        """
        # MPS is easy, iso_towards considers first/last orthogonal site
        # iso_towards can be used always
        self.iso_towards(self.default_iso_pos)
        return

    def _iter_tensors(self):
        """Iterate over all tensors forming the tensor network (for convert etc)."""
        yield from self._tensors

    def norm(self):
        """
        Returns the norm of the MPS as sqrt(<self|self>)

        Return
        ------
        norm: float
            norm of the MPS
        """
        idx = self.first_non_orthogonal_right

        if self.first_non_orthogonal_left != self.first_non_orthogonal_right:
            self.left_canonize(self.first_non_orthogonal_right, keep_singvals=True)

        return self[idx].norm_sqrt()

    def sanity_check(self):
        """
        A set of sanity checks helping for debugging which can be activated via
        the global variable `RUN_SANITY_CHECK` in this file.

        Raises
        ------

        QTeaLeavesError for any failing check.

        Details
        -------

        Runs checks on

        * Bond dimension between neighboring tensors.
        * Non-trivial local dimension
        """
        if not RUN_SANITY_CHECKS:
            return

        # Check links between neighbors
        for ii in range(1, self.num_sites):
            if self[ii - 1].shape[-1] != self[ii].shape[0]:
                logger.error(
                    "Error information: sites %d and %d, chi %d and %d",
                    ii - 1,
                    ii,
                    self[ii - 1].shape[-1],
                    self[ii].shape[0],
                )
                raise QTeaLeavesError("Mismatch links")

        # Check local dimension non-trivial
        for ii, tensor in enumerate(self):
            if tensor.shape[1] == 1:
                logger.error("Error information: %d, %s", ii, str(tensor.shape))
                raise QTeaLeavesError("trivial local dimension.")

    def scale(self, factor):
        """
        Scale the MPS state by a scalar constant using the gauge center.

        Parameters
        ----------

        factor : scalar
             Factor is multiplied to the MPS at the gauge center.
        """
        self._tensors[self.iso_center] *= factor

    def scale_inverse(self, factor):
        """
        Scale the MPS state by a scalar constant using the gauge center.

        Parameters
        ----------

        factor : scalar
             Factor is multiplied to the MPS at the gauge center.
        """
        self._tensors[self.iso_center] /= factor

    def set_singvals_on_link(self, pos_a, pos_b, s_vals):
        """Update or set singvals on link via two positions."""
        if pos_a < pos_b:
            self._singvals[pos_b] = s_vals
        else:
            self._singvals[pos_a] = s_vals

    # pylint: disable-next=arguments-differ
    def site_canonize(self, idx, keep_singvals=False, normalize=False):
        """
        Apply the gauge transformation to shift the isometry
        center to a specific site `idx`.

        Parameters
        ----------
        idx: int
            index of the tensor up to which the canonization
            occurs from the left and right side.
        keep_singvals : bool, optional
            If True, keep the singular values even if shifting the iso with a
            QR decomposition. Default to False.
        normalize : bool, optional
            Flag if intermediate steps should normalize.
            Default to `False`
        """
        self.iso_towards(idx, keep_singvals=keep_singvals, normalize=normalize)

    def mps_multiply_mps(self, other):
        """
        Elementwise multiplication of the MPS with another MPS,
        resulting multiplying the coefficients of the statevector representation.
        If `self` represents the state `a|000>+b|111>` and `other` represent `c|000>+d|111>`
        then `self.mps_multiply_mps(other)=ac|000>+bd|111>`.
        It is very computationally demanding and the new bond dimension
        is the product of the two original bond dimensions.

        Parameters
        ----------
        other : MPS
            MPS to multiply

        Returns
        -------
        MPS
            Summation of the first MPS with the second
        """

        if not isinstance(other, MPS):
            raise TypeError("Only two MPS classes can be summed")
        if self.num_sites != other.num_sites:
            raise ValueError("Number of sites must be the same to concatenate MPS")
        if np.any(self.local_dim != other.local_dim):
            raise ValueError("Local dimension must be the same to concatenate MPS")

        # pylint: disable=protected-access
        max_bond_dim = max(
            self.convergence_parameters.max_bond_dimension,
            other.convergence_parameters.max_bond_dimension,
        )
        cut_ratio = min(
            self._convergence_parameters.cut_ratio,
            other._convergence_parameters.cut_ratio,
        )
        convergence_params = deepcopy(self.convergence_parameters)
        convergence_params._max_bond_dimension = max_bond_dim
        convergence_params._cut_ration = cut_ratio
        # pylint: enable=protected-access

        tensor_list = []
        for tens_a, tens_b in zip(self, other):
            tens_c = tens_a.kron(tens_b, idxs=(0, 2))
            tensor_list.append(tens_c)

        return MPS.from_tensor_list(
            tensor_list, convergence_params, self._tensor_backend
        )

    def apply_local_kraus_channel(self, kraus_ops):
        """
        Apply local Kraus channels to tensor network. Does not work for MPS!
        -------
        Parameters
        -------
        kraus_ops : dict of :py:class:`QTeaTensor`
            Dictionary, keys are site indices and elements the corresponding 3-leg kraus tensors

        Returns
        -------
        singvals_cut: float
            Sum of singular values discarded due to truncation.
        """
        raise NotImplementedError(
            "Application of quantum channels only works for density operator ansätze!"
        )

    def get_substate(self, first_site, last_site, truncate=False):
        """
        Returns the smaller MPS built of tensors from `first_site` to `last_site`.

        Parameters
        ----------

        first_site : int
            First site defining a range of tensors which will compose the new MPS.
            Python indexing assumed, i.e. counting starts from 0.
        last_site : int
            Last site of a range of tensors which will compose the new MPS.
            Python indexing assumed, i.e. counting starts from 0.
        truncate : Bool
            If False, the MPS tensors are returned as is - possibly with non-dummy links
            on edge tensors, i.e. a mixed state in MPS form.
            If True, the edges of MPS will be truncated to dummy links.
            Default to False.

        Return
        ------
        submps : :py:class:`MPS`
        """
        if self[0].has_symmetry:
            raise NotImplementedError("Function not implemented for symmetric MPS.")

        if (first_site > self.num_sites) or (last_site > self.num_sites):
            raise ValueError(
                "Input site range cannot be larger than original MPS size."
            )

        # make sure that isometry center is within the new submps
        if first_site != self.iso_center:
            logger_warning("Moving the isometry center to leftmost site of new subMPS.")
            self.iso_towards(first_site)

        submps_tensors = self[first_site:last_site]
        submps = MPS.from_tensor_list(
            submps_tensors, self.convergence_parameters, self._tensor_backend
        )

        if truncate:
            # left side
            if submps[0].shape[0] != 1:
                dummy_conv_params = TNConvergenceParameters(max_bond_dimension=1)
                _, submps[0], _, _ = submps[0].split_svd(
                    [0],
                    [1, 2],
                    contract_singvals="R",
                    conv_params=dummy_conv_params,
                    is_link_outgoing_left=False,
                )
            # shift iso center to right and truncate along the way
            submps.left_canonize(idx=len(submps) - 1, trunc=True)

            # right side
            if submps[-1].shape[-1] != 1:
                dummy_conv_params = TNConvergenceParameters(max_bond_dimension=1)
                submps[-1], _, _, _ = submps[-1].split_svd(
                    [0, 1],
                    [2],
                    contract_singvals="L",
                    conv_params=dummy_conv_params,
                    is_link_outgoing_left=False,
                )
            # shift iso center to left and truncate along the way
            submps.right_canonize(idx=0, trunc=True)
        else:
            submps.iso_center = self.iso_center - first_site

        return submps

    # --------------------------------------------------------------------------
    #                   Choose to overwrite instead of inheriting
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    #                                  Unsorted
    # --------------------------------------------------------------------------

    def flipped(self):
        """
        Flip an MPS completely left-right.

        Returns
        -------

        psi : :class:`MPS`
            Wave function with the reverse order of sites with respect
            to `self`.
        """
        tensor_list = []
        for tensor in self[::-1]:
            tensor_list.append(tensor.transpose([2, 1, 0]))

        obj = self.from_tensor_list(
            tensor_list,
            conv_params=self.convergence_parameters,
            tensor_backend=self.tensor_backend,
            target_device="any",
        )
        obj.iso_center = self.num_sites - self.iso_center - 1

        return obj

    def _iter_all_links(self, pos):
        """
        Iterate through all the links of
        a given position of the MPS

        Parameters
        ----------
        pos : int
            Index of the tensor

        Yields
        ------
        int
            Index of the tensor. The order is
            left-physical-right
        """
        yield pos - 1, 2
        yield -pos - 2, 1
        yield pos + 1, 0

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
        for pos in range(self.num_sites):
            yield -pos - 2, pos

    def right_canonize(
        self,
        idx,
        trunc=False,
        keep_singvals=False,
        conv_params=None,
        move_to_memory_device=True,
        normalize=False,
    ):
        """
        Isometrize from right to left, applying a gauge transformation
        to all bonds between :py:method:`MPS.num_sites` and
        `idx`. All sites between the last (rightmost one) and idx
        are set to (semi)-unitary tensors.

        Parameters
        ----------
        idx: int
            index of the tensor up to which the canonization occurs
        trunc: bool, optional
            If True, use the SVD instead of the QR for the canonization.
            It might be useful to reduce the bond dimension. Default to False.
        keep_singvals : bool, optional
            If True, keep the singular values even if shifting the iso with a
            QR decomposition. Default to False.
        conv_params : :py:class:`TNConvergenceParameters`, optional
            Convergence parameters to use for the SVD in the procedure.
            If `None`, convergence parameters are taken from the TTN.
            Default to `None`.
        move_to_memory_device : bool, optional
            If True, when a mixed device is used, move the tensors that are not the
            isometry center back to the memory device. Default to True.
        normalize : bool, optional
            Flag if intermediate steps should normalize.
            Default to `False`
        """
        self.sanity_check()
        do_svd = self._requires_singvals or trunc

        if idx > self.num_sites - 1 or idx < 0:
            raise ValueError(
                "The canonization index must be between the "
                + "number of sites-1 and 0"
            )
        if conv_params is None:
            conv_params = self._convergence_parameters

        if self.first_non_orthogonal_right > idx:
            self.move_pos(
                self.first_non_orthogonal_right,
                device=self._tensor_backend.computational_device,
                stream=True,
            )

        for ii in range(self.first_non_orthogonal_right, idx, -1):
            if ii > idx:
                self.move_pos(
                    ii - 1,
                    device=self._tensor_backend.computational_device,
                    stream=True,
                )

            if self[ii].ndim == 4:
                # We want to allow this for TN ML (label link as LPTN Kraus link and order)
                legs_iso = [0, 2]
                legs_uni = [1, 3]
            else:
                legs_iso = [0]
                legs_uni = [1, 2]

            if self._decomposition_free_iso_towards:
                pass

            elif do_svd:
                rr_mat, tensor, singvals, _ = self[ii].split_svd(
                    legs_iso,
                    legs_uni,
                    contract_singvals="L",
                    conv_params=conv_params,
                    no_truncation=not trunc,
                )

                if normalize:
                    if tensor.linear_algebra_library == "tensorflow" and (
                        not tensor.has_symmetry
                    ):
                        # tensorflow is missing flatten method
                        raise NotImplementedError(
                            "tensorflow needs manual implementation."
                        )

                    ss = np.array(singvals.flatten())
                    norm = np.sqrt((ss**2).sum())
                    singvals /= norm
                    rr_mat /= norm

                self._singvals[ii] = singvals
            else:
                rr_mat, tensor = self[ii].split_rq(legs_iso, legs_uni)

                if normalize:
                    norm = rr_mat.norm()
                    rr_mat /= norm

                if not keep_singvals or rr_mat.shape[0] != tensor.shape[0]:
                    self._singvals[ii] = None

            if not self._decomposition_free_iso_towards:
                # Update the tensors in the MPS
                self._tensors[ii] = tensor

                # Even for resulting rank-4 tensor of ML-MPS tensordot is correct
                self._tensors[ii - 1] = self[ii - 1].tensordot(rr_mat, ([2], [0]))

            self._update_eff_ops([ii, ii - 1])

            if ii > idx and move_to_memory_device:
                self.move_pos(
                    ii, device=self._tensor_backend.memory_device, stream=True
                )

            self.sanity_check()

        self._first_non_orthogonal_left = min(self.first_non_orthogonal_left, idx)
        self._first_non_orthogonal_right = idx

        self.sanity_check()

    def left_canonize(
        self,
        idx,
        trunc=False,
        keep_singvals=False,
        conv_params=None,
        move_to_memory_device=True,
        normalize=False,
    ):
        """
        Isometrize from left to right, applying a gauge transformation
        to all bonds between 0 and `idx`. All sites between the
        first (leftmost one) and idx are set to (semi)-unitary tensors.

        Parameters
        ----------
        idx: int
            index of the tensor up to which the canonization occurs
        trunc: bool, optional
            If True, use the SVD instead of the QR for the canonization.
            It might be useful to reduce the bond dimension. Default to False.
        keep_singvals : bool, optional
            If True, keep the singular values even if shifting the iso with a
            QR decomposition. Default to False.
        conv_params : :py:class:`TNConvergenceParameters`, optional
            Convergence parameters to use for the SVD in the procedure.
            If `None`, convergence parameters are taken from the MPS.
            Default to `None`.
        move_to_memory_device : bool, optional
            If True, when a mixed device is used, move the tensors that are not the
            isometry center back to the memory device. Default to True.
        normalize : bool, optional
            Flag if singular values should be normalized.
            Default to `False`
        """
        self.sanity_check()
        do_svd = self._requires_singvals or trunc

        if idx > self.num_sites - 1 or idx < 0:
            raise ValueError(
                "The canonization index must be between the "
                + f"number of sites-1 and 0, not {idx}"
            )
        if conv_params is None:
            conv_params = self._convergence_parameters

        if self.first_non_orthogonal_left < idx:
            self.move_pos(
                self.first_non_orthogonal_left,
                device=self._tensor_backend.computational_device,
                stream=True,
            )

        for ii in range(self.first_non_orthogonal_left, idx):
            if ii < idx:
                self.move_pos(
                    ii + 1,
                    device=self._tensor_backend.computational_device,
                    stream=True,
                )

            tensor = self[ii]
            if tensor.ndim == 4:
                # We want to allow this for TN ML (label link as LPTN Kraus link and order)
                legs_iso = [2, 3]
                legs_uni = [0, 1]
                estr = "abc,cxy->axby"
            else:
                legs_iso = [2]
                legs_uni = [0, 1]
                estr = "ab,bxy->axy"

            if self._decomposition_free_iso_towards:
                pass

            elif do_svd:
                tensor, rr_mat, singvals, _ = self[ii].split_svd(
                    legs_uni,
                    legs_iso,
                    contract_singvals="R",
                    conv_params=conv_params,
                    no_truncation=not trunc,
                )
                if normalize:
                    if tensor.linear_algebra_library == "tensorflow" and (
                        not tensor.has_symmetry
                    ):
                        # tensorflow is missing flatten method
                        raise NotImplementedError(
                            "tensorflow needs manual implementation."
                        )

                    ss = np.array(singvals.flatten())
                    norm = np.sqrt((ss**2).sum())
                    singvals /= norm
                    rr_mat /= norm

                self._singvals[ii + 1] = singvals
            else:
                tensor, rr_mat = self[ii].split_qr(legs_uni, legs_iso)

                if normalize:
                    norm = rr_mat.norm()
                    rr_mat /= norm

                if not keep_singvals:
                    self._singvals[ii + 1] = None

            if not self._decomposition_free_iso_towards:
                # Update the tensors in the MPS
                self._tensors[ii] = tensor
                self._tensors[ii + 1] = rr_mat.einsum(estr, self[ii + 1])

            self._update_eff_ops([ii, ii + 1])

            if ii < idx and move_to_memory_device:
                self.move_pos(
                    ii, device=self._tensor_backend.memory_device, stream=True
                )
            self.sanity_check()

        self._first_non_orthogonal_left = idx
        self._first_non_orthogonal_right = max(self.first_non_orthogonal_right, idx)
        self.sanity_check()

    def normalize(self):
        """
        Normalize the MPS state, by dividing by :math:`\\sqrt{<\\psi|\\psi>}`.
        """
        # Compute the norm. Internally, it set the gauge center
        norm = self.norm()
        # Update the norm
        self._tensors[self.iso_center] /= norm

    def modify_local_dim(self, value, idxs=None):
        """
        Modify the local dimension of sites `idxs` to the value `value`.
        By default modify the local dimension of all the sites. If `value` is
        a vector then it must have the same length of `idxs`.
        Notice that there may be loss of information, it is up to the
        user to be sure no error is done in this procedure.

        Parameters
        ----------
        value : int or array-like
            New value of the local dimension. If an int, it is assumed
            it will be the same for all sites idxs, otherwise its length
            must be the same of idxs.
        idxs : int or array-like, optional
            Indexes of the sites to modify. If None, all the sites are
            modified. Default to None.
        """
        # Transform scalar arguments in vectors
        if np.isscalar(value) and idxs is None:
            value = np.repeat(value, self.num_sites).astype(int)
        if idxs is None:
            idxs = np.arange(self.num_sites)
        elif np.isscalar(idxs) and np.isscalar(value):
            idxs = np.array([idxs])
            value = np.array([value])

        # Checks on parameters
        if np.any(idxs > self.num_sites - 1) or np.any(idxs < 0):
            raise ValueError(
                "The index idx must be between the " + "number of sites-1 and 0"
            )
        if np.min(value) < 2:
            raise ValueError(
                f"The local dimension must be at least 2, not {min(value)}"
            )
        if len(value) != len(idxs):
            raise ValueError(
                "value and idxs must have the same length, but "
                + f"{len(value)} != {len(idxs)}"
            )

        # Quick return
        if len(idxs) == 0:
            return
        # Sort arguments to avoid moving the gauge back and forth
        value = value[np.argsort(idxs)]
        idxs = np.sort(idxs)

        for ii, idx in enumerate(idxs):
            initial_local_dim = self.local_dim[idx]
            new_local_dim = value[ii]

            if initial_local_dim == new_local_dim:
                # Already right dimension
                continue

            self.site_canonize(idx, keep_singvals=True)
            initial_norm = self.norm()

            if new_local_dim < initial_local_dim:
                # Get subtensor along link
                res = self[idx].subtensor_along_link(1, 0, new_local_dim)
            else:
                shape = [
                    self[idx].shape[0],
                    new_local_dim - initial_local_dim,
                    self[idx].shape[2],
                ]
                kwargs = self._tensor_backend.tensor_cls_kwargs()

                # Will fail for symmetric tensors
                pad = self._tensor_backend(shape, **kwargs)

                res = self[idx].stack_link(pad, 1)

            self._tensors[idx] = res

            final_norm = self.norm()
            self._tensors[self.iso_center] *= initial_norm / final_norm

            self._local_dim[idx] = new_local_dim

    def add_site(self, idx, state=None):
        """
        Add a site in a product state in the link idx
        (idx=0 is before the first site, idx=N+1 is after the last).
        The state of the new index is |0> or the one provided.

        Parameters
        ----------
        idx : int
            index of the link where you want to add the site
        state: None or array-like
            Vector state that you want to add

        Details
        -------
        To insert a new site in the MPS we first insert an identity on a link,
        then add a dimension-1 link to the identity and lastly contract the
        new link with the initial state, usually a |0>
        """
        if idx < 0 or idx > self.num_sites:
            raise ValueError(f"idx must be between 0 and N+1, not {idx}")
        if state is None:
            local_dim = int(np.min(self.local_dim))
            kwargs = self._tensor_backend.tensor_cls_kwargs()
            state = self._tensor_backend([1, local_dim, 1], ctrl="ground", **kwargs)

        old_norm = self.norm()

        # Insert an identity on link idx
        if idx == 0:
            id_dim = self[0].shape[0]
        else:
            id_dim = self[idx - 1].shape[2]

        identity = state.eye_like(id_dim)
        identity.reshape_update([id_dim, 1, id_dim])

        # Contract the identity with the desired state of the new tensor
        state = state.reshape([np.prod(state.shape), 1])
        new_site = identity.tensordot(state, ([1], [1]))
        new_site = new_site.transpose([0, 2, 1])

        # Insert it in the data structure
        self._tensors.insert(idx, new_site)
        # False positive for pylint
        # pylint: disable-next=attribute-defined-outside-init
        self._local_dim = np.insert(self._local_dim, idx, new_site.shape[1])
        # False positive for pylint
        # pylint: disable-next=no-member
        self._num_sites += 1
        self._singvals.insert(idx + 1, None)

        # Update the gauge center if we didn't add the site at the end of the chain
        if idx < self.num_sites - 1 and idx < self.iso_center:
            self._first_non_orthogonal_right += 1
            self._first_non_orthogonal_left += 1

        # Renormalize
        new_norm = self.norm()

        self._tensors[self.iso_center] *= old_norm / new_norm

    def to_statevector(self, qiskit_order=False, max_qubit_equivalent=20):
        """
        Given a list of N tensors *MPS* [U1, U2, ..., UN] , representing
        a Matrix Product State, perform the contraction in the Examples,
        leading to a single tensor of order N, representing a dense state.

        The index ordering convention is from left-to-right.
        For instance, the "left" index of U2 is the first, the "bottom" one
        is the second, and the "right" one is the third.

        Parameters
        ----------
        qiskit_order: bool, optional
            weather to use qiskit ordering or the theoretical one. For
            example the state |011> has 0 in the first position for the
            theoretical ordering, while for qiskit ordering it is on the
            last position.
        max_qubit_equivalent: int, optional
            Maximum number of qubit sites the MPS can have and still be
            transformed into a statevector.
            If the number of sites is greater, it will throw an exception.
            Default to 20.

        Returns
        -------
        psi : ndarray of shape (d ^ N, )
            N-order tensor representing the dense state.

        Examples
        --------
        >>> U1 - U2 - ... - UN
        >>>  |    |          |
        """
        if np.prod(self.local_dim) > 2**max_qubit_equivalent:
            raise RuntimeError(
                "Maximum number of sites for the statevector is "
                + f"fixed to the equivalent of {max_qubit_equivalent} qubit sites"
            )
        self.move_pos(0, device=self._tensor_backend.computational_device)
        self.move_pos(1, device=self._tensor_backend.computational_device)
        psi = self[0]
        for ii, tensor in enumerate(self[1:]):
            if ii < self.num_sites - 2:
                self.move_pos(
                    ii + 2,
                    device=self._tensor_backend.computational_device,
                    stream=True,
                )
            psi = psi.tensordot(tensor, ([-1], [0]))
            if ii + 1 != self._iso_center:
                self.move_pos(
                    ii + 1, device=self._tensor_backend.memory_device, stream=True
                )

        if qiskit_order:
            order = "F"
        else:
            order = "C"

        return psi.reshape(np.prod(self.local_dim), order=order)

    def to_tensor_list(self):
        """
        Return the tensor list representation of the MPS.
        Required for compatibility with TTN emulator

        Return
        ------
        list
            List of tensors of the MPS
        """
        return self.tensors

    def to_ttn(self, trunc=False, convergence_parameters=None):
        """
        Return a tree tensor network (TTN) representation as binary tree.

        Details
        -------

        The TTN is returned as a listed list where the tree layer with the
        local Hilbert space is the first list entry and the uppermost layer in the TTN
        is the last list entry. The first list will have num_sites / 2 entries. The
        uppermost list has two entries.

        The order of the legs is always left-child, right-child, parent with
        the exception of the left top tensor. The left top tensor has an
        additional link, i.e., the symmetry selector; the order is left-child,
        right-child, parent, symmetry-selector.

        Also see :py:func:ttn_simulator:`from_tensor_list`.
        """
        nn = len(self)
        if abs(np.log2(nn) - int(np.log2(nn))) > 1e-15:
            raise QTeaLeavesError(
                "A conversion to a binary tree requires 2**n "
                "sites; but having %d sites." % (nn)
            )

        if nn == 4:
            # Special case: iterations will not work
            left_tensor = self[0].tensordot(self[1], [[2], [0]])
            right_tensor = self[2].tensordot(self[3], [[2], [0]])

            # Use left link of dimension 1 as symmetry selector
            left_tensor.transpose_update([1, 2, 3, 0])

            # Eliminate one link
            right_tensor.reshape_update(right_tensor.shape[:-1])

            return [[left_tensor, right_tensor]]

        # Initial iteration
        child_list = []
        parent_list = []
        for ii in range(nn // 2):
            ii1 = 2 * ii
            ii2 = ii1 + 1

            for jj in [ii1, ii2]:
                if jj != self.iso_center:
                    self[jj].convert(device=self.computational_device)

            theta = self[ii1].tensordot(self[ii2], [[2], [0]])

            for jj in [ii1, ii2]:
                if jj != self.iso_center:
                    self[jj].convert(device=self.memory_device)

            if trunc:
                qmat, rmat, _, _ = theta.split_svd(
                    [1, 2],
                    [0, 3],
                    perm_right=[1, 0, 2],
                    contract_singvals="R",
                    conv_params=convergence_parameters,
                )
            else:
                qmat, rmat = theta.split_qr([1, 2], [0, 3], perm_right=[1, 0, 2])

            qmat.convert(device=self.memory_device)
            rmat.convert(device=self.memory_device)

            child_list.append(qmat)
            parent_list.append(rmat)

        layer_list = [child_list]
        while len(parent_list) > 4:
            child_list = []
            new_parent_list = []
            for ii in range(len(parent_list) // 2):
                ii1 = 2 * ii
                ii2 = ii1 + 1

                for jj in [ii1, ii2]:
                    parent_list[jj].convert(device=self.computational_device)

                theta = parent_list[ii1].tensordot(parent_list[ii2], [[2], [0]])

                if trunc:
                    qmat, rmat, _, _ = theta.split_svd(
                        [1, 2],
                        [0, 3],
                        perm_right=[1, 0, 2],
                        contract_singvals="R",
                        conv_params=convergence_parameters,
                    )
                else:
                    qmat, rmat = theta.split_qr([1, 2], [0, 3], perm_right=[1, 0, 2])

                qmat.convert(device=self.memory_device)
                rmat.convert(device=self.memory_device)

                child_list.append(qmat)
                new_parent_list.append(rmat)

            parent_list = new_parent_list
            layer_list.append(child_list)

        # Last iteration
        for jj in [0, 1, 2, 3]:
            # Send all of them, no way the garbage collector kicks in
            # soon enough without custom handling
            parent_list[jj].convert(device=self.computational_device)

        left_tensor = parent_list[0].tensordot(parent_list[1], [[2], [0]])
        right_tensor = parent_list[2].tensordot(parent_list[3], [[2], [0]])

        # In case of symmetric tensor networks, we need a global-symmetry
        # sector link, coming from the MPS, this is the outgoing link to
        # the right, which has to go to the top-left tensor in the TTN
        left_tensor.remove_dummy_link(0)

        if trunc:
            right_tensor, r_mat, _, _ = right_tensor.split_svd(
                [1, 2],
                [0, 3],
                contract_singvals="R",
                conv_params=convergence_parameters,
            )
        else:
            right_tensor, r_mat = right_tensor.split_qr([1, 2], [0, 3])
        left_tensor = left_tensor.tensordot(r_mat, ([2], [1]))

        right_tensor.convert(device=self.memory_device)
        layer_list.append([left_tensor, right_tensor])

        return layer_list

    @classmethod
    def from_tensor_list(
        cls,
        tensor_list,
        conv_params=None,
        tensor_backend=None,
        target_device=None,
    ):
        """
        Initialize the MPS tensors using a list of correctly shaped tensors

        Parameters
        ----------
        tensor_list : list of ndarrays or cupy arrays or :class:`_AbstractQteaTensors`
            List of tensor for initializing the MPS
        conv_params : :py:class:`TNConvergenceParameters`, optional
            Convergence parameters for the new MPS. If None, the maximum bond
            bond dimension possible is assumed, and a cut_ratio=1e-9.
            Default to None.
        tensor_backend : `None` or instance of :class:`TensorBackend`
            Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.
        target_device: None | str, optional
            If `None`, take memory device of tensor backend.
            If string is `any`, do not convert. Otherwise,
            use string as device string.

        Returns
        -------
        obj : :py:class:`MPS`
            The MPS class
        """
        mismatches = [
            tensor_list[ii].shape[2] != tensor_list[ii + 1].shape[0]
            for ii in range(len(tensor_list) - 1)
        ]
        if any(mismatches):
            msg = f"Mismatches for tensors equals to True: {mismatches}."
            logger.error(msg)
            raise ValueError("Dimension mismatch when constructing MPS.")

        if conv_params is None:
            max_bond_dim = max(elem.shape[2] for elem in tensor_list)
            conv_params = TNConvergenceParameters(max_bond_dimension=int(max_bond_dim))
        if tensor_backend is None:
            # Have to resolve it here in case target device is not given
            tensor_backend = TensorBackend()
        if target_device is None:
            target_device = tensor_backend.memory_device
        elif target_device == "any":
            target_device = None

        local_dim = [elem.shape[1] for elem in tensor_list]
        obj = cls(
            len(tensor_list), conv_params, local_dim, tensor_backend=tensor_backend
        )
        obj.iso_center = None

        qtea_tensor_list = []
        for elem in tensor_list:
            if not isinstance(elem, _AbstractQteaTensor):
                qtea_tensor_list.append(
                    obj._tensor_backend.tensor_cls.from_elem_array(elem)
                )
            else:
                qtea_tensor_list.append(elem)

        obj._tensors = qtea_tensor_list

        obj.convert(obj._tensor_backend.dtype, target_device)

        return obj

    @classmethod
    def product_state_from_local_states(
        cls,
        mat,
        padding=None,
        convergence_parameters=None,
        tensor_backend=None,
    ):
        """
        Construct a product (separable) state in MPS form, given the local
        states of each of the sites.

        Parameters
        ----------
        mat : List[np.array of rank 1] or np.array of rank 2
            Matrix with ii-th row being a (normalized) local state of
            the ii-th site.
            Number of rows is therefore equal to the number of sites,
            and number of columns corresponds to the local dimension.
            Pass a list if different sites have different local dimensions so
            that they require arrays of different size.

        padding : np.array of length 2 or `None`, optional
            Used to enable the growth of bond dimension in TDVP algorithms
            for MPS (necessary as well for two tensor updates).
            If not `None`, all the MPS tensors are padded such that the bond
            dimension is equal to `padding[0]`. The value `padding[1]`
            tells with which value are we padding the tensors. Note that
            `padding[1]` should be very small, as it plays the role of
            numerical noise.
            If False, the bond dimensions are equal to 1.
            Default to None.

        convergence_parameters : :py:class:`TNConvergenceParameters`, optional
            Convergence parameters for the new MPS.

        tensor_backend : `None` or instance of :class:`TensorBackend`
            Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.

        Return
        ------
        :py:class:`MPS`
            Corresponding product state MPS.
        """
        if tensor_backend is None:
            logger_warning("Choosing default tensor backend because not given.")
            tensor_backend = TensorBackend()

        nn = len(mat) if isinstance(mat, list) else mat.shape[0]
        for ii in range(0, nn):
            # Small vectors, stay on default device CPU
            mat_tmp = tensor_backend.tensor_cls.from_elem_array(
                mat[ii], dtype=tensor_backend.dtype
            )
            norm = mat_tmp.norm()
            if abs(norm - 1) > 100 * mat_tmp.dtype_eps:
                raise ValueError(
                    f"Local state on site {ii+1} not normalized. " f"Norm = {norm}."
                )

        local_dim = [len(elem) for elem in mat]

        if padding is not None:
            pad, pad_value = padding[0], padding[1]

        # convergence parameters are hard-coded for now
        if convergence_parameters is None:
            convergence_parameters = TNConvergenceParameters(
                max_bond_dimension=local_dim
            )

        # Prepare the tensor list
        tensor_list = []
        for idx, local_state in enumerate(mat):
            theta = tensor_backend.tensor_cls.from_elem_array(
                local_state.reshape(1, -1, 1),
                dtype=tensor_backend.dtype,
                device=tensor_backend.device,
            )
            if padding is not None and idx > 0:
                # pylint: disable-next=possibly-used-before-assignment
                theta = theta.expand_tensor(0, pad, ctrl=pad_value)
            if padding is not None and idx < nn - 1:
                # pylint: disable-next=possibly-used-before-assignment
                theta = theta.expand_tensor(2, pad, ctrl=pad_value)
            tensor_list.append(theta)

        prod_mps = cls.from_tensor_list(
            tensor_list=tensor_list,
            conv_params=convergence_parameters,
            tensor_backend=tensor_backend,
        )

        return prod_mps

    def apply_one_site_operator(self, op, pos):
        """
        Applies a one operator `op` to the site `pos` of the MPS.

        Parameters
        ----------
        op: QteaTensor of shape (local_dim, local_dim)
            Matrix representation of the quantum gate
        pos: int
            Position of the qubit where to apply `op`.

        """
        if pos < 0 or pos > self.num_sites - 1:
            raise ValueError(
                "The position of the site must be between 0 and (num_sites-1)"
            )
        op.convert(dtype=self[pos].dtype, device=self[pos].device)

        res = self[pos].tensordot(op, ([1], [1]))
        self._tensors[pos] = res.transpose([0, 2, 1])

    def apply_two_site_operator(self, op, pos, swap=False, svd=True, parallel=False):
        """
        Applies a two-site operator `op` to the site `pos`, `pos+1` of the MPS.

        Parameters
        ----------
        op: QteaTensor (local_dim, local_dim, local_dim, local_dim)
            Matrix representation of the quantum gate
        pos: int or list of ints
            Position of the qubit where to apply `op`. If a list is passed,
            the two sites should be adjacent. The first index is assumed to
            be the control, and the second the target. The swap argument is
            overwritten if a list is passed.
        swap: bool
            If True swaps the operator. This means that instead of the
            first contraction in the following we get the second.
            It is written is a list of pos is passed.
        svd: bool
            If True, apply the usual contraction plus an SVD, otherwise use the
            QR approach explained in https://arxiv.org/pdf/2212.09782.pdf.
        parallel: bool
            If True, perform an approximation of the two-qubit gates faking
            the isometry center

        Returns
        -------
        singular_values_cutted: ndarray
            Array of singular values cutted, normalized to the biggest singular value

        Examples
        --------

        .. code-block::

            swap=False  swap=True
              -P-M-       -P-M-
              2| |2       2| |2
              3| |4       4| |3
               GGG         GGG
              1| |2       2| |1
        """
        if not np.isscalar(pos) and len(pos) == 2:
            if max(pos[0], pos[1]) - min(pos[0], pos[1]) > 1:
                logger_warning("Using non-local gates. Errors might increase.")
                return self.apply_nonlocal_two_site_operator(op, pos[0], pos[1], swap)
            pos = min(pos[0], pos[1])
        elif not np.isscalar(pos):
            raise ValueError(
                f"pos should be only scalar or len 2 array-like, not len {len(pos)}"
            )

        if pos < 0 or pos > self.num_sites - 1:
            raise ValueError(
                "The position of the site must be between 0 and (num_sites-1)"
            )
        op = op.reshape([self._local_dim[pos], self._local_dim[pos + 1]] * 2)

        if swap:
            op = op.transpose([1, 0, 3, 2])
        if parallel:
            self[pos].scale_link_update(self.singvals[pos], 0)
            contract_singvals = "L"
        else:
            # Set orthogonality center
            self.iso_towards(pos, keep_singvals=True)
            self.move_pos(
                pos + 1, device=self._tensor_backend.computational_device, stream=True
            )
            contract_singvals = "R"
            op.convert(dtype=self[pos].dtype, device=self[pos].device)
        # Perform SVD
        if svd:
            # Contract the two qubits
            twoqubit = self[pos].tensordot(self[pos + 1], ([2], [0]))

            # Contract with the gate
            twoqubit = twoqubit.tensordot(op, ([1, 2], [2, 3]))
            twoqubit.transpose_update([0, 2, 3, 1])
            tens_left, tens_right, singvals, singvals_cutted = twoqubit.split_svd(
                [0, 1],
                [2, 3],
                contract_singvals=contract_singvals,
                conv_params=self._convergence_parameters,
            )
        else:
            tens_left, tens_right, singvals, singvals_cutted = self[pos].split_qrte(
                self[pos + 1],
                self.singvals[pos],
                op,
                conv_params=self._convergence_parameters,
            )
        # Update state
        self._tensors[pos] = tens_left
        self._tensors[pos + 1] = tens_right
        self._singvals[pos + 1] = singvals

        if parallel:
            self[pos].scale_link_update(1 / self.singvals[pos], 0)

        else:
            self._first_non_orthogonal_left = pos + 1
            self._first_non_orthogonal_right = pos + 1
            # Move back to memory the site pos
            self.move_pos(pos, device=self._tensor_backend.memory_device, stream=True)

        # Update maximum bond dimension reached
        if self[pos].shape[2] > self.max_bond_dim_reached:
            self.max_bond_dim_reached = self[pos].shape[2]
        return singvals_cutted

    def swap_qubits(self, sites, conv_params=None, trunc=True):
        """
        This function applies a swap gate to sites in an MPS,
        i.e. swaps these two qubits

        Parameters
        ----------
        sites : Tuple[int]
            The qubits on site sites[0] and sites[1] are swapped
        conv_params : :py:class:`TNConvergenceParameters`, optional
            Convergence parameters to use for the SVD in the procedure.
            If `None`, convergence parameters are taken from the TTN.
            Default to `None`.

        Return
        ------
        np.ndarray
            Singualr values cut in the process of shifting the isometry center.
            None if moved through the QR.
        """
        if conv_params is None:
            conv_params = self._convergence_parameters
        # transform input into np array just in case the
        # user passes the list
        sites = np.sort(sites)
        singvals_cut_tot = []
        self.iso_towards(sites[0], True, False, conv_params)
        self.move_pos(
            sites[0] + 1, device=self._tensor_backend.computational_device, stream=True
        )

        # Move sites[0] in sites[1] position
        for pos in range(sites[0], sites[1]):
            if pos < sites[1] - 1:
                self.move_pos(
                    pos + 2,
                    device=self._tensor_backend.computational_device,
                    stream=True,
                )
            # Contract the two sites
            two_sites = self[pos].tensordot(self[pos + 1], ([2], [0]))
            # Swap the qubits
            two_sites.transpose_update([0, 2, 1, 3])
            if trunc:
                left, right, singvals, singvals_cut = two_sites.split_svd(
                    [0, 1], [2, 3], contract_singvals="R", conv_params=conv_params
                )
                self._singvals[pos + 1] = singvals
                singvals_cut_tot.append(singvals_cut)
            else:
                left, right = two_sites.split_qr([0, 1], [2, 3])

            if pos < sites[1] - 2:
                left.convert(device=self._tensor_backend.memory_device, stream=True)
            # Update tensor and iso center
            self._tensors[pos] = left
            self._tensors[pos + 1] = right
            self._first_non_orthogonal_left += 1
            self._first_non_orthogonal_right += 1

        self.iso_towards(sites[1] - 1, True, False, conv_params)
        # Move sites[1] in sites[0] position
        for pos in range(sites[1] - 1, sites[0], -1):
            if pos > sites[0] + 1:
                self.move_pos(
                    pos - 2,
                    device=self._tensor_backend.computational_device,
                    stream=True,
                )
            # Contract the two sites
            two_sites = self[pos - 1].tensordot(self[pos], ([2], [0]))
            # Swap the qubits
            two_sites.transpose_update([0, 2, 1, 3])
            if trunc:
                left, right, singvals, singvals_cut = two_sites.split_svd(
                    [0, 1], [2, 3], contract_singvals="L", conv_params=conv_params
                )
                self._singvals[pos] = singvals
                singvals_cut_tot.append(singvals_cut)
            else:
                right, left = two_sites.split_qr(
                    [2, 3], [0, 1], perm_left=[2, 0, 1], perm_right=[1, 2, 0]
                )

            right.convert(device=self._tensor_backend.memory_device, stream=True)
            # Update tensor and iso center
            self._tensors[pos - 1] = left
            self._tensors[pos] = right
            self._first_non_orthogonal_left -= 1
            self._first_non_orthogonal_right -= 1

        return singvals_cut_tot

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
        rho_i, meas_state, old_norm = self._apply_projective_operator_common(
            site, selected_output
        )
        state_prob = rho_i.elem[meas_state, meas_state]

        # Renormalize and come back to previous norm
        if remove:
            ii = meas_state
            tens_to_remove = self._tensors[site].subtensor_along_link(1, ii, ii + 1)
            tens_to_remove.remove_dummy_link(1)

            if site < self.num_sites - 1:
                self.move_pos(
                    site + 1, device=self._tensor_backend.computational_device
                )
                # contract the measured tensor in the next tensor
                self._tensors[site + 1] = tens_to_remove.tensordot(
                    self[site + 1], ([1], [0])
                )
            else:
                self.move_pos(
                    site - 1, device=self._tensor_backend.computational_device
                )
                self._tensors[site - 1] = self[site - 1].tensordot(
                    tens_to_remove, ([2], [0])
                )

            self._tensors.pop(site)
            self._singvals.pop(site)
            # False positive for pylint
            # pylint: disable-next=attribute-defined-outside-init
            self._local_dim = np.delete(self._local_dim, site)
            # False positive for pylint
            # pylint: disable-next=no-member
            self._num_sites -= 1
            # False positive for pylint
            # pylint: disable-next=no-member
            site = min(site, self._num_sites - 1)
            self._first_non_orthogonal_left = site
            self._first_non_orthogonal_right = site
        else:
            projector = _projector_for_rho_i(meas_state, rho_i)
            self.apply_one_site_operator(projector, site)

        # Renormalize
        self._tensors[site] = self._tensors[site] / self.norm()
        self._tensors[site] = self._tensors[site] * old_norm

        # Set to None all the singvals
        self._singvals = [None for _ in self.singvals]

        return meas_state, complex(state_prob)

    def apply_nonlocal_two_site_operator(self, op, control, target, swap=False):
        """Apply a non-local two-site operator, by taking first the SVD of the operator,
        contracting the almost-single-site operator to the respective sites and then
        propagating the operator to the correct site

        .. warning::
            The operations in this method are NOT ALWAYS well defined. If the left-operator
            tensor is not unitary, then we are applying a non-unitary operation to the
            state, and thus we will see a vanishing norm. Notice that, if the error can
            happen a warning message will be issued

        Parameters
        ----------
        op : np.ndarray
            Operator to be applied
        control : int
            control qubit index
        target : int
            target qubit index
        swap : bool, optional
            If True, transpose the tensor legs such that the control and target
            are swapped. Default to False

        Returns
        -------
        np.ndarray
            Singular values cutted when the gate link is contracted
        """

        if min(control, target) < 0 or max(control, target) > self.num_sites - 1:
            raise ValueError(
                "The position of the site must be between 0 and (num_sites-1)"
            )
        if list(op.shape) != [self._local_dim[control], self._local_dim[target]] * 2:
            raise ValueError(
                "Shape of the input operator must be (local_dim, "
                + "local_dim, local_dim, local_dim)"
            )
        if swap:
            op = op.transpose([1, 0, 3, 2])

        min_site = min(control, target)
        max_site = max(control, target)
        left_gate, right_gate, _, _ = op.split_svd(
            [0, 2],
            [1, 3],
            perm_left=[0, 2, 1],
            perm_right=[1, 0, 2],
            contract_singvals="L",
            no_truncation=True,
            conv_params=self._convergence_parameters,
        )

        test = right_gate.tensordot(right_gate.conj(), ([0, 1], [0, 1]))
        if not test.is_close_identity():
            warn(
                "Right-tensor is not unitary thus the contraction is not optimal. We "
                "suggest to linearize the circuit instead of using non-local operators",
                RuntimeWarning,
            )

        self.site_canonize(min_site, keep_singvals=True)
        self._tensors[min_site] = self[min_site].tensordot(
            left_gate / np.sqrt(2), ([1], [2])
        )

        self._tensors[min_site] = self._tensors[min_site].transpose([0, 2, 3, 1])

        for idx in range(min_site, max_site):
            double_site = self[idx].tensordot(self[idx + 1], ([3], [0]))
            (self._tensors[idx], self._tensors[idx + 1]) = double_site.split_qr(
                [0, 1], [2, 3, 4], perm_right=[0, 2, 1, 3]
            )

        self._tensors[max_site] = self[max_site].tensordot(
            right_gate * np.sqrt(2), ([1, 2], [2, 1])
        )
        self._tensors[max_site] = self._tensors[max_site].transpose([0, 2, 1])

        # double_site = np.tensordot(self[max_site-1], self[max_site], ([3, 2], [0, 2]) )
        # self._tensors[max_site-1], self._tensors[max_site], _, singvals_cut = \
        #        self.tSVD(double_site, [0, 1], [2, 3], contract_singvals='R' )

        self._first_non_orthogonal_left = max_site
        self._first_non_orthogonal_right = max_site
        self.iso_towards(min_site, keep_singvals=True, trunc=True)

        return []

    def apply_mpo(self, mpo):
        """
        Apply an MPO to the MPS on the sites `sites`.
        The MPO should have the following convention for the links:
        0 is left link. 1 is physical link pointing downwards.
        2 is phisical link pointing upwards. 3 is right link.

        The sites are encoded inside the DenseMPO class.

        Parameters
        ----------
        mpo : DenseMPO
            MPO to be applied

        Returns
        -------
        np.ndarray
            Singular values cutted when the gate link is contracted
        """
        # Sort sites
        # mpo.sort_sites()
        sites = np.array([mpo_site.site for mpo_site in mpo])
        # if not np.isclose(sites, np.sort(sites)).all():
        #    raise RuntimeError("MPO sites are not sorted")

        # transform input into np array just in case the
        # user passes the list
        operators = [site.operator * site.weight for site in mpo]
        if mpo[0].strength is not None:
            operators[0] *= mpo[0].strength

        self.site_canonize(sites[0], keep_singvals=True)

        tot_singvals_cut = []
        # Operator index
        oidx = 0
        next_site = self[sites[0]].eye_like(self[sites[0]].shape[0])
        for sidx in range(sites[0], sites[-1] + 1):
            if sidx < sites[-1]:
                self.move_pos(
                    sidx + 1,
                    device=self._tensor_backend.computational_device,
                    stream=True,
                )
            tens = self[sidx]
            if sidx in sites:
                # i -o- k
                #    |j     = T(i,k,l,m,n) -> T(i,l,m, k,n)
                # l -o- n
                #    |m
                tens = tens.tensordot(operators[oidx], ([1], [2]))
                tens.transpose_update((0, 2, 3, 1, 4))
                # T(i,l,m, k,n) -> T(il, m, kn)
                tens.reshape_update((np.prod(tens.shape[:2]), tens.shape[2], -1))

                # The matrix next, from the second cycle, is bringing the isometry center in tens
                # next = next.reshape(-1, tens.shape[0])
                # x -o- il -o- kn = x -o- kn
                #           |m         |m
                tens = next_site.tensordot(tens, ([1], [0]))
                oidx += 1

                if sidx + 1 in sites:
                    # Move the isometry when the next site has an MPO (and thus left-dimension kn)
                    # x -o- kn -->  x -o- y -o- kn
                    #    |m            |m
                    self._tensors[sidx], next_site, _, singvals_cut = tens.split_svd(
                        [0, 1],
                        [2],
                        contract_singvals="R",
                        conv_params=self._convergence_parameters,
                        no_truncation=True,
                    )

                    tot_singvals_cut += list(singvals_cut)
                elif sidx == sites[-1]:
                    # End of the procedure
                    self._tensors[sidx] = tens
                else:
                    # Move the isometry when the next site does not have an MPO
                    # x -o- kn -->  x -o- y -o- kn
                    #    |m
                    self._tensors[sidx], next_site = tens.split_qr([0, 1], [2])
                    #                n|
                    # y -o- kn --> y -o- k
                    # T(y,kn) -> T(y, k, n) -> T(y, n, k)
                    next_site.reshape_update(
                        (next_site.shape[0], -1, operators[oidx - 1].shape[3])
                    )
                    next_site.transpose_update((0, 2, 1))

            else:
                # Site does not have an operator, just bring the isometry here
                #   n|
                # y -o- i -o- k -> T(y, n, j, k) -> T(y, j, n, k)
                #          | j
                tens = next_site.tensordot(tens, ([2], [0]))
                tens.transpose_update((0, 2, 1, 3))

                if sidx + 1 in sites:
                    tens.reshape_update((tens.shape[0], tens.shape[1], -1))
                    self._tensors[sidx], next_site, _, singvals_cut = tens.split_svd(
                        [0, 1],
                        [2],
                        contract_singvals="R",
                        conv_params=self._convergence_parameters,
                        no_truncation=True,
                    )
                    tot_singvals_cut += list(singvals_cut)
                else:
                    #   n|                 |n
                    # y -o- k --> y -o- s -o- k
                    #    |j          |j
                    self._tensors[sidx], next_site = tens.split_qr([0, 1], [2, 3])

            if sidx < sites[-1]:
                self.move_pos(
                    sidx, device=self._tensor_backend.memory_device, stream=True
                )

        self._first_non_orthogonal_left = sites[-1]
        self._first_non_orthogonal_right = sites[-1]
        self.iso_towards(sites[0], trunc=True, keep_singvals=True)

        return tot_singvals_cut

    def reset(self, idxs=None):
        """
        Reset the states of the sites idxs to the |0> state

        Parameters
        ----------
        idxs : int or list of ints, optional
            indexes of the sites to reinitialize to 0.
            If default value is left all the sites are restarted.
        """
        if idxs is None:
            idxs = np.arange(self.num_sites)
        elif np.isscalar(idxs):
            idxs = [idxs]
        else:
            idxs = np.array(idxs)
            idxs = np.sort(idxs)

        for idx in idxs:
            state, _ = self.apply_projective_operator(idx)
            if state != 0:
                new_projector = np.zeros((self._local_dim[idx], self._local_dim[idx]))
                new_projector[0, state] = 1
                self.apply_one_site_operator(new_projector, idx)

        self.left_canonize(self.num_sites - 1, trunc=True)
        self.right_canonize(0, trunc=True)

    #########################################################################
    ######################### Optimization methods ##########################
    #########################################################################

    def default_sweep_order(self, skip_exact_rgtensors=False):
        """
        Default sweep order to be used in the ground state search/time evolution.
        Default for MPS is left-to-right.

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
        List[int]
            The generator that you can sweep through
        """
        site_1 = 0
        site_n = self.num_sites

        if skip_exact_rgtensors:
            # Iterate first from left to right
            for ii in range(self.num_sites - 1):
                link_idx = self[ii].ndim - 1
                if self[ii].is_link_full(link_idx):
                    site_1 += 1
                else:
                    break

            # Now check from right to left
            for ii in range(1, self.num_sites)[::-1]:
                if self[ii].is_link_full(0):
                    site_n -= 1
                else:
                    break

            # Safe-guard to ensure one-site is optimized (also for d=2 necessary)
            if site_1 == site_n:
                if site_1 > 0:
                    site_1 -= 1
                elif site_n < self.num_sites:
                    site_n += 1
                else:
                    warn("Setup of skip_exact_rgtensors failed.")
                    site_1 = 0
                    site_n = self.num_sites

        return list(range(site_1, site_n))

    def get_pos_partner_link_expansion(self, pos):
        """
        Get the position of the partner tensor to use in the link expansion
        subroutine. It is the tensor towards the center, that is supposed to
        be more entangled w.r.t. the tensor towards the edge

        Parameters
        ----------
        pos : int
            Position w.r.t. which you want to compute the partner

        Returns
        -------
        int
            Position of the partner
        int
            Link of pos pointing towards the partner
        int
            Link of the partner pointing towards pos
        """
        pos_partner = pos + 1 if pos < self.num_sites / 2 else pos - 1
        link_self = 2 if pos < pos_partner else 0
        link_partner = 0 if pos < pos_partner else 2

        return pos_partner, link_self, link_partner

    #########################################################################
    ######################## Time evolution methods #########################
    #########################################################################

    def _partial_iso_towards_for_timestep(self, pos, next_pos, no_rtens=False):
        """
        Move by hand the iso for the evolution backwards in time

        Parameters
        ----------
        pos : Tuple[int]
            Position of the tensor evolved
        next_pos : Tuple[int]
            Position of the next tensor to evolve

        Returns
        -------
        QTeaTensor | link_self
            The R tensor of the iso movement
            link_self in no_rtens=True mode
        Tuple[int]
            The position of the partner (pos+-1 in MPSs)
        int
            The link of the partner pointing towards pos
        List[int]
            The update path to pass to _update_eff_ops
        """
        requires_singvals = self._requires_singvals

        # Needed in other TN geometries
        link_partner = 0 if pos < next_pos else 2
        pos_partner = pos + 1 if pos < next_pos else pos - 1
        self.move_pos(
            pos_partner, device=self._tensor_backend.computational_device, stream=True
        )

        path_elem = [pos, next_pos]
        if no_rtens:
            link_self = 2 if pos < next_pos else 0
            return link_self, pos_partner, link_partner, path_elem

        if (pos < next_pos) and requires_singvals:
            # Going left-to-right, SVD
            qtens, rtens, s_vals, _ = self[pos].split_svd(
                [0, 1],
                [2],
                no_truncation=True,
                conv_params=self._convergence_parameters,
                contract_singvals="R",
            )
            self.set_singvals_on_link(pos, pos_partner, s_vals)

        elif pos < next_pos:
            # Going left-to-right, QR
            qtens, rtens = self[pos].split_qr([0, 1], [2])
            self.set_singvals_on_link(pos, pos_partner, None)
        elif requires_singvals:
            # Going right-to-left, SVD
            qtens, rtens, s_vals, _ = self[pos].split_svd(
                [1, 2],
                [0],
                no_truncation=True,
                conv_params=self._convergence_parameters,
                contract_singvals="R",
                perm_left=[2, 0, 1],
            )
            self.set_singvals_on_link(pos, pos_partner, s_vals)
        else:
            # Going right-to-left, RQ. Need to permute Q tensor (this is called
            # also by abstractTN where R cannot be permuted, always the first
            # link needs to go to the Q-tensor.)
            qtens, rtens = self[pos].split_qr([1, 2], [0], perm_left=[2, 0, 1])
            self.set_singvals_on_link(pos, pos_partner, None)
        self[pos] = qtens

        return rtens, pos_partner, link_partner, path_elem

    def contract(self, other, boundaries=None):
        """
        Contract the MPS with another MPS other <other|self>.
        By default it is a full contraction, but also a partial
        contraction is possible

        Parameters
        ----------
        other : MPS
            other MPS to contract with
        boundaries : tuple of two ints, optional
            Contract to MPSs from boundaries[0] to boundaries[1].
            In this case the output will be a tensor of shape
            (chi_self, chi_other, 1) or (1, chi_self, chi_other).
            Default to None, which is  full contraction

        Returns
        -------
        contraction : complex | :class:`_AbstractQteaTensor`
            Result of the contraction
        """
        if not isinstance(other, MPS):
            raise TypeError("Only two MPS classes can be contracted")
        if self.num_sites != other.num_sites:
            raise ValueError(
                "Number of sites must be the same to contract two MPS together"
            )
        if np.any(self.local_dim != other.local_dim):
            raise ValueError(
                "Local dimension must be the same to contract MPS: "
                + f"{self.local_dim}!={other.local_dim}."
            )

        if boundaries is None:
            full_contraction = True
            boundaries = (0, self.num_sites, 1)
        else:
            full_contraction = False
            boundaries = (*boundaries, np.sign(boundaries[1] - boundaries[0]))

        idx = 0 if boundaries[1] > boundaries[0] else 2
        self.move_pos(boundaries[0], device=self._tensor_backend.computational_device)
        other.move_pos(boundaries[0], device=self._tensor_backend.computational_device)

        transfer_mat = self[boundaries[0]].eye_like(self[boundaries[0]].links[idx])
        for ii in range(*boundaries):
            if ii + boundaries[2] != boundaries[1]:
                self.move_pos(
                    ii + boundaries[2],
                    device=self._tensor_backend.computational_device,
                    stream=True,
                )
                other.move_pos(
                    ii + boundaries[2],
                    device=self._tensor_backend.computational_device,
                    stream=True,
                )

            if boundaries[2] > 0:
                transfer_mat = transfer_mat.tensordot(self[ii], ([0], [idx]))
            else:
                transfer_mat = self[ii].tensordot(transfer_mat, ([idx], [0]))

            transfer_mat = transfer_mat.tensordot(
                other[ii].conj(), ([idx, 1], [idx, 1])
            )

            if ii != self.iso_center:
                self.move_pos(
                    ii, device=self._tensor_backend.memory_device, stream=True
                )
            if ii != other.iso_center:
                other.move_pos(
                    ii, device=self._tensor_backend.memory_device, stream=True
                )

        if full_contraction:
            contraction = transfer_mat.get_entry()
        else:
            new_shape = (
                (1, *transfer_mat.shape)
                if boundaries[1] > boundaries[0]
                else (*transfer_mat.shape, 1)
            )
            contraction = transfer_mat.reshape(new_shape)
        return contraction

    def kron(self, other, inplace=False, install_iso=False):
        """
        Concatenate two MPS, taking the kronecker/outer product
        of the two states. The bond dimension assumed is the maximum
        between the two bond dimensions.
        The function does not renormalize the MPS.

        Parameters
        ----------
        other : :py:class:`MPS`
            MPS to concatenate
        inplace : bool, optional
            If True apply the kronecker product in place. Instead, if
            inplace=False give as output the product. Default to False.
        install_iso : bool, optional
            If true, the isometry center will be installed in the resulting
            tensor network. The isometry centers of `self` and `other` might
            be shifted in order to do so. For `False`, the isometry center
            in the new MPS is not set.
            Default to `False`.

        Returns
        -------
        :py:class:`MPS`
            Concatenation of the first MPS with the second in order

        Details
        -------

        The tensors in the new MPS are not copied, inplace modifications
        in either `self` or `other` to their tensors will be reflected
        in both MPS, `self` or `other` and the new MPS. Inplace-updates
        include operations like multiplying in-place an MPS and therefore
        one of its tensors. Since copies on this scale might be expensive
        for two MPS, they have to be done explicitly.
        """
        # pylint: disable=protected-access
        if not isinstance(other, MPS):
            raise TypeError("Only two MPS classes can be concatenated")
        if self[-1].shape[2] != 1 and other[0].shape[0] != 1:
            raise ValueError(
                "Head and tail of the MPS not compatible. Last "
                + "and first dimensions of the tensors must be the same"
            )
        if self._tensor_backend.device != other._tensor_backend.device:
            raise RuntimeError(
                "MPS to be kron multiplied must be on the same "
                + f"device, not {self._tensor_backend.device} and "
                + f"{other._tensor_backend.device}."
            )
        max_bond_dim = max(
            self._convergence_parameters.max_bond_dimension,
            other._convergence_parameters.max_bond_dimension,
        )
        cut_ratio = min(
            self._convergence_parameters.cut_ratio,
            other._convergence_parameters.cut_ratio,
        )
        convergence_params = deepcopy(self._convergence_parameters)
        convergence_params._max_bond_dimension = int(max_bond_dim)
        convergence_params._cut_ratio = cut_ratio

        if install_iso:
            self.iso_towards(self.num_sites - 1)
            other.iso_towards(0)

        tensor_list = self.tensors + other.tensors

        # pylint: disable-next=invalid-name
        add_mps = MPS.from_tensor_list(
            tensor_list,
            convergence_params,
            tensor_backend=self._tensor_backend,
            target_device="any",
        )
        add_mps._singvals[: self.num_sites + 1] = self.singvals
        add_mps._singvals[self.num_sites + 1 :] = other.singvals[1:]
        # pylint: enable=protected-access

        if install_iso:
            # Currently two non-gauged tensors at previous last
            # and first site
            add_mps.iso_center = self.num_sites
            add_mps.iso_towards(self.num_sites - 1)

        if inplace:
            self.__dict__.update(add_mps.__dict__)
            return None
        return add_mps

    # ---------------------------
    # ----- MEASURE METHODS -----
    # ---------------------------

    def meas_tensor_product(self, ops, idxs):
        """
        Measure the tensor products of n operators `ops` acting on the indexes `idxs`.
        The operators should be MPOs, i.e. rank-4 tensors of shape (left, up, down, right).
        To retrieve the tensor product operators, left=right=1.

        Parameters
        ----------
        ops : list of ndarrays
            List of numpy arrays which are one-site operators
        idxs : list of int
            Indexes where the operators are applied

        Returns
        -------
        measure : float
            Result of the measurement
        """
        self.check_obs_input(ops, idxs)

        if len(idxs) == 0:
            return 1

        order = np.argsort(idxs)
        idxs = np.array(idxs)[order]
        self.iso_towards(idxs[0], keep_singvals=True)

        transfer_mat = (
            self[idxs[0]].eye_like(self[idxs[0]].links[0]).attach_dummy_link(1)
        )
        jj = 0
        closed = False
        for ii in range(idxs[0], self.num_sites):
            if ii < self.num_sites - 1:
                self.move_pos(
                    ii + 1,
                    device=self._tensor_backend.computational_device,
                    stream=True,
                )
            if closed:
                break

            # Case of finished tensors
            if jj == len(idxs):
                # close with transfer matrix of correct size
                closing_transfer_mat = (
                    self[ii].eye_like(self[ii].links[0]).attach_dummy_link(1)
                )
                measure = transfer_mat.tensordot(
                    closing_transfer_mat, ([0, 1, 2], [0, 1, 2])
                )
                closed = True
            # Case of operator inside
            elif idxs[jj] == ii:
                op_jj = ops[order[jj]]
                transfer_mat = transfer_mat.tensordot(self[ii], ([0], [0]))
                transfer_mat = transfer_mat.tensordot(op_jj, ([0, 2], [0, 2]))
                transfer_mat = transfer_mat.tensordot(self[ii].conj(), ([0, 2], [0, 1]))
                jj += 1
            # Case of no operator between the sites
            else:
                transfer_mat = transfer_mat.tensordot(self[ii], ([0], [0]))
                transfer_mat = transfer_mat.tensordot(self[ii].conj(), ([1, 2], [0, 1]))
                transfer_mat.transpose_update([1, 0, 2])

            # The idxs[0] is still the isometry, so we want to keep it on the computational device
            if ii > idxs[0]:
                self.move_pos(
                    ii, device=self._tensor_backend.memory_device, stream=True
                )

        if not closed:
            # close with transfer matrix of correct size
            closing_transfer_mat = (
                self[idxs[0]].eye_like(self[-1].links[2]).attach_dummy_link(1)
            )
            measure = transfer_mat.tensordot(
                closing_transfer_mat, ([0, 1, 2], [0, 1, 2])
            )
            closed = True

        # pylint: disable-next=used-before-assignment
        measure = measure.get_entry()

        return np.real(measure)

    def meas_weighted_sum(self, op_strings, idxs_strings, coefs):
        """
        Measure the weighted sum of tensor product operators.
        See :py:func:`meas_tensor_product`

        Parameters
        ----------
        op_strings : list of lists of ndarray
            list of tensor product operators
        idxs_strings : list of list of int
            list of indexes of tensor product operators
        coefs : list of complex
            list of the coefficients of the sum

        Return
        ------
        measure : complex
            Result of the measurement
        """
        if not (
            len(op_strings) == len(idxs_strings) and len(idxs_strings) == len(coefs)
        ):
            raise ValueError(
                "op_strings, idx_strings and coefs must all have the same length"
            )

        measure = 0.0
        for ops, idxs, coef in zip(op_strings, idxs_strings, coefs):
            measure += coef * self.meas_tensor_product(ops, idxs)

        return measure

    def meas_bond_entropy(self):
        """
        Measure the entanglement entropy along all the sites of the MPS
        using the Von Neumann entropy :math:`S_V` defined as:

        .. math::

            S_V = - \\sum_i^{\\chi} s^2 \\ln( s^2)

        with :math:`s` the singular values

        Return
        ------
        measures : dict
            Keys are the range of the bipartition from 0 to which the entanglement
            (value) is relative
        """
        measures = {}
        # ensure that all the bonds have the correct singular values set
        self.right_canonize(0, trunc=True)

        for ii, ss in enumerate(self.singvals[1:-1]):
            if hasattr(ss, "get"):
                ss = ss.get()
            if ss is None:
                s_von_neumann = None
            elif self[0].linear_algebra_library != "tensorflow" or self[0].has_symmetry:
                # flatten singvals for the case of symmetric TN
                ss = np.array(ss.flatten())
                s_von_neumann = -2 * (ss**2 * np.log(ss)).sum()
            else:
                # Only tensorflow has no flatten method, even AbelianLinkWeights do
                flatten = self[0].get_attr("flatten")
                ss = np.array(flatten(ss))
                s_von_neumann = -2 * (ss**2 * np.log(ss)).sum()

            measures[(0, ii + 1)] = s_von_neumann

        return measures

    def meas_even_probabilities(self, threshold, qiskit_convention=False):
        """
        Compute the probabilities of measuring a given state if it is greater
        than a threshold. The function goes down "evenly" on the probability
        tree. This means that there is the possibility that no state is
        returned, if their probability is lower then threshold. Furthermore,
        notice that the **maximum** number of states returned is
        :math:`(\frac{1}{threshold})`.

        For a different way of computing the probability tree see the
        function :py:func:`meas_greedy_probabilities` or
        :py:func:`meas_unbiased_probabilities`.

        Parameters
        ----------
        threshold : float
            Discard all the probabilities lower then the threshold
        qiskit_convention : bool, optional
            If the sites during the measure are represented such that
            |201> has site 0 with value one (True, mimicks bits ordering) or
            with value 2 (False usually used in theoretical computations).
            Default to False.

        Return
        ------
        probabilities : dict
            Dictionary where the keys are the states while the values their
            probabilities. The keys are separated by a comma if local_dim > 9.
        """

        if threshold < 0:
            raise ValueError("Threshold value must be positive")
        if threshold < 1e-3:
            warn("A too low threshold might slow down the sampling exponentially.")

        # Put in canonic form
        self.right_canonize(0, keep_singvals=True)
        old_norm = self.norm()
        self._tensors[0] /= old_norm

        self._temp_for_prob = {}
        self._measure_even_probabilities(threshold, 1, "", 0, self[0])

        # Rewrite with qiskit convention
        probabilities = postprocess_statedict(
            self._temp_for_prob,
            local_dim=self.local_dim,
            qiskit_convention=qiskit_convention,
        )

        self._tensors[0] *= old_norm

        return probabilities

    def _measure_even_probabilities(self, threshold, probability, state, idx, tensor):
        """
        Hidden recursive function to compute the probabilities

        Parameters
        ----------
        threshold : float
            Discard of all state with probability less then the threshold
        probability : float
            probability of having that state
        states : string
            string describing the state up to that point
        idx : int
            Index of the tensor currently on the function
        tensor : np.ndarray
            Tensor to measure

        Returns
        -------
        probabilities : dict
            Dictionary where the keys are the states while the values their
            probabilities. The keys are separated by a comma if local_dim > 9.
        """
        local_dim = self.local_dim[idx]

        if probability > threshold:
            probabilities, tensors_list = self._get_children_prob(tensor, idx)
            # Multiply by the probability of having the given state
            probabilities = probability * probabilities
            states = [state + str(ii) + "," for ii in range(local_dim)]

            if idx < self.num_sites - 1:
                # Call recursive part
                for tens, prob, ss in zip(tensors_list, probabilities, states):
                    self._measure_even_probabilities(threshold, prob, ss, idx + 1, tens)
            else:
                # Save the results
                for prob, ss in zip(probabilities, states):
                    if prob > threshold:
                        ss = ss[:-1]  # Remove trailing comma
                        self._temp_for_prob[ss] = prob

    def meas_greedy_probabilities(
        self, max_prob, max_iter=None, qiskit_convention=False
    ):
        """
        Compute the probabilities of measuring a given state until the total
        probability measured is greater than the threshold max_prob.
        The function goes down "greedily" on the probability
        tree. This means that there is the possibility that a path that was
        most promising at the tree root will become very computationally
        demanding and not so informative once reached the leaves. Furthermore,
        notice that there is no **maximum** number of states returned, and so
        the function might be exponentially slow.

        For a different way of computing the probability tree see the
        function :py:func:`meas_even_probabilities` or
        :py:func:`meas_unbiased_probabilities`

        Parameters
        ----------
        max_prob : float
            Compute states until you reach this probability
        qiskit_convention : bool, optional
            If the sites during the measure are represented such that
            |201> has site 0 with value one (True, mimicks bits ordering) or
            with value 2 (False usually used in theoretical computations).
            Default to False.

        Return
        ------
        probabilities : dict
            Dictionary where the keys are the states while the values their
            probabilities. The keys are separated by a comma if local_dim > 9.
        """
        max_iter = 2**self.num_sites if max_iter is None else max_iter
        if max_prob > 0.95:
            warn(
                "Execution of the function might be exponentially slow due "
                "to the highness of the threshold",
                RuntimeWarning,
            )

        # Set gauge on the left and renormalize
        self.right_canonize(0)
        old_norm = self.norm()
        self._tensors[0] /= old_norm

        all_probs = [{}]
        probabilities = {}
        probability_sum = 0

        tensor = self[0]
        site_idx = 0
        curr_state = ""
        curr_prob = 1
        cnt = 0
        while probability_sum < max_prob and cnt < max_iter:
            if len(all_probs) < site_idx + 1:
                all_probs.append({})
            if site_idx > 0:
                states = [
                    curr_state + f",{ii}" for ii in range(self.local_dim[site_idx])
                ]
            else:
                states = [
                    curr_state + f"{ii}" for ii in range(self.local_dim[site_idx])
                ]
            # Compute the children if we didn't already follow the branch
            if not np.all([ss in all_probs[site_idx] for ss in states]):
                probs, tensor_list = self._get_children_prob(tensor, site_idx)
                probs = curr_prob * probs

                # Update probability tracker for next branch
                for ss, prob, tens in zip(states, probs, tensor_list):
                    all_probs[site_idx][ss] = [prob, tens]
            # Retrieve values if already went down the path
            else:
                probs = []
                tensor_list = []
                for ss, (prob, tens) in all_probs[site_idx].items():
                    probs.append(prob)
                    tensor_list.append(tens)
            # Greedily select the next branch if we didn't reach the leaves
            if site_idx < self.num_sites - 1:
                # Select greedily next path
                tensor = tensor_list[np.argmax(probs)]
                curr_state = states[np.argmax(probs)]

                # We get probs on host, but not necessarily ndarray
                probs = np.array(probs)
                curr_prob = np.max(probs)
                site_idx += 1
            # Save values if we reached the leaves
            else:
                for ss, prob in zip(states, probs):
                    if not np.isclose(prob, 0, atol=1e-10):
                        probabilities[ss] = prob
                        probability_sum += prob
                # Remove this probability from the tree
                for ii in range(self.num_sites - 1):
                    measured_state = states[0].split(",")[: ii + 1]
                    measured_state = ",".join(measured_state)

                    # We get probs on host, but not necessarily ndarray
                    probs = np.array(probs)
                    all_probs[ii][measured_state][0] -= np.sum(probs)
                # Restart from the beginning
                site_idx = 0
                curr_state = ""
                cnt += 1

        # Rewrite with qiskit convention
        final_probabilities = postprocess_statedict(
            probabilities, local_dim=self.local_dim, qiskit_convention=qiskit_convention
        )

        self._tensors[0] *= old_norm

        return final_probabilities

    def _get_children_prob(self, tensor, site_idx, *args):
        """
        Compute the probability and the relative tensor state of all the
        children of site `site_idx` in the tensor tree

        Parameters
        ----------
        tensor : np.ndarray
            Parent tensor, with respect to which we compute the children
        site_idx : int
            Index of the parent tensor
        args : list
            other arguments are not needed for the MPS implementation
            and stored in `*args`.

        Returns
        -------
        probabilities : list of floats
            Probabilities of the children. Real part and on host,
            but not necessary numpy if `qredtea` is used.
        tensor_list : list of ndarray
            Child tensors, already contracted with the next site
            if not last site.
        """
        local_dim = self.local_dim[site_idx]
        if tensor is None:
            tmp = self[site_idx].vector_with_dim_like(local_dim)
            tmp *= 0.0
            return tmp, np.repeat(None, local_dim)

        tensor.convert(device=self._tensor_backend.computational_device)
        if site_idx + 1 < self.num_sites:
            self[site_idx + 1].convert(
                device=self._tensor_backend.computational_device, stream=True
            )
        conjg_tens = tensor.conj()
        tensors_list = []

        # Construct rho at effort O(chi_l * chi_r * d^2) which is
        # equal to contracting one projector to one tensor
        reduced_rho = tensor.tensordot(conjg_tens, ([0, 2], [0, 2]))

        # Convert to array on host/CPU with real values; select diagonal elements
        probabilities = reduced_rho.diag(real_part_only=True, do_get=True)

        # Loop over basis states
        for jj, prob_jj in enumerate(probabilities):
            # Compute probabilities of the state; projecting always to
            # one index `j`, we can read the diagonal entries of the
            # reduced density matrix
            # --> we have it already due to the trace

            # Create list of updated tensors after the projection
            if prob_jj > 0 and site_idx < self.num_sites - 1:
                # Extract the rank-2 tensor without tensordot as we operator
                # on a diagonal projector with a single index
                temp_tens = tensor.subtensor_along_link(1, jj, jj + 1)
                temp_tens.remove_dummy_link(1)

                # Contract with the next site in the MPS
                temp_tens = temp_tens.tensordot(self[site_idx + 1], ([1], [0]))
                temp_tens.convert(
                    device=self._tensor_backend.memory_device, stream=True
                )
                tensors_list.append(temp_tens * (prob_jj ** (-0.5)))
            else:
                tensors_list.append(None)

        if site_idx + 1 < self.num_sites:
            self[site_idx + 1].convert(
                device=self._tensor_backend.memory_device, stream=True
            )
        return probabilities, tensors_list

    def _get_children_magic(self, transfer_matrix, site_idx, *args):
        """
        Compute the probability and the relative tensor state of all the
        children of site `site_idx` in the tensor tree

        Parameters
        ----------
        transfer_matrix : np.ndarray
            Parent tensor, with respect to which we compute the children
        site_idx : int
            Index of the parent tensor
        args : list
            other arguments are not needed for the MPS implementation
            and stored in `*args`.

        Returns
        -------
        probabilities : list of floats
            Probabilities of the children
        tensor_list : list of ndarray
            Child tensors, already contracted with the next site
            if not last site.
        """
        tensor = deepcopy(self.get_tensor_of_site(site_idx))
        tensor.convert(device=self._tensor_backend.computational_device, stream=True)

        if transfer_matrix is None:
            tmp = tensor.vector_with_dim_like(4)
            tmp *= 0.0
            return tmp, np.repeat(None, 4)

        transfer_matrix.convert(
            device=self._tensor_backend.computational_device, stream=True
        )
        probabilities = tensor.vector_with_dim_like(4)
        tensors_list = []

        rho_i = tensor.tensordot(tensor.conj(), ([0, 2], [0, 2]))
        pauli_1 = rho_i.zeros_like()
        pauli_x = rho_i.zeros_like()
        pauli_y = rho_i.zeros_like()
        pauli_z = rho_i.zeros_like()

        pauli_1.set_diagonal_entry(0, 1)
        pauli_1.set_diagonal_entry(1, 1)
        pauli_x.set_matrix_entry(0, 1, 1)
        pauli_x.set_matrix_entry(1, 0, 1)
        pauli_y.set_matrix_entry(0, 1, -1j)
        pauli_y.set_matrix_entry(1, 0, 1j)
        pauli_z.set_diagonal_entry(0, 1)
        pauli_z.set_diagonal_entry(1, -1)
        paulis = [pauli_1, pauli_x, pauli_y, pauli_z]

        original_transfer_matrix = deepcopy(transfer_matrix)
        for ii, pauli in enumerate(paulis):
            temp_tens = tensor.tensordot(pauli, ([1], [1]))
            transfer_matrix = original_transfer_matrix.tensordot(temp_tens, ([0], [0]))
            transfer_matrix = transfer_matrix.tensordot(tensor.conj(), ([0, 2], [0, 1]))

            probability_as_tensor = transfer_matrix.tensordot(
                transfer_matrix.conj(), ([0, 1], [0, 1])
            )

            prob_host = np.real(probability_as_tensor.get_entry()) / 2
            probabilities[ii] = prob_host
            if prob_host > 0 and site_idx < self.num_sites - 1:
                transfer_matrix.convert(device=self._tensor_backend.memory_device)
                tensors_list.append(transfer_matrix / np.sqrt(np.real(prob_host * 2)))
            else:
                tensors_list.append(None)

        probabilities = tensor.get_of(probabilities)
        probabilities = np.real(probabilities)

        return probabilities, tensors_list

    def _get_child_prob(self, tensor, site_idx, target_prob, unitary_setup, *args):
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
        args : list
            Other argument are not needed for the MPS implementation
            and stored in `*args`.
        """
        tensor.convert(device=self._tensor_backend.computational_device, stream=True)
        if site_idx < self.num_sites - 1:
            self[site_idx + 1].convert(
                device=self._tensor_backend.computational_device, stream=True
            )
        # Get functions for elemtary arrays
        cumsum, sqrt = tensor.get_attr("cumsum", "sqrt")

        local_dim = self.local_dim[site_idx]

        if unitary_setup is not None:
            # Have to apply local unitary
            unitary = unitary_setup.get_unitary(site_idx)

            # Contract and permute back
            tensor = unitary.tensordot(tensor, ([1], [1]))
            tensor.transpose_update([1, 0, 2])

        conjg_tens = tensor.conj()

        # Calculate the cumulated probabilities via the reduced
        # density matrix
        reduced_rho = tensor.tensordot(conjg_tens, ([0, 2], [0, 2]))

        probs = reduced_rho.diag(real_part_only=True)
        cumul_probs = cumsum(probs)
        measured_idx = None

        for jj in range(local_dim):
            if cumul_probs[jj] < target_prob:
                continue

            prob_jj = probs[jj]

            # Reached interval with target probability ... project
            measured_idx = jj
            temp_tens = tensor.subtensor_along_link(1, jj, jj + 1)
            temp_tens.remove_dummy_link(1)
            temp_tens /= sqrt(probs[jj])

            if site_idx < self.num_sites - 1:
                temp_tens = temp_tens.tensordot(self[site_idx + 1], ([1], [0]))
            else:
                temp_tens = None

            break

        if site_idx > 1:
            tensor.convert(device=self._tensor_backend.memory_device, stream=True)
        if site_idx < self.num_sites - 1:
            self[site_idx + 1].convert(
                device=self._tensor_backend.memory_device, stream=True
            )

        return measured_idx, temp_tens, prob_jj

    # ------------------------
    # ---- I/O Operations ----
    # ------------------------

    def write(self, filename, cmplx=True):
        """
        Write an MPS in python format into a FORTRAN format, i.e.
        transforms row-major into column-major

        Parameters
        ----------
        filename: str
            PATH to the file
        cmplx: bool, optional
            If True the MPS is complex, real otherwise. Default to True

        Returns
        -------
        None
        """
        self.convert(None, "cpu")

        with open(filename, "w") as fh:
            fh.write(str(len(self)) + " \n")
            for tens in self:
                tens.write(fh, cmplx=cmplx)

        return None

    @classmethod
    def read(cls, filename, tensor_backend, cmplx=True, order="F"):
        """
        Read an MPS via pickle or in the old formatted way shared
        with the Quantum TEA fortran modules.

        Parameters
        ----------
        filename: str
            PATH to the file
        tensor_backend : :class:`TensorBackend`
            Setup which tensor class to create.
        cmplx: bool, optional
            If True the MPS is complex, real otherwise. Default to True
        order: str, optional
            If 'F' the tensor is transformed from column-major to row-major, if 'C'
            it is left as read.

        Returns
        -------
        obj: py:class:`MPS`
            MPS class read from file

        Details
        -------

        The formatted format looks like in the following:

        Reads in column-major order but the output is in row-major.
        This is the only method that overrides the number of sites,
        since you may not know before reading.
        """
        ext = "pkl" + cls.extension
        if filename.endswith(ext):
            return cls.read_pickle(filename, tensor_backend=tensor_backend)

        tensors = []
        with open(filename, "r") as fh:
            num_sites = int(fh.readline())

            for _ in range(num_sites):
                tens = tensor_backend.tensor_cls.read(
                    fh,
                    tensor_backend.dtype,
                    tensor_backend.device,
                    tensor_backend.base_tensor_cls,
                    cmplx=cmplx,
                    order=order,
                )
                tensors.append(tens)

        obj = cls.from_tensor_list(tensors, tensor_backend=tensor_backend)

        return obj

    # --------------------------------------
    # ---- Effective operators methods -----
    # --------------------------------------

    # pylint: disable-next=unused-argument
    def build_effective_operators(self, measurement_mode=False):
        """
        Build the complete effective operator on each
        of the links. It assumes `self.eff_op` is set.
        Also builds effective projectors, self.eff_proj.

        Parameters
        ----------
        measurement_mode : bool, optional
            If True, enable measurement mode of effective operators
        """
        self.iso_towards(self.default_iso_pos, keep_singvals=True)

        if self.eff_op is None and len(self.eff_proj) == 0:
            # This might be a problem in the future if you want to use effective
            # projectors without the eff_op. It requires an update to the logic.
            # Luka Oct 2024
            raise QTeaLeavesError(
                "Trying to build eff_op or eff_proj without attribute being set."
            )
        if self.eff_op is None:
            logger.info("No effective operators to build.")
        if len(self.eff_proj) == 0:
            logger.info("No effective projectors to build.")

        self.move_pos(0, device=self._tensor_backend.computational_device)
        for pos, tens in enumerate(self[:-1]):
            self.move_pos(
                pos + 1, device=self._tensor_backend.computational_device, stream=True
            )
            # Retrieve the index of the operators for the left link
            # and the physical link
            idx_out = 2
            pos_links = self.get_pos_links(pos)
            self.eff_op.contr_to_eff_op(tens, pos, pos_links, idx_out)
            # get the effective projectors for this tensor
            for proj in self.eff_proj:
                proj.contr_to_eff_op(tens, pos, pos_links, idx_out)

            if measurement_mode:
                # pylint: disable-next=unsubscriptable-object
                self.eff_op[pos, pos_links[idx_out]].run_measurements(
                    tens, idx_out, self.singvals[pos + 1]
                )
            self.move_pos(pos, device=self._tensor_backend.memory_device, stream=True)

        if measurement_mode:
            # To finish measurements, we keep going through the last site as
            # well
            pos = self.num_sites - 1
            idx_out = 2
            pos_links = self.get_pos_links(pos)
            self.eff_op.contr_to_eff_op(self[-1], pos, pos_links, idx_out)

            # Last center must be isometry center
            link_weights = None
            # pylint: disable-next=unsubscriptable-object
            self.eff_op[(pos, pos_links[idx_out])].run_measurements(
                self[-1], idx_out, link_weights
            )

    def _update_eff_ops(self, id_step):
        """
        Update the effective operators after the iso shift.
        Also updates the effective projectors.

        Parameters
        ----------
        id_step : list of ints
            List with the iso path, i.e. `[src_tensor, dst_tensor]`

        Returns
        -------
        None
            Updates the effective operators in place
        """
        # Get info on the source tensor
        tens = self[id_step[0]]
        src_link = 0 if id_step[0] > id_step[1] else 2
        links = self.get_pos_links(id_step[0])

        # Perform the contraction if needed
        for proj in self.eff_proj:
            proj.contr_to_eff_op(tens, id_step[0], links, src_link)

        if self.eff_op is not None:
            self.eff_op.contr_to_eff_op(tens, id_step[0], links, src_link)

    def deprecated_get_eff_op_on_pos(self, pos):
        """
        Obtain the list of effective operators adjacent
        to the position pos and the index where they should
        be contracted

        Parameters
        ----------
        pos : list
            list of [layer, tensor in layer]

        Returns
        -------
        list of IndexedOperators
            List of effective operators
        list of ints
            Indexes where the operators should be contracted
        """
        # pylint: disable-next=unsubscriptable-object
        eff_ops = [self.eff_op[oidx] for oidx in self.op_neighbors[:, pos]]
        idx_list = np.arange(3)

        return eff_ops, idx_list

    # --------------------------------------------------------------------------
    #                               ML Operations
    # --------------------------------------------------------------------------

    def ml_reorder_pos_pair(self, pos, pos_partner, link_pos, link_partner):
        """
        MPS order is with left tensor first.

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

        if pos < pos_partner:
            if self[pos].ndim == 4:
                link_pos = 3
            return pos, pos_partner, link_pos, link_partner

        if self[pos_partner].ndim == 4:
            link_partner = 3
        return pos_partner, pos, link_partner, link_pos

    def ml_default_sweep_order(self, num_tensor_rule):
        """
        Default sweep order for a machine learning optimization, where we
        replace the ground state sweep order.

        Arguments
        ---------

        num_tensor_rule: int
            Specify if it is a one-tensor or two-tensor update.

        Returns
        -------

        sweep_order : List
            List of tensor positions compatible with the corresponding
            ansatz. For two-site rules, each pair is optimized once
            which skips one center position in respect to the ground state
            search for the two-tensor update.
        """

        logger_warning(
            "DeprecationWarning: The machine learning methods in qtealeaves classes are deprecated."
            + " For machine learning tasks, please utilize the qchaitea classes instead."
        )

        if num_tensor_rule == 2:
            sweep = []
            prev = None
            for ii in range(self.num_sites):
                pos_p, _, _ = self.get_pos_partner_link_expansion(ii)
                pair = (min(ii, pos_p), max(ii, pos_p))
                if pair != prev:
                    sweep.append(ii)

                prev = pair

            return sweep
        if num_tensor_rule == 1:
            return self.default_sweep_order()

        raise QTeaLeavesError(f"num_tensor_rule={num_tensor_rule} not available.")

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

        logger_warning(
            "DeprecationWarning: The machine learning methods in qtealeaves classes are deprecated."
            + " For machine learning tasks, please utilize the qchaitea classes instead."
        )

        pos_links = self.get_pos_links(pos)

        tensor = self[self.iso_center]
        eff_op_0 = self.eff_op[(pos_links[0], pos)].tensor
        eff_op_1 = self.eff_op[(pos_links[1], pos)].tensor
        eff_op_2 = self.eff_op[(pos_links[2], pos)].tensor

        has_label_link = self[self.iso_center].ndim == 4
        my_abs, real, my_sum = tensor.get_attr("abs", "real", "sum")

        if has_label_link:
            estr_labels = "abdc,xmayi,ynbzi,zlcxi->di"
        else:
            estr_labels = "abc,xmayi,ynbzi,zlcxi->mi"

        labels = tensor.einsum(
            estr_labels,
            eff_op_0,
            eff_op_1,
            eff_op_2,
        )

        grad = eff_op_0.conj().einsum(
            "xmayi,ynbzi,zlcxi->abci",
            eff_op_1,
            eff_op_2.conj(),
        )

        if self.tn_ml_mode in ["linkfree", "linkfree_isofree"]:
            dtype = self[self.iso_center].dtype
            device = self[self.iso_center].device

            # pylint: disable-next=protected-access
            true_labels = self.eff_op._current_labels
            dim = np.prod(labels.shape)
            labels = labels.reshape([dim])
            diff = true_labels - labels

            dim = np.prod(diff.shape)
            diff = diff.reshape([dim])  # must be dim=1
            grad = grad.einsum("abci,i->abci", diff)

            grad = grad.from_elem_array(
                my_sum(grad.elem, axis=3), dtype=dtype, device=device
            )

            diff = diff.elem**2
        elif self.tn_ml_mode in ["labellink"]:
            # pylint: disable-next=protected-access
            true_labels = self.eff_op._current_labels
            test_idx = np.arange(true_labels.shape[0], dtype=int)

            if true_labels.has_symmetry:
                # Access to elem in the next step would fail for symmetric tensors
                raise ValueError("How can labels be a symmetric tensor?")

            dtype_int = true_labels.dtype_from_char("I")
            axis0_idx = true_labels.copy().convert(dtype=dtype_int).elem

            labels.elem[axis0_idx, test_idx] -= 1
            diff = -1 * labels

            grad = grad.einsum("abci,xi->abxc", diff)
            diff = my_sum(my_abs(diff.elem**2), axis=0)
        else:
            raise QTeaLeavesError(f"Got {self.tn_ml_mode=}, which is invalid here.")

        # Calculate loss and move to CPU / host
        loss = my_sum(my_abs(real(diff)))
        loss = self[pos].get_of(loss)

        # normalize loss
        loss /= true_labels.shape[0]
        grad /= true_labels.shape[0]

        return grad, loss

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

        logger_warning(
            "DeprecationWarning: The machine learning methods in qtealeaves classes are deprecated."
            + " For machine learning tasks, please utilize the qchaitea classes instead."
        )

        if pos_p is None:
            pos_p, _, _ = self.get_pos_partner_link_expansion(pos)
        if pos_p < pos:
            raise QTeaLeavesError("Case not covered. Open a ticket.")

        my_abs, real, my_sum = self[self.iso_center].get_attr("abs", "real", "sum")
        if self.extension == "mps":
            self.iso_towards(pos, keep_singvals=True, trunc=True)
        else:
            self.site_canonize(pos, True)

        num_sites = self.num_sites
        dtype = self[self.iso_center].dtype
        device = self[self.iso_center].device

        # Indices / positions of left, partner, and right of partner
        pos_l = pos - 1 if pos > 0 else None
        pos_p = pos + 1
        pos_r = pos + 2 if pos + 2 < num_sites else None

        eff_op_l = self.eff_op[(pos_l, pos)].tensor
        eff_op_i = self.eff_op[(-pos - 2, pos)].tensor
        eff_op_p = self.eff_op[(-pos_p - 2, pos_p)].tensor
        eff_op_r = self.eff_op[(pos_r, pos_p)].tensor

        tens_i = self[pos]
        tens_p = self[pos + 1]

        if tens_i.ndim == 4:
            # Remove b, must be one dimensional if label-link in TN
            estr = "abcde,cfxg,dhfie,gjk,iljme,mnkae->hlnxe"
        elif tens_p.ndim == 4:
            # Remove b, must be one dimensional if label-link in TN
            estr = "abcde,cfg,dhfie,gjxk,iljme,mnkae->hlnxe"
        else:
            estr = "abcde,cfg,dhfie,gjk,iljme,mnkae->bhlne"

        labels = eff_op_l.einsum(
            estr,
            tens_i,
            eff_op_i.conj(),
            tens_p,
            eff_op_p.conj(),
            eff_op_r,
        )
        labels.fuse_links_update(0, 3)

        grad = eff_op_l.conj().einsum(
            "abcde,dfghe,hklme,mnoae->cgloe",
            eff_op_i,
            eff_op_p,
            eff_op_r.conj(),
        )

        # pylint: disable-next=protected-access
        if labels.shape[0] == 1:
            # pylint: disable-next=protected-access
            true_labels = self.eff_op._current_labels
            dim = np.prod(labels.shape)
            labels = labels.reshape([dim])
            diff = true_labels - labels

            dim = np.prod(diff.shape)
            diff = diff.reshape([dim])  # must be dim=1
            grad = grad.einsum("abcdi,i->abcdi", diff)

            grad = grad.from_elem_array(
                my_sum(grad.elem, axis=4), dtype=dtype, device=device
            )

            diff = diff.elem**2

        else:
            # pylint: disable-next=protected-access
            true_labels = self.eff_op._current_labels
            test_idx = np.arange(true_labels.shape[0], dtype=int)

            if true_labels.has_symmetry:
                # Access to elem in the next step would fail for symmetric tensors
                raise ValueError("How can labels be a symmetric tensor?")

            dtype_int = true_labels.dtype_from_char("I")
            axis0_idx = true_labels.copy().convert(dtype=dtype_int).elem

            labels.elem[axis0_idx, test_idx] -= 1
            diff = -1 * labels

            grad = grad.einsum("abcdi,xi->abxcd", diff)
            diff = my_sum(my_abs(diff.elem**2), axis=0)

        # Calculate loss and move to CPU / host
        loss = my_sum(my_abs(real(diff)))
        loss = self[pos].get_of(loss)

        # normalize loss
        loss /= true_labels.shape[0]
        grad /= true_labels.shape[0]

        return grad, loss

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

        logger_warning(
            "DeprecationWarning: The machine learning methods in qtealeaves classes are deprecated."
            + " For machine learning tasks, please utilize the qchaitea classes instead."
        )

        pos_p, _, _ = self.get_pos_partner_link_expansion(pos)

        i1 = min(pos, pos_p)
        i2 = max(pos, pos_p)
        self.iso_towards(i1)

        pos_links1 = self.get_pos_links(i1)
        pos_links2 = self.get_pos_links(i2)

        tensor1 = self[i1]
        tensor2 = self[i2]
        eff_op_0 = self.eff_op[(pos_links1[0], i1)].tensor
        eff_op_1 = self.eff_op[(pos_links1[1], i1)].tensor
        eff_op_2 = self.eff_op[(pos_links2[1], i2)].tensor
        eff_op_3 = self.eff_op[(pos_links2[2], i2)].tensor

        tensor1.elem.requires_grad_(True)
        tensor2.elem.requires_grad_(True)

        optim, nn = tensor1.get_attr("optim", "nn")
        optimizer = optim.AdamW([tensor1.elem, tensor2.elem])  # *args, **kwargs)
        gradient_clipper = nn.utils.clip_grad_value_

        # pylint: disable-next=protected-access
        true_labels = self.eff_op._current_labels
        test_idx = np.arange(true_labels.shape[0], dtype=int)

        has_label_link_1 = tensor1.ndim == 4
        has_label_link_2 = tensor2.ndim == 4
        has_label_link = has_label_link_1 or has_label_link_2

        if not has_label_link:
            estr_labels = "abc,cde,wkaxi,xlbyi,ymdzi,znewi->klmni"
        elif has_label_link_1:
            # t is target link
            estr_labels = "abtc,cde,wkaxi,xlbyi,ymdzi,znewi->klmnti"
        elif has_label_link_2:
            # t is target link
            estr_labels = "abc,cdte,wkaxi,xlbyi,ymdzi,znewi->klmnti"
        else:
            raise QTeaLeavesError("Undefined TN-ML case for einsum.")

        # else not required with replace("t", "") as not t in einsum_str
        if has_label_link:
            estr_labels = estr_labels.replace("klmn", "")

        # Actually do the iteration
        for _ in range(num_grad_steps):

            # Call the optimization function:
            loss = self._cost_func_two_tensor(
                tensor1,
                tensor2,
                eff_op_0,
                eff_op_1,
                eff_op_2,
                eff_op_3,
                estr_labels,
                true_labels,
                test_idx,
                self.tn_ml_mode,
            )

            optimizer.zero_grad()
            loss.backward(retain_graph=False)

            # If the gradients are too large, this clips their value.
            gradient_clipper([tensor1.elem, tensor2.elem], 1e10)

            # iterate the optimizer
            optimizer.step()

        # turn of the requires_grad() and detach
        tensor1.elem.requires_grad_(False)
        tensor1 = tensor1.from_elem_array(tensor1.elem.detach().clone())
        tensor2.elem.requires_grad_(False)
        tensor2 = tensor2.from_elem_array(tensor2.elem.detach().clone())

        self[i1] = tensor1
        self[i2] = tensor2

        loss = tensor1.get_of(loss)
        loss = loss.detach().clone()

        return loss

    def ml_environment_two_tensors(self, pos, pos_p: None):
        """
        Calculate the tensor environment for the two tensors at position pos
        and pos_p:
                                    |
                                    |
            ---(   )---        ---(pos)------(pos_p)---       ---(   )---
                |                  |           |                  |
                |                                                 |
                |                                                 |
                |                  |           |                  |
                - - - - - - - ---(   )-------(   )--- - - - - - - -
                                    ENVIRONMENT

        Parameters
        ----------
        pos : int
            Index of the 1st tensor in the "two tensor" notation

        pos_p : int | None
            Index of partner tensor. If `None`, partner
            tensor will be queried.

        Returns
        -------
        environment : :class:`_AbstractQteaTensor`
            Environment for the tensor nodes at position pos and pos_p.

        """
        if pos_p is None:
            pos_p, _, _ = self.get_pos_partner_link_expansion(pos)
        if pos_p < pos:
            raise QTeaLeavesError("Case not covered. Open a ticket.")

        # my_abs, real, my_sum = self[self.iso_center].get_attr("abs", "real", "sum")
        if self.extension == "mps":
            self.iso_towards(pos, keep_singvals=True, trunc=True)
        else:
            self.site_canonize(pos, True)

        num_sites = self.num_sites

        # Indices / positions of left, partner, and right of partner
        pos_l = pos - 1 if pos > 0 else None
        pos_p = pos + 1
        pos_r = pos + 2 if pos + 2 < num_sites else None

        eff_op_l = self.eff_op[(pos_l, pos)].tensor
        eff_op_i = self.eff_op[(-pos - 2, pos)].tensor
        eff_op_p = self.eff_op[(-pos_p - 2, pos_p)].tensor
        eff_op_r = self.eff_op[(pos_r, pos_p)].tensor

        # Environment/Gradient of MPS
        environment = eff_op_l.conj().einsum(
            "abcde,dfghe,hklme,mnoae->cgloe",
            eff_op_i,
            eff_op_p,
            eff_op_r.conj(),
        )

        return environment

    def ml_decision_function_two_tensors(self, two_tensors, environment):
        """
        Calculate the decision function from a input tensor named "twotensors" that
        consists in the contraction of 2 neighbor nodes of the MPS at a certain position:
                                     |
                                     |
             ---(   )---        ---(pos)------(pos_p)---       ---(   )---
                  |                  |           |                  |
                  |                   TWO TENSORS                   |
                  |                                                 |       ENVIRONMENT
                  |                  |           |                  |
                  - - - - - - - ---(   )-------(   )--- - - - - - - -

        Parameters
        ----------
        two_tensors : py:class:`_AbstractQteaTensor`
                Tensor used to get the decision function. It stands for the contraction of
                two neighbor nodes.
        environment : :class:`_AbstractQteaTensor`
            Environment for the 'two tensors contraction'.
        Returns
        -------
        decision_function : :class:`_AbstractQteaTensor`
            Contraction of two_tensors and environment.

        """
        # Non-trivial-label case
        if two_tensors.ndim == 5:
            estr = "abxcd,abcdl->xl"
        # Trivial-label case
        elif two_tensors.ndim == 4:
            # Remove b, must be one dimensional if label-link in TN
            estr = "abcd,abcdl->l"
        else:
            raise QTeaLeavesError("Not expected shape. Something wrong here")

        # Decision function array
        decision_function = two_tensors.einsum(estr, environment)

        return decision_function

    def ml_gradient_of_cost_function_two_tensors(self, two_tensors, environment):
        """
        Get the gradient w.r.t. a given tensor named "twotensors"
        knowing its environment, following the procedure
        explained in https://arxiv.org/pdf/1605.05775.pdf for the
        data_sample given.

                                    |
                                    |
            ---(   )---        ---(pos)------(pos_p)---       ---(   )---
                |                  |           |                  |
                |                   TWO TENSORS                   |
                |                                                 |       ENVIRONMENT
                |                  |           |                  |
                - - - - - - - ---(   )-------(   )--- - - - - - - -

        Parameters
        ----------
        two_tensors : py:class:`_AbstractQteaTensor`
                Tensor used to get the decision function. It stands for the contraction of
                two neighbor nodes.
        environment : :class:`_AbstractQteaTensor`
            Environment for the 'two tensors contraction'.

        Returns
        -------
        tgrad : :class:`_AbstractQteaTensor`
            update/variation/gradient w.r.t. "twotensors".

        loss : float
            The loss function.

        """
        my_abs, real, my_sum = self[self.iso_center].get_attr("abs", "real", "sum")
        dtype = self[self.iso_center].dtype
        device = self[self.iso_center].device

        # Decision function array
        prediction = self.ml_decision_function_two_tensors(two_tensors, environment)

        # pylint: disable-next=protected-access
        if prediction.ndim == 1:
            # pylint: disable-next=protected-access
            true_labels = self.eff_op._current_labels
            diff = true_labels - prediction
            tgrad = environment.einsum("abcdi,i->abcdi", diff)

            tgrad = tgrad.from_elem_array(
                my_sum(tgrad.elem, axis=4), dtype=dtype, device=device
            )

            diff = diff.elem**2

        else:
            # pylint: disable-next=protected-access
            true_labels = self.eff_op._current_labels
            test_idx = np.arange(true_labels.shape[0], dtype=int)

            if true_labels.has_symmetry:
                # Access to elem in the next step would fail for symmetric tensors
                raise ValueError("How can labels be a symmetric tensor?")

            dtype_int = true_labels.dtype_from_char("I")
            axis0_idx = true_labels.copy().convert(dtype=dtype_int).elem

            prediction.elem[axis0_idx, test_idx] -= 1
            diff = -1 * prediction

            tgrad = environment.einsum("abcdi,xi->abxcd", diff)
            diff = my_sum(my_abs(diff.elem**2), axis=0)
        # Calculate loss and move to CPU / host
        loss = my_sum(my_abs(real(diff)))
        loss = prediction.get_of(loss)

        # normalize loss
        loss /= true_labels.shape[0]
        tgrad /= true_labels.shape[0]

        return tgrad, loss

    def ml_update_conjugate_gradient_two_tensors(self, pos, pos_p=None):
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
        opt_two_tensors : :class:`_AbstractQteaTensor`
            Optimized tensor through gradient descent algorithm

        loss : float
            The loss function.

        """
        # Initial Check (copied from ml_get_gradient_two_tensors)
        if pos_p is None:
            pos_p, _, _ = self.get_pos_partner_link_expansion(pos)
        if pos_p < pos:
            raise QTeaLeavesError("Case not covered. Open a ticket.")

        if self.extension == "mps":
            self.iso_towards(pos, keep_singvals=True, trunc=True)
        else:
            self.site_canonize(pos, True)

        # Two tensors and temporary two tensors.
        if self[pos].ndim == 4:
            estr_twotn = "abxc,cde->abxde"
        elif self[pos + 1].ndim == 4:
            estr_twotn = "abc,cdxe->abxed"
        else:
            estr_twotn = "abc,cde->abde"

        if self[pos_p].ndim == 4:
            # Partner position in MPS and TTO should always be rank-3 now
            raise QTeaLeavesError("Label link should now always be on `pos`.")

        two_tensors = self[pos].einsum(estr_twotn, self[pos + 1])
        opt_two_tensors = two_tensors.copy()
        # pylint: disable-next=protected-access
        batch_size = self.eff_op._current_labels.shape[0]

        # Environment
        environment = self.ml_environment_two_tensors(pos, pos_p)

        # 1st iteration conjugate gradient descent:
        gradient, _ = self.ml_gradient_of_cost_function_two_tensors(
            two_tensors, environment
        )

        # need a way to track loss during multiple steps of conjugate.
        rr, pp = gradient.copy(), gradient.copy()
        kk = 0
        auto_learning_rate = 1

        # Hardcoded for the moment:
        steps = 5  # SHOULD BE AN INPUT PARAMETER FOR THE USER

        # einsum string for pap
        if two_tensors.ndim == 5:
            estr_pap = "abcdl,abxcd,efxgh,efghm->lm"
        elif two_tensors.ndim == 4:
            estr_pap = "abcdl,abcd,efgh,efghm->lm"
        else:
            raise QTeaLeavesError(
                f"'two tensors' has an unexpected rank: {two_tensors.ndim}"
            )

        for kk in range(steps):
            # pAp conjugate tensor
            pap_matrix = environment.conj().einsum(
                estr_pap, pp, pp.conj(), environment
            )  # Check this einsum
            pap = pap_matrix.trace()

            # Boundaries on pap value
            type_pap = str(pap.dtype).rsplit(".", maxsplit=1)[-1]
            min_val, max_val = np.finfo(type_pap).tiny, np.finfo(type_pap).max

            if pap < min_val:
                logger_warning(
                    "Unexpectedly low value encountered during"
                    + " auto-learning rate calculation."
                )
            elif pap > max_val:
                logger_warning(
                    "Unexpectedly high value encountered during"
                    + " auto-learning rate calculation."
                )

            pap = max(min_val, min(pap, max_val))

            auto_learning_rate = (rr.norm() ** 2) / pap
            # update two_tensors
            opt_two_tensors = opt_two_tensors + pp * auto_learning_rate * batch_size
            # Compute new gradient and cost function
            nr, loss = self.ml_gradient_of_cost_function_two_tensors(
                opt_two_tensors, environment
            )

            # Note: add a way to collect losses during different conj. grad. steps
            # Now loss is only saved for last step on 1 node optimization.

            if kk < steps - 1:
                beta = (nr.norm() / rr.norm()) ** 2
                # pylint: disable-next=protected-access
                rr._elem = nr.elem
                # pylint: disable-next=protected-access
                pp._elem = rr.elem - pp.elem * beta
        return opt_two_tensors, loss

    # --------------------------------------------------------------------------
    #                              Internal functions
    # --------------------------------------------------------------------------

    def _add(self, other, stack_first=False):
        """
        Add two MPS states in a "non-physical" way. Notice that this function
        is highly inefficient if the number of sites is very high.
        For example, adding |00> to |11> will result in |00>+|11> not normalized.
        Remember to take care of the normalization yourself.

        Parameters
        ----------
        other : MPS
            MPS to concatenate
        stack_first : bool, optional
            If False, MPS will have bond dimension 1 (or incoming of both MPS)
            on the left boundary. If True, bond dimension on the left boundary
            is the sum of the two bond dimensions.
            Default to False

        Returns
        -------
        MPS
            Summation of the first MPS with the second

        Details
        -------

        Mixed device: the algorithm selects the device depending on the
        device of `self` for each site. The resulting MPS has all the
        tensors on the memory device as it uses `from_tensor_list` with
        the tensor backend of `self` and does not install an isometry
        center.
        """
        if not isinstance(other, MPS):
            raise TypeError("Only two MPS classes can be summed")
        if self.num_sites != other.num_sites:
            raise ValueError("Number of sites must be the same to concatenate MPS")
        if np.any(self.local_dim != other.local_dim):
            raise ValueError("Local dimension must be the same to concatenate MPS")

        max_bond_dim = max(
            self.convergence_parameters.max_bond_dimension,
            other.convergence_parameters.max_bond_dimension,
        )
        cut_ratio = min(
            self.convergence_parameters.cut_ratio,
            other.convergence_parameters.cut_ratio,
        )
        convergence_params = TNConvergenceParameters(
            max_bond_dimension=int(max_bond_dim), cut_ratio=cut_ratio
        )

        tensor_list = []
        idx = 0
        for tens_a, tens_b in zip(self, other):
            shape_c = np.array(tens_a.shape) + np.array(tens_b.shape)
            shape_c[1] = tens_a.shape[1]

            is_first = idx == 0
            is_last = idx == self.num_sites - 1

            # Can be on any device right now, we have to resolve the device
            if tens_a.device == tens_b.device:
                tens_b_device_of_a = tens_b
            else:
                tens_b_device_of_a = tens_b.copy().convert(device=tens_a.device)

            if (
                is_first
                and [tens_a.shape[0], tens_b.shape[0]] == [1, 1]
                and (not stack_first)
            ):
                tens_c = tens_a.stack_link(tens_b_device_of_a, 2)
            elif is_last and [tens_a.shape[2], tens_b.shape[2]] == [1, 1]:
                tens_c = tens_a.stack_link(tens_b_device_of_a, 0)
            else:
                tens_c = tens_a.stack_first_and_last_link(tens_b_device_of_a)

            tensor_list.append(tens_c)
            idx += 1

        add_mps = MPS.from_tensor_list(
            tensor_list,
            conv_params=convergence_params,
            tensor_backend=self._tensor_backend,
        )

        return add_mps

    #########################################################################
    ########################  Summing and projecting ########################
    #########################################################################

    @classmethod
    def sum_approximate(
        cls,
        sum_states,
        sum_amplitudes=None,
        convergence_parameters=None,
        initial_state=None,
        max_iterations=10,
        dif_goal=None,
        normalize_result=True,
    ):
        """
        Computes the optimal MPS representation of the sum a_i psi_i
        for a set of MPS psi_i and ampltudes a_i.
        Uses the MPSProjectors to optimize the sum.

        **Arguments**
        sum_states : list[MPS]
            List of MPSs to sum.
        sum_amplitudes : list[float] | np.ndarray[float] | None
            List of amplitudes for each summand. If None, all are set to 1.
        convergence_parameters : :py:class:`TNConvergenceParameters`
            The convergence parameters for the resulting state.
            If None, a default convergence parameters object is created.
        initial_state : :py:class:`MPS` | None
            The initial state for the optimization. If None will start with a random state.
        max_iterations : int
            The maximal number of iterations to optimize the sum.
        dif_goal : float
            The convergence is gauged by computing |<psi|psi_i> - a_i|. We stop if this is
            smaller than dif_goal for all i. Default to machine precision.
        normalize_result : bool
            Whether to normalize the result.

        **Returns**
        :py:class:`MPS` : A MPS approximation of the sum.
        """
        if dif_goal is None:
            dif_goal = max(state[0].dtype_eps for state in sum_states)

        if sum_amplitudes is None:
            sum_amplitudes = np.ones(len(sum_states), dtype=np.float64)
        elif not isinstance(sum_amplitudes, np.ndarray):
            sum_amplitudes = np.array(sum_amplitudes)

        if len(sum_states) != len(sum_amplitudes):
            raise QTeaLeavesError(
                f"Got lists of {len(sum_states)} states and {len(sum_amplitudes)} amplitudes."
                + "Should be of equal length."
            )

        if normalize_result:
            # Just normalize the amplitudes here for stability.
            # The sum_states are not necessarily orthogonal, so
            # this should be done by computing all overlaps.
            amp_norm = 0.0

            for ii, psi_ii in enumerate(sum_states):
                amp_ii = sum_amplitudes[ii]
                for jj, psi_jj in enumerate(sum_states):
                    amp_jj = sum_amplitudes[jj]

                    amp_norm += np.conj(amp_ii) * amp_jj * psi_ii.dot(psi_jj)
            sum_amplitudes = sum_amplitudes / np.sqrt(amp_norm)

        if convergence_parameters is None:
            convergence_parameters = TNConvergenceParameters()

        # read stuff from the sum_states
        num_sites = sum_states[0].num_sites
        local_dim = sum_states[0].local_dim
        # pylint: disable-next=protected-access
        requires_singvals = sum_states[0]._requires_singvals
        tensor_backend = sum_states[0].tensor_backend

        # initialize a random MPS state
        if initial_state is None:
            initial_state = cls(
                num_sites=num_sites,
                convergence_parameters=convergence_parameters,
                local_dim=local_dim,
                requires_singvals=requires_singvals,
                tensor_backend=tensor_backend,
                initialize="random",
            )

        # initialize the effective projectors
        for psi_ii in sum_states:
            projector_ii = MPSProjector(psi0=psi_ii)
            projector_ii.setup_as_eff_ops(initial_state)
            initial_state.eff_proj.append(projector_ii)
        result = initial_state

        # loop to iterate
        for ii in range(max_iterations):

            #### optimize the sum ####
            for pos in range(result.num_sites):

                result.iso_towards(pos)
                pos_links = result.get_pos_links(pos)

                local_projectors = [
                    projector.contract_to_projector(
                        tensor=None, pos=pos, pos_links=pos_links
                    )
                    for projector in result.eff_proj
                ]

                # Compute the sum of the projectors
                sum_tensor = local_projectors[0] * sum_amplitudes[0]

                for prefactor, local_projector in zip(
                    sum_amplitudes[1:], local_projectors[1:]
                ):
                    sum_tensor.add_update(other=local_projector, factor_other=prefactor)
                result[pos] = sum_tensor
            ############################

            if normalize_result:
                result.normalize()

            # Figure out if how good the sum is:
            # Compute a list of |<psi|psi_i> - a_i|. These should be small.
            overlaps_diff = [
                abs(sum_states[ii].dot(result) - sum_amplitudes[ii])
                for ii in range(len(sum_amplitudes))
            ]
            # We can stop when all differences are smaller than the dif_goal.
            if all(dif < dif_goal for dif in overlaps_diff):
                break

        # remove the projectors
        result.eff_proj = []

        logger.info(
            "Returning after %i iterations with the maximal dif: %d and norm %d.",
            ii,
            max(overlaps_diff),
            result.norm(),
        )
        return result

    #########################################################################
    ######################## Visualisation methods ##########################
    #########################################################################

    def plot(
        self,
        fig,
        axis,
        link_quantity=None,
        plot_tensors=False,
        noticks=True,
        colormap="jet",
        cmap_label=None,
    ):
        """
        Plot the MPS in a matplotlib figure on a specific axis. The plot is an MPS,
        with links and tensors. The physical links are not represented.
        The color of the links is encoding the link_quantity value.
        For example, if the link quantity is the entanglement,
        the color of the link will encode the entanglement of that link.
        You can pass some quantity that will be represented as a colorcode on the link.

        TODO: add color code for quantities for the tensors too.

        Parameters
        ----------
        fig : matplotlib Figure
            The figure where to plot
        axis : matplotlib axis
            The axis where to plot
        link_quantity : np.ndarray, optional
            Colorcode of the link through np.ndarray of double, by default None.
            If None, black is used
        plot_tensors : bool, optional
            If True, plot tensors as white dots with black edge, by default False
        noticks : bool, optional
            If True, remove the ticks from the axis, by default True
        colormap : str, optional
            Colormap to use, by default "jet"
        cmap_label: str, optional
            Label of the colormap, by default None.

        Returns
        -------
        None
            Acts in place on the figure/axis
        """
        # Colors for the links
        cmap = plt.get_cmap(colormap)
        if link_quantity is not None:
            cnorm = colors.Normalize(vmin=link_quantity.min(), vmax=link_quantity.max())
            scalarmap = cmx.ScalarMappable(norm=cnorm, cmap=cmap)
            cols = [scalarmap.to_rgba(val) for val in link_quantity]
        else:
            cols = ["black"] * link_quantity

        # Generate the segments of the MPS
        segs = [[[i, 0], [i + 1, 0]] for i in range(self.num_sites - 1)]
        # Plot lines
        line_segments = LineCollection(
            segs, linewidths=2, colors=cols, linestyle="solid"
        )
        axis.add_collection(line_segments)

        # Generate and plot points (tensors)
        if plot_tensors:
            x_coord = list(range(self.num_sites))
            y_coord = [0] * self.num_sites
            axis.scatter(x_coord, y_coord, c="white", edgecolors="black")
            axis.set_xlim(-1, self.num_sites)
            axis.set_ylim(1, -1)

        # Add colorbar to the figure
        if link_quantity is not None:
            fig.colorbar(scalarmap, ax=axis, label=cmap_label)

        if noticks:
            axis.tick_params(
                axis="both",  # changes apply to the x-axis
                which="both",  # both major and minor ticks are affected
                bottom=False,  # ticks along the bottom edge are off
                top=False,  # ticks along the top edge are off
                labelbottom=False,
                left=False,
                labelleft=False,
            )  # labels along the bottom edge are off
