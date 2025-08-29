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
Dense Matrix Product Operators representing Hamiltonians or observables.
 | | | |
-O-O-O-O-
 | | | |

There are 3 classes in this module: `MPOSite`, `DenseMPO`, `DenseMPOList`

DenseMPO :      is the standard textbook-like MPO that acts on specified sites
                (DenseMPO.sites). It is a list of MPOSite-s

MPOSite :       each tensor in the DenseMPO is stored as MPOSite. For example,
                a 4-body DenseMPO is going to be a list of 4 MPOSites.

DenseMPOList :  a list of DenseMPO-s. Here, usually, it's used to represent
                Hamiltonians which consist of multiple terms. In this case,
                each Hamiltonian term is represented as a DenseMPO. For example,
                Ising model contains nearest-neighbour sigma_x sigma_x and
                sigma_z terms, and every 2-body term sigma_x sigma_x and
                local term sigma_z would be stored as a separate DenseMPO
                added to a DenseMPOList


Some useful attributes/functions:

MPOSite :       initialize with MPOSite([list of sites], tensor_str_name, pstrength=None,
                                        prefactor=1.0, operators=op_dict, params={})

                - self.site = on which site in a system does this MPOSite act
                - self.operator = get an actual tensor

DenseMPO :      initialize with DenseMPO([list of MPOSite-s], tensor_backend)

                - self.num_sites = on how many sites does this MPO act
                - self.sites = list of sites on which MPO acts
                - self[ind].operator = get tensor on site ind
                - self.append(MPOSite) = add MPOSite to Dense MPO

DenseMPOList :  initialize with DenseMPOList() and then append DenseMPO-s

                - self[ind] = get ind-th DenseMPO in a list
                - DenseMPOList.from_model_prepared(...) = creates a DenseMPOList
                - object from a given Hamiltonian model

"""
# pylint: disable=too-many-arguments
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=too-many-public-methods

import logging
import warnings
from copy import deepcopy

import numpy as np

from qtealeaves.abstracttns.abstract_matrix_tn import _AbstractMatrixTN
from qtealeaves.convergence_parameters import TNConvergenceParameters
from qtealeaves.operators import TNOperators
from qtealeaves.tensors import TensorBackend
from qtealeaves.tensors.abstracttensor import _AbstractQteaTensor
from qtealeaves.tooling import QTeaLeavesError
from qtealeaves.tooling.operatorstrings import _op_string_mul
from qtealeaves.tooling.parameterized import _ParameterizedClass
from qtealeaves.tooling.restrictedclasses import _RestrictedList

__all__ = ["MPOSite", "DenseMPO", "DenseMPOList"]

logger = logging.getLogger(__name__)


class MPOSite(_ParameterizedClass):
    """
    One site in a dense MPO term. For example, a 4-body DenseMPO is
    going to be a list of 4 MPOSites.

    Initialize with MPOSite([list of sites], tensor_str_name, pstrength=None,
                                    prefactor=1.0, operators=op_dict, params={})

    **Arguments**

    site : integer
        Site index.

    str_op : str
        Key for the operator.

    pstrength : pstrength, callable, numeric
        Containing the parameterization of the term.

    weight : scalar
        Scalar constant prefactor.

    operators : :class:`TNOperators` or None
        If present, operators will be directly extracted.

    params : dict or None
        If present, parameterization will be directly extracted.
    """

    def __init__(self, site, str_op, pstrength, weight, operators=None, params=None):
        self.site = site
        self.str_op = str_op
        self.pstrength = pstrength

        self.operator = None if operators is None else operators[(site, str_op)].copy()
        self.strength = (
            None if params is None else self.eval_numeric_param(self.pstrength, params)
        )
        if self.pstrength is None:
            self.strength = 1.0
        self.weight = weight

    # --------------------------------------------------------------------------
    #                             Overwritten magic methods
    # --------------------------------------------------------------------------

    def __repr__(self):
        """
        User-friendly representation of object for print().
        """
        str_repr = (
            f"{self.__class__.__name__} on site {self.site} with ("
            f"\noperator={self.operator},"
            f"\npstrength={self.pstrength},"
            f" weight={self.weight} )"
        )

        return str_repr

    @property
    def total_scaling(self):
        """Returns the scaling combining params and weight."""
        return self.strength * self.weight

    @property
    def shape(self):
        """Shape attribute equivalent to tensor's shape: bond dimension of links."""
        return self.operator.shape

    def initialize(self, operators, params):
        """Resolve operators and parameterization for the given input."""
        self.set_op(operators)
        self.set_param(params)

    def set_op(self, operators):
        """Resolve operators for the given input."""
        if self.str_op is None:
            raise QTeaLeavesError("Operator string no longer available.")
        self.operator = operators[(self.site, self.str_op)]

    def set_param(self, params):
        """Resolve parameterization for the given input."""
        if self.pstrength is None:
            self.strength = 1.0
            return

        strength = self.eval_numeric_param(self.pstrength, params)

        if hasattr(strength, "__len__"):
            raise QTeaLeavesError("Strength cannot be a list.")

        if strength == 0.0:
            warnings.warn("Adding term with zero-coupling.")

        self.strength = strength

    def copy_with_new_op(self, operator):
        """
        Create a copy of self, but with replacing the operator with the one passed.
        Corresponding string identifier will be set to `None`.
        """
        obj = deepcopy(self)
        obj.operator = operator
        obj.str_op = None

        return obj

    @classmethod
    def from_operator(cls, site, operator):
        """
        Create MPOSite object from a given operator tensor.

        Arguments
        ---------
        site : int
            Which site in a system.
        operator : :class:`_AbstractQteaBaseTensor`'
            Rank-4 tensor which will be the operator for this MPOSite.

        Return
        ------
        mpo_site : :class:`MPOSite`'
            The resulting MPO site.
        """
        if len(operator.shape) != 4:
            raise ValueError(
                "MPOSite can be built only from rank-4 operators and "
                f"not rank-{len(operator.shape)}."
            )

        str_op = f"MPO_{site}"
        mpo_site = cls(
            site, str_op, pstrength=None, weight=1, operators=None, params=None
        )
        # set the operator tensor
        mpo_site.operator = operator

        return mpo_site


