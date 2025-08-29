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
The module contains a light-weight TTO emulator.
"""

# pylint: disable=too-many-lines
# pylint: disable=too-many-arguments, too-many-locals

import logging
import math as mt
from copy import deepcopy

import numpy as np
import numpy.linalg as nla
import scipy.linalg as scla
import scipy.optimize as scop

from qtealeaves.abstracttns.abstract_tn import _AbstractTN
from qtealeaves.convergence_parameters import TNConvergenceParameters
from qtealeaves.emulator.lptn_simulator import LPTN
from qtealeaves.mpos.mldatampo import MLDataMPO
from qtealeaves.tensors import TensorBackend
from qtealeaves.tooling import QTeaLeavesError

from .mps_simulator import MPS
from .ttn_simulator import TTN, TTNLayer

__all__ = ["TTO"]

logger = logging.getLogger(__name__)


# pylint: disable-next=dangerous-default-value
def logger_warning(*args, storage=[]):
    """Workaround to display warnings only once in logger."""
    if args in storage:
        return

    storage.append(args)
    logger.warning(*args)


# pylint: disable-next=too-many-public-methods
class TTO(TTN):
    r"""
    TREE TENSOR OPERATOR - represents a density matrix

    Parameters
    ----------
    num_sites : int
        Number of sites

    convergence_parameters : :py:class::`TNConvergenceParameters`
        Input for handling convergence parameters.
        In particular, in the TTO simulator we are
        interested in:
        - the maximum bond dimension (max_bond_dimension)
        - the cut ratio (cut_ratio) after which the singular
        values in SVD are neglected, all singular values
        such that lambda/lambda_max <= eps
        are truncated

    local_dim : int, optional
        Dimension of Hilbert space of single site
        (defined as the same for each site).
        Default is 2.

    tensor_backend : `None` or instance of :class:`TensorBackend`
        Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.

    initialize : str, optional
        Available are `vacuum` / `ground`, `random`, or `empty`. Options for
        tensor class as well allowed.
        Default to "ground"

    iso_center : None or np.ndarray/list of two ints, optional
        Position of the gauge center. [i,j] means j-th
        tensor of i-th layer, i=0 is uppermost, j=0 is
        the leftmost tensor. If TTO has no gauge
        center, iso_center = None.
        Default is None.

    Initialization
    --------------
    |000...000><000---000| , where Z|0>=|0>

    Tensor representation
    ---------------------

    .. code-block::

    \ / \ /
     O   O
      \ /            } --> complex conjugates of tensors below,
       O                   access with TTO.cc_layers.tensors
       |
       O
      / \            } --> these are contained in TTO.layers
     O   O
    / \ / \

    Attributes
    ----------
    TTO.num_sites : int
        Number of sites in TTO

    TTO.local_dim : np.ndarray of ints
        Local Hilbert space dimension

    TTO.num_layers : int
        Number of layers in TTO

    TTO.layers : list of :py:class::`TTOLayer`-s
        Layers of the TTO, list of 'TTOLayer'
        objects

    TTO.cc_layers : list of :py:class::`TTOLayer`-s
        Complex conjugate part of the TTO, list
        of 'TTOLayer' objects

    TTO.probabilities : np.ndarray of float
        Mixed state probabilities for the case when
        TTO is a density matrix.

    TTO.iso_center : None or np.ndarray/list of two ints
        Position of the gauge center. [i,j] means j-th
        tensor of i-th layer, i=0 is uppermost, j=0 is
        the leftmost tensor. If the TTO has no gauge
        center, TTO.iso_center = None.

    TTO._max_bond_dim : int
        Maximal bond dimension

    TTO._cut_ratio : float
        Cut ratio

    Access to tensors
    -----------------
    - access to i-th layer with TTO[i]

        [ uppermost layer is indexed with i = 0 ]
    - access to [i,j]-th tensor with TTO[i][j]

        [ leftmost tensor is indexed with j = 0 ]
    - order of legs in tensor

        [ left leg - right leg - upper leg]
    """

    extension = "tto"
    is_ttn = False
    skip_tto = True

    def __init__(
        self,
        num_sites,
        convergence_parameters,
        local_dim=2,
        tensor_backend=None,
        initialize="ground",
        iso_center=None,
        **kwargs,
    ):
        if "sectors" in kwargs:
            if not kwargs["sectors"] in [{}, None]:
                logger.warning(
                    "An input for sectors has been introduced. Symmetries are not implemented "
                    + "for TTOs yet, so this input will be ignored"
                )

        super().__init__(
            num_sites,
            convergence_parameters,
            local_dim=local_dim,
            tensor_backend=tensor_backend,
            initialize=initialize,
        )

        self._probabilities = None

        if iso_center is not None and not isinstance(iso_center, (list, np.ndarray)):
            raise TypeError(
                "The iso_center must be None or list or np.ndarray,"
                f" not {type(iso_center)}."
            )
        if iso_center is not None:
            if len(iso_center) != 2:
                raise TypeError(
                    "The iso_center must contain exactly 2 elements,"
                    f" not {len(iso_center)} elements."
                )
            if iso_center[0] < 0 or iso_center[1] < 0:
                raise ValueError("Values in iso_center must be positive.")
            if iso_center[0] >= self.num_layers:
                raise ValueError(
                    "Invalid input for iso_center. A TTO does not"
                    f" contain {iso_center[0]}-th layer."
                )
            if iso_center[1] >= int(2 ** iso_center[0]):
                raise ValueError(
                    "Invalid input for iso_center."
                    f" The {iso_center[0]}-th layer does not contain"
                    f" {iso_center[1]} tensors."
                )

        # Handle iso_center argument (never overwrites existing iso_center with None)
        if (self.iso_center is None) and (iso_center is not None):
            # To install as requested by the user, first isometrize and shift
            # in the next step
            self.isometrize_all()

        if iso_center is not None:
            # Move iso center
            self.iso_towards(iso_center)

            self.iso_center = iso_center

        # TTO initializetion not aware of device
        self.convert(self.tensor_backend.dtype, self.tensor_backend.memory_device)

    # --------------------------------------------------------------------------
    #                               Properties
    # --------------------------------------------------------------------------

    @property
    def cc_layers(self):
        """
        complex conjugate part of TTO, returns complex conjugate tensors
        stored in TTOLayers
        """
        c_conj = [
            TTNLayer.from_tensorlist(
                x.cc_tensors,
                self.local_dim,
                self._convergence_parameters.max_bond_dim,
                self.tensor_backend.device,
            )
            for x in self.layers
        ]
        return c_conj

    @property
    def local_dim(self):
        """
        The local dimension is constrained to be always the same on the TTO
        """
        if isinstance(self._local_dim, int):
            return [self._local_dim] * self.num_sites

        return self._local_dim

    @property
    def probabilities(self):
        """
        Extracts the mixed, e.g. finite temperature, state probabilities
        from a TTO density matrix.

        Return
        ------
        prob : np.ndarray
            Mixed state probabilities in
            descending order.
        """
        if self._probabilities is not None:
            # Probabilities have been calculated before
            return self._probabilities

        if self.iso_center is None:
            logger.warning(
                "Mixed state probabilities can be extracted"
                " only from TTO with gauge center at the"
                " uppermost tensor. Installing a gauge center"
                " to the TTO."
            )
            self.install_gauge_center()
        elif any(self.iso_center) != 0:
            logger.warning(
                "Mixed state probabilities can be extracted"
                " only from TTO with gauge center at the"
                " uppermost tensor. Shifting a gauge center"
                " from %s to [0,0].",
                self.iso_center,
            )
            self.shift_gauge_center([0, 0])

        top = self[0][0]
        _, _, sing_val, _ = top.split_svd(
            [0, 1], [2], no_truncation=True, conv_params=self._convergence_parameters
        )  # compute_uv=False)

        # In case of symmetries, flatten returns one vector and sorts it
        prob = sing_val.flatten() ** 2

        self._probabilities = prob
        return self._probabilities

    # --------------------------------------------------------------------------
    #                       classmethod, classmethod like
    # --------------------------------------------------------------------------

    @classmethod
    def from_statevector(
        cls, statevector, local_dim=2, conv_params=None, tensor_backend=None
    ):
        """
        Initialize the TTO by decomposing a statevector into TTO form.

        We use the dm_to_tto function instead of mapping the statevector to
        TTN and the TTN to TTO since in this way we avoid the problems arising
        from the different structures of the top layer.

        Parameters
        ----------

        statevector : ndarray of shape( [local_dim]*num_sites, )
            Statevector describing the interested state for initializing the TTN

        tensor_backend : `None` or instance of :class:`TensorBackend`
            Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.
        """
        if not isinstance(statevector, np.ndarray):
            raise TypeError("`from_statevector` requires numpy array.")

        # Check if statevector contains all zeros
        if np.all(statevector == 0):
            raise ValueError("State vector contains all zeros.")

        num_sites = len(statevector.shape)

        if local_dim != statevector.shape[0]:
            raise QTeaLeavesError("Mismatch local dimension (passed and one in array).")

        tto = cls.dm_to_tto(
            num_sites,
            local_dim,
            statevector.reshape(-1),
            1,
            conv_params=conv_params,
            tensor_backend=tensor_backend,
        )
        tto.convert(tto.tensor_backend.dtype, tto.tensor_backend.device)

        return tto

    @classmethod
    def from_density_matrix(
        cls, rho, n_sites, dim, conv_params, tensor_backend=None, prob=False
    ):
        """
        Computes the TTO form of a given density matrix

        Parameters
        ----------
        num_sites : int
            Number of sites

        dim : int
            Local Hilbert space dimension

        psi,prob : matrix or vector, matrix or int
            - Mixed states :
                psi is a matrix with eigenstates as columns,
                prob is 1D array containing (possibly truncated)
                probabilities for each state
            - Pure states : psi is a state, prob = 1


        conv_params : :py:class::`TNConvergenceParameters`
            Input for handling convergence parameters.
            in particular, we are interested in:
            - the maximum bond dimension (max_bond_dimension)
            - the cut ratio (cut_ratio) after which the singular
            values in SVD are neglected, all singular values
            such that lambda/lambda_max <= eps
            are truncated

        padding : `np.array` of length 2 or `None`, optional
            Used to increase the bond dimension of the TTO. Also necessary to allow
            the growth of bond dimension in TDVP algorithms (two tensor updates).
            If not `None`, all the TTO tensors are padded such that the maximal bond
            dimension is equal to `padding[0]`. The value `padding[1]`
            tells with which value are we padding the tensors. Note that
            `padding[1]` should be very small, as it plays the role of
            numerical noise.
            Default to `None`.

        tensor_backend : `None` or instance of :class:`TensorBackend`
            Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.

        Return
        ------
        rho_tt : :py:class:`TTO`
            TTO form of the density matrix
        """
        return cls.dm_to_tto(
            n_sites,
            dim,
            rho,
            prob,
            conv_params=conv_params,
            tensor_backend=tensor_backend,
        )

    @classmethod
    def from_lptn(
        cls,
        lptn,
        conv_params=None,
        tensor_backend=None,
        method="moving",
        **kwargs,
    ):
        """Converts LPTN to TTO.

        Parameters
        ----------
        lptn: :py:class:`LPTN`
            Object to convert to TTO.
        conv_params: :py:class:`TNConvergenceParameters`, optional
            Input for handling convergence parameters
            If None, the algorithm will try to
            extract conv_params from lptn.convergence_parameters.
            Default is None.
        kwargs : additional keyword arguments
            They are accepted and passed to the conversion method for
            LPTN to TTO.

        Return
        ------

        tto: :py:class:`TTO`
            Decomposition of lptn.
        """
        cls.assert_extension(lptn, "lptn")
        if conv_params is None:
            conv_params = lptn.convergence_parameters
        if tensor_backend is None:
            tensor_backend = lptn.tensor_backend
        conversion_methods = {
            "recursive": cls.lptn_to_tto,
            "recursive-iso": cls.lptn_to_tto_iso,
            "moving": cls.lptn_to_tto_move_tensors,
        }
        if method not in conversion_methods:
            raise ValueError(
                f"Invalid method {method}. Use `recursive`, `recursive-iso` or `moving`."
            )
        if method == "moving":
            lptn.iso_towards(lptn.num_sites // 2 - 1)
        return conversion_methods[method](
            lptn.tensors, conv_params, tensor_backend=tensor_backend, **kwargs
        )

    @classmethod
    def from_mps(cls, mps, conv_params=None, **kwargs):
        """Converts MPS to TTO.

        Parameters
        ----------
        mps: :py:class:`MPS`
            object to convert to TTO.
        conv_params: :py:class:`TNConvergenceParameters`, optional
            Input for handling convergence parameters
            Default is None.

        Return
        ------

        tto: :py:class:`TTO`
            Decomposition of mps.
        """
        cls.assert_extension(mps, "mps")
        ttn = TTN.from_mps(mps.copy())
        return cls.from_ttn(ttn, conv_params=conv_params)

    @classmethod
    def from_ttn(cls, ttn, conv_params=None, **kwargs):
        """Converts TTN to TTO.

        Parameters
        ----------
        ttn: :py:class:`TTN`
            object to convert to TTO.
        conv_params: :py:class:`TNConvergenceParameters`, optional
            Input for handling convergence parameters
            Default is None.
        kwargs : additional keyword arguments
            They are accepted, but not passed to calls in this function.

        Return
        ------

        tto: :py:class:`TTO`
            Decomposition of ttn.
        """
        cls.assert_extension(ttn, "ttn")
        tto = cls.ttn_to_tto(ttn)
        tto.convergence_parameters = conv_params
        return tto

    @classmethod
    def from_tto(cls, tto, conv_params=None, **kwargs):
        """Converts TTO to TTO.

        Parameters
        ----------
        tto: :py:class:`TTO`
            Object to convert to TTO.
        conv_params: :py:class:`TNConvergenceParameters`, optional
            Input for handling convergence parameters.
            Default is None.
        kwargs : additional keyword arguments
            They are accepted, but not passed to calls in this function.

        Return
        ------

        new_tto: :py:class:`TTO`
            Decomposition of tto, here just a copy.
        """
        cls.assert_extension(tto, "tto")
        new_tto = tto.copy()
        new_tto.convergence_parameters = conv_params
        return new_tto

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
            `ml_data_mpo`.

        has_trivial_link : bool
            With a trivial link (`True`), the ML-MPS learns solely based on the overlap
            of the sample with the ansatz rounded to the closest integer. Instead,
            the typical ML approach with argmax over a vector is used with
            `has_trivial_link=False`.

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

        if initialize != "superposition-data":
            rho = TTO(
                num_sites,
                convergence_parameters,
                local_dim=local_dim,
                initialize=initialize,
                tensor_backend=tensor_backend,
            )

            if not has_trivial_label_link:
                # We have to adapt
                iso_pos = rho.default_iso_pos
                rho.iso_towards(iso_pos)
                tensor = rho[iso_pos]
                tmp = list(tensor.shape)
                if has_env_label_link:
                    shape = tmp[:2] + [ml_data_mpo.num_labels]
                else:
                    shape = tmp + [ml_data_mpo.num_labels]

                tensor = tensor_backend(shape, ctrl="R")
                tensor.normalize()
                rho[iso_pos] = tensor

            return rho

        psi = MPS.ml_initial_guess(
            convergence_parameters,
            tensor_backend,
            initialize,
            ml_data_mpo,
            dataset,
            has_trivial_label_link=has_trivial_label_link,
        )

        shape_0 = psi[0].shape
        if not has_trivial_label_link:
            # Conversion will fail, we have to do some magic increasing the
            # size of link
            psi[0].fuse_links_update(1, 2)

        ttn_list = psi.to_ttn(trunc=True, convergence_parameters=convergence_parameters)
        psi = TTN.from_tensor_list(
            ttn_list, tensor_backend=tensor_backend, conv_params=convergence_parameters
        )
        psi.iso_center = (0, 0)

        obj = TTO.ttn_to_tto(
            psi, conv_params=convergence_parameters, tensor_backend=tensor_backend
        )

        if (not has_trivial_label_link) and (not has_env_label_link):
            pos = (obj.num_layers - 1, 0)
            obj.site_canonize(0)
            new_shape = (shape_0[1], shape_0[2], obj[pos].shape[1], obj[pos].shape[2])
            obj[pos].reshape_update(new_shape)
            obj[pos].transpose_update([0, 2, 3, 1])
            obj.leg_towards([pos, (0, 0)], trunc=True)

        return obj

    # --------------------------------------------------------------------------
    #                            Checks and asserts
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    #                     Abstract methods to be implemented
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    #                                  Unsorted
    # --------------------------------------------------------------------------

    def _ml_predict_label_link(self, data_samples, n_jobs=1, do_round=True):
        self.iso_towards(self.default_iso_pos, trunc=True)

        tensor = self[self.iso_center]
        tensor_backend = TensorBackend(
            tensor_cls=type(tensor),
            base_tensor_cls=tensor.base_tensor_cls,
            device=tensor.device,
            dtype=tensor.dtype,
            datamover=tensor.get_default_datamover(),
        )

        nn = len(data_samples)
        labels = np.array([0] * nn, dtype=int)

        ml_data_mpo = MLDataMPO(data_samples, labels, nn, tensor_backend)

        orig_eff_op = self.eff_op
        self.eff_op = None
        ml_data_mpo.setup_as_eff_ops(self)

        eff_0 = self.eff_op[((1, 0), (0, 0))].tensor
        eff_1 = self.eff_op[((1, 1), (0, 0))].tensor
        eff_2 = self.eff_op[(None, (0, 0))].tensor

        labels = tensor.einsum(
            "abcd,xmayi,ynbzi,zlcxi->di",
            eff_0,
            eff_1,
            eff_2,
        )

        if do_round:
            argmax = tensor.get_attr("argmax")
            labels = argmax(labels.elem, axis=0)
            labels = tensor.get_of(labels)
            labels = list(np.array(labels))
        else:
            # Would return vector for each sample, basically before the argmax?
            raise NotImplementedError(
                "ML predict without rounding for TTO and label link."
            )

        self.eff_op = orig_eff_op

        return labels

    def trunc_probabilities(self, return_singvals=False):
        """
        Truncates the mixed state probabilities of a TTO.

        Parameters
        ----------
        return_singvals : Boolean, optional
            If True, the truncated singualr values are returned.

        Return
        ------
        singvals_cut : float, returned if `return_singvals`==True
            Discarded singular values due to the truncation.
        """
        root = self[0][0]

        if self.convergence_parameters is None:
            conv_params = TNConvergenceParameters()
            logger.warning(
                "Trying to cut probabilities of TTO without convergence parameters!"
                "Default parameters are used."
            )
        else:
            conv_params = self.convergence_parameters

        conv_params_root = TNConvergenceParameters(
            max_bond_dimension=conv_params.max_kraus_dimension,
            cut_ratio=conv_params.cut_ratio,
        )
        root, _, _, singvals_cut = root.split_svd(
            [0, 1],
            [2],
            contract_singvals="L",
            conv_params=conv_params_root,
        )
        self[0][0] = deepcopy(root)
        self._probabilities = None
        self.iso_center = [0, 0]

        if return_singvals:
            return singvals_cut

        return None

    def install_gauge_center(self):
        """
        Install a gauge center to the position [0,0] (uppermost tensor)
        of the TTO.

        Return
        ------
        None
        """

        self.isometrize_all()
        return None

    def shift_gauge_center(self, ind_final, keep_singvals=False):
        """
        Shift a gauge center of the TTO to a given position.

        Parameters
        ----------
        ind_final : list or np.array of lenght 2
            Index where we want the new gauge center to be.
        keep_singvals : bool, optional
            If True, keep the singular values even if shifting the iso with a
            QR decomposition. Default to False.

        Returns
        -------
        None

        **Remark : [i,j] means j-th tensor of i-th layer, i=0 is uppermost, j=0 is
                   the most left tensor
        """
        self.iso_towards(ind_final, keep_singvals)

        return None

    def purity(self, prob=None):
        """
        Computes the purity entanglement monotone for a
        density matrix in the TTO form.

        purity = Tr(rho^2), where rho is a density matrix.
        The above relation is equivalent to:
        purity = sum(prob^2), where prob are mixed state
        probabilities.

        Parameters
        ----------
        prob : np.ndarray, optional
            Mixed state probabilities.
            If given, purity is calculated
            with them. If None, the probabilities
            are calculated from the TTO.
            Default is None.

        Return
        ------
        float :
            Purity of the TTO density matrix.
        """
        if prob is None:
            prob = self.probabilities

        tsum = self[0][0].get_attr("sum")

        return tsum(prob * prob)

    def negativity(self, sqrt=False):
        """
        Computes the negativity entanglement monotone
        for a mixed state density matrix in the TTO form.

        - Measures the entanglement between the left and right half of
        the 1D system.

        Parameters
        ----------
        sqrt : Boolean
            Mathematically, negativity can be computed in two different ways.
            If True, it is computed via the square of partially transposed density
            matrix, and if False, it is computed via the eigenvalues of partially
            transposed density matrix.

        Return
        ------
        neg : float
            Negativity of the TTO.
        """
        if self.iso_center is None:
            logger.warning(
                "Negativity can be computed only for TTO"
                " with gauge center at the uppermost tensor."
                " Installing a gauge center to the uppermost"
                " tensor."
            )
            self.install_gauge_center()
        elif any(self.iso_center) != 0:
            logger.warning(
                "Negativity can be computed only for TTO"
                " with gauge center at the uppermost tensor."
                " Shifting a gauge center from %s"
                " to [0,0].",
                self.iso_center,
            )
            self.shift_gauge_center([0, 0])

        part_transpose = self[0][0].tensordot(self[0][0].conj(), [[2], [2]])
        # partial transpose with respect to one subsystem (half of
        # the system in this case)
        # the resulting negativity is independent of the
        # choice of which from the two subsystems we transpose
        part_transpose.transpose_update((2, 1, 0, 3))
        dims = part_transpose.shape
        part_transpose.reshape_update((dims[0] * dims[1], dims[0] * dims[1]))

        if part_transpose.device in ["gpu"]:
            sqrt = False

        # depending on a chosen method, perform corresponding calculation
        if sqrt:
            tmp = part_transpose.tensordot(part_transpose.conj(), ([1], [1]))
            neg = tmp.sqrtm()
            neg = neg.trace(return_real_part=True, do_get=True)
            neg = 0.5 * (neg - 1)
        else:
            absval, summe = part_transpose.get_attr("abs", "sum")
            eig_vals = part_transpose.eigvalsh()
            neg = summe(absval(eig_vals) - eig_vals)
            neg = part_transpose.get_of(neg)
            neg *= 0.5

        return neg

    def log_negativity(self, root=None, local_dim=2):
        """
        Computes the logarithmic negativity for a given root tensor.
        Default is the "half cut", i.e., the entanglement between
        left and right halves of the system.
        For computing other partitions, see also meas_log_negativity().


        Parameters
        ----------
        root : instance of :class:`_AbstractQteaTensor`
            Root tensor for which the logarithmic negativity should be computed.
            Default to None, i.e., "half cut".

        local_dim : int or [int]
            local dimension of the system.

        Return
        ------
        log_neg : float
            Logarithmic negativity of the TTO.
        """
        if self.iso_center is None:
            logger.warning(
                "Logarithmic negativity can be computed only for TTO"
                " with gauge center at the uppermost tensor."
                " Installing a gauge center to the uppermost"
                " tensor."
            )
            self.install_gauge_center()

        elif any(self.iso_center) != 0:
            logger.warning(
                "Logarithmic negativity can be computed only for TTO"
                " with gauge center at the uppermost tensor."
                " Shifting a gauge center from %s"
                " to [0,0].",
                self.iso_center,
            )
            self.shift_gauge_center([0, 0])

        if root is None:
            root = self[0, 0]

        part_transpose = root.tensordot(root.conj(), [[2], [2]])

        part_transpose.transpose_update((2, 1, 0, 3))
        dims = part_transpose.shape
        part_transpose.reshape_update((dims[0] * dims[1], dims[0] * dims[1]))

        tabs, tsum, tlog = part_transpose.get_attr("abs", "sum", "log")
        eig_vals = part_transpose.eigvalsh()
        neg = tsum(tabs(eig_vals) - eig_vals)
        neg *= 0.5

        if isinstance(local_dim, int):
            log_neg = tlog(2.0 * neg + 1.0) / mt.log(local_dim)
        elif len(set(local_dim)) > 1:
            logger_warning(
                "Using log based on first Hilbert space for logarithmic negativity in "
                "TTO but different local dimensions."
            )
            log_neg = tlog(2.0 * neg + 1.0) / mt.log(local_dim[0])
        else:
            log_neg = tlog(2.0 * neg + 1.0) / mt.log(local_dim[0])

        return log_neg

    def entropy(self, prob=None, local_dim=2, eps=1e-10):
        """
        This function calculates Von Neumann entropy of
        a TTO mixed state density matrix.
        entropy = -sum(prob log(prob)), where prob are the mixed state
        probabilities and logarithm base is local_dim.

        Parameters
        ----------
        prob : np.ndarray, optional
            Mixed state probabilities.
            If given, the entropy is calculated
            faster.
            Default is None.

        local_dim : int, optional
            Dimension of local Hilbert space.
            Default is 2.

        eps : float, optional
            To make calculation faster and avoid division
            by zero, all the probabilities smaller than
            <eps> are cut off.
            Default is 1e-10.

        Return
        ------
        entropy : float
            Von Neumann entropy of a TTO density matrix.
        """
        # if not given, get mixed state probabilities
        if prob is None:
            prob = self.probabilities

        # truncate probabilities
        mask = prob > eps
        prob = prob[mask]
        # convert logarithm base to local_dim and calculate entropy
        tlog, tsum = self[0][0].get_attr("log", "sum")
        if isinstance(local_dim, int):
            log_val = tlog(prob) / mt.log(local_dim)
        elif len(set(local_dim)) > 1:
            logger_warning(
                "Using log based on first Hilbert space for entropy in "
                "TTO but different local dimensions."
            )
            log_val = tlog(prob) / mt.log(local_dim[0])
        else:
            log_val = tlog(prob) / mt.log(local_dim[0])
        entropy = -tsum(prob * log_val)

        return float(self[0][0].get_of(entropy))

    def renyi_entropy(self, alpha, prob=None, local_dim=2, eps=1e-10):
        """
        This function calculates Renyi entropy of order alpha for
        a TTO mixed state density matrix.
        Renyi entropy = 1/(1-alpha)*sum(log(prob**alpha)), where prob are
        the mixed state probabilities and logarithm base is local_dim

        Parameters
        ----------
        alpha : float
            order of Renyi entropy.

        prob : np.ndarray, optional
            Mixed state probabilities.
            If given, the entropy is calculated
            faster.
            Default is None.

        local_dim : int, optional
            Dimension of local Hilbert space.
            Default is 2.

        eps : float, optional
            To make calculation faster and avoid division
            by zero, all the probabilities smaller than
            <eps> are cut off.
            Default is 1e-10.

        Return
        ------
        entropy : float
            Alpha-order Rényi entropy of the given TTO
            density matrix.
        """
        if abs(alpha - 1) < 1e-8:
            raise ValueError("Value for input parameter alphacannot be equal to 1.")

        # if not given, get mixed state probabilities
        if prob is None:
            prob = self.probabilities

        # cut off all probabilities smaller than <eps>
        mask = prob > eps
        prob = prob[mask]

        # convert logarithm base to local_dim and calculate Rényi
        # entropy
        tlog, tsum = self[0][0].get_attr("log", "sum")
        if isinstance(local_dim, int):
            log_val_sum = tlog(tsum(prob**alpha)) / mt.log(local_dim)
        elif len(set(local_dim)) > 1:
            logger_warning(
                "Using log based on first Hilbert space for Renyi entropy in "
                "TTO but different local dimensions."
            )
            log_val_sum = tlog(tsum(prob**alpha)) / mt.log(local_dim[0])
        else:
            log_val_sum = tlog(tsum(prob**alpha)) / mt.log(local_dim[0])
        rentropy = 1 / (1 - alpha) * log_val_sum

        return float(self[0][0].get_of(rentropy))

    def renyi_negativity(self, alpha, root=None, prob=None, local_dim=2):
        """
        Computes the Renyi negativity for a given root tensor, defined as
        -log(Tr[rho^T_B**alpha]/Tr[rho**alpha]), where rho^T_B is the
        partial transpose w.r.t. subsystem B.
        Default is the "half cut", i.e., B is the left/right half of the system.


        Parameters
        ----------
        alpha : int
            order of Renyi negativity.

        root : instance of :class:`_AbstractQteaTensor`
            Root tensor for which the Renyi negativity should be computed.
            Default to None, i.e., "half cut".

        prob : np.ndarray, optional
            Mixed state probabilities.
            If given, computation is faster.
            Default is None.

        local_dim : int or [int], optional
            local dimension of the system.

        Return
        ------
        ren_neg : float
            Renyi negativity of the TTO.
        """
        if self.iso_center is None and root is None:
            logger.warning(
                "Renyi negativity can be computed only for TTO"
                " with gauge center at the uppermost tensor."
                " Installing a gauge center to the uppermost"
                " tensor."
            )
            self.install_gauge_center()

        elif any(self.iso_center) != 0 and root is None:
            logger.warning(
                "Renyi negativity can be computed only for TTO"
                " with gauge center at the uppermost tensor."
                " Shifting a gauge center from %s"
                " to [0,0].",
                self.iso_center,
            )
            self.shift_gauge_center([0, 0])

        if not isinstance(alpha, int):
            raise ValueError("Input parameter alpha needs to be an integer!")

        # if not given, get mixed state probabilities
        if prob is None:
            prob = self.probabilities

        if root is None:
            root = self[0, 0]

        # compute partial transpose from root tensor
        part_transpose = root.tensordot(root.conj(), [[2], [2]])
        part_transpose.transpose_update((2, 1, 0, 3))
        dims = part_transpose.shape
        part_transpose.reshape_update((dims[0] * dims[1], dims[0] * dims[1]))

        part_transpose_alpha = part_transpose.copy()

        # compute rho^T_B**alpha via consecutive contractions
        for _ in range(alpha - 1):
            part_transpose_alpha = part_transpose_alpha.tensordot(
                part_transpose, [[1], [0]]
            )

        # compute trace and get the denominator
        ren_neg = part_transpose_alpha.trace()
        tabs, tlog, tsum = part_transpose.get_attr("abs", "log", "sum")
        factor = tsum(prob**alpha)
        ren_neg /= factor

        if isinstance(local_dim, int):
            ren_neg = -tlog(ren_neg) / mt.log(local_dim)
        elif len(set(local_dim)) > 1:
            logger_warning(
                "Using log based on first Hilbert space for Renyi negativity in "
                "TTO but different local dimensions."
            )
            ren_neg = -tlog(ren_neg) / mt.log(local_dim[0])
        else:
            ren_neg = -tlog(ren_neg) / mt.log(local_dim[0])

        return tabs(ren_neg)

    def concurrence(self):
        """
        This function calculates the concurrence entanglement
        monotone for two qubits:

        C(rho) = sqrt(sqrt(rho)*rho_tilde*sqrt(rho)),

        where rho is a density matrix and rho_tilde
        is (sigma_y sigma_y) rho* (sigma_y sigma_y).

        Parameters
        ----------
        self : :pyclass:`TTO`
            Two-qubit density matrix TTO.

        Returns
        -------
        conc : float
            The concurrence entanglement monotone
            of a given TTO.
        """
        if (self.num_sites != 2) or (self.local_dim != 2):
            raise ValueError(
                "Concurrence can only be computed for the"
                f" case of two qubits, not {self.num_sites} sites with"
                f" local dimension {self.local_dim}."
            )

        if self.iso_center is None:
            logger.warning(
                "Concurrence can be computed only for TTO"
                " with gauge center at the uppermost tensor."
                " Installing a gauge center to the uppermost"
                " tensor."
            )
            self.install_gauge_center()
        elif any(self.iso_center) != 0:
            logger.warning(
                "Concurrence can be computed only for TTO"
                " with gauge center at the uppermost tensor."
                " Shifting a gauge center from %s to [0,0].",
                self.iso_center,
            )
            self.shift_gauge_center([0, 0])

        root_dm = self[0][0].tensordot(self[0][0].conj(), [[2], [2]])

        root_dm = root_dm.reshape(
            (root_dm.shape[0] * root_dm.shape[1], root_dm.shape[2] * root_dm.shape[3]),
        )

        rho_sqrt = root_dm.sqrtm()

        sigma_y_mat = rho_sqrt.zeros_like(root_dm)
        sigma_y_mat.set_matrix_entry(0, 3, -1)
        sigma_y_mat.set_matrix_entry(1, 2, 1)
        sigma_y_mat.set_matrix_entry(2, 1, 1)
        sigma_y_mat.set_matrix_entry(3, 0, -1)

        rho_tilde = sigma_y_mat @ root_dm.conj() @ sigma_y_mat
        conc_mat = rho_sqrt @ rho_tilde @ rho_sqrt

        conc_mat = conc_mat.sqrtm()

        # Move to host
        conc_mat = conc_mat.get().to_dense()

        val, _ = np.linalg.eig(conc_mat)
        val = np.sort(val)[::-1]
        conc = abs(2 * val[0] - np.sum(val))
        conc = max([0, conc])

        return conc

    def eof(self, init_guess=None, unitary=None, extra=0, maxiter=300):
        """
        This function estimates entanglement of formation
        (EoF) of a TTO mixed state density matrix.

        Definition:
        EoF = min( sum( p_j * E( psi_j ) ) ),
        where the minimum is found over all the possible
        decompositions of density matrix to states psi_j
        and corresponding probabilities p_j. E() is the
        entropy of entanglement with respect to two halves
        of the system.

        Parameters
        ----------
        extra : int, optional
            The minimization for computing EoF
            is run over unitary matrices of
            dimension K0 x k_dim, where k_dim = K0 + <extra>,
            K0 is the number of probabilities kept in a mixed
            state density matrix.
            Default is 0.

        init_guess : np.ndarray or list of real numbers, optional
            Initial entries for elements of Hermitian matrix needed for
            constructing the unitary matrix.
            First k_dim entries are the values on the diagonal.
            Next (k_dim^2-k_dim)/2 entries are the values for real
            part of matrix elements above the diagonal.
            Next (k_dim^2-k_dim)/2 entries are the values for imaginary
            part of matrix elements above the diagonal.
            When initializing the Hermitian matrix, the elements above
            the diagonal will be filled with the values from <init_guess>
            list row by row.
            Default is None.

        unitary : 2D np.ndarray, 1st axis dimension must be equal to the
                  number of probabilities kept in a density matrix, optional
            The EoF is computed only for the density matrix decomposition defined
            with this unitary matrix and no optimization is done.
            Either init_guess or unitary must be specified.
            Default is None.

        maxiter : int, optional
            Maximal number of iterations for minimization.
            Default is 300.

        Return
        ------
        eof : float
            An estimate of the EoF of a given mixed state
            density matrix.

        Only if init_params is not None:
        params.x : np.ndarray
            Optimal solution for entries for Hermitian matrix defining
            the decomposition of density matrix.
        """

        if (init_guess is None) and (unitary is None):
            raise ValueError("Either init_guess or unitary must be specified.")

        if self.iso_center is None:
            logger.warning(
                "EoF can be computed only for TTO"
                " with gauge center at the uppermost tensor."
                " Installing a gauge center to the uppermost"
                " tensor."
            )
            self.install_gauge_center()
        elif any(self.iso_center) != 0:
            logger.warning(
                "EoF can be computed only for TTO"
                " with gauge center at the uppermost tensor."
                " Shifting a gauge center from %s to [0,0].",
                self.iso_center,
            )
            self.shift_gauge_center([0, 0])

        # take the root tensor of TTO, as all the important info
        # is stored in it
        root = self[0][0]
        n_20 = deepcopy(root.shape[0])
        n_21 = deepcopy(root.shape[1])
        # reshape it into matrix
        root = np.reshape(root, (root.shape[0] * root.shape[1], root.shape[2]))

        def func_target(params, unitary=None):
            """
            Takes an array of parameters and from it constructs the
            unitary matrix used to get the new decomposition of mixed state density
            matrix. Calculates the entropy of entanglement for each of
            the new pure states in this decomposition and multiplies it
            with the new probabilities to obtain the target function.

            Parameters
            ----------
            params : np.array
                Entry values for Hermitian matrix from which
                the unitary matrix is constructed.
                For the details of construction, see eof docstring
                above.

            Return
            ------
            target : float
                For EoF, we are looking for the decomposition which minimizes
                this target function:
                sum_j( pj * E(psi_j) ), where E() is entropy of entanglement
            """
            if unitary is None:
                # construct the hermitian matrix from input
                # parameters
                herm = np.zeros((k_dim, k_dim), dtype=np.complex128)

                num = int(0.5 * k_dim * (k_dim + 1))
                new_params = np.complex128(params[k_dim:num] + 1j * params[num:])
                ind = np.triu_indices_from(herm, 1)
                herm[ind] = new_params
                herm += herm.conj().T
                herm += np.diag(params[:k_dim])

                # get the unitary matrix from Hermitian by taking
                # an exponential
                unitary = scla.expm(herm * 1j)

                # take K0 rows for matrix to be compatible for
                # matrix matrix multiplication with <root> matrix
                unitary = unitary[:k_dim, :]

            # find the new root matrix for new decomposition
            new_root = np.matmul(root, unitary)

            # find the new probabilities
            new_prob = np.real(np.sum(new_root.conj() * new_root, axis=0))

            # now calculate the entropy of entanglement of each of the new
            # states in the decomposition (that is, every column of the
            # new_root matrix) - in code do loop over jj

            # The entanglement entropy E() for a pure state system composed of
            # two subsystems, A and B, is the Von Neumann entropy of the reduced
            # density matrix for any of the subsystems.

            # It can be shown that E(psi_AB) can be expressed through singular
            # values of the Schmidt decomposition of the system, by using the
            # squared singular values as probabilities for Von Neumann entropy.

            # reshape the matrix so it has two legs for two subsystems - needed
            # for Schmidt decomposition
            root_bipartite = np.reshape(new_root, (n_20, n_21, new_root.shape[1]))

            # find the minimization target value
            target = 0
            for jj in range(0, root_bipartite.shape[2]):
                # find the Schmidt decomposition singular values
                sing_vals = nla.svd(root_bipartite[:, :, jj], compute_uv=False)

                # use sing_vals to calculate the Von Neumann entropy
                # the sing_vals are divided with new_prob[jj] here, because of
                # the normalization of the new wave functions
                ent = self.entropy(
                    prob=sing_vals**2 / new_prob[jj], local_dim=self.local_dim
                )

                # the function which has to be minimized
                target += ent * new_prob[jj]

            return target

        if unitary is None:
            k_dim = root.shape[1] + extra

            # minimization
            params = scop.minimize(
                func_target,
                init_guess,
                method="Nelder-Mead",
                options={"maxiter": maxiter},
            )
            eof = params.fun
            return eof, params.x

        # Case with given unitary

        # compute EoF for the specific density matrix decomposition defined
        # with unitary
        eof = func_target(init_guess, unitary=unitary)
        return eof

    def tree(self, matrix_in, conv_params):
        """
        Transforms a given matrix into a tensor network as below:

        .. code-block::

                    |
            |       O
            O ---> / \
            |     O   O
                  |   |

        the first index of a matrix corresponds to the lower
        leg of the input tensor

        Parameters
        ----------

        self : :py:class:`TTO`
            Initialized TTO for which the tree method is used.
            From it, the local dimension and convergence parameters
            for SVD are extracted.

        matrix_in : ndarray
            Matrix to be transformed.

        conv_params : [TNConvergenceParameters]
            Input for handling convergence parameters.

        Returns
        -------

        tens_left, tens_mid, tens_right : ndarray
            Tensors of the second TN on the picture above,
            read from left to right.
            --> order of indices:
                tens_left, tens_right - [lower, upper]
                tens_mid - [lower left, upper, lower right]
        """
        dim = self.local_dim
        if len(set(list(dim))) != 1:
            raise QTeaLeavesError(
                "Different local dimensions not yet supported for TTO."
            )

        dim = dim[0]
        num_sites2 = int(mt.log(matrix_in.shape[0], dim) / 2)

        matrix_in = matrix_in.reshape(
            (int(dim**num_sites2), int(dim**num_sites2), matrix_in.shape[1]),
        )
        tens_left, tens_mid, _, _ = matrix_in.split_svd(
            [0], [2, 1], contract_singvals="R", conv_params=conv_params
        )

        tens_mid, tens_right, _, _ = tens_mid.split_svd(
            [0, 1],
            [2],
            perm_left=[0, 2, 1],
            perm_right=[1, 0],
            contract_singvals="L",
            conv_params=conv_params,
        )

        return tens_left, tens_mid, tens_right

    @classmethod
    def dm_to_tto(
        cls,
        num_sites,
        dim,
        psi,
        prob,
        conv_params=None,
        padding=None,
        tensor_backend=None,
    ):
        """
        Computes the TTO form of a given density matrix

        Parameters
        ----------
        num_sites : int
            Number of sites

        dim : int
            Local Hilbert space dimension

        psi,prob : matrix or vector, matrix or int
            - Mixed states :
                psi is a matrix with eigenstates as columns,
                prob is 1D array containing (possibly truncated)
                probabilities for each state
            - Pure states : psi is a state, prob = 1


        conv_params : :py:class::`TNConvergenceParameters`
            Input for handling convergence parameters.
            in particular, we are interested in:
            - the maximum bond dimension (max_bond_dimension)
            - the cut ratio (cut_ratio) after which the singular
            values in SVD are neglected, all singular values
            such that lambda/lambda_max <= eps
            are truncated

        padding : `np.array` of length 2 or `None`, optional
            Used to increase the bond dimension of the TTO. Also necessary to allow
            the growth of bond dimension in TDVP algorithms (two tensor updates).
            If not `None`, all the TTO tensors are padded such that the maximal bond
            dimension is equal to `padding[0]`. The value `padding[1]`
            tells with which value are we padding the tensors. Note that
            `padding[1]` should be very small, as it plays the role of
            numerical noise.
            Default to `None`.

        tensor_backend : `None` or instance of :class:`TensorBackend`
            Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.

        Return
        ------
        rho_tt : :py:class:`TTO`
            TTO form of the density matrix
        """
        if dim < 2:
            raise ValueError("Local dimension must be at least 2")

        # Initialize the TTO
        if conv_params is None:
            conv_params = TNConvergenceParameters()
            logger.warning(
                "Trying to initialize TTO without convergence parameters!"
                "Default parameters are used."
            )

        rho_tt = cls(
            num_sites,
            local_dim=dim,
            convergence_parameters=conv_params,
            tensor_backend=tensor_backend,
        )
        tensor_cls = rho_tt.tensor_backend.tensor_cls

        # First construct the density matrix so that it is split in two parts,
        # sqrt(pj)|psi_j> and sqrt(pj)<psi_j|
        # Take the first part and work with it, the rest will be the complex
        # conjugate

        psi = np.sqrt(prob) * psi
        if len(psi.shape) == 1:
            psi = psi.reshape((len(psi), 1))  # =O-

        psi = tensor_cls.from_elem_array(psi)

        # Start growing branches layer by layer, starting from the uppermost
        # tensor towards below (check what TTO.tree function does)
        # tree2 wil be the tensor in TTO layer and tree1,tree3 are used to
        # grow lower branches
        mid = [deepcopy(psi)]
        for ii in range(0, rho_tt.num_layers - 1):  # iterate to get all the layers
            mid_t = deepcopy(mid)
            mid = []
            lay = []
            for tensor in mid_t:
                tree1, tree2, tree3 = rho_tt.tree(tensor, conv_params=conv_params)
                mid.append(tree1)
                mid.append(tree3)
                lay.append(tree2)
            sites = rho_tt[ii].sites
            n_links = rho_tt[ii].max_num_links  # TEMPORARY SOLUTION
            rho_tt[ii] = TTNLayer.from_tensorlist(lay, dim)
            rho_tt[ii].sites = sites
            rho_tt[ii].max_num_links = n_links  # TEMPORARY SOLUTION

        lay = []

        # Reshape the lowest layer tensors to get the shape we need
        for tensor in mid:
            tensor = tensor.reshape((dim, dim, tensor.shape[1]))
            lay.append(tensor)
        sites = rho_tt[-1].sites
        n_links = rho_tt[-1].max_num_links  # TEMPORARY SOLUTION
        rho_tt[-1] = TTNLayer.from_tensorlist(lay)
        rho_tt[-1].sites = sites
        rho_tt[-1].max_num_links = (
            n_links  # TEMPORARY SOLUTION, WHY DO THEY GET RESET in TNNLayer?
        )

        if padding is not None:
            pad, pad_value = padding[0], padding[1]

            for lidx in range(rho_tt.num_layers):
                for tidx in range(rho_tt[lidx].num_tensors):
                    target = rho_tt[lidx, tidx]

                    # lowest layer, physical legs are not padded
                    if lidx != rho_tt.num_layers - 1:
                        target = target.expand_tensor(0, pad, ctrl=pad_value)
                        target = target.expand_tensor(1, pad, ctrl=pad_value)
                    # root tensor, upper leg is not padded
                    if lidx != 0:
                        target = target.expand_tensor(2, pad, ctrl=pad_value)

                    rho_tt[lidx, tidx] = target

            rho_tt.normalize()

        rho_tt.install_gauge_center()
        rho_tt.convert(rho_tt.tensor_backend.dtype, rho_tt.tensor_backend.device)

        return rho_tt

    def get_eigenstates(self, eigen_num_ll):
        """
        Extracts the eigenstates from the input TTO.

        Parameters
        ----------

        tto : :py:class:`TTO`
            The input TTO from which the eigenvector is extracted.

        eigen_num_ll : list of int
            The list of indices corresponding to the eigenstates to
            be extracted from the TTO.

        Returns
        -------

        ttn_list : list of :py:class:`TTN`
            The extracted eigenstates in TTN format.

        prob_list: list of float
            The corresponding probabilites.
        """
        # Make sure the iso center is at the top tensor, because we will rely on it
        self.iso_towards((0, 0))

        ttn_list = []
        prob_list = []

        # iterate over the target states
        for state_idx in eigen_num_ll:

            if state_idx >= self[0][0].shape[2]:
                raise ValueError(
                    f"The {state_idx+1}-th eigenvector is requested, "
                    "but only {self[0][0].shape[2]} are available."
                )

            # Tensor obtained by fixing the eigenstate index
            tensor = self[0][0].subtensor_along_link(2, state_idx, state_idx + 1)

            # Contraction between the new tensor and the leftmost one of the middle layer
            tensor = self[1][0].tensordot(tensor, ([2], [0]))

            # Generation of the TTN using the newly obtained tensor

            ll = [self[jj][:] for jj in range(self.num_layers - 1, 1, -1)]
            ll.extend([[tensor, self[1][1]]])

            new_ttn = TTN.from_tensor_list(
                ll,
                tensor_backend=self.tensor_backend,
                conv_params=self.convergence_parameters,
            ).copy()

            new_ttn.iso_center = (0, 0)

            # Normalization if the extracted eigenstate
            new_ttn.normalize()

            ttn_list.append(new_ttn)
            prob_list.append(self.probabilities[state_idx])

        return ttn_list, prob_list

    @classmethod
    def lptn_to_tto(cls, tensor_list, conv_params, tensor_backend):
        """
        Transforms the density matrix from LPTN to TTO form

        Parameters
        ----------
        tensor_list : list
            Tensors in LPTN, LPTN.tensors

        conv_params : :py:class:`TNConvergenceParameters`
            Input for handling convergence parameters
            in particular, we are interested in:
            - the maximum bond dimension (max_bond_dimension)
            - the cut ratio (cut_ratio) after which the singular
            values in SVD are neglected, all singular values
            such that lambda/lambda_max <= eps
            are truncated

        tensor_backend : `None` or instance of :class:`TensorBackend`
            Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.

        Return
        ------
        tto : :py:class:`TTO`
            TTO form of the input LPTN
        """

        num_sites = len(tensor_list)
        dim = tensor_list[0].shape[1]

        tto = cls(
            num_sites,
            local_dim=dim,
            convergence_parameters=conv_params,
            tensor_backend=tensor_backend,
        )

        for ii in range(tto.num_layers - 1, 0, -1):
            work = tensor_list
            tensor_list = []
            for jj in range(0, len(work), 2):
                # First combine and merge tensors from the tensor_list
                # (initially LPTN tensors) into pairs
                work2 = work[jj].tensordot(work[jj + 1], [[3], [0]])
                work2 = work2.transpose([1, 3, 0, 2, 4, 5])

                #                 ||
                # SVD decompose  --O--  into l_mat,r_mat so that lower legs
                #                 ||   go to l_mat and the rest goes to r_mat

                # we do the SVD decomposition, truncate the
                # singular values and contract them into r_mat
                l_mat, r_mat, _, _ = work2.split_svd(
                    [0, 1],
                    [2, 3, 4, 5],
                    contract_singvals="R",
                    conv_params=conv_params,
                )

                # --> l_mat will be one of the tensors in TTO layer
                tto[ii][jj // 2] = l_mat

                #                                  ||
                # Now SVD decompose r_mat matrix --O-- so that lower and side legs
                #                                  |
                # go to tens_down and upper legs go to tens_up
                # tens_down is contracted with singular values, ignore tens_up because
                # it is unitary and it cancels out with the
                # complex conjugate from the upper part of the TN
                tens_down, _, _, _ = r_mat.split_svd(
                    [1, 0, 4],
                    [2, 3],
                    perm_left=[0, 1, 3, 2],
                    contract_singvals="L",
                    conv_params=conv_params,
                )

                # Now append tens_down to the new tensor_list and repeat the same
                # procedure in next iteration over ii to get the upper layers
                tensor_list.append(deepcopy(tens_down))

                # The whole procedure will be repeated with the new
                # lptn-like list stored in tensor_list.

        # For the uppermost tensor we do not need to do all of the above.
        # Contract the two remaining tensors from tensor_list and reshape
        # them to get the shape we need.
        work2 = tensor_list[0].tensordot(tensor_list[1], [[3], [0]])
        work2 = work2.transpose([0, 1, 2, 4, 3, 5])
        work2.reshape_update(
            (work2.shape[1], work2.shape[2] * work2.shape[3], work2.shape[4])
        )

        # To truncate the probabilities, SVD the tensor so that lower and
        # side legs + singular values go to work2.
        # Ignore the other tensor because it is unitary and cancels out with the
        # complex conjugate from the upper part of the TTO.
        work2, _, _, _ = work2.split_svd(
            [0, 2],
            [1],
            contract_singvals="L",
            conv_params=conv_params,
        )
        tto[0][0] = deepcopy(work2)
        tto.iso_center = [0, 0]

        tto.convert(tto.tensor_backend.dtype, tto.tensor_backend.device)
        return tto

    @classmethod
    def lptn_to_tto_iso(cls, tensor_list, conv_params, tensor_backend):
        """
        Transforms the density matrix from LPTN to TTO form,
        keeping the TN isometrized throughout the procedure.

        Parameters
        ----------
        tensor_list : list
            List of tensors in LPTN, LPTN.tensors.

        conv_params : :py:class:`TNConvergenceParameters`
            Input for handling convergence parameters
            in particular, we are interested in:
            - the maximum bond dimension (max_bond_dimension)
            - the maximum Kraus dimension (max_kraus_dimension), i.e.,
            Dimension of link connecting two sides
            of TTO (upper link of the root tensor).
            - the cut ratio (cut_ratio) after which the singular
            values in SVD are neglected, all singular values
            such that lambda/lambda_max <= eps
            are truncated.

        Return
        ------
        tto : :py:class:`TTO`
            TTO form of the input LPTN

        norm_track : float
            Norm of the TTO obtained by keeping
            the track of singular value truncations.
            Note that this is not the actual norm of the TTO,
            as the singular values are renormalized after
            each truncation and therefore actual norm is kept
            to 1. Higher values are better, norm_track of
            1 means no truncations.
        """
        if conv_params.trunc_tracking_mode != "C":
            logger.warning("Running TTO conversion without trunc tracking `C`.")

        num_sites = len(tensor_list)
        dim = tensor_list[0].shape[1]
        k_0 = conv_params.max_kraus_dimension

        tto = cls(
            num_sites,
            local_dim=dim,
            convergence_parameters=conv_params,
            tensor_backend=tensor_backend,
        )

        conv_params_lptn = TNConvergenceParameters(
            max_bond_dimension=int(dim**num_sites), cut_ratio=1e-8
        )

        norm_track = 1

        for ii in range(tto.num_layers - 1, 0, -1):
            # first move the isometry center of the LPTN tensors to the first
            # tensor
            n_lptn = len(tensor_list)
            lptn_work = LPTN.from_tensor_list(
                tensor_list,
                conv_params=conv_params_lptn,
                iso_center=[n_lptn - 1, n_lptn + 1],
            )
            lptn_work.shift_gauge_center([0, 2])

            work = deepcopy(lptn_work.tensors)
            tensor_list = []

            for jj in range(0, len(work), 2):
                # combine and merge tensors from the tensor_list
                # (initially LPTN tensors) into pairs
                work2 = work[jj].tensordot(work[jj + 1], [[3], [0]])
                work2 = work2.transpose([1, 3, 0, 2, 4, 5])

                #                 ||
                # SVD decompose  --O--  into l_mat,r_mat so that lower legs
                #                 ||   go to l_mat and the rest goes to r_mat

                # we do the SVD decomposition, truncate the
                # singular values and contract them into r_mat
                # Remark: work2 matrix is divided by 100 to solve some SVD convergence issue,
                # this is taken into account later so that the results remain the same.
                l_mat, r_mat, _, track = work2.split_svd(
                    [0, 1],
                    [2, 3, 4, 5],
                    contract_singvals="R",
                    conv_params=conv_params,
                )

                # track the norm loss
                norm_track *= 1 - (track**2).sum()

                # --> l_mat will be one of the tensors in TTO layer
                tto[ii][jj // 2] = deepcopy(l_mat)

                #                                  ||
                # Now SVD decompose r_mat matrix --O-- so that lower and side legs
                #                                  |

                # go to tens_down and upper legs go to tens_up
                # tens_down is contracted with singular values, ignore tens_up because
                # it is unitary and it cancels out with the
                # complex conjugate from the upper part of the TN
                tens_down, _, _, track = r_mat.split_svd(
                    [1, 0, 4],
                    [2, 3],
                    perm_left=[0, 1, 3, 2],
                    contract_singvals="L",
                    conv_params=conv_params,
                )

                # track the norm loss
                norm_track *= 1 - (track**2).sum()

                # QR decompose tens_down so that the tens_down becomes unitary, and contract
                # the R matrix with the next left tensor in order to shift the isometry center
                tens_down, r_mat = tens_down.split_qr([0, 1, 2], [3])
                if jj != (len(work) - 2):
                    work[jj + 2] = r_mat.tensordot(work[jj + 2], [[1], [0]])

                # Now append tens_down to the new tensor_list and repeat the same
                # procedure in next iteration over ii to get the upper layers
                tensor_list.append(deepcopy(tens_down))

                # The whole procedure will be repeated with the new
                # lptn-like list stored in tensor_list.

        # For the uppermost tensor we do not need to do all of the above.
        # Contract the two remaining tensors from tensor_list and reshape
        # them to get the shape we need.
        work2 = tensor_list[0].tensordot(tensor_list[1], [[3], [0]])
        work2 = np.transpose(work2, axes=[0, 1, 2, 4, 3, 5])
        work2 = np.reshape(
            work2, (work2.shape[1], work2.shape[2] * work2.shape[3], work2.shape[4])
        )

        # To truncate the probabilities, SVD the tensor so that lower and
        # side legs + singular values go to work2.
        # Ignore the other tensor because it is unitary and cancels out with the
        # complex conjugate from the upper part of the TTO.

        # Remark: the multiplication with 100 in tto.tSVD is because the SVD algorithm
        # otherwise has a problem with convergence. The result is later divided with
        # 100 to restore the original value.
        # conv_params.cut_ratio = np.sqrt(conv_params.cut_ratio)
        conv_params2 = TNConvergenceParameters(max_bond_dimension=k_0, cut_ratio=1e-8)
        work2, _, _, track = work2.split_svd(
            [0, 2],
            [1],
            contract_singvals="L",
            conv_params=conv_params2,
        )
        # track the norm loss
        norm_track *= 1 - (track**2).sum()
        tto[0][0] = deepcopy(work2)
        tto.iso_center = [0, 0]

        return tto, norm_track

    @classmethod
    # pylint: disable-next=too-many-statements, too-many-branches
    def lptn_to_tto_move_tensors(cls, tensor_list, conv_params, tensor_backend):
        # pylint: disable=anomalous-backslash-in-string
        """
        Transforms the density matrix from LPTN to TTO form.

        Parameters
        ----------
        tensor_list : list
            Tensors in LPTN, LPTN.tensors

        conv_params : :py:class:`TNConvergenceParameters`
            Input for handling convergence parameters
            in particular, we are interested in:
            - the maximum bond dimension (max_bond_dimension)
            - the maximum Kraus dimension (max_kraus_dimension), i.e.,
            Dimension of link connecting two sides
            of TTO (upper link of the root tensor).
            - the cut ratio (cut_ratio) after which the singular
            values in SVD are neglected, all singular values
            such that lambda/lambda_max <= eps
            are truncated

        tensor_backend : `None` or instance of :class:`TensorBackend`
            Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.

        Return
        ------
        tto : :py:class:`TTO`
            TTO form of the input LPTN

        norm_track : float
            Norm of the TTO obtained by keeping
            the track of singular value truncations.
            Note that this is not the actual norm of the TTO,
            as the singular values are renormalized after
            each truncation and therefore actual norm is kept
            to 1. Higher values are better, norm_track of
            1 means no truncations.

        Details
        -------

        .. code-block::

            LPTN + TTO
                                 |
                                 1
                                / \
                               /   \
                              1     1
                             / \   / \
                            /  |   |  \
                           1   1   1   1
              |  |  |  |  /\  / \ / \ / \  |  |  |  |
            --L--L--L--L--               --L--L--L--L--
              |  |  |  |                   |  |  |  |

        .. code-block::

            LPTN after QR + TTO
                                 |
                                 1
                                / \
                               /   \
                              1     1
                             / \   / \
                            /  |   |  \
                           1   T   T   1
                          /\  / \ / \ / \           |
            --R--R--R--R--               --R--R--R--L--
              |  |  |  |                   |  |  |  |
              Q  Q  Q  Q                   Q  Q  Q
             /| /| /| /|                  /| /| /|

        with

        * L: being an original LPTN site
        * 1: being identities with two links at chi and one trivial
             link. chi is the bond dimension at the center of the LPTN.
             The links with chi point to the LPTN halves.
        * T : trivial tensor with all link identical irreps.
        * R, Q: separating the horizontal links in the LPTN.

        The algorithm now:

        1) Move tensor R to the top (we can move an additional leg easily)
        2) Contract Q and merge the Kraus link of the top tensor with the
           Kraus link inside Q.
        3) New top tensor has four links, move Hilbert-space link down
           to its position in the TTO.
        4) Remove dummy link and keep local link just moved down.
        5) Re-iterate.

        Procedure for last tensor is sligthly modified.

        """
        # pylint: enable=anomalous-backslash-in-string
        num_sites = len(tensor_list)
        idx_center_r = num_sites // 2
        idx_center_l = num_sites // 2 - 1

        if conv_params.trunc_tracking_mode != "C":
            logger.warning("Running TTO conversion without trunc tracking `C`.")

        conv_k0 = TNConvergenceParameters(
            max_bond_dimension=conv_params.max_kraus_dimension,
            cut_ratio=conv_params.cut_ratio,
        )

        if abs(tensor_list[idx_center_l].norm() - 1.0) > 10 * tensor_list[0].dtype_eps:
            # We require the LTPN to have its isometry center on the left
            # tensor with respect to the center. The condition is not sufficient,
            # but a good starting point.
            norm = tensor_list[idx_center_l].norm()
            raise ValueError(
                f"LPTN must be isometrized at the left center sites, but norm={norm}."
            )

        if abs(np.log2(num_sites) - int(np.log2(num_sites))) > 1e-15:
            raise ValueError("Number of sites must be power of 2.")

        # Prepare a trival TTO connecting the two LPTN halves
        # ---------------------------------------------------

        dense_backend = deepcopy(tensor_backend)
        dense_backend.tensor_cls = tensor_backend.base_tensor_cls

        # Generate TTN of the right shape
        psi = TTN(
            num_sites, conv_params, tensor_backend=dense_backend, initialize="vacuum"
        )
        obj = TTO.ttn_to_tto(psi, conv_params=conv_params, tensor_backend=dense_backend)

        # We need two type of links to construct the TTO, the center link of the LPTN
        # and a dummy link.
        link_a = tensor_list[0].dummy_link(tensor_list[0].links[0])
        link_b = tensor_list[idx_center_r].links[0]

        # We construct four type of tensors for the TTO
        #
        # a) all trivial links
        # b) identities with trivial link for left child
        # c) identities with trivial link for right child
        # d) identities with trivial link for parent link
        eye_a = tensor_list[idx_center_r].eye_like(link_a)
        eye_b = tensor_list[idx_center_r].eye_like(link_b)
        tensor_a = eye_a.copy().attach_dummy_link(1, is_outgoing=False)
        tensor_b = eye_b.copy().attach_dummy_link(0, is_outgoing=False)
        tensor_c = eye_b.copy().attach_dummy_link(1, is_outgoing=False)

        _, tmp = eye_b.split_qr([1], [0], is_q_link_outgoing=True)
        tensor_d = tmp.transpose([1, 0]).attach_dummy_link(2, is_outgoing=True)

        tto_list = []
        num_layers = int(np.log2(num_sites))
        layer_size = num_sites
        for ii in range(num_layers):
            layer_size = layer_size // 2
            layer_list = [tensor_a] * layer_size

            layer_list[0] = tensor_c
            layer_list[-1] = tensor_b

            tto_list.append(layer_list)

        tto_list[-1][0] = tensor_d
        tto_list = tto_list[::-1]

        # We cannot use tto_list to generate TTO with `from_tensor_list`
        # because the local Hilbert space has dimension 1 and will not
        # be counted as sites
        local_links = [tensor_list[ii].links[1] for ii in range(num_sites)]

        for ii, layer in enumerate(tto_list):
            obj[ii].singvals = [None] * len(obj[ii].singvals)
            obj[ii].local_dim = local_links
            # pylint: disable-next=protected-access
            obj[ii]._tensor_backend = tensor_backend
            for jj, elem in enumerate(layer):
                obj[ii][jj] = elem

        # It is defined in the `abstract_tn.py` ...
        # pylint: disable-next=attribute-defined-outside-init
        obj._tensor_backend = tensor_backend

        # The isometry center is not existant yet, but as soon as we contract
        # the first LPTN into the network, it will be at:
        obj.iso_center = (obj.num_layers - 1, 0)

        # Prepare the LTPN ("fuse" links via QR)
        # ----------------

        q_list = []
        r_list = []
        for ii, tens in enumerate(tensor_list):
            qtens, rtens = tens.split_qr([1, 2], [0, 3])

            # qtens has legs: ket, kraus-bra, fuse
            # rtens has legs: fuse, left, right

            if ii >= num_sites // 2:
                # Tree expect leaves to have incoming legs, but we
                # can flip links accordingly
                rtens.flip_links_update([1, 2])

            q_list.append(qtens)
            r_list.append(rtens)

        # Move tensors into the TTO
        # -------------------------

        norm_track = 1.0

        # ii refers to layer
        ii = num_layers - 1

        move_left = True
        idx_del_l = 1
        idx_del_r = 0

        for _ in range(num_sites - 1):
            # indices: idx is index in LPTN, jj of the tensor in the
            # bottom layer of the TTO.
            if move_left:
                idx = idx_center_l
                idx_center_l -= 1
                jj = 0
                c_idx_tto = 0
                c_idx_lptn = 2
                perm_a = [3, 0, 1, 2]
            else:
                idx = idx_center_r
                idx_center_r += 1
                jj = num_sites // 2 - 1
                c_idx_tto = 1
                c_idx_lptn = 1
                perm_a = [0, 3, 1, 2]

            tens = r_list[idx]

            track_cuts = obj.iso_towards([ii, jj], trunc=True, conv_params=conv_params)
            norm_track *= np.prod(1 - track_cuts)

            tensor = obj[ii][jj].tensordot(r_list[idx], ([c_idx_tto], [c_idx_lptn]))
            obj[ii][jj] = tensor.transpose(perm_a)
            # New tensor in tree with legs: left, right, parent, additional

            # Move additional leg to top tensor and merge with Kraus leg
            path = np.array([[ii, jj], [0, 0]], dtype=int)
            track_cuts = obj.leg_towards(path, trunc=True, conv_params=conv_params)
            norm_track *= np.prod(1 - track_cuts)
            tensor = obj[0][0].tensordot(q_list[idx], ([3], [2]))
            # legs: left, right, kraus, ket, kraus-bra

            _, top, _, track_cut = tensor.split_svd(
                [2, 4],
                [0, 1, 3],
                contract_singvals="R",
                perm_right=[1, 2, 0, 3],
                is_link_outgoing_left=False,
                conv_params=conv_k0,
            )
            # right before perm: kraus, left, right, ket
            obj[0][0] = top
            norm_track *= 1 - (track_cut**2).sum()

            jj = idx // 2
            if move_left:
                idx_del = idx_del_l
                idx_del_l = (idx_del_l + 1) % 2
            else:
                idx_del = idx_del_r
                idx_del_r = (idx_del_r + 1) % 2

            if idx_del == 0:
                perm = [2, 0, 1]
            else:
                perm = [0, 2, 1]

            # Move additional leg downwards (only local Hilbert space remains)
            path = np.array([[0, 0], [ii, jj]], dtype=int)
            track_cuts = obj.leg_towards(path, trunc=True, conv_params=conv_params)
            norm_track *= np.prod(1 - track_cuts)
            tensor = obj[ii, jj]
            tensor.remove_dummy_link(idx_del)
            if perm is not None:
                obj[ii][jj] = tensor.transpose(perm)

            # Next iteration, move site into TTO from other side
            move_left = not move_left

        # Take care of the last tensor carrying the global sector
        jj = num_sites // 2 - 1
        track_cuts = obj.iso_towards([ii, jj], trunc=True, conv_params=conv_params)
        norm_track *= np.prod(1 - track_cuts)

        # Just need to flip link to the left neighbor, global sector link
        # will be moved and SVDed away
        last_site = tensor_list[-1].copy().flip_links_update([0])
        tensor = obj[ii][jj].tensordot(last_site, ([1], [0]))
        # links are: left, parent, ket, kraus-bra, global
        qtens, rtens = tensor.split_qr([3, 4], [0, 1, 2])
        obj[ii][jj] = rtens.transpose([1, 3, 2, 0])

        path = np.array([[ii, jj], [0, 0]], dtype=int)
        track_cuts = obj.leg_towards(path, trunc=True, conv_params=conv_params)
        norm_track *= np.prod(1 - track_cuts)

        top, _, sing_val, track_cut = obj[0][0].split_svd(
            [0, 1],
            [2, 3],
            contract_singvals="L",
            is_link_outgoing_left=True,
            conv_params=conv_k0,
        )
        obj[0][0] = top
        norm_track *= 1 - (track_cut**2).sum()

        # In case of symmetries, flatten returns one vector and sorts it
        prob = sing_val.flatten() ** 2

        obj._probabilities = prob

        # Isometry center is at (0, 0)
        obj.iso_center = (0, 0)

        return obj, norm_track

    def to_ttn(self):
        """
        Converts a pure state TTO (projector) into a TTN.
        """

        if self[0, 0].shape[-1] != 1:
            raise QTeaLeavesError(
                "Root tensors upper leg dimension is larger than 1,"
                + " TTO is not a pure state! Can not convert to TTN."
            )
        top_tensor = self[1, 0].tensordot(self[0, 0], [[2], [0]])
        tensor_list = []
        for lidx in range(self.num_layers - 1, 0, -1):
            tensor_list.append(self[lidx])
        tensor_list[-1][0] = top_tensor
        ttn = TTN.from_tensor_list(tensor_list)
        return ttn

    def to_statevector(self, qiskit_order=False, max_qubit_equivalent=20):
        """
        Decompose a given pure state TTO (projector) into statevector form.

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
        """
        return self.to_ttn().to_statevector(
            qiskit_order=qiskit_order, max_qubit_equivalent=max_qubit_equivalent
        )

    @classmethod
    def ttn_to_tto(
        cls,
        ttn,
        conv_params=None,
        no_truncation=True,
        padding=None,
        tensor_backend=None,
    ):
        """
        Converts a state (TTN) to the respective projector (TTO).

        Parameters
        ----------
        ttn : :py:class:`TTN`
            The TTN to be converted.

        conv_params : :py:class:`TNConvergenceParameters`, optional
            Convergence parameters for the resulting TTO. If `None` is given,
            then use the convergence parameters of the input TTN.
            Default to `None`.

        no_truncation : boolean, optional
            Allows to run SVD without truncation.
            Default to `True`.

        padding : `np.array` of length 2 or `None`, optional
            Used to increase the bond dimension of the TTO. Also necessary to allow
            the growth of bond dimension in TDVP algorithms (two tensor updates).
            If not `None`, all the TTO tensors are padded such that the maximal bond
            dimension is equal to `padding[0]`. The value `padding[1]`
            tells with which value are we padding the tensors. Note that
            `padding[1]` should be very small, as it plays the role of
            numerical noise.
            Default to `None`.

        tensor_backend : `None` or instance of :class:`TensorBackend`
            Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.

        Returns
        -------
        tto : :py:class:`TTO`
            TTO form of the input TTN
        """
        if conv_params is None:
            conv_params = ttn.convergence_parameters

        tens_u, tens_v, _, _ = ttn[0, 0].split_svd(
            legs_left=[0, 1],
            legs_right=[2, 3],
            contract_singvals="R",
            no_truncation=no_truncation,
            conv_params=conv_params,
        )

        # Initialization with random is necessary (empty has bug, ground/vacuum
        # lead to infinite recursion when calling TTO.state_from_local_states -->
        # TTN.from_local_states --> TTN._initialize_tree --> self/TTO.from_local_states
        tto = cls(
            num_sites=ttn.num_sites,
            local_dim=ttn.local_dim,
            convergence_parameters=conv_params,
            tensor_backend=tensor_backend,
            initialize="random",
        )

        tto[0, 0] = tens_v
        tto[1, 0] = tens_u
        tto[1, 1] = ttn[0, 1]

        for idx in range(ttn.num_layers):
            if idx > 0:
                tto[idx + 1] = ttn[idx]
                tto[idx + 1].layer_idx = idx + 1

        if padding is not None:
            pad, pad_value = padding[0], padding[1]

            for lidx in range(tto.num_layers):
                for tidx in range(tto[lidx].num_tensors):
                    target = tto[lidx, tidx]

                    # lowest layer, physical legs are not padded
                    if lidx != tto.num_layers - 1:
                        target = target.expand_tensor(0, pad, ctrl=pad_value)
                        target = target.expand_tensor(1, pad, ctrl=pad_value)
                    # root tensor, upper leg is not padded
                    if lidx != 0:
                        target = target.expand_tensor(2, pad, ctrl=pad_value)

                    tto[lidx, tidx] = target

            tto.normalize()

        tto.install_gauge_center()

        return tto

    @classmethod
    def product_state_from_local_states(
        cls,
        mat,
        padding=None,
        convergence_parameters=None,
        tensor_backend=None,
    ):
        """
        Construct a pure product state in TTO form, given the local
        states of each of the sites.

        Parameters
        ----------
        mat : 2D `np.array`
            Matrix with ii-th row being a (normalized) local state of
            the ii-th site.
            Number of rows is therefore equal to the number of sites,
            and number of columns corresponds to the local dimension.

        padding : `np.array` of length 2 or `None`, optional
            Used to increase the bond dimension of the TTO. Also necessary to allow
            the growth of bond dimension in TDVP algorithms (two tensor updates).
            If not `None`, all the TTO tensors are padded such that the maximal bond
            dimension is equal to `padding[0]`. The value `padding[1]`
            tells with which value are we padding the tensors. Note that
            `padding[1]` should be very small, as it plays the role of
            numerical noise.
            Default to `None`.

        convergence_parameters : :py:class:`TNConvergenceParameters`, optional
            Convergence parameters for the new TT0.

        tensor_backend : `None` or instance of :class:`TensorBackend`
            Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.

        Return
        ------
        prod_tto : :py:class:`TTO`
            Corresponding product state TTO.
        """

        prod_ttn = TTN.product_state_from_local_states(
            mat=mat,
            padding=padding,
            convergence_parameters=convergence_parameters,
            tensor_backend=tensor_backend,
        )
        prod_ttn.normalize()  # do we need this for padding?
        prod_tto = cls.ttn_to_tto(
            prod_ttn, conv_params=convergence_parameters, tensor_backend=tensor_backend
        )

        return prod_tto

    @classmethod
    def product_state_from_local_states_2d(
        cls,
        mat_2d,
        padding=None,
        mapping="HilbertCurveMap",
        return_map=False,
        convergence_parameters=None,
        tensor_backend=None,
    ):
        """
        Construct a pure product state in TTO form, given the local
        states of each of the sites.

        Parameters
        ----------
        mat_2d : np.array of rank 2
            Array with third axis being a (normalized) local state of
            the (ii,jj)-th site (where ii and jj are indices of the
            first and second axes).
            Product of first two axes' dimensions is therefore equal
            to the total number of sites, and third axis dimension
            corresponds to the local dimension.

        padding : `np.array` of length 2 or `None`, optional
            Used to increase the bond dimension of the TTO. Also necessary to allow
            the growth of bond dimension in TDVP algorithms (two tensor updates).
            If not `None`, all the TTO tensors are padded such that the maximal bond
            dimension is equal to `padding[0]`. The value `padding[1]`
            tells with which value are we padding the tensors. Note that
            `padding[1]` should be very small, as it plays the role of
            numerical noise.
            Default to `None`.

        mapping : string or instance of :py:class:`HilbertCurveMap`,
                  optional
            Which 2d to 1d mapping to use. Possible inputs are:
            'HilbertCurveMap', 'SnakeMap', and 'ZigZagMap'.
            Default is 'HilbertCurveMap'.

        return_map : boolean, optional
            If True, the function returns array `map` with indices
            of 2d to 1d mapping.
            Default to False.

        convergence_parameters : :py:class:`TNConvergenceParameters`, optional
            Convergence parameters for the new TTO.

        Return
        ------
        prod_tto : :py:class:`TTO`
            Corresponding product state TTO.
        map : np.array, returned only if return_map==True
            Nx2 Matrix, where N is a total number of particles.
            The values in the ii-th row of the matrix denote
            particle's position in a corresponding 2d grid.
        """
        if return_map:
            prod_ttn, map_array = TTN.product_state_from_local_states_2d(
                mat_2d=mat_2d,
                padding=padding,
                mapping=mapping,
                return_map=return_map,
                convergence_parameters=convergence_parameters,
                tensor_backend=tensor_backend,
            )
            prod_ttn.normalize()
            prod_tto = cls.ttn_to_tto(
                prod_ttn,
                conv_params=convergence_parameters,
                tensor_backend=tensor_backend,
            )

            return prod_tto, map_array

        prod_ttn = TTN.product_state_from_local_states_2d(
            mat_2d=mat_2d,
            padding=padding,
            mapping=mapping,
            return_map=return_map,
            convergence_parameters=convergence_parameters,
            tensor_backend=tensor_backend,
        )
        prod_ttn.normalize()
        prod_tto = cls.ttn_to_tto(
            prod_ttn,
            conv_params=convergence_parameters,
            tensor_backend=tensor_backend,
        )

        return prod_tto

    def unset_all_singvals(self):
        """
        Unset all the singvals in the TTO due to a
        local operation that is modifying the global
        state and the entanglement structure, such as
        a projective measurement.

        Returns
        -------
        None
        """
        for layer in self:
            for ii in range(layer.num_tensors):
                layer.unset_singvals(ii)

    # --------------------------------------------------------------------------
    #                     Unsorted
    # --------------------------------------------------------------------------

    def _get_parent_info(self, pos):
        """
        Return informations about the parent of
        the tensor in position `pos`. The parent is
        the leg pointing upwards.
        Works only for binary trees.

        Parameters
        ----------
        pos : Tuple[int]
            Position in the tree as `(layer_idx, tensor_idx)`

        Returns
        -------

        link : int
            Link index of the tensor at `pos` which connects to
            the parent tensor.

        info : list of three ints
            Layer index of parent tensor, tensor index within
            layer of parent tensor, link index in parent tensor
            connecting to tensor at `pos`.
        """
        self.assert_binary_tree()
        info = -np.ones(3, dtype=int)
        link = 2

        if list(pos) == [0, 0]:
            # Pick one of the children, with [1, 0] the two
            # last steps of the default sweep order are the same
            return 0, [1, 0, 1]

        info[0] = max(0, pos[0] - 1)
        info[1] = pos[1] // 2
        info[2] = pos[1] % 2

        return link, list(info)

    def _iter_all_links(self, pos):
        """
        Return an iterator over all the links of a position
        `pos` in the TTO.

        Parameters
        ----------
        pos : Tuple[int]
            Position in the tree as `(layer_idx, tensor_idx)`

        Returns
        -------
        Tuple[int]
            Tuple of `(layer_link, tensor_link, leg_toward_link)`
        """
        yield from self._iter_children_pos(pos)

        if list(pos) != [0, 0]:
            _, info = self._get_parent_info(pos)
            yield tuple(info)

        else:
            yield (None, None, None)

    #########################################################################
    ############################ Apply methods ##############################
    #########################################################################
    def apply_local_kraus_channel(self, kraus_ops):
        """
        Apply local Kraus channels to tensor network
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
        conv_params = self.convergence_parameters
        singvals_cut = 0.0

        lidx = self.num_layers - 1

        for key in kraus_ops:

            sidx = key
            kraus_tensor_contr = kraus_ops[key]
            tidx = sidx // 2
            pos = np.array([[lidx, tidx], [0, 0]])

            # move kraus tensor to computational device
            kraus_tensor_contr.convert(device=self.computational_device)

            self.iso_towards(tuple(pos[0]))
            self[lidx, tidx] = self[lidx, tidx].tensordot(
                kraus_tensor_contr, contr_idx=[[sidx % 2], [2]]
            )
            # move kraus tensor back to memory device
            kraus_tensor_contr.convert(device=self.memory_device)

            if sidx % 2 == 0:
                self[lidx, tidx] = self[lidx, tidx].transpose((3, 0, 1, 2))

            else:
                self[lidx, tidx] = self[lidx, tidx].transpose((0, 3, 1, 2))

            singvals_cut += self.leg_towards(
                pos, trunc=True, conv_params=conv_params
            ).sum()  # shift leg via truncated svd to control d_max
            self[0, 0].reshape_update((self[0, 0].shape[0], self[0, 0].shape[1], -1))
            self._probabilities = None
            singvals_cut += self.trunc_probabilities(return_singvals=True).sum()

        return singvals_cut

    #########################################################################
    ######################### Measurement methods ###########################
    #########################################################################

    def meas_bond_entropy(self):
        """
        Measure the entropy(!) along all possible connected partitions of the TTO
        using the Von Neumann entropy, which is not an entanglement measure if the state is mixed.
        Von Neumann entropy :math:`S_V` is defined as:

        .. math::

            S_V = - \\sum_i^{\\chi} s^2 \\log2( s^2)

        with :math:`s` the singular values

        Return
        ------
        measures : dict
            Keys are the range of sites to which the entropy corresponds
        """
        measures = {}

        if self.iso_center is None:
            raise ValueError("There is no iso-center when trying to measure.")
        if list(self.iso_center) != list(self.default_iso_pos):
            self.iso_towards(self.default_iso_pos)

        # total system entropy
        local_dim = self.local_dim
        key = tuple([0, self.num_sites - 1])
        measures[key] = self.entropy(local_dim=local_dim)
        tlog, tsum = self[0][0].get_attr("log", "sum")
        local_dim = self.local_dim

        for layer_idx, layer in enumerate(self.layers):
            for idx, singvals in enumerate(layer.singvals):
                # If the singvals are not present for some reason the bond entropy
                # value for that bond is set to None

                if singvals is None:
                    s_von_neumann = None
                else:
                    # Remove 0s from the singvals (they might come from the from_statevector method)
                    singvals = singvals.flatten()
                    singvals = singvals[singvals > 0]

                    if isinstance(local_dim, int):
                        rescale = mt.log(local_dim)
                    elif len(set(local_dim)) > 1:
                        logger_warning(
                            "Using log based on first Hilbert space for entropy in "
                            "TTO but different local dimensions."
                        )
                        rescale = mt.log(local_dim[0])
                    else:
                        rescale = mt.log(local_dim[0])
                    s_von_neumann = -tsum(singvals**2 * tlog(singvals**2) / rescale)

                    s_von_neumann = self[0][0].get_of(s_von_neumann)

                pos_src = (layer_idx, idx)

                if layer_idx != 0:

                    _, pos_parent = self._get_parent_info(pos_src)
                    pos_parent = pos_parent[:2]
                    sites_src, _ = self.get_bipartition_link(pos_src, pos_parent)

                    key = tuple([np.min(sites_src), np.max(sites_src)])

                    measures[key] = s_von_neumann

        return measures

    # pylint: disable-next=too-many-branches, too-many-statements
    def meas_log_negativity(self, mode="H"):
        """
        Measures the logarithmic negativity for a set of partitions.
        Computation can be expensive if big tensors are involved!
        Starting from the root tensor of the TTO, we contract it with
        a tensor from the layer below and split the resulting tensor afterwards
        such that we get a new "root".
        This new root contains the information on entanglement between a different partition.
        We repeat this procedure until we reach the desired partition.

        Parameters
        -------
        mode : str, optional
            Measurment mode determining what partitions are measured. Available are:
            - "H": only the left (right) half of the system.
            - "L": all available partitions that overlab with the left boundary of the system.
            - "R": all available partitions that overlab with the right boundary of the system
            - "LR": the combination of "L" and "R".
            - "A": all partitons native in the TTO.
            Default to "H".

        Return
        ------
        measures : dict
            Keys are the range of sites to which the log negativity corresponds
        """

        measures = {}

        if self.iso_center is None:
            raise ValueError("There is no iso-center when trying to measure.")
        if list(self.iso_center) != list(self.default_iso_pos):
            self.iso_towards(self.default_iso_pos)

        local_dim = self.local_dim
        conv_params = self.convergence_parameters

        def _get_key(pos):

            _, pos_parent = self._get_parent_info(tuple(pos))
            pos_parent = pos_parent[:2]
            sites_src, _ = self.get_bipartition_link(tuple(pos), pos_parent)
            key = tuple([np.min(sites_src), np.max(sites_src)])

            return key

        if mode == "H":

            pos_sub = [1, 0]
            key = _get_key(pos_sub)

            root = self[0, 0]
            log_neg = self.log_negativity(root=root, local_dim=local_dim)
            measures[key] = log_neg

            return measures

        if mode in ["L", "LR"]:

            root = self[0, 0].copy()  # since the root is modified we need a copy

            for layer_idx in range(self.num_layers - 1):

                pos_sub = [layer_idx + 1, 0]
                key = _get_key(pos_sub)

                if layer_idx > 0:

                    self[layer_idx, 0].convert(device=self.computational_device)
                    root = root.tensordot(self[layer_idx, 0], [[0], [2]])
                    self[layer_idx, 0].convert(device=self.memory_device)
                    root, _, _, _ = root.split_svd(
                        [1, 2], [0, 3], contract_singvals="L", conv_params=conv_params
                    )
                    root.transpose_update((1, 2, 0))

                log_neg = self.log_negativity(root=root, local_dim=local_dim)
                measures[key] = log_neg

            if mode == "L":
                return measures

        if mode in ["R", "LR"]:

            root = self[0, 0].copy()  # since the root is modified we need a copy

            layer_idx0 = 0

            if mode == "LR":
                layer_idx0 = 1

            for layer_idx in range(layer_idx0, self.num_layers - 1):

                pos_sub = [layer_idx + 1, int(2 ** (layer_idx + 1) - 1)]
                key = _get_key(pos_sub)

                if layer_idx > 0:

                    self[layer_idx, -1].convert(device=self.computational_device)
                    root = root.tensordot(self[layer_idx, -1], [[1], [2]])
                    self[layer_idx, -1].convert(device=self.memory_device)
                    root, _, _, _ = root.split_svd(
                        [1, 3],
                        [0, 2],
                        contract_singvals="L",
                        conv_params=self.convergence_parameters,
                    )
                    root.transpose_update((2, 1, 0))

                log_neg = self.log_negativity(root=root, local_dim=local_dim)
                measures[key] = log_neg

            return measures
        # pylint: disable-next=too-many-nested-blocks
        if mode == "A":

            # half cut
            pos_sub = [1, 0]
            key = _get_key(pos_sub)

            root = self[0, 0]
            log_neg = self.log_negativity(root=root, local_dim=local_dim)
            measures[key] = log_neg

            # we loop through the network (excluding the first and last layer)
            # the position of each tensor corresponds to two partitions for
            # which we calculate the logarithmic negativity
            for layer_idx in range(1, self.num_layers - 1):

                for tensor_idx in range(2**layer_idx):

                    root = self[
                        0, 0
                    ].copy()  # since the root is modified we need a copy

                    # we get the path to the target tensor and the keys
                    # for the two corresponding partitions
                    final_pos = [layer_idx, tensor_idx]
                    pos_sub_left = [layer_idx + 1, 2 * tensor_idx]
                    pos_sub_right = [layer_idx + 1, 2 * tensor_idx + 1]

                    key_sub_left = _get_key(pos_sub_left)
                    key_sub_right = _get_key(pos_sub_right)

                    path = self.get_path(final_pos)

                    # we loop through the path
                    for elem_idx, elem in enumerate(path):
                        # we contract the current root with the tensor in the path
                        pos = elem[3:5]
                        contr_idx = elem[2]
                        self[pos].convert(device=self.computational_device)
                        root = root.tensordot(self[pos], [[contr_idx], [2]])
                        self[pos].convert(device=self.memory_device)

                        if pos == final_pos:
                            # we arrived at the final tensor in the path
                            # the logarithmic negativity is calculated for the two respective
                            # partitions, which correspond to different splittings
                            if contr_idx == 0:

                                root_sub_left, _, _, _ = root.split_svd(
                                    [1, 2],
                                    [0, 3],
                                    contract_singvals="L",
                                    conv_params=conv_params,
                                )
                                root_sub_left.transpose_update((1, 2, 0))

                                root_sub_right, _, _, _ = root.split_svd(
                                    [1, 3],
                                    [0, 2],
                                    contract_singvals="L",
                                    conv_params=conv_params,
                                )
                                root_sub_right.transpose_update((1, 2, 0))

                            elif contr_idx == 1:

                                root_sub_left, _, _, _ = root.split_svd(
                                    [1, 2],
                                    [0, 3],
                                    contract_singvals="L",
                                    conv_params=conv_params,
                                )
                                root_sub_left.transpose_update((2, 1, 0))

                                root_sub_right, _, _, _ = root.split_svd(
                                    [1, 3],
                                    [0, 2],
                                    contract_singvals="L",
                                    conv_params=conv_params,
                                )
                                root_sub_right.transpose_update((2, 1, 0))

                            log_neg = self.log_negativity(
                                root=root_sub_left, local_dim=local_dim
                            )
                            measures[key_sub_left] = log_neg

                            log_neg = self.log_negativity(
                                root=root_sub_right, local_dim=local_dim
                            )
                            measures[key_sub_right] = log_neg

                        else:
                            # based on the position in the path, we split the current root
                            next_elem = path[elem_idx + 1]
                            next_contr_idx = next_elem[2]

                            if next_contr_idx == 0:  # moving to the left

                                root, _, _, _ = root.split_svd(
                                    [1, 2],
                                    [0, 3],
                                    contract_singvals="L",
                                    conv_params=conv_params,
                                )
                                root.transpose_update((1, 2, 0))

                            elif next_contr_idx == 1:  # moving to the right

                                root, _, _, _ = root.split_svd(
                                    [1, 3],
                                    [0, 2],
                                    contract_singvals="L",
                                    conv_params=conv_params,
                                )
                                root.transpose_update((2, 1, 0))

            return measures

    #########################################################################
    ####### Methods not well defined for TTOs, but inherited from TTN #######
    #########################################################################
    def dot(self, other):
        """
        Not implemented
        """
        raise NotImplementedError("dot product not implemented for TTOs")

    @classmethod
    def mpi_bcast(cls, state, comm, tensor_backend, root=0):
        """
        Broadcast a whole tensor network.

        Arguments
        ---------

        state : :class:`TTO` (for MPI-rank root, otherwise None is acceptable)
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
        # Requires `to_tensor_list`
        raise NotImplementedError("TTO cannot be broadcasted yet.")

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
        ansatz = TTO

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

    def to_tensor_list(self):
        """
        Not implemented
        """
        raise NotImplementedError("to_tensor_list product not implemented for TTOs")

    def write(self, filename, cmplx=True):
        """
        Not implemented
        """
        raise NotImplementedError("write product not implemented for TTOs")

    @classmethod
    def read(cls, filename, tensor_backend, cmplx=True, order="F"):
        """
        Read a TTO in a unformatted way via pkl (formatted files are not supported
        by TTOs).

        Parameters
        ----------

        filename: str
            PATH to the file
        tensor_backend : :class:`TensorBackend`
            Setup which tensor class to create.
        cmplx: bool, optional
            If True the TTO is complex, real otherwise. Default to True
        order: str, optional
            If 'F' the tensor is transformed from column-major to row-major, if 'C'
            it is left as read.

        Returns
        -------

        obj: py:class:`TTO`
            TTO class read from file

        """
        ext = "pkl" + cls.extension
        if filename.endswith(ext):
            return cls.read_pickle(filename, tensor_backend=tensor_backend)

        raise NotImplementedError("read from formatted file not implemented for TTOs")

    @classmethod
    def read_v0_2_29(cls, filename, tensor_backend, cmplx=True, order="F"):
        """
        Not implemented
        """
        raise NotImplementedError("read product not implemented for TTOs")

    # --------------------------------------------------------------------------
    # ---- ML Operations -----
    # --------------------------------------------------------------------------

    def contract(self, other, boundaries=None):
        """
        Contract the TTO `self` with another TN `other` <other|self>.
        By default it is a full contraction, but also a partial
        contraction is possible. If TTO is not pure, tensor will be returned
        even if boundaries is `None`.

        Parameters
        ----------
        other : :class:`_AbstractTN` (currently only MPS enabled)
            other ansatz to contract with
        boundaries : tuple of ints, optional (currently only `None` enabled)
            Contract to MPSs from boundaries[0] to boundaries[1].
            In this case the output will be a tensor.
            Default to None, which is  full contraction

        Returns
        -------
        contraction : complex | :class:`AbstractQteaTensor`
            Result of the contraction
        """

        if isinstance(other, MPS):
            return self._contract_with_mps(other, boundaries=boundaries)

        raise NotImplementedError("Contract for TTO not implemented yet.")

    def _contract_with_mps(self, other, boundaries=None):
        """
        Contract the TTO `self` with an MPS `other` <other|self>.
        See docstring `contract`.

        Parameters
        ----------
        other : :class:`MPS`
            MPS to contract with
        boundaries : tuple of ints, optional (currently only `None` enabled)
            Contract to MPSs from boundaries[0] to boundaries[1].
            In this case the output will be a tensor.
            Default to None, which is  full contraction

        Returns
        -------
        contraction : complex | :class:`AbstractQteaTensor`
            Result of the contraction
        """
        if boundaries is not None:
            raise NotImplementedError("Boundaries not enabled for <TTO|MPS>.")

        if not isinstance(other, MPS):
            raise TypeError("This methods targets <TTO/TTN|MPS>.")

        if np.any(self.local_dim != other.local_dim):
            raise ValueError("Local dimension must be the same to contract TNs.")

        if self.num_sites != other.num_sites:
            raise ValueError(
                "Number of sites must be the same to contract two TNs together"
            )

        # Initial layer
        tensor_list = other

        for ii in range(self.num_layers - 1, -1, -1):
            layer = self.layers[ii]
            next_list = []

            for jj, ttx_tensor in enumerate(layer):
                # Assumes binary tree
                tensor_a = tensor_list[2 * jj].conj()
                tensor_b = tensor_list[2 * jj + 1].conj()

                tensor = ttx_tensor.einsum("ijk,aib,bjc->akc", tensor_a, tensor_b)
                next_list.append(tensor)

            tensor_list = next_list

        if len(tensor_list) == 2:
            # TTN or derivatives
            result = tensor_list[0].einsum("ijkl,kji->l", tensor_list[1])
        else:
            result = tensor_list[0]

        if np.prod(result.shape) == 1:
            result = result.get_entry()

        return result

    def ml_reorder_pos_pair(self, pos, pos_partner, link_pos, link_partner):
        """
        TTO order is with lower-layer tensor first (but higher layer-index).

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

        if pos[0] > pos_partner[0]:
            # Already the good order
            return pos, pos_partner, link_pos, link_partner

        # This is a TTO, only one top tensor, can never be in the same layer
        return pos_partner, pos, link_partner, link_pos

    def ml_to_id_step(self, pos, pos_p):
        """
        Construct the id_step variables to shift effective operators given two
        positions in the tensor network.

        Arguments
        ---------

        pos : tuple[int]
            First position in the TTO.

        pos_p : tuple[int]
            Second position in the TTO.

        Returns
        -------

        id_step : list[int]
            Compatible step with TTO, i.e., list of
            [src_layer, src_tensor, src_link, dst_layer, dst_tensor, dst_link].
        """

        logger_warning(
            "DeprecationWarning: The machine learning methods in qtealeaves classes are deprecated."
            + " For machine learning tasks, please utilize the qchaitea classes instead."
        )

        if pos[0] > pos_p[0]:

            neighbors_partner = self.get_pos_links(pos_p)

            if neighbors_partner[0] == pos:
                partner_link = 0
            else:
                partner_link = 1

            # Assume binary tree
            id_step = [pos[0], pos[1], 2, pos_p[0], pos_p[1], partner_link]
            return id_step

        # pos_p[0] > pos[0]: partner in the lower TTO layer
        # pylint: disable-next=arguments-out-of-order
        tmp = self.ml_to_id_step(pos_p, pos)
        return tmp[3:] + tmp[:3]

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
            which skips the last position in respect to the ground state
            search for the two-tensor update.
        """

        logger_warning(
            "DeprecationWarning: The machine learning methods in qtealeaves classes are deprecated."
            + " For machine learning tasks, please utilize the qchaitea classes instead."
        )

        if num_tensor_rule == 2:
            sweep = self.default_sweep_order()
            return sweep[:-1]

        if num_tensor_rule == 1:
            return self.default_sweep_order()

        raise QTeaLeavesError(f"num_tensor_rule={num_tensor_rule} not available.")

    def ml_get_gradient_single_tensor(self, pos):
        """
        Get the gradient w.r.t. to the tensor at ``pos`` similar to the
        two-tensor version.

        Parameters
        ----------

        pos : tuple of two ints
            Layer index and tensor index withn layer of the tensor to work with.

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
            estr = "abcd,xmayi,ynbzi,zlcxi->di"
        else:
            estr = "abc,xmayi,ynbzi,zlcxi->mi"

        labels = tensor.einsum(
            estr,
            eff_op_0,
            eff_op_1,
            eff_op_2,
        )

        grad = eff_op_0.conj().einsum(
            "xmayi,ynbzi,zlcxi->abci",
            eff_op_1,
            eff_op_2.conj(),
        )

        if labels.shape[0] == 1:
            dtype = self[self.iso_center].dtype
            device = self[self.iso_center].device

            true_labels = self.eff_op.current_labels
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
        else:
            true_labels = self.eff_op.current_labels
            test_idx = np.arange(true_labels.shape[0], dtype=int)

            if true_labels.has_symmetry:
                # Access to elem in the next step would fail for symmetric tensors
                raise ValueError("How can labels be a symmetric tensor?")

            dtype_int = true_labels.dtype_from_char("I")
            axis0_idx = true_labels.copy().convert(dtype=dtype_int).elem

            labels.elem[axis0_idx, test_idx] -= 1
            diff = -1 * labels

            grad = grad.einsum("abci,xi->abcx", diff)
            diff = my_sum(my_abs(diff.elem**2), axis=0)

        # Calculate loss and move to CPU / host
        loss = my_sum(my_abs(real(diff)))
        loss = self[pos].get_of(loss)

        # normalize loss
        loss /= true_labels.shape[0]
        grad /= true_labels.shape[0]

        return grad, loss

    # pylint: disable-next=too-many-statements
    def ml_get_gradient_two_tensors(self, pos, pos_p=None):
        """
        Get the gradient w.r.t. the tensors at position `idx`, `idx+1`
        of the MPS following the procedure explained in
        https://arxiv.org/pdf/1605.05775.pdf for the
        data_sample given

        Parameters
        ----------

        idx : int
            Index of the tensor to optimize

        pos_p : int | None
            Index of partner tensor. If `None`, error
            will be raised as we prefer the good ordering.

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

        my_abs, real, my_sum = self[self.iso_center].get_attr("abs", "real", "sum")
        if pos_p is None:
            # Require this for now
            raise QTeaLeavesError("We need the good order for TTO ML.")

        self.iso_towards(pos, trunc=True)
        dtype = self[self.iso_center].dtype
        device = self[self.iso_center].device

        neighbors_pos = self.get_pos_links(pos)

        # We assume binary trees here ... iso_center is in lower tensor
        # and might be rank-4
        #
        #     4             4
        #     |             |
        #     o             o
        #    / \           / \
        #   o   3    or   3   o
        #  /\                / \
        #  1 2              1   2
        #

        has_label_link = self[self.iso_center].ndim == 4

        eff_op_1 = self.eff_op[(neighbors_pos[0], pos)].tensor
        eff_op_2 = self.eff_op[(neighbors_pos[1], pos)].tensor

        neighbors_partner = self.get_pos_links(pos_p)
        connected_via_left = neighbors_partner[0] == pos
        if has_label_link and connected_via_left:
            eff_op_3 = self.eff_op[(neighbors_partner[1], pos_p)].tensor
            # n is 1-dim, can go away
            einsum_labels = "abcde,dfghe,cgix,hjkle,ikm,lnmae->bfjxe"
            einsum_grad = "abcde,dfghe,hjkle,lnmae->cgkme"
        elif has_label_link:
            # Connected via right
            eff_op_3 = self.eff_op[(neighbors_partner[0], pos_p)].tensor
            einsum_labels = "abcde,dfghe,cgix,jklae,lim,hnmje->bfkxe"
            einsum_grad = "abcde,dfghe,jklae,hnmje->cglme"
        elif connected_via_left:
            eff_op_3 = self.eff_op[(neighbors_partner[1], pos_p)].tensor
            einsum_labels = "abcde,dfghe,cgi,hjkle,ikm,lnmae->bfjne"
            einsum_grad = "abcde,dfghe,hjkle,lnmae->cgkme"
        else:
            eff_op_3 = self.eff_op[(neighbors_partner[0], pos_p)].tensor
            einsum_labels = "abcde,dfghe,cgi,jklae,lim,hnmje->bfkne"
            einsum_grad = "abcde,dfghe,jklae,hnmje->cglme"

        eff_op_4 = self.eff_op[(neighbors_partner[2], pos_p)].tensor

        labels = eff_op_1.einsum(
            einsum_labels,
            eff_op_2,
            self[pos],
            eff_op_3,
            self[pos_p],
            eff_op_4,
        )
        labels.fuse_links_update(0, 3)

        grad = eff_op_1.conj().einsum(
            einsum_grad,
            eff_op_2,
            eff_op_3,
            eff_op_4.conj(),
        )

        if labels.shape[0] == 1:
            true_labels = self.eff_op.current_labels
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
            true_labels = self.eff_op.current_labels
            test_idx = np.arange(true_labels.shape[0], dtype=int)

            if true_labels.has_symmetry:
                # Access to elem in the next step would fail for symmetric tensors
                raise ValueError("How can labels be a symmetric tensor?")

            dtype_int = true_labels.dtype_from_char("I")
            axis0_idx = true_labels.copy().convert(dtype=dtype_int).elem

            labels.elem[axis0_idx, test_idx] -= 1
            diff = -1.0 * labels

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

        pos : tuple(int)
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

        if pos[0] <= pos_p[0]:
            raise QTeaLeavesError(
                f"Partner tensor has to be higher layer: {pos[0]} vs. {pos_p[0]}."
            )
        self.iso_towards(pos)

        # Aiming at:
        # We assume binary trees here ... iso_center is in lower tensor
        # and might be rank-4
        #
        #     4             4
        #     |             |
        #     o             o
        #    / \           / \
        #   o   3    or   3   o
        #  /\                / \
        #  1 2              1   2
        #

        neighbors_pos = self.get_pos_links(pos)
        eff_op_1 = self.eff_op[(neighbors_pos[0], pos)].tensor
        eff_op_2 = self.eff_op[(neighbors_pos[1], pos)].tensor

        neighbors_partner = self.get_pos_links(pos_p)
        connected_via_left = neighbors_partner[0] == pos
        has_label_link = self[self.iso_center].ndim == 4

        if connected_via_left:
            eff_op_3 = self.eff_op[(neighbors_partner[1], pos_p)].tensor
            einsum_labels = "abct,cde,wmaxi,xnbyi,yodzi,zpewi->mnopti"
        else:
            eff_op_3 = self.eff_op[(neighbors_partner[0], pos_p)].tensor
            einsum_labels = "abct,dce,wmaxi,xnbyi,zpdwi,yoezi->mnopti"
        eff_op_4 = self.eff_op[(neighbors_partner[2], pos_p)].tensor

        # Modify einsum string removing unncessary parts
        if has_label_link:
            einsum_labels = einsum_labels.replace("mnop", "")
        else:
            einsum_labels = einsum_labels.replace("t", "")

        tensor1 = self[pos]
        tensor2 = self[pos_p]

        tensor1.elem.requires_grad_(True)
        tensor2.elem.requires_grad_(True)

        optim, nn = tensor1.get_attr("optim", "nn")
        optimizer = optim.AdamW([tensor1.elem, tensor2.elem])  # *args, **kwargs)
        gradient_clipper = nn.utils.clip_grad_value_

        # pylint: disable-next=protected-access
        true_labels = self.eff_op._current_labels
        test_idx = np.arange(true_labels.shape[0], dtype=int)

        # Actually do the iteration
        for _ in range(num_grad_steps):

            # Call the optimization function:
            loss = self._cost_func_two_tensor(
                tensor1,
                tensor2,
                eff_op_1,
                eff_op_2,
                eff_op_3,
                eff_op_4,
                einsum_labels,
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

        self[pos] = tensor1
        self[pos_p] = tensor2

        loss = tensor1.get_of(loss)
        loss = loss.detach().clone()

        return loss

    def get_substate(self, first_site, last_site, truncate=True):
        """
        Returns the smaller TN built of tensors from the subtree. `first_site` and
        `last_site` (where sites refer to physical sites) define the subtree.
        """
        raise NotImplementedError("Substate not implemented yet for TTO, but possible.")

    def kron(self, other, inplace=False, fill_identity=True, install_iso=False):
        """
        Concatenate two TTO, taking the kronecker/outer product
        of the two states.

        Parameters
        ----------
        other : :py:class:`TTO`
            TTO to concatenate
        inplace : bool, optional
            If True apply the kronecker product in place. Instead, if
            inplace=False give as output the product. Default to False.
        fill_identity : Bool
            If True, uppermost layer tensors are simply set to identity tensors.
            Otherwise, constructs last layer by QR-ing the top tensors of self and other.
            Defatult to True
        install_iso : bool, optional
            If true, the isometry center will be installed in the resulting
            tensor network. The isometry centers of `self` and `other` might
            be shifted in order to do so. For `False`, the isometry center
            in the new TTO is not set.
            Default to `False`.

        Returns
        -------
        :py:class:`TTO`
            Concatenation of the first TTO with the second.
        """
        raise NotImplementedError(
            "Function not yet implemented for TTO, implementation possible."
        )
