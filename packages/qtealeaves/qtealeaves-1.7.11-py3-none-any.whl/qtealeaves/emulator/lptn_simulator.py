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
This module contains a light-weight LPTN emulator.
"""

# pylint: disable=protected-access
# pylint: disable=too-many-lines
# pylint: disable=too-many-branches
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-statements

import logging

import numpy as np
import numpy.linalg as nla

from qtealeaves.abstracttns.abstract_matrix_tn import _AbstractMatrixTN
from qtealeaves.abstracttns.abstract_tn import _projector_for_rho_i
from qtealeaves.emulator.mps_simulator import MPS
from qtealeaves.tensors.abstracttensor import _AbstractQteaTensor
from qtealeaves.tooling import QTeaLeavesError

__all__ = ["LPTN"]

logger = logging.getLogger(__name__)


class LPTN(_AbstractMatrixTN):
    """
    LOCALLY PURIFIED TENSOR NETWORK CLASS - operator
    order of legs: 0 - left bond, 1 - lower (physical) leg,
    2 - upper leg, 3 - right bond


    Parameters
    ----------
    num_sites : int
        Number of sites
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

    local_dim : int, optional
        Dimension of Hilbert space of single site
        (defined as the same for each site).
        Default is 2
    tensor_backend : `None` or instance of :class:`TensorBackend`
        Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.
    initialize : str
        How to initialize the LPTN. Options are 'vacuum' or 'pure_random'.
        Default to 'vacuum'.
    iso_center : None or list of two ints, optional
        Isometry center is between the two sites
        specified in a list. The counting starts at 1.
        If the LPTN has no
        isometry center, iso_center = None.
        Default is None
    initialize : str, optional
        Available options are `vacuum`, `pure_random` (pure state, but random),
        and `infinite_t`.
        Default to `vacuum`

    Initialization
    --------------

    |000...000><000---000|

    Tensor representation
    ---------------------

    .. code-block::

      |   |   |   |   |
    --O---O---O---O---O--  } --> complex conjugates of tensors below,
      |   |   |   |   |          access with LPTN.cc_tensors
    --O---O---O---O---O--  } --> these are contained in LPTN.tensors
      |   |   |   |   |


    Attributes
    ----------
    LPTN.num_sites : int
        Number of sites
    LPTN.local_dim : int
        Local Hilbert space dimension
    LPTN.tensors : list
        Values of tensors in LPTN
    LPTN.cc_tensors : list
        Values of tensors in complex conjugate part of
        LPTN
    LPTN._max_bond_dim : int
        Maximal bond dimension
    LPTN._cut_ratio : float
        Cut ratio
    LPTN.iso_center : None or list of int, optional
        Isometry center is between the two sites
        specified in a list. The counting starts at 1.
        If the LPTN has no
        isometry center, iso_center = None.
    """

    extension = "lptn"

    def __init__(
        self,
        num_sites,
        conv_params,
        local_dim=2,
        tensor_backend=None,
        iso_center=None,
        initialize="vacuum",
        **kwargs,
    ):
        sectors = kwargs.get("sectors", None)
        requires_singvals = kwargs.get("requires_singvals", False)

        super().__init__(
            num_sites,
            conv_params,
            local_dim=local_dim,
            tensor_backend=tensor_backend,
            requires_singvals=requires_singvals,
        )

        # initialize tensors as |00...0>
        tensor_backend = self._tensor_backend
        self._singvals = [None] * (self.num_sites + 1)
        self._initialize_lptn(initialize, sectors)
        self.num_links = 3 * self.num_sites + 2
        self.eff_op = None

        if isinstance(iso_center, (np.ndarray, list)):
            if not all(isinstance(element, int) for element in iso_center) or (
                len(iso_center) != 2
            ):
                raise TypeError(
                    "iso_center must be None or list of two"
                    " ints, not list of "
                    f"{len(iso_center)} "
                    f"{type(iso_center[0])}."
                )
            self._iso_center = iso_center
            logger.warning(
                "The set iso_center does not correspond to the actual "
                + "iso center of the initialized LPTN."
            )
        elif iso_center is not None:
            raise TypeError(
                f"iso_center must be None or list of two ints, not {type(iso_center)}."
            )

        # LPTN initializetion not aware of device or data type
        self.convert(self._tensor_backend.dtype, self._tensor_backend.memory_device)

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
    def cc_tensors(self):
        """
        complex conjugate part of LPTN, returns complex conjugate tensors
        """
        c_conj = [elem.conj() for elem in self.tensors]
        return c_conj

    @property
    def tensors(self):
        """List of MPS tensors"""
        return self._tensors

    # --------------------------------------------------------------------------
    #                          Overwritten operators
    # --------------------------------------------------------------------------

    def __getitem__(self, key):
        """You can access tensors in the LPTN using

        .. code-block::
            LPTN[0]
            >>> tensor for a site at position 0

        Parameters
        ----------
        key : int
            index (=site) of the LPTN you are interested in

        Return
        ------
        np.ndarray
            Tensor at position key in the LPTN.tensor array
        """
        return self.tensors[key]

    def __setitem__(self, key, value):
        """
        Modify a tensor in the LPTN by using a syntax corresponding
        to lists.

        .. code-block::
            tens = np.ones( (1, 2, 1) )
            LPTN[1] = tens

        Parameters
        ----------
        key : int
            index of the array
        value : np.array
            value of the new tensor

        Return
        ------
        None
        """
        if not isinstance(value, _AbstractQteaTensor):
            raise TypeError(
                "New tensor must be a _AbstracQteaTensor, not {type(value)}"
            )
        self._tensors[key] = value

        return None

    def __iter__(self):
        """
        Iterator through the LPTN

        Return
        ------
        QteaTensor
            Tensor at position key in the LPTN.tensor array
        """
        yield from self.tensors

    # --------------------------------------------------------------------------
    #                       classmethod, classmethod like
    # --------------------------------------------------------------------------

    @classmethod
    def from_statevector(
        cls, statevector, local_dim=2, conv_params=None, tensor_backend=None
    ):
        """Decompose statevector to tensor network."""
        psi = MPS.from_statevector(
            statevector,
            local_dim=local_dim,
            conv_params=conv_params,
            tensor_backend=tensor_backend,
        )
        lptn = cls.from_tensor_list_mps(
            psi.to_tensor_list(), conv_params=psi.convergence_parameters
        )
        lptn.iso_center = (lptn.num_sites - 1, lptn.num_sites + 1)

        return lptn

    @classmethod
    def from_tensor_list_mps(cls, tensor_list, conv_params=None, iso_center=None):
        """
        Initialize the LPTN tensors using a list of MPS
        shaped tensors. A dummy leg is added and then the function
        from_tensor_list is called.

        Parameters
        ----------
        tensor_list : list of ndarrays
            List of tensors for initializing the LPTN
        conv_params : :py:class:`TNConvergenceParameters`, optional
            Input for handling convergence parameters.
            In particular, in the LPTN simulator we
            are interested in:
            - the maximum bond dimension (`max_bond_dimension`)
            - the cut ratio (`cut_ratio`) after which the
            singular values in SVD are neglected, all
            singular values such that :math:`\\lambda` /
            :math:`\\lambda_max` <= :math:`\\epsilon` are truncated
        iso_center : None or list of int, optional
            Isometry center is between the two sites
            specified in a list. If the LPTN has no
            isometry center, iso_center = None.
            Default is None

        Return
        ------
        obj : :py:class:`LPTN`
            The LPTN class composed of the given tensors
        --------------------------------------------------------------------
        """
        if iso_center is not None:
            if len(iso_center) != 2:
                raise ValueError(
                    "Iso-center for LPTN has to be of length two (f90-index)."
                )

        # reshape to rank 4
        new_tensor_list = []
        for tens in tensor_list:
            new_tensor_list.append(
                tens.reshape((tens.shape[0], tens.shape[1], 1, tens.shape[2]))
            )

        obj = cls.from_tensor_list(
            tensor_list=new_tensor_list, conv_params=conv_params, iso_center=iso_center
        )

        # Ensure we have _AbstractQteaTensors from here on
        for ii, elem in enumerate(obj.tensors):
            if not isinstance(elem, _AbstractQteaTensor):
                obj.tensors[ii] = obj._tensor_backend.tensor_cls.from_elem_array(elem)

        obj.convert(obj._tensor_backend.dtype, obj._tensor_backend.device)
        return obj

    @classmethod
    def from_mps(cls, mps, conv_params=None, **kwargs):
        """Converts MPS to LPTN.

        Parameters
        ----------
        mps: :py:class:`MPS`
            object to convert to LPTN.
        conv_params: :py:class:`TNConvergenceParameters`, optional
            Input for handling convergence parameters.
            If None, the algorithm will try to
            extract conv_params from mps.convergence_parameters.
            Default to `None`.
        kwargs : additional keyword arguments
            They are accepted, but not passed to calls in this function.

        Return
        ------

        lptn: :py:class:`LPTN`
            Decomposition of mps.
        """
        cls.assert_extension(mps, "mps")
        if conv_params is None:
            conv_params = mps.convergence_parameters
        lptn = cls.from_tensor_list_mps(
            mps.copy().to_tensor_list(), conv_params=conv_params
        )
        lptn.iso_center = (lptn.num_sites - 1, lptn.num_sites + 1)
        return lptn

    @classmethod
    def from_lptn(cls, lptn, conv_params=None, **kwargs):
        """Converts LPTN to LPTN.

        Parameters
        ----------
        lptn: :py:class:`LPTN`
            object to convert to LPTN.
        conv_params: :py:class:`TNConvergenceParameters`, optional
            Input for handling convergence parameters
            Default is None.
        kwargs : additional keyword arguments
            They are accepted, but not passed to calls in this function.

        Return
        ------

        new_lptn: :py:class:`LPTN`
            Decomposition of lptn.
        """
        cls.assert_extension(lptn, "lptn")
        new_lptn = lptn.copy()
        new_lptn.convergence_parameters = conv_params
        return new_lptn

    @classmethod
    def from_ttn(cls, ttn, conv_params=None, **kwargs):
        """Converts TTN to LPTN.

        Parameters
        ----------
        ttn: :py:class:`TTN`
            object to convert to LPTN.
        conv_params: :py:class:`TNConvergenceParameters`, optional
            Input for handling convergence parameters.
            If None, the algorithm will try to
            extract conv_params from ttn.convergence_parameters.
            Default is None.
        kwargs : additional keyword arguments
            They are accepted, but not passed to calls in this function.

        Return
        ------

        lptn: :py:class:`LPTN`
            Decomposition of ttn.
        """
        cls.assert_extension(ttn, "ttn")

        if conv_params is None:
            conv_params = ttn.convergence_parameters
        lptn = cls.from_tensor_list_mps(
            ttn.copy().to_mps_tensor_list(conv_params)[0], conv_params=conv_params
        )
        lptn.iso_center = (lptn.num_sites - 1, lptn.num_sites + 1)
        return lptn

    @classmethod
    def from_tto(cls, tto, conv_params=None, **kwargs):
        """Converts TTO to LPTN.

        Parameters
        ----------
        tto: :py:class:`TTO`
            object to convert to LPTN.
        conv_params: :py:class:`TNConvergenceParameters`
            Input for handling convergence parameters
            Default is None.
        kwargs : additional keyword arguments
            They are accepted, but not passed to calls in this function.

        Return
        ------

        lptn: :py:class:`LPTN`
            Decomposition of tto.
        """
        cls.assert_extension(tto, "tto")
        return cls.from_ttn(tto.copy().to_ttn(), conv_params)

    @classmethod
    def from_density_matrix(
        cls, rho, n_sites, dim, conv_params, tensor_backend=None, prob=False
    ):
        """
        For a given density matrix in matrix form returns LPTN form

        Parameters
        ----------
        rho : ndarray
            Density matrix
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
        tensor_backend : `None` or instance of :class:`TensorBackend`
            Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.
        prob : Boolean, optional
            If True, returns eigenvalues of initial eigenvalue
            decomposition. If everything is correct, should
            correspond to mixed state probabilities

        Return
        ------
        rho_lptn : :py:class::`LPTN`
            Density matrix in LPTN form
        (if prob==True) :
        val : 1D np.ndarray
            Eigenvalues of initial EVD
            = mixed state probabilities
        """
        return cls.dm_to_lptn(rho, n_sites, dim, conv_params, tensor_backend, prob)

    def to_ttn(self):
        """Converts LPTN to TTN"""
        mps = MPS.from_lptn(self)
        return mps.to_ttn()

    @classmethod
    def product_state_from_local_states(
        cls,
        mat,
        padding=None,
        convergence_parameters=None,
        tensor_backend=None,
    ):
        """
        Construct a product (separable) state in LPTN form, given the local
        states of each of the sites.

        Parameters
        ----------
        mat : List[np.array of rank 2]
            Matrix with ii-th row being a (normalized) local state of
            the ii-th site.
            Number of rows is therefore equal to the number of sites,
            and number of columns corresponds to the local dimension.

        padding : np.array of length 2 or `None`, optional
            Used to enable the growth of bond dimension in TDVP algorithms
            for LPTN (necessary as well for two tensor updates).
            If not `None`, all the MPS tensors are padded such that the bond
            dimension is equal to `padding[0]`. The value `padding[1]`
            tells with which value are we padding the tensors. Note that
            `padding[1]` should be very small, as it plays the role of
            numerical noise.
            If False, the bond dimensions are equal to 1.
            Default to None.

        convergence_parameters : :py:class:`TNConvergenceParameters`, optional
            Convergence parameters for the new LPTN.

        tensor_backend : `None` or instance of :class:`TensorBackend`
            Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.

        Return
        ------
        :py:class:`LPTN`
            Corresponding product state LPTN.

        """
        prod_mps = MPS.product_state_from_local_states(
            mat,
            padding=padding,
            convergence_parameters=convergence_parameters,
            tensor_backend=tensor_backend,
        )
        prod_lptn = cls.from_tensor_list_mps(
            prod_mps.to_tensor_list(), conv_params=prod_mps.convergence_parameters
        )

        return prod_lptn

    @classmethod
    def dm_to_lptn(
        cls, rho, n_sites, dim, conv_params, tensor_backend=None, prob=False
    ):
        """
        For a given density matrix in matrix form returns LPTN form

        Parameters
        ----------
        rho : ndarray
            Density matrix
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
        tensor_backend : `None` or instance of :class:`TensorBackend`
            Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.
        prob : Boolean, optional
            If True, returns eigenvalues of initial eigenvalue
            decomposition. If everything is correct, should
            correspond to mixed state probabilities

        Return
        ------
        rho_lptn : :py:class::`LPTN`
            Density matrix in LPTN form
        (if prob==True) :
        val : 1D np.ndarray
            Eigenvalues of initial EVD
            = mixed state probabilities
        """
        if not isinstance(n_sites, int):
            raise TypeError(
                "Input number of sites must be an integer, not {type(n_sites)}"
            )
        if not isinstance(dim, int):
            raise TypeError(
                "Input local Hilbert space dimension must be an integer, "
                "not {type(dim)}"
            )
        rho_lptn = cls(
            n_sites,
            local_dim=dim,
            conv_params=conv_params,
            tensor_backend=tensor_backend,
        )

        # --O--   --[EVD, no truncating]--> --O--o--O--
        val, vec = nla.eigh(rho)
        val, vec = val[::-1], vec[:, ::-1]

        # absorb the eigenvalues,    | --> dimension dim**n_sites
        # square root to each side,  O
        # and take only one side:    | --> physical legs, dimension dim**n_sites
        work = vec * np.sqrt(val)
        tensorlist = LPTN.matrix_to_tensorlist(
            work, n_sites, dim, conv_params, tensor_backend=rho_lptn._tensor_backend
        )
        # False positive for linter
        # pylint: disable-next=attribute-defined-outside-init
        rho_lptn._tensors = tensorlist
        rho_lptn._iso_center = (n_sites - 1, n_sites - 1)

        # Ensure we have _AbstractQteaTensors from here on
        tensor_cls = rho_lptn._tensor_backend.tensor_cls
        for ii, elem in enumerate(rho_lptn.tensors):
            if not isinstance(elem, _AbstractQteaTensor):
                rho_lptn[ii] = tensor_cls.from_elem_array(elem)

        rho_lptn.convert(
            rho_lptn._tensor_backend.dtype, rho_lptn._tensor_backend.device
        )

        if prob:
            return rho_lptn, val

        return rho_lptn

    @classmethod
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
        raise NotImplementedError("LPTN has no support for machine learning yet.")

    @classmethod
    def mpi_bcast(cls, state, comm, tensor_backend, root=0):
        """
        Broadcast a whole tensor network.

        Arguments
        ---------

        state : :class:`LPTN` (for MPI-rank root, otherwise None is acceptable)
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
        raise NotImplementedError("LPTN cannot be broadcasted yet.")

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
        ansatz = LPTN

        return _AbstractMatrixTN.mpi_sample_n_unique_states(
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
        """Convert into a TN with dense tensors (without symmetries)."""
        if self.has_symmetry:
            raise NotImplementedError("Cannot convert LPTN with symmetry to dense yet.")

        # Cases without symmetry

        if true_copy:
            return self.copy()

        return self

    @classmethod
    def read(cls, filename, tensor_backend, cmplx=True, order="F"):
        """
        Read an LPTN via pickle or in the old formatted way shared
        with the Quantum TEA fortran modules.

        Parameters
        ----------
        filename: str
            PATH to the file
        tensor_backend : :class:`TensorBackend`
            Setup which tensor class to create.
        cmplx: bool, optional
            If True the LPTN is complex, real otherwise. Default to True
        order: str, optional
            If 'F' the tensor is transformed from column-major to row-major, if 'C'
            it is left as read.

        Returns
        -------
        obj: py:class:`LPTN`
            LPTN class read from file

        Details
        -------

        For the formatted format:

        Read the LPTN written by FORTRAN in a formatted way on file.
        Reads in column-major order but the output is in row-major.

        """
        ext = "pkl" + cls.extension
        if filename.endswith(ext):
            return cls.read_pickle(filename, tensor_backend=tensor_backend)

        tensors = []
        with open(filename, "r") as fh:
            # read real/complex datatype stored in file
            _ = fh.readline()

            # total number of sites
            num_sites = int(fh.readline())

            # isometry
            iso = fh.readline().split()
            iso_center = [int(iso[0]), int(iso[1])]

            # ds, bc, sr N-N and sr N-N+1
            for _ in range(num_sites):
                _ = fh.readline()
            _ = fh.readline()

            # reading tensors
            for _ in range(num_sites):
                tens = tensor_backend.tensor_cls.read(
                    fh,
                    tensor_backend.dtype,
                    tensor_backend.device,
                    tensor_backend.base_tensor_cls,
                    cmplx=cmplx,
                    order=order,
                )

                # skip empty lines
                if not fh.readline():
                    continue

                tensors.append(tens)

        obj = cls.from_tensor_list(
            tensors, iso_center=iso_center, tensor_backend=tensor_backend
        )

        return obj

    # --------------------------------------------------------------------------
    #                            Checks and asserts
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    #                     Abstract methods to be implemented
    # --------------------------------------------------------------------------

    def _initialize_lptn(self, initialize, sectors):
        """
        Initialize the LPTN with a given structure. Available are:
        - "vacuum", initializes the LPTN in |00...0><0...00|
        - "pure_random", initializes the MPS in a random state at fixed bond dimension

        Parameters
        ----------
        initialize : str
            Type of initialization.

        Returns
        -------
        None

        Details
        -------

        For the initialization of finite-temperature state, we choose the
        following strategy:

        .. code-block::

                   ^           ^ __->                       ^
           ->I->   |    a)     |/       b)           c)     |
             |___->S->  ==>  ->A---->   ==>  ->B-->  ==>  ->S->
                   ^           ^               ^            ^
                   |           |               |            |

        where

        1) the horizontal links in I are an identity matrix and the
           vertical link is a dummy link (identical irreps)
        2) the vertical links in S are an identity and both horizontal
           links are dummy links.
        3) We contract in step a) over the dummy link to get a link
           which can be contracted with the right neighbor.
        4) The resulting five-link tensor A is split in a QR as
           incoming links vs. outgoing links.
        5) The resulting tensor B has three links, where we split
           the outgoing links in in two links on carrying all the
           degeneracies (sum d_i of each sector i) and one link
           carrying the quantum numbers (still of bond dimension
           equal to the number of sectors). The former is used
           as vertical outgoing link, the latter as outgoing
           horizontal link to the left.
        6) On the last site and its outgoing link to the left, we
           can pick the sector picked by the user knowing that
           all other vertical outgoing links do not carry any
           non-identical irrep.
        """
        kwargs = self._tensor_backend.tensor_cls_kwargs()
        tensor_cls = self._tensor_backend.tensor_cls

        if (sectors is not None) and (initialize != "infinite_t"):
            msg = "Sectors will be ignored with `%s`." % (initialize)
            logger.warning(msg)

        if initialize.lower() == "vacuum":
            for ii in range(self.num_sites):
                state0 = tensor_cls(
                    [1, self._local_dim[ii], 1, 1], ctrl="ground", **kwargs
                )
                self._tensors.append(state0)
            self._singvals = [
                np.ones(1, dtype=np.double) for _ in range(self.num_sites + 1)
            ]
            self._iso_center = (0, 2)
        elif initialize.lower() == "pure_random":
            # Works only for qubits right now
            chi_ini = self._convergence_parameters.ini_bond_dimension
            chis = [1] + [chi_ini] * (self.num_sites - 1) + [1]

            chi_tmp = 1
            for ii in range(self.num_sites):
                chi_tmp *= self._local_dim[ii]
                if chi_tmp < chis[ii + 1]:
                    chis[ii + 1] = chi_tmp
                    chis[-ii - 2] = chi_tmp
                else:
                    break

            for ii in range(self.num_sites):
                bd_left = chis[ii]
                bd_right = chis[ii + 1]

                mat = np.random.rand(bd_left, self._local_dim[ii], bd_right)

                self._tensors.append(
                    tensor_cls.from_elem_array(
                        mat,
                        kwargs.get("dtype", np.double),
                        kwargs.get("device", "cpu"),
                    ).reshape([bd_left, self._local_dim[ii], 1, bd_right])
                )

            self._iso_center = (0, 2)
            self.site_canonize(self.num_sites - 1, normalize=True)
            self.normalize()
        elif initialize.lower() == "infinite_t":
            # Device and data type are automatically set using tensor backend callable
            eye_v = self._tensor_backend(
                [self.local_links[0], self.local_links[0]],
                ctrl="1",
                are_links_outgoing=[False, True],
            )
            eye_h = eye_v.eye_like(eye_v.dummy_link(eye_v.links[0]))
            eye_h.attach_dummy_link(2)
            eye_v.attach_dummy_link(2, is_outgoing=False)
            site = eye_h.tensordot(eye_v, ([2], [2]))

            _, site = site.split_qr([1, 3], [0, 2], is_q_link_outgoing=False)
            site = site.split_link_deg_charge(0)
            site = site.transpose([2, 3, 0, 1])
            self._tensors.append(site)

            for ii in range(1, self.num_sites):
                eye_h = self._tensors[-1].eye_like(self._tensors[-1].links[-1])
                eye_v = self._tensors[-1].eye_like(self.local_links[ii])

                eye_h.attach_dummy_link(2)
                eye_v.attach_dummy_link(2, is_outgoing=False)
                site = eye_h.tensordot(eye_v, ([2], [2]))
                _, site = site.split_qr([1, 3], [0, 2], is_q_link_outgoing=False)
                site = site.split_link_deg_charge(0)
                site = site.transpose([2, 3, 0, 1])
                self._tensors.append(site)

            sector = None if sectors is None else sectors.get("global", None)
            if sector is not None:
                self._tensors[-1] = self._tensors[-1].restrict_irreps(3, sector)

            self.site_canonize(0, normalize=True)
            self.normalize()
        else:
            raise QTeaLeavesError(f"Unknown option `{initialize}`.")

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

        # Renormalize and come back to previous norm
        if remove:
            # Removing is tricky, the Kraus leg needs to go somewhere ...
            raise QTeaLeavesError(
                "Cannot remove site in projection for LPTN (for now)."
            )

        state_prob = rho_i.diag(do_get=True)[meas_state]
        projector = _projector_for_rho_i(meas_state, rho_i)
        self.apply_one_site_operator(projector, site)

        # Renormalize
        self.normalize()
        self.scale(old_norm)

        # Set to None all the singvals
        self._singvals = [None for _ in self._singvals]

        return meas_state, state_prob

    def build_effective_operators(self, measurement_mode=False):
        """
        Build the complete effective operator on each
        of the links. Now assumes `self.eff_op` is set.

        Parameters
        ----------
        measurement_mode : bool, optional
            If True, enable measurement mode of effective operators
        """
        tmp = self.eff_op
        self.eff_op = None
        self.iso_towards(self.num_sites - 1, keep_singvals=True)
        self.eff_op = tmp

        if self.eff_op is None:
            raise QTeaLeavesError("Trying to build eff_op without attribute being set.")

        self.move_pos(0, device=self._tensor_backend.computational_device)
        for pos, tens in enumerate(self[:-1]):
            self.move_pos(
                pos + 1, device=self._tensor_backend.computational_device, stream=True
            )
            # Retrieve the index of the operators for the left link
            # and the physical link
            idx_out = 3
            pos_links = self.get_pos_links(pos)
            self.eff_op.contr_to_eff_op(tens, pos, pos_links, idx_out)

            if measurement_mode:
                # pylint: disable-next=unsubscriptable-object
                self.eff_op[pos, pos_links[idx_out]].run_measurements(
                    tens, idx_out, self._singvals[pos + 1]
                )
            self.move_pos(pos, device=self._tensor_backend.memory_device, stream=True)

        if measurement_mode:
            # To finish measurements, we keep going through the last site as
            # well
            pos = self.num_sites - 1
            idx_out = 3
            pos_links = self.get_pos_links(pos)
            self.eff_op.contr_to_eff_op(self[-1], pos, pos_links, idx_out)

            # Last center must be isometry center
            link_weights = None
            # pylint: disable-next=unsubscriptable-object
            self.eff_op[(pos, pos_links[idx_out])].run_measurements(
                self[-1], idx_out, link_weights
            )

    def _convert_singvals(self, dtype, device):
        """Convert the singular values of the tensor network to dtype/device."""
        # No singvals stored
        if len(self) == 0:
            return

        # Take any example tensor
        tensor = self[0]

        singvals_list = []
        for elem in self._singvals:
            if elem is None:
                singvals_list.append(None)
            else:
                singvals_ii = tensor.convert_singvals(elem, dtype, device)
                singvals_list.append(singvals_ii)

        self._singvals = singvals_list

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
            None,
            pos + 1 if pos < self.num_sites - 1 else None,
        ]

    def get_rho_i(self, idx):
        """
        Calculate the reduced density matrix for a single site.

        Parameters
        ----------
        idx : integer
            Calculate the reduced density matrix of site ``idx``.
            Recall python indices start at zero.

        Returns
        -------
        2D np.ndarray :
            Reduced density matrix.
        """
        if idx in self._cache_rho:
            return self._cache_rho[idx]

        return self.reduced_dm(sites=[idx])

    def _update_eff_ops(self, id_step):
        """
        Update the effective operators after the iso shift

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
        src_link = 0 if id_step[0] > id_step[1] else 3
        links = self.get_pos_links(id_step[0])

        # Perform the contraction
        self.eff_op.contr_to_eff_op(tens, id_step[0], links, src_link)

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
        link_partner = 0 if pos < next_pos else 3
        pos_partner = pos + 1 if pos < next_pos else pos - 1
        self.move_pos(
            pos_partner, device=self._tensor_backend.computational_device, stream=True
        )

        path_elem = [pos, next_pos]
        if no_rtens:
            link_self = 3 if pos < next_pos else 0
            return link_self, pos_partner, link_partner, path_elem

        if (pos < next_pos) and requires_singvals:
            # Going left-to-right, SVD
            qtens, rtens, s_vals, _ = self[pos].split_svd(
                [0, 1, 2],
                [3],
                no_truncation=True,
                conv_params=self._convergence_parameters,
                contract_singvals="R",
            )
            self.set_singvals_on_link(pos, pos_partner, s_vals)

        elif pos < next_pos:
            # Going left-to-right, QR
            qtens, rtens = self[pos].split_qr([0, 1, 2], [3])
            self.set_singvals_on_link(pos, pos_partner, None)
        elif requires_singvals:
            # Going right-to-left, SVD
            qtens, rtens, s_vals, _ = self[pos].split_svd(
                [1, 2, 3],
                [0],
                no_truncation=True,
                conv_params=self._convergence_parameters,
                contract_singvals="R",
                perm_left=[3, 0, 1, 2],
            )
            self.set_singvals_on_link(pos, pos_partner, s_vals)
        else:
            # Going right-to-left, RQ. Need to permute Q tensor (this is called
            # also by abstractTN where R cannot be permuted, always the first
            # link needs to go to the Q-tensor.)
            qtens, rtens = self[pos].split_qr([1, 2, 3], [0], perm_left=[3, 0, 1, 2])
            self.set_singvals_on_link(pos, pos_partner, None)
        self[pos] = qtens

        return rtens, pos_partner, link_partner, path_elem

    def _iter_tensors(self):
        """Iterate over all tensors forming the tensor network (for convert etc)."""
        yield from self.tensors

    def norm(self):
        """
        Calculate the norm of the state, where the state is X of
        rho = X Xdagger.
        """
        if self.iso_center is None:
            self.install_gauge_center()

        return self[self.iso_center].norm_sqrt()

    def normalize(self):
        """
        Normalize the LPTN state, by dividing by :math:`\\sqrt{Tr(rho)}`.
        """
        norm = 1 / self.norm()
        self[self.iso_center] *= norm

    def scale(self, factor):
        """
        Multiply the tensor network state by a scalar factor.

        Parameters
        ----------
        factor : float
            Factor for multiplication of current tensor network state.
        """
        if self.iso_center is None:
            self.install_gauge_center()

        self[self.iso_center] *= factor

    def scale_inverse(self, factor):
        """
        Multiply the tensor network state by a scalar factor.

        Parameters
        ----------
        factor : float
            Factor for multiplication of current tensor network state.
        """
        if self.iso_center is None:
            self.install_gauge_center()

        self[self.iso_center] /= factor

    def set_singvals_on_link(self, pos_a, pos_b, s_vals):
        """Update or set singvals on link via two positions."""
        if pos_a < pos_b:
            self._singvals[pos_b] = s_vals
        else:
            self._singvals[pos_a] = s_vals

    def site_canonize(self, idx, keep_singvals=False, normalize=False):
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
        normalize : bool, optional
            If True, normalize the state after the isometry movement.
            Default to False.
        """

        self.iso_towards(
            [idx, idx + 2], keep_singvals=keep_singvals, normalize=normalize
        )

    # --------------------------------------------------------------------------
    #                                 ML operations
    # --------------------------------------------------------------------------

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
        raise NotImplementedError("LPTN do not support machine learning.")

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
        raise NotImplementedError("LPTN do not support machine learning.")

    def ml_two_tensor_step(self, pos, num_grad_steps=1):
        """
        Do a gradient descent step via backpropagation with two tensors
        and the label link in the environment.
        """
        raise NotImplementedError("ML gradient descent for LPTN.")

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
        grad : :class:`_AbstractQteaTensor`
            Gradient tensor

        loss : float
            The loss function.

        """
        raise NotImplementedError("LPTN do not support machine learning.")

    # --------------------------------------------------------------------------
    #                   Choose to overwrite instead of inheriting
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    #                                  Unsorted
    # --------------------------------------------------------------------------

    def print_tensors(self, how_many=None):
        """
        Prints the tensors in LPTN together with their shape

        Parameters
        ----------
        how_many : int, optional
            Only the first :py:name::`how_many` tensors are printed.
            If :py:name::`how_many=None`, all of the tensors are printed

        Return
        ------
        None
        """
        if how_many is None:
            how_many = len(self.tensors)
        if how_many > len(self.tensors) or how_many < 0:
            raise ValueError("Invalid number of tensors")

        for ii in range(0, how_many):
            print("site", ii, ":")
            print("Shape: ", self.tensors[ii].shape)
            print(self.tensors[ii], "\n")
        print("\n")

    def print_tensor_shapes(self, how_many=None):
        """
        Prints the shape of tensors in LPTN

        Parameters
        ----------
        how_many : int
            Only the shapes of the first <how_many> tensors
            are printed. If how_many=None, shapes of all of
            the tensors are printed

        Return
        ------
        None
        """
        if how_many is None:
            how_many = len(self.tensors)
        if how_many > len(self.tensors) or how_many < 0:
            raise ValueError("Invalid number of tensors")

        for ii in range(0, how_many):
            print("site", ii, ":")
            print("Shape: ", self.tensors[ii].shape)
        print("\n")

        return None

    def reduced_dm(self, sites, max_qubits=10):
        """
        Get a reduced density matrix of a given LPTN. The
        result is in a matrix form.

        Parameters
        ----------
        sites : list of int
            Specifies the sites for the reduced density
            matrix. The partial trace is performed over
            all of the other tensors.
            Currently, a reduced density matrix is implemented
            only for single and neighbour sites.
            The sites are counted from zero to num_sites-1.

        max_qubits : int, optional
            Maximal number of qubits a reduced density matrix
            can have. If the number of qubits is greater, it
            will throw an exception.
            If the local Hilbert space dimension is not 2, The
            number of qubits is calculated as np.log2(D),
            where D is a total Hilbert space dimension of
            reduced density matrix.
            Default to 10.

        Returns
        -------
        red_dm : 2D np.ndarray
            Reduced density matrix.
        """
        if self.iso_center is None:
            self.install_gauge_center()
            logger.warning(
                "Passed an LPTN with no gauge center. The gauge center installed."
            )

        if not isinstance(sites, (np.ndarray, list)):
            raise TypeError(f"Input sites must be list of ints, not {type(sites)}.")

        if not all(isinstance(element, (int, np.int64, np.int32)) for element in sites):
            raise TypeError(
                "Input sites must be int or list of"
                f" ints. First element type: {type(sites[0])}."
            )

        if min(sites) < 0 or max(sites) > self.num_sites - 1:
            raise ValueError(
                "Invalid input for remaining sites. The"
                " site index must be between"
                f" [0,{self.num_sites-1}], not"
                f" [{min(sites)},{max(sites)}]"
            )

        if np.any(np.array(sites[:-1]) > np.array(sites[1:])):
            raise ValueError(
                "Remaining sites must be ordered from the"
                " smallest to the largest value."
            )

        if np.isscalar(self.local_dim):
            dim = self.local_dim ** len(sites)
        else:
            dim = np.prod(np.array(self.local_dim)[sites])

        if np.log2(dim) > max_qubits:
            raise RuntimeError(
                "Cannot generate a density matrix of"
                f" {len(sites)} qubits. Maximal"
                " number of qubits a reduced density"
                f" matrix can have is set to {max_qubits}."
            )

        if len(sites) > 2:
            raise ValueError(
                "Partial trace for more than"
                " two remaining particles is not"
                " yet implemented."
            )

        # shift the gauge center to one of the sites remaining in
        # the reduced density matrix
        iso_index = self.iso_center
        if iso_index < min(sites):
            self.shift_gauge_center([min(sites), min(sites) + 2])
        elif iso_index > max(sites):
            self.shift_gauge_center([max(sites), max(sites) + 2])

        # Since the gauge center of the LPTN is now among the sites
        # in the reduced density matrix, the other sites can simply be
        # ignored because they are unitary and will add into identity
        # when the partial trace is performed.
        # Therefore, the operation we need to perform is:
        # (suppose there are two sites left in the reduced dm)

        #     |   |
        #  ---O---O---               |   |            ||          |
        # |   |   |   |   --->       O===O    --->    O   --->    O
        #  ---O---O---               |   |            ||          |
        #     |   |

        # step:            [1]                  [2]         [3]

        if len(sites) > 1:
            # step [1]
            tens_left = self[sites[0]].tensordot(
                self[sites[0]].conj(), [[0, 2], [0, 2]]
            )
            tens_right = self[sites[1]].tensordot(
                self[sites[1]].conj(), [[2, 3], [2, 3]]
            )

            # step [2]
            dm_red = tens_left.tensordot(tens_right, [[1, 3], [0, 2]])
            dm_red.transpose_update([0, 2, 1, 3])
            # step [3]
            dm_red.reshape_update(
                (dm_red.shape[0] * dm_red.shape[1], dm_red.shape[2] * dm_red.shape[3]),
            )

        # analog procedure with the one tensor, now only step [1] is needed
        else:
            dm_red = self[sites[0]].tensordot(
                self[sites[0]].conj(), [[0, 2, 3], [0, 2, 3]]
            )

        return dm_red

    def get_rho_ij(self, idx):
        """
        Calculate the reduced density matrix for two
        neighbour sites.

        Parameters
        ----------
        idx : integer
            Calculate the reduced density matrix of sites ``idx``
            and ``idx``+1.
            Recall python indices start at zero.

        Returns
        -------
        2D np.ndarray :
            Reduced density matrix.
        """
        return self.reduced_dm(sites=[idx, idx + 1])

    def shift_gauge_center(self, ind_final):
        """
        Shift a gauge center of the LPTN.

        ind_final : list or np.array of two ints
            The new gauge center will be installed between
            these two sites (when considering the non-python
            index starting at 1).

        Returns
        -------
        None
        """
        # checks of input
        if isinstance(ind_final, (np.ndarray, list)):
            if not all(
                isinstance(element, (int, np.int64, np.int32)) for element in ind_final
            ) or (len(ind_final) != 2):
                raise TypeError(
                    "iso_center must be None or list of two"
                    " ints, not list of "
                    f"{len(ind_final)}"
                    f" {type(ind_final[0])}."
                )

        elif ind_final is not None:
            raise TypeError(
                f"iso_center must be None or list of two ints, not {type(ind_final)}."
            )

        self.iso_towards(ind_final[0])
        return None

    def to_statevector(self, qiskit_order=False, max_qubit_equivalent=20):
        """
        Decompose a given LPTN into statevector form if pure.

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
        psi = MPS.from_tensor_list(
            self.to_tensor_list_mps(),
            conv_params=self.convergence_parameters,
            tensor_backend=self.tensor_backend,
        )

        return psi.to_statevector(
            qiskit_order=qiskit_order, max_qubit_equivalent=max_qubit_equivalent
        )

    def to_mps(self):
        """
        Converts a given LPTN into MPS if pure.

        Returns
        -------

        psi : :py:class:`MPS`
            The wave-function as MPS if a pure density matrix.

        Raises
        ------

        Mixed state: if mixed-state representations are not pure, an
            error will be raised.
        """
        psi = MPS.from_tensor_list(
            self.to_tensor_list_mps(),
            conv_params=self.convergence_parameters,
            tensor_backend=self.tensor_backend,
        )
        return psi

    def to_tensor_list_mps(self):
        """
        Return the tensor list representation of the LPTN
        as MPS. If the upper link has dimension one, the tensors
        are reshaped to rank 3.

        Return
        ------
        list
            List of tensors of the LPTN as MPS.
        """
        # check if link of complex conjugate has dimension 1
        for tens in self.tensors:
            if tens.shape[2] != 1:
                raise QTeaLeavesError(
                    "Cannot convert LPTN to MPS tensor list if the state is not pure -",
                    "Tensor with upper leg dimension other than 1 found in the list.",
                )
        # reshape to rank 3
        new_tensors = []
        for tens in self.tensors:
            new_tensors.append(
                tens.reshape((tens.shape[0], tens.shape[1], tens.shape[3]))
            )

        return new_tensors

    def to_tensor_list(self):
        """
        Return the tensor list representation of the LPTN.

        Return
        ------
        list[QteaTensor]
            List of tensors of the LPTN.
        """

        return self.tensors

    def write(self, filename, cmplx=True):
        """
        Write an LPTN in python format into a FORTRAN format, i.e.
        transforms row-major into column-major

        Parameters
        ----------
        filename: str
            PATH to the file
        cmplx: bool, optional
            If True the MPS is complex, real otherwise. Default to True

        Returns
        -------
        obj: py:class:`LPTN`
            LPTN class read from file
        """
        with open(filename, "w") as fh:
            # write real/complex
            # currently it is always set to 'Z'!
            fh.write("%c\n" % ("Z"))

            # write total number of sites
            fh.write("%d\n" % (len(self.tensors)))

            # isometry
            fh.write("%d %d\n" % (self.iso_center, self._iso_center[1]))

            # local dim, kappa, bond dimension to the left for each site (this
            # information refers to the maximum allowed for kappa and the bond
            # dimension, not to the current one. Usually, this should be overwritten
            # or set from the simulations reading the LPTN, but set it to sensbile
            # value derived from the convergence parameters stored)
            for tens in self.tensors:
                fh.write(
                    "%d %d %d\n"
                    % (
                        tens.shape[1],
                        self._convergence_parameters.max_bond_dimension,
                        self._convergence_parameters.max_bond_dimension,
                    )
                )

            # bond dimension to the right for the last site
            fh.write("%d\n" % (self.tensors[-1].shape[3]))

            for tens in self.tensors:
                tens.write(fh, cmplx=cmplx)
                fh.write("\n")

        return None

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
            site when a new measurement begins.

        Returns
        -------
        probabilities : list of floats
            Probabilities of the children

        tensor_list : list of ndarray
            Child tensors, already contracted with the next site
            if not last site.
        """
        raise NotImplementedError("No support projective measurements for LPTN.")

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
        raise NotImplementedError("No support projective measurements for LPTN.")