class DenseMPO(_AbstractMatrixTN, _RestrictedList):
    """
    Dense MPO is the standard textbook-like MPO that acts on specified sites
    (DenseMPO.sites). It is a list of :class:`MPOSite`'s.

    Initialize with DenseMPO([list of MPOSite-s], tensor_backend)
    """

    class_allowed = MPOSite

    def __init__(
        self,
        sites=None,
        convergence_parameters=None,
        is_oqs=False,
        tensor_backend=TensorBackend(),
        require_singvals=False,
        local_dim=2,
    ):
        if convergence_parameters is None:
            # Not really allowed in the next step
            convergence_parameters = TNConvergenceParameters()
        if sites is None:
            sites = []
        _RestrictedList.__init__(self, sites)
        _AbstractMatrixTN.__init__(
            self,
            num_sites=1,  # is required, otherwise some local dim fails**
            convergence_parameters=convergence_parameters,
            local_dim=local_dim,
            requires_singvals=require_singvals,
            tensor_backend=tensor_backend,
        )
        # **: Should be fine, although _num_sites is something else
        # than the property num_sites defined in this class. Similar
        # problem in _AbstractMatrixTN, where _tensors is empty, but
        # singular values set according to num_sites. But it looks
        # like everything is overwritten consistently.

        self.is_oqs = is_oqs

    # --------------------------------------------------------------------------
    #                             Overwritten magic methods
    # --------------------------------------------------------------------------

    def __repr__(self):
        """
        User-friendly representation of object for print().
        """
        return f"{self.__class__.__name__}(sites={self.sites})"

    @property
    def num_sites(self):
        """Length of the Dense MPO"""
        return len(self)

    @property
    def sites(self):
        """Generate list of site indices."""
        sites = [elem.site for elem in self]
        return sites

    def get_tensor_of_site(self, idx):
        """
        Return the tensor representing the MPO operator at site `idx`
        """
        return self[idx].operator

    def _iter_tensors(self):
        """Iterate over all tensors forming the tensor network (for convert etc)."""
        for ii in range(self.num_sites):
            yield self.get_tensor_of_site(ii)

    def __len__(self):
        return super(_RestrictedList, self).__len__()

    def __setitem__(self, index, elem):
        """
        New setitem with the possibility of just setting the tensor
        """
        if isinstance(elem, _AbstractQteaTensor):
            site = self[index]
            site.operator = elem
            site.str_op = f"MPO_{index}"
        else:
            site = elem
        super(_RestrictedList, self).__setitem__(index, self._check_class(site))

    def append(self, elem):
        """Overwriting append to extend as well the list of singvals."""
        super().append(elem)

        # Copy last singvals - assumption: cannot change with local operators
        self._singvals.append(self._singvals[-1])

    def compress_links(self, idx_start, idx_end, trunc=False, conv_params=None):
        """
        Compresses links between sites in a dense MPO by performing a QR or SVD,
        optionally performs the additional truncation along the way.

        Parameters
        ----------
        idx_start : int
            MPO site from which to start the compression.

        idx_end : int
            MPO site on which to end the compression.

        trunc : Boolean, optional
            If True, the truncation will be done according to the `conv_params`.
            Default to False.

        conv_params : :py:class:`TNConvergenceParameters`, optional
            Convergence parameters for the truncation. Must be specified if
            `trunc` is set to True.
            Default to `None`.
        """
        # pylint: disable=access-member-before-definition
        if len(self) > len(self._singvals):
            # Note: the linter does not recognize the call to
            # super, which initializes _singlvals in the _AbstractMatrixTN
            # pylint: disable=attribute-defined-outside-init, access-member-before-definition
            self._singvals = [None] * (len(self) * 2)
        self.iso_towards(idx_start, True)
        self.iso_towards(idx_end, True, trunc, conv_params)

    def add_identity_on_site(self, idx, link_vertical):
        """
        Add identity with the correct links to neighboring terms on site `idx`.

        Parameters
        ----------
        idx : int
            Site to which add the identity. Goes from 0 to num sites in a system.

        link_vertical : link as returned by corresponding QteaTensor
            Needed to build the local Hilbert space (in case it is different across
            the system).
        """
        if len(self) == 0:
            raise QTeaLeavesError(
                "Cannot use `add_identity_on_site` on empty DenseMPO."
            )

        sites = np.array(self.sites)
        if np.any(sites[1:] - sites[:-1] <= 0):
            raise QTeaLeavesError(
                "Cannot use `add_identity_on_site` on unsorted DenseMPO."
            )

        if idx in self.sites:
            raise QTeaLeavesError("Site is already in DenseMPO.")

        sites = np.array(self.sites + [idx])

        # Figure out the index where to insert
        # the identity, and the index of the site
        # on the left of it.
        # This takes care of the periodic boundary
        # conditions on the indices of the dense_mpo.
        sites_sorted = sorted(sites)
        insert_site_index = sites_sorted.index(idx)
        left_index = insert_site_index - 1

        op = self[left_index].operator
        if op is None:
            raise QTeaLeavesError(
                "Cannot use `add_identity_on_site` on uninitialized DenseMPO."
            )

        eye_horizontal = op.eye_like(op.links[3])
        eye_vertical = op.eye_like(link_vertical)

        # Contract together
        eye_horizontal.attach_dummy_link(0, False)
        eye_vertical.attach_dummy_link(0, True)

        eye = eye_horizontal.tensordot(eye_vertical, ([0], [0]))
        eye.transpose_update([0, 2, 3, 1])

        key = str(id(eye))
        op_dict = TNOperators()
        op_dict[key] = eye

        # add it to the correct site
        site = MPOSite(idx, key, None, 1.0, operators=op_dict, params={})

        self.insert(insert_site_index, site)

        # add the singular values, identity cannot change them, so insert
        # the same ones
        self._singvals.insert(insert_site_index, self._singvals[insert_site_index])

    def initialize(self, operators, params):
        """Resolve operators and parameterization for the given input for each site."""
        for elem in self:
            elem.initialize(operators, params)

    def sort_sites(self):
        """Sort sites while and install matching link for symmetries."""

        sites = [elem.site for elem in self]

        # Potentially no fast return possible here, because even if the sites
        # are sorted, we need to manage the links for symmetric tensor
        # networks
        if not self[0].operator.has_symmetry:
            if all(sites[ii] <= sites[ii + 1] for ii in range(len(sites) - 1)):
                # sites already sorted, return
                return self

        inds = np.argsort(sites)

        dims_l = [elem.operator.shape[0] for elem in self]
        dims_r = [elem.operator.shape[3] for elem in self]

        max_l = np.max(dims_l)
        max_r = np.max(dims_r)

        max_chi = max(max_l, max_r)

        if max_chi == 1:
            return self._sort_sites_chi_one(inds)

        raise QTeaLeavesError("For now, we only sort product terms.")

    def pad_identities(self, num_sites, eye_ops):
        """Pad identities on sites which are not in MPO yet respecting the symmetry."""
        sites = np.array([elem.site for elem in self])
        if np.any(sites[1:] - sites[:-1] < 1):
            sorted_mpo = self.sort_sites()
            return sorted_mpo.pad_identities(num_sites, eye_ops)

        raise QTeaLeavesError("Not implemtented yet.")

    def trace(self, local_dim):
        """
        Compute the trace of and MPO written in DenseMPO form.

        Parameters
        ----------

        local_dim : list[int]
            Physical dimension of each of the sites in self.

        Returns
        -------

        operator_trace : float | complex
            Corresponds to the trace of the operator.
        """
        partial_trace = 1
        dims = local_dim.copy()
        for mpo_site in self:
            # for a dense_mpo the trace is the product of the traces of the
            # operators at each site.
            if mpo_site.operator.shape[0] != 1 or mpo_site.operator.shape[-1] != 1:
                raise NotImplementedError(
                    "Trace not yet impemented if DenseMPO list contains MPOsite "
                    "with non-dummy horizontal links."
                )

            operator = mpo_site.operator.copy()
            operator.remove_dummy_link(3)
            operator.remove_dummy_link(0)
            partial_trace *= operator.trace() * mpo_site.total_scaling

            # Cancel contribution from dims
            dims[mpo_site.site] = 1

        partial_trace *= float(np.prod(np.array(dims)))
        return partial_trace

    def _sort_sites_chi_one(self, inds):
        """Sorting sites in the case of bond dimension equal to one."""
        new_mpo = DenseMPO(is_oqs=self.is_oqs, tensor_backend=self._tensor_backend)
        link = self[0].operator.dummy_link(self[0].operator.links[0])

        for ii in inds:
            # Trivial tensor porting the sector
            one = self._tensor_backend(
                [link, link],
                ctrl="O",
                are_links_outgoing=[False, True],
                device=self[ii].operator.device,
                dtype=self[ii].operator.dtype,
            )
            one.attach_dummy_link(2, True)

            op = self[ii].operator.copy().attach_dummy_link(4, is_outgoing=False)
            tens = one.tensordot(op, ([2], [4]))

            # We have six links [left, right-1, right-former-left, bra, ket, right-2]
            tens.transpose_update([0, 3, 4, 1, 2, 5])
            tens.fuse_links_update(3, 5)

            mpo_site = self[ii].copy_with_new_op(tens)
            mpo_site.str_op = self[ii].str_op
            new_mpo.append(mpo_site)

            # For the next loop iteration
            link = new_mpo[-1].operator.links[-1]

        # Check that MPO does conserve symmetry
        if not self.is_oqs:
            new_mpo[-1].operator.assert_identical_irrep(3)

        return new_mpo

    @classmethod
    def from_matrix(
        cls,
        matrix,
        sites,
        dim,
        conv_params,
        tensor_backend=TensorBackend(),
        operators=TNOperators(),
        pad_with_identities=False,
    ):
        """
        For a given matrix returns dense MPO form decomposing with SVDs

        Parameters
        ----------
        matrix : QteaTensor | ndarray
            Matrix to write in (MPO) format
        sites : List[int]
            Sites to which the MPO is applied
        dim : int
            Local Hilbert space dimension
        conv_params : :py:class:`TNConvergenceParameters`
            Convergence parameters. The relevant attribute is the `max_bond_dimension`
        tensor_backend : instance of :class:`TensorBackend`
            Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.
        pad_with_identities: bool, optional
            If True, pad with identities the sites between min(sites) and max(sites)
            that have no operator. Default to False.

        Return
        ------
        DenseMPO
            The MPO decomposition of the matrix
        """

        if not isinstance(matrix, tensor_backend.tensor_cls):
            matrix = tensor_backend.tensor_cls.from_elem_array(matrix)

        mpo = cls(
            convergence_parameters=conv_params,
            tensor_backend=tensor_backend,
            local_dim=dim,
        )
        bond_dim = 1
        names = []
        work = matrix

        op_set_name = operators.set_names[0]

        if len(operators.set_names) > 1:
            raise QTeaLeavesError(
                "Can use matrix to MPO decomposition only for one set of operators."
            )

        site_cnt = 0
        for ii in range(sites[0], sites[-1], 1):
            if ii in sites:
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
                        dim ** (len(sites) - 1 - site_cnt),
                        dim,
                        dim ** (len(sites) - 1 - site_cnt),
                    ),
                )
                tens_left, work, _, _ = work.split_svd(
                    [0, 1, 3], [2, 4], contract_singvals="R", conv_params=conv_params
                )
                bond_dim = deepcopy(work.shape[0])
                operators[(op_set_name, f"mpo{ii}")] = tens_left
                names.append(f"mpo{ii}")
                site_cnt += 1
            elif pad_with_identities:
                operators[(op_set_name, f"id{ii}")] = DenseMPO.generate_mpo_identity(
                    bond_dim, dim, bond_dim, tensor_backend
                )
                names.append((op_set_name, f"id{ii}"))

        work = work.reshape((work.shape[0], dim, dim, 1))
        operators[(op_set_name, f"mpo{sites[-1]}")] = work
        names.append(f"mpo{sites[-1]}")
        # Note: the linter does not recognize the call to
        # super, which initializes _local_dim in the _AbstractMatrixTN
        # pylint: disable=attribute-defined-outside-init
        mpo._local_dim = np.zeros(len(sites), dtype=int)

        cnt = 0
        for site, name in zip(sites, names):
            mpo.append(MPOSite(site, name, 1, 1, operators=operators))

            mpo._local_dim[cnt] = mpo[cnt].operator.shape[1]
            mpo._singvals.append(None)
            cnt += 1
        # pylint: disable=attribute-defined-outside-init
        mpo._iso_center = (cnt - 1, cnt)
        return mpo

    @classmethod
    def from_tensor_list(
        cls,
        tensor_list,
        conv_params=None,
        iso_center=None,
        tensor_backend=TensorBackend(),
        operators=TNOperators(),
        sites=None,
    ):
        """
        Initialize the dense MPO from a list of tensors.

        Parameters
        ----------
        tensor_list : List[QteaTensor] | List[MPOSite]
            Matrix to write in (MPO) format
        conv_params : :py:class:`TNConvergenceParameters`, None
            Input for handling convergence parameters. Default to None
        iso_center : None, int, List[int], str, optional
            If None, the center is None.
            If str, the iso center is installed
            If int, the iso center is that integer.
            Default is None
        tensor_backend : instance of :class:`TensorBackend`
            Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.
        operators: TNOperators, optional
            Operator class
        sites : List[int], None
            Sites to which the MPO is applied. If None, they are assumed to be
            [0, 1, ..., len(tensorlist)-1]. Default to None

        Return
        ------
        DenseMPO
            The MPO decomposition of the matrix
        """
        if sites is None:
            sites = list(range(len(tensor_list)))

        mpo = cls(convergence_parameters=conv_params, tensor_backend=tensor_backend)

        # Check if they are MPOSites
        if isinstance(tensor_list[0], MPOSite):
            tensor_list = [ss.operator * ss.weight for ss in tensor_list]

        names = []
        for ii, tens in enumerate(tensor_list):
            names.append(_duplicate_check_and_set(operators, f"mpo{ii}", tens))

        # pylint: disable=attribute-defined-outside-init
        mpo._local_dim = np.zeros(len(tensor_list), dtype=int)
        cnt = 0
        for site, name in zip(sites, names):
            mpo.append(
                MPOSite(site, name, pstrength=None, weight=1, operators=operators)
            )
            mpo._local_dim[cnt] = mpo[cnt].operator.shape[1]
            mpo._singvals.append(None)
            cnt += 1

        if isinstance(iso_center, str):
            mpo.install_gauge_center()
        elif isinstance(iso_center, int):
            # Note: the linter does not recognize the call to
            # super, which initializes iso_center in the _AbstractMatrixTN
            # pylint: disable=attribute-defined-outside-init
            mpo._iso_center = (iso_center, iso_center + 2)
        elif isinstance(iso_center, (list, tuple)):
            # pylint: disable=attribute-defined-outside-init
            mpo.iso_center = iso_center

        return mpo

    @staticmethod
    def generate_mpo_identity(left_bd, local_dim, right_bd, tensor_backend):
        """
        Generate an identity in MPO form with given dimensions.
        """
        id_tens = tensor_backend([left_bd, local_dim, local_dim, right_bd])
        for ii in range(min(left_bd, right_bd)):

            id_tens[ii : ii + 1, :local_dim, :local_dim, ii : ii + 1] = (
                id_tens.eye_like(local_dim)
            )

        return id_tens

    ############################################################
    # Abstract methods that should not work with the DenseMPO
    ############################################################
    @classmethod
    def from_density_matrix(
        cls, rho, n_sites, dim, conv_params, tensor_backend=None, prob=False
    ):
        """Conversion of density matrix to DenseMPO (not implemented yet)."""
        raise NotImplementedError("Feature not yet implemented.")

    @classmethod
    def from_lptn(cls, lptn, conv_params=None, **kwargs):
        """Conversion of LPTN to DenseMPO (not implemented yet)."""
        raise NotImplementedError("Feature not yet implemented.")

    @classmethod
    def from_mps(cls, mps, conv_params=None, **kwargs):
        """Conversion of MPS to DenseMPO (not implemented yet)."""
        raise NotImplementedError("Feature not yet implemented.")

    @classmethod
    def from_ttn(cls, ttn, conv_params=None, **kwargs):
        """Conversion of TTN to DenseMPO (not implemented yet)."""
        raise NotImplementedError("Feature not yet implemented.")

    @classmethod
    def from_tto(cls, tto, conv_params=None, **kwargs):
        """Conversion of TTO to DenseMPO (not implemented yet)."""
        raise NotImplementedError("Feature not yet implemented.")

    @classmethod
    def product_state_from_local_states(
        cls,
        mat,
        padding=None,
        convergence_parameters=None,
        tensor_backend=None,
    ):
        """
        Construct a product (separable) state in a suitable tensor network form, given the local
        states of each of the sites.
        """
        raise NotImplementedError(
            "DenseMPO cannot be initialized from local product state."
        )

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
        raise NotImplementedError("DenseMPO has no support for machine learning yet.")

    @classmethod
    def mpi_bcast(cls, state, comm, tensor_backend, root=0):
        """
        Broadcast a whole tensor network.

        Arguments
        ---------

        state : :class:`DenseMPO` (for MPI-rank root, otherwise None is acceptable)
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
        raise NotImplementedError("DenseMPO cannot be broadcasted yet.")

    @classmethod
    def from_statevector(
        cls, statevector, local_dim=2, conv_params=None, tensor_backend=None
    ):
        """No statevector for operators"""
        raise NotImplementedError("No statevector for operators")

    def get_rho_i(self, idx):
        """No density matrix for operators"""
        raise NotImplementedError("No density matrix for operators")

    # pylint: disable-next=unused-argument
    def to_dense(self, true_copy=False):
        """Convert into a TN with dense tensors (without symmetries)."""
        return

    @classmethod
    def read(cls, filename, tensor_backend, cmplx=True, order="F"):
        """Read a MPO from a formatted file."""
        raise NotImplementedError("No read method for DenseMPO")

    def apply_projective_operator(self, site, selected_output=None, remove=False):
        """No measurements in MPO"""
        raise NotImplementedError("No apply_projective_operator method for DenseMPO")

    def ml_get_gradient_single_tensor(self, pos):
        """
        Get the gradient w.r.t. to the tensor at ``pos`` similar to the
        two-tensor version. Not implemented.
        """
        raise NotImplementedError("ML gradient for DenseMPO.")

    def ml_get_gradient_two_tensors(self, pos, pos_p=None):
        """
        Get the gradient w.r.t. to the tensor at ``pos`` similar to the
        two-tensor version. Not implemented.
        """
        raise NotImplementedError("ML gradient for DenseMPO.")

    def ml_two_tensor_step(self, pos, num_grad_steps=1):
        """
        Do a gradient descent step via backpropagation with two tensors
        and the label link in the environment.
        """
        raise NotImplementedError("ML gradient descent for DenseMPO.")

    def ml_update_conjugate_gradient_two_tensors(self, pos, pos_p=None):
        """
        Get the optimized "two_tensors" at position `pos`, `pos_p` through
        Conjugate gradient descent strategy following a procedure based upon
        https://arxiv.org/pdf/1605.05775.pdf for the
        data_sample given.

        the name of the variables in the following is chosen upon Conj. Grad. Algor. in
        https://en.wikipedia.org/wiki/Conjugate_gradient_method.

        Not Implemented.
        """
        raise NotImplementedError("ML gradient descent for DenseMPO.")

    # pylint: disable-next=unused-argument
    def build_effective_operators(self, measurement_mode=False):
        """Pass"""
        return

    # pylint: disable-next=unused-argument
    def _convert_singvals(self, dtype, device):
        """Pass"""
        return

    def _iter_physical_links(self):
        """Pass"""
        return

    # pylint: disable-next=unused-argument
    def get_bipartition_link(self, pos_src, pos_dst):
        """Pass"""
        return

    # pylint: disable-next=unused-argument
    def get_pos_links(self, pos):
        """Pass"""
        return

    def norm(self):
        """Pass"""
        return

    # pylint: disable-next=unused-argument
    def set_singvals_on_link(self, pos_a, pos_b, s_vals):
        """Pass"""
        return

    # pylint: disable-next=unused-argument
    def _update_eff_ops(self, id_step):
        """Pass"""
        return

    # pylint: disable-next=unused-argument
    def _partial_iso_towards_for_timestep(self, pos, next_pos, no_rtens=False):
        """Pass"""
        return

    # pylint: disable-next=unused-argument
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

    def to_statevector(self, qiskit_order=False, max_qubit_equivalent=20):
        """No statevector for operators"""
        raise NotImplementedError("No statevector for operators")

    def write(self, filename, cmplx=True):
        """Write the TN in python format into a FORTRAN compatible format."""
        raise NotImplementedError("No write method for DenseMPO")


class DenseMPOList(_RestrictedList):
    """
    A list of dense MPOs, i.e., for building iTPOs or other MPOs.

    Initialize with DenseMPOList() and then append DenseMPO-s

    Here, usually, it's used to represent Hamiltonians which consist
    of multiple terms. In this case, each Hamiltonian term is represented
    as a DenseMPO. For example, Ising model contains nearest-neighbour
    sigma_x sigma_x and sigma_z terms, and every 2-body term
    sigma_x sigma_x and local term sigma_z would be stored as a separate
    DenseMPO added to a DenseMPOList

    """

    class_allowed = DenseMPO

    @property
    def has_oqs(self):
        """Return flag if the `DenseMPOList` contains any open system term."""
        has_oqs = False
        for elem in self:
            logger.debug("elem.is_oqs %s %s", has_oqs, elem.is_oqs)
            has_oqs = has_oqs or elem.is_oqs

        return has_oqs

    @classmethod
    def from_model(cls, model, params, tensor_backend=TensorBackend()):
        """Fill class with :class:`QuantumModel` and its parameters. Not ready
        for measurement before initializing with the operators. For full
        preparation use `from_model_prepared()`.

        """
        obj = cls()

        lx_ly_lz = model.eval_lvals(params)

        for term in model.hterms:
            for elem, coords in term.get_interactions(lx_ly_lz, params, dim=model.dim):

                weight = term.prefactor
                if "weight" in elem:
                    weight *= elem["weight"]

                pstrength = term.strength
                mpo = DenseMPO(is_oqs=term.is_oqs, tensor_backend=tensor_backend)

                for idx, coord in enumerate(coords):
                    site_term = MPOSite(
                        coord, elem["operators"][idx], pstrength, weight
                    )
                    mpo.append(site_term)
                    # pylint: disable-next=protected-access
                    mpo._singvals.append(None)

                    # Only needed on first site
                    pstrength = None
                    weight = 1.0

                obj.append(mpo)

        return obj

    @classmethod
    def from_model_prepared(
        cls,
        model,
        params,
        operators,
        tensor_backend=TensorBackend(),
        sym=None,
        generators=None,
    ):
        """
        Returns fully prepared dense MPOs from a model, ready for the
        measurement. (Pay attention: this classmethod has two return
        values.)

        Arguments
        ---------

        model : :class:`QuantumModel`
            The model to build the :class:`DenseMPOList` for.

        params : dict
            Simulation dictionary containing parameterization and
            similar settings for the model and simulation.

        operators : :class:`TNOperators`
            The operators to be used with the simulation.

        tensor_backend : :class:`TensorBackend`, optional
            Choose the tensor backend to be used for the operators
            and simulation.
            Default to `TensorBackend()` (numpy, CPU, complex128, etc.)

        sym : list, optional
            Information on symmetry in case of symmetric tensors.
            Default to `None` (no symmetries).

        generators : list, optional
            Information on the generators of the symmetry in case of
            symmetric tensors.
            Default to `None` (no symmetries).

        Returns
        -------

        obj : :class:`DenseMPOListt`
            MPO representation of the model for the given
            parameterization.

        operators : :class:`TNOperators`
            Operators converted to the corresponding tensor backend.

        """
        if sym is None:
            sym = []
        if generators is None:
            generators = []

        obj = cls.from_model(model, params, tensor_backend)

        # prepare the operators
        base_tensor_cls = tensor_backend.base_tensor_cls
        tensor_cls = tensor_backend.tensor_cls

        operators = base_tensor_cls.convert_operator_dict(
            operators,
            params=params,
            symmetries=[],
            generators=[],
            base_tensor_cls=base_tensor_cls,
            dtype=tensor_backend.dtype,
            device=tensor_backend.memory_device,
        )
        if base_tensor_cls != tensor_cls:
            operators = tensor_cls.convert_operator_dict(
                operators,
                symmetries=sym,
                generators=generators,
                base_tensor_cls=base_tensor_cls,
            )
        # initialize mpo with the operators
        obj.initialize(operators, params)

        return obj, operators

    def initialize(self, operators, params, do_sort=True):
        """Resolve operators and parameterization for the given input."""
        for elem in self:
            elem.initialize(operators, params)

        if do_sort:
            mpos_sorted = self.sort_sites()

            for ii, elem in enumerate(mpos_sorted):
                self[ii] = elem

    def sort_sites(self):
        """Sort the sites in each :class:`DenseMPO`."""
        mpos_sorted = DenseMPOList()

        for elem in self:
            elem_sorted = elem.sort_sites()
            mpos_sorted.append(elem_sorted)

        return mpos_sorted

    def trace(self, local_dim):
        """
        Compute the trace of and MPO written in DenseMPOList form.

        Parameters
        ----------

        local_dim : list[int]
            Physical dimension of each of the sites in self.

        Returns
        -------

        operator_trace : float | complex
            Corresponds to the trace of the operator.
        """
        operator_trace = 0
        # we compute the trace of each dense_mpo in self and then sum the results
        for dense_mpo in self:
            # This is potentially dangerous for overflows and problems with
            # machine precision if the offsets are very different. 1000
            # qubits are about 1e300 so beyond one-thousand qubits we
            # soon run into overflows with double precision numbers
            # and partial_trace being of the order of one
            operator_trace += dense_mpo.trace(local_dim)

        return operator_trace

    def mpo_product(
        self,
        other,
        operators,
        self_conj=False,
        self_transpose=False,
        other_conj=False,
        other_transpose=False,
    ):
        """
        Compute the product of two MPOs encoded as DenseMPOList. The order of
        product is self*other. If the operators at site j are self_op_j and
        other_op_j respectively, `mpo_product` returns the DenseMPOList whose
        operator at site j is the operator product self_op_j*other_op_j. The
        input arguments `self` and `other` remain unchanged in this method.

        Parameters
        ----------

        other : :py:class:`DenseMPOList`
            Representing the operator that we are multiplying to self.

        operators : :class:`TNOperators`
            The operator dictionary for the simulation. The corresponding second
            order operators are generated within the function if not set yet.

        self_conj : Boolean, optional
            Tells if self needs to be complex conjugated.
            Default is False.

        self_transpose : Boolean, optional
            Tells if self needs to be transposed.
            Default is False.

        other_conj : Boolean, optional
            Tells if other needs to be complex conjugated.
            Default is False.

        other_transpose : Boolean, optional
            Tells if other needs to be transposed.
            Default is False.

        Return
        ------
        mpo_product : :py:class:`DenseMPOList`
            The product of the operators represented by self and other.

        Details
        -------

        This function is potentially costly in terms of memory and computation
        time. While the computational complexity of this approach cannot be
        mitigated within `DenseMPOLists`, the memory requirements can be tuned
        by using `_mpo_product_iter`, which is an iterator over smaller
        `DenseMPOLists`.

        """
        # We will need all combinations of the operators (can be called
        # multiple times without generating 4th order etc).
        operators.generate_products_2nd_order()

        new_dense_mpo_list = []
        for elem in self._mpo_product_term_iter(
            other,
            operators,
            self_conj=self_conj,
            self_transpose=self_transpose,
            other_conj=other_conj,
            other_transpose=other_transpose,
        ):
            new_dense_mpo_list.append(elem)

        return DenseMPOList(new_dense_mpo_list)

    def _mpo_product_iter(
        self,
        other,
        operators,
        self_conj=False,
        self_transpose=False,
        other_conj=False,
        other_transpose=False,
        batch_size=None,
        print_progress=False,
    ):
        """
        Compute the product of two MPOs encoded as DenseMPOList. This version
        is the iterator version, i.e., it can return multiple
        :class:`DenseMPOList` building the full product via an iterator. The
        order of product is self*other. If the operators at site j are
        self_op_j and other_op_j respectively, `mpo_product` returns the
        DenseMPOList whose operator at site j is the operator product
        self_op_j*other_op_j. The input arguments `self` and `other` remain
        unchanged in this method.

        Parameters
        ----------

        other : :py:class:`DenseMPOList`
            Representing the operator that we are multiplying to self.
            `other` is the right-hand operator in the multiplcation.

        operators : :class:`TNOperators`
            The operator dictionary for the simulation. The corresponding second
            order operators are generated within the function if not set yet.

        self_conj : Boolean, optional
            Tells if self needs to be complex conjugated.
            Default is False.

        self_transpose : Boolean, optional
            Tells if self needs to be transposed.
            Default is False.

        other_conj : Boolean, optional
            Tells if other needs to be complex conjugated.
            Default is False.

        other_transpose : Boolean, optional
            Tells if other needs to be transposed.
            Default is False.

        batch_size : int | None, optional
            Build smaller MPOs to keep memory cost low. Efficiency might
            suffer to a certain extent at the same time as work has to
            be redone.
            Default to `None` (one MPO).

        print_progress : bool, optional
            If True, progress will be printed to logger.
            Default to False.

        Yields as iterator
        ------------------

        mpo_product : :py:class:`DenseMPOList`
            The product of the operators represented by self and other
            as one or more :py:class:`DenseMPOList`.
        """
        # We will need all combinations of the operators (can be called
        # multiple times without generating 4th order etc).
        operators.generate_products_2nd_order()

        if batch_size is None:
            is_next_mpo = lambda ii, nn: False
        else:
            is_next_mpo = lambda ii, nn: ii % nn == 0

        new_dense_mpo_list = []
        cntr = 0
        nn = len(self) * len(other)
        for elem in self._mpo_product_term_iter(
            other,
            operators,
            self_conj=self_conj,
            self_transpose=self_transpose,
            other_conj=other_conj,
            other_transpose=other_transpose,
        ):
            new_dense_mpo_list.append(elem)

            cntr += 1
            if is_next_mpo(cntr, batch_size):
                if print_progress:
                    progress_str = (
                        f"_mpo_product_iter: {np.round(cntr / nn, decimals=3)}%"
                    )
                    logger.info(progress_str)
                yield new_dense_mpo_list

                new_dense_mpo_list = []

        if len(new_dense_mpo_list) > 0:
            yield new_dense_mpo_list

    def _mpo_product_term_iter(
        self,
        other,
        operators,
        self_conj=False,
        self_transpose=False,
        other_conj=False,
        other_transpose=False,
    ):
        """
        Build the product between two MPO represented as :class:`DenseMPOList`
        via an iterator, which returns term by term to build a new
        :class:`DenseMPOList`

        Arguments
        ---------
        other : :py:class:`DenseMPOList`
            Representing the operator that we are multiplying to self.
            `other` is the right-hand operator in the multiplcation.

        operators : :class:`TNOperators`
            The operator dictionary for the simulation. The corresponding second
            order operators are generated within the function if not set yet.

        self_conj : Boolean, optional
            Tells if self needs to be complex conjugated.
            Default is False.

        self_transpose : Boolean, optional
            Tells if self needs to be transposed.
            Default is False.

        other_conj : Boolean, optional
            Tells if other needs to be complex conjugated.
            Default is False.

        other_transpose : Boolean, optional
            Tells if other needs to be transposed.
            Default is False.

        Yields as iterator
        ------------------

        MPOs : :class:`DenseMPO`
            Term-by-term which can build for example
            a DenseMPOList representing the product.
        """
        # Figure out the name of the operators set once
        set_names = operators.set_names
        if len(set_names) > 1:
            # This would be tricky, but probably another loop would be sufficient
            # under the assumption there are no cross-terms between operators sets.
            raise QTeaLeavesError("Multiple operators sets not yet supported here.")
        set_name = set_names[0]

        # Collect id terms in one (added at the end)
        weight_id = 0.0

        for dense_mpo1 in self:
            if dense_mpo1.current_max_bond_dim != 1:
                raise ValueError(
                    "One MPO in `self` has non-dummy links. Product not implemented."
                )
            for dense_mpo2 in other:
                new_mpo_sites_list = []
                if dense_mpo2.current_max_bond_dim != 1:
                    raise ValueError(
                        "One MPO in `other` has non-dummy links. Product not implemented."
                    )
                # create the new list of sites in the DenseMPO
                new_sites = sorted(
                    list(set().union(dense_mpo1.sites, dense_mpo2.sites))
                )

                for xx in new_sites:
                    strength = 1.0
                    weight = 1.0
                    op_str = ""
                    # First MPO
                    if xx in dense_mpo1.sites:
                        idx = dense_mpo1.sites.index(xx)
                        strength *= dense_mpo1[idx].strength
                        weight *= dense_mpo1[idx].weight
                        op_str = _op_string_mul(
                            op_str, dense_mpo1[idx].str_op, self_conj, self_transpose
                        )

                    # 2nd MPO
                    if xx in dense_mpo2.sites:
                        idx = dense_mpo2.sites.index(xx)
                        strength *= dense_mpo2[idx].strength
                        weight *= dense_mpo2[idx].weight
                        op_str = _op_string_mul(
                            op_str, dense_mpo2[idx].str_op, other_conj, other_transpose
                        )

                    check_entry = operators.check_alternative_op(set_name, op_str)
                    if isinstance(check_entry, str):
                        if check_entry == "id":
                            # We can reduce the number of terms by collecting them
                            # and add a single offset at the end.
                            weight_id += weight
                            continue

                        op_str = check_entry

                    name = op_str

                    # Add actual MPO
                    pstrength = None
                    new_mpo_site = MPOSite(
                        xx, name, pstrength, weight, operators=operators
                    )
                    new_mpo_site.strength = strength

                    new_mpo_sites_list.append(new_mpo_site)
                yield DenseMPO(new_mpo_sites_list)

        if weight_id != 0:
            new_mpo_site = MPOSite(0, "id", None, weight_id, operators=operators)
            new_mpo_site.strength = 1.0

            yield DenseMPO([new_mpo_site])


def _duplicate_check_and_set(ops_dict, key, op):
    """
    Checks if an equivalent operator is already in the dictionary and returns
    the key, otherwise sets operator and returns key passed to the function.

    Arguments
    ---------

    ops_dict : :class:`TNOperators`
        Operator dictionary. Restricted to single-set of operators (for now).

    key : str
        Suggested key for operator if not already in the dictionary.

    op : :class:`_AbstractQteaTensor`
        Operator represented as tensor.

    Returns
    -------

    existing_key : str
        The key under which `op` can be found now. Either existing key
         or `key` from the function arguments.
    """
    if len(ops_dict.set_names) != 1:
        # We can resolve this by appending something to the string name
        raise NotImplementedError("Not implemented for different sets.")

    set_name = ops_dict.set_names[0]

    # pylint: disable=protected-access
    if key in ops_dict._ops_dicts[set_name]:
        original_key = key
        idx = 0
        while op.are_equal(ops_dict._ops_dicts[set_name][key], tol=10 * op.dtype_eps):
            idx += 1
            key = f"{original_key}_{idx}"

            if key not in ops_dict._ops_dicts[set_name]:
                # Condition 1: key not inside dict, exit
                break

    existing_key = None

    for key_ii, op_ii in ops_dict._ops_dicts[set_name].items():
        if op.are_equal(op_ii, tol=10 * op.dtype_eps):
            existing_key = key_ii
            break

    if existing_key is None:
        ops_dict[(set_name, key)] = op
        existing_key = key

    # pylint: enable=protected-access
    return existing_key
