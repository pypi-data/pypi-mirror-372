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
Abstract tensor network for matrices-like structure
"""

# pylint: disable=too-many-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-lines
# pylint: disable=too-many-public-methods


from copy import deepcopy
from warnings import warn

import numpy as np

from qtealeaves.convergence_parameters import TNConvergenceParameters
from qtealeaves.tensors.abstracttensor import _AbstractQteaTensor

from .abstract_tn import _AbstractTN

__all__ = ["_AbstractMatrixTN"]


class _AbstractMatrixTN(_AbstractTN):
    """
    Abstract class for tensor networks of the type:
     | | |
    -o-o-o-
     | | |

    It will be used for both the LPTN and the DenseMPO

    Parameters
    ----------
    num_sites : int
        Number of sites
    convergence_parameters : :py:class:`TNConvergenceParameters`
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
    requires_singvals : boolean, optional
        Allows to enforce SVD to have singular values on each link available
        which might be useful for measurements, e.g., bond entropy (the
        alternative is traversing the whole TN again to get the bond entropy
        on each link with an SVD).
    tensor_backend : `None` or instance of :class:`TensorBackend`
        Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.
    """

    def __init__(
        self,
        num_sites,
        convergence_parameters,
        local_dim,
        requires_singvals,
        tensor_backend,
    ):
        super().__init__(
            num_sites,
            convergence_parameters,
            local_dim,
            requires_singvals,
            tensor_backend,
        )

        # Potential danger: it does not make sense to generate singvals
        # according to num_sites if the tensors are empty.
        self._tensors = []
        self._singvals = [None] * (self.num_sites + 1)

    # --------------------------------------------------------------------------
    #                               Properties
    # --------------------------------------------------------------------------

    @property
    def iso_center(self):
        """Scalar isometry center"""
        if self._iso_center is None:
            return self._iso_center
        return self._iso_center[0]

    @iso_center.setter
    def iso_center(self, value):
        """Change the value of the iso center"""
        if np.isscalar(value):
            self._iso_center = (value, value + 2)
        elif value is None:
            self._iso_center = value
        elif isinstance(value, tuple):
            self._iso_center = value
        else:
            self._iso_center = tuple(value)

    @property
    def default_iso_pos(self):
        """Returns default iso position to use in iso_towards"""
        return self.num_sites - 1

    @property
    def current_max_bond_dim(self):
        """Maximum bond dimension of the mps"""
        max_bond_dims = [(tt.shape[0], tt.shape[3]) for tt in self]
        return np.max(max_bond_dims)

    # --------------------------------------------------------------------------
    #                          Overwritten operators
    # --------------------------------------------------------------------------

    def __len__(self):
        """
        Provide number of sites in the _AbstractMatrixTN
        """
        return self.num_sites

    def __add__(self, other):
        """
        Perform the addition of two _AbstractMatrixTN, such that:
        |abs_mat_sum> = |abs_mat_1>+|abs_mat_2>

        Parameters
        ----------
        other : _AbstractMatrixTN
            _AbstractMatrixTN to sum with this

        Returns
        -------
        _AbstractMatrixTN
            summation
        """
        if not isinstance(other, _AbstractMatrixTN):
            raise TypeError("Only two _AbstractMatrixTN classes can be summed")
        if self.num_sites != other.num_sites:
            raise ValueError(
                "Number of sites must be the same to concatenate _AbstractMatrixTN"
            )
        if np.any(self.local_dim != other.local_dim):
            raise ValueError(
                "Local dimension must be the same to concatenate _AbstractMatrixTN"
            )

        other.iso_towards(self.iso_center, True)
        max_bond_dim = max(
            self.convergence_parameters.max_bond_dimension,
            other.convergence_parameters.max_bond_dimension,
        )
        convergence_params = deepcopy(self.convergence_parameters)
        convergence_params.sim_params["max_bond_dimension"] = max_bond_dim

        tensor_list = []
        for idx in range(self.num_sites):
            tens_a = self.get_tensor_of_site(idx)
            tens_b = other.get_tensor_of_site(idx)
            shape_c = np.array(tens_a.shape) + np.array(tens_b.shape)
            shape_c[1] = tens_a.shape[1]
            shape_c[2] = tens_a.shape[2]
            if idx == 0 and [tens_a.shape[0], tens_b.shape[0]] == [1, 1]:
                tens_c = tens_a.stack_link(tens_b, 3)
            elif idx == self.num_sites - 1 and [tens_a.shape[3], tens_b.shape[3]] == [
                1,
                1,
            ]:
                tens_c = tens_a.stack_link(tens_b, 0)
            else:
                tens_c = tens_a.stack_first_and_last_link(tens_b)

            tensor_list.append(tens_c)
            idx += 1

        tn_sum = self.__class__.from_tensor_list(
            tensor_list,
            conv_params=convergence_params,
            iso_center=self._iso_center,
            tensor_backend=self._tensor_backend,
        )

        return tn_sum

    def __iadd__(self, other):
        """Concatenate the _AbstractMatrixTN other with self inplace"""
        tn_sum = self.__add__(other)

        return tn_sum

    # --------------------------------------------------------------------------
    #                       classmethod, classmethod like
    # --------------------------------------------------------------------------

    @classmethod
    def from_tensor_list(
        cls, tensor_list, conv_params=None, iso_center=None, tensor_backend=None
    ):
        """
        Initialize the _AbstractMatrixTN tensors using a list of correctly
        shaped tensors

        Parameters
        ----------
        tensor_list : list of ndarrays
            List of tensors for initializing the _AbstractMatrixTN
        conv_params : :py:class:`TNConvergenceParameters`, optional
            Input for handling convergence parameters.
            In particular, in the _AbstractMatrixTN simulator we
            are interested in:
            - the maximum bond dimension (`max_bond_dimension`)
            - the cut ratio (`cut_ratio`) after which the
            singular values in SVD are neglected, all
            singular values such that :math:`\\lambda` /
            :math:`\\lambda_max` <= :math:`\\epsilon` are truncated
        iso_center : None or list of int, optional
            Isometry center is between the two sites
            specified in a list. If the _AbstractMatrixTN has no
            isometry center, iso_center = None.
            Default is None
        tensor_backend : `None` or instance of :class:`TensorBackend`
            Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.

        Return
        ------
        obj : :py:class:`_AbstractMatrixTN`
            The _AbstractMatrixTN class composed of the given tensors
        --------------------------------------------------------------------
        """
        local_dim = tensor_list[0].shape[1]
        max_bond_dims = [(tt.shape[0], tt.shape[3]) for tt in tensor_list]
        max_bond_dim = np.max(max_bond_dims)

        if conv_params is None:
            conv_params = TNConvergenceParameters(max_bond_dimension=int(max_bond_dim))
        obj = cls(
            len(tensor_list),
            conv_params,
            local_dim=local_dim,
            tensor_backend=tensor_backend,
            requires_singvals=False,
        )
        obj._tensors = tensor_list
        obj.iso_center = iso_center

        # Ensure we have _AbstractQteaTensors from here on
        tensor_cls = obj._tensor_backend.tensor_cls
        for ii, elem in enumerate(obj._tensors):
            if not isinstance(elem, _AbstractQteaTensor):
                obj._tensors[ii] = tensor_cls.from_elem_array(elem)

        obj.convert(obj._tensor_backend.dtype, obj._tensor_backend.device)
        return obj

    # --------------------------------------------------------------------------
    #                     Abstract methods to be implemented
    # --------------------------------------------------------------------------

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

    def get_tensor_of_site(self, idx):
        """
        Generic function to retrieve the tensor for a specific site. Compatible
        across different tensor network geometries.

        Parameters
        ----------
        idx : int
            Return tensor containin the link of the local
            Hilbert space of the idx-th site.
        """
        return self._tensors[idx]

    def iso_towards(
        self,
        new_iso,
        keep_singvals=False,
        trunc=False,
        conv_params=None,
        move_to_memory_device=None,
        normalize=False,
    ):
        """Shift the isometry center to the tensor"""
        if np.isscalar(new_iso):
            ind_final = [new_iso, new_iso + 2]
        else:
            ind_final = new_iso
        if conv_params is None:
            conv_params = self.convergence_parameters
        if self.iso_center is None:
            # Complete reisometrization
            self._iso_center = (0, 2)
            self.iso_towards(self.num_sites - 1)

        do_svd = self._requires_singvals or trunc
        ind_init = self._iso_center

        # How to shift? Suppose X is the gauge center and we want to shift it to
        # one place to the right.

        #   |  |  |                                     |  |     |
        # --O--X--O--  --(QR decompose middle one)->  --O--Q--R--O--
        #   |  |  |                                     |  |     |

        #                                              |  |  |
        # --(contract R with tensor on the right)->  --O--O--X--  :)
        #           (rename Q --> O)                   |  |  |

        # Remark: when shifting gauge center to the left, we must ensure
        # that the unitary matrix (Q) is on the right, and the upper
        # triangular matrix (R) is on the left.

        # calculate the direction in which the QR decompositions must be
        # done (direction = -1 means we shift gauge center to the left,
        # and direction = 1 means we shift gauge center to the right)
        center_init = ind_init[0]
        center_final = ind_final[0]
        if center_init == center_final:
            return
        direction = np.sign(center_final - center_init)

        # two separate cases for shifting to the left and to the right

        if direction > 0:
            # Moving to the right
            for ii in range(center_init, center_final):
                if do_svd:
                    tensor, rr_mat, singvals, _ = self.get_tensor_of_site(ii).split_svd(
                        [0, 1, 2],
                        [3],
                        contract_singvals="R",
                        conv_params=conv_params,
                        no_truncation=not trunc,
                        is_link_outgoing_left=True,
                    )
                    self._singvals[ii + 1] = singvals
                else:
                    tensor, rr_mat = self.get_tensor_of_site(ii).split_qr(
                        [0, 1, 2], [3], is_q_link_outgoing=True
                    )
                    if not keep_singvals:
                        self._singvals[ii + 1] = None

                self[ii] = tensor
                self[ii + 1] = rr_mat @ self.get_tensor_of_site(ii + 1)
                if self.eff_op is not None:
                    self._update_eff_ops([ii, ii + 1])

        else:
            # Moving to the left
            for ii in range(center_init, center_final, -1):
                if do_svd:
                    rr_mat, tensor, singvals, _ = self.get_tensor_of_site(ii).split_svd(
                        [0],
                        [1, 2, 3],
                        contract_singvals="L",
                        conv_params=conv_params,
                        no_truncation=not trunc,
                        is_link_outgoing_left=False,
                    )
                else:
                    tensor, rr_mat = self.get_tensor_of_site(ii).split_qr(
                        [1, 2, 3],
                        [0],
                        perm_left=[3, 0, 1, 2],
                        perm_right=[1, 0],
                        is_q_link_outgoing=False,
                    )
                    if not keep_singvals:
                        self._singvals[ii + 1] = None

                self[ii] = tensor
                self[ii - 1] = self.get_tensor_of_site(ii - 1).tensordot(
                    rr_mat, ([3], [0])
                )
                if self.eff_op is not None:
                    self._update_eff_ops([ii, ii - 1])
        self._iso_center = (center_final, center_final + 2)
        if normalize:
            self.normalize()

    def isometrize_all(self):
        """
        Isometrize towards the default isometry center with no assumption of previous
        isometry center, e.g., works as well on random states.

        Returns
        -------

        None
        """
        # MatrixTN is easy, iso_towards considers first/last orthogonal site
        # iso_towards can be used always as long as None or distance 2
        if self._iso_center is not None:
            if self._iso_center[1] - self._iso_center[0] != 2:
                raise NotImplementedError(
                    "Partially isometrized MatrixTN needs to be implemtented."
                )
        self.iso_towards(self.default_iso_pos)
        return

    def default_sweep_order(self, skip_exact_rgtensors=False):
        """
        Default sweep order to be used in the ground state search/time evolution.
        Default for _AbstractMatrixTN is left-to-right.

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
        link_self = 3 if pos < pos_partner else 0
        link_partner = 0 if pos < pos_partner else 3

        return pos_partner, link_self, link_partner

    def scale(self, factor):
        """
        Multiply the tensor network by a scalar factor.

        Parameters
        ----------
        factor : float
            Factor for multiplication of current tensor network.
        """
        if self.iso_center is None:
            self.install_gauge_center()

        tens = self.get_tensor_of_site(self.iso_center)
        tens *= factor
        self[self.iso_center] = tens

    def scale_inverse(self, factor):
        """
        Multiply the tensor network by a scalar factor.

        Parameters
        ----------
        factor : float
            Factor for multiplication of current tensor network.
        """
        if self.iso_center is None:
            self.install_gauge_center()

        tens = self.get_tensor_of_site(self.iso_center)
        tens /= factor
        self[self.iso_center] = tens

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
        """

        self.iso_towards(idx, keep_singvals=keep_singvals, normalize=normalize)

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
        raise NotImplementedError("Not yet implemented for _AbstractMatrixTN.")

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
        raise NotImplementedError("Not yet implemented for _AbstractMatrixTN.")

    # --------------------------------------------------------------------------
    #                   Choose to overwrite instead of inheriting
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    #                                  Unsorted
    # --------------------------------------------------------------------------

    def kron(self, other):
        """
        Concatenate _AbstractMatrixTN tensors with other _AbstractMatrixTN's
        tensors. The function doesn't renormalize tensor network.

        Parameters
        ----------
        other : _AbstractMatrixTN
            _AbstractMatrixTN to concatenate

        Return
        ------
        _AbstractMatrixTN
            kronecker product of the
            two _AbstractMatrixTN's
        """

        if not isinstance(other, _AbstractMatrixTN):
            raise TypeError(
                "Only two _AbstractMatrixTN classes can be concatenated, not "
                f"{type(other)} and _AbstractMatrixTN."
            )
        if self.get_tensor_of_site(-1).shape[3] != other.get_tensor_of_site(0).shape[0]:
            raise ValueError(
                "Given _AbstractMatrixTN with boundary bond dimension "
                f"{other.get_tensor_of_site(0).shape[0]}, not compatible"
                " for performing Kronecker product with _AbstractMatrixTN"
                " with boundary bond dimension "
                f"{self.get_tensor_of_site(-1).shape[3]}"
            )

        # concatenates the tensors from both LPTN's to one list
        tensor_list = self[:] + other[:]
        max_bond_dim = max(
            self.convergence_parameters.max_bond_dimension,
            other.convergence_parameters.max_bond_dimension,
        )
        cut_ratio = min(
            self.convergence_parameters.cut_ratio,
            other.convergence_parameters.cut_ratio,
        )
        conv_params = TNConvergenceParameters(
            max_bond_dimension=max_bond_dim, cut_ratio=cut_ratio
        )

        lptn_kron = self.__class__.from_tensor_list(
            tensor_list=tensor_list,
            conv_params=conv_params,
            tensor_backend=self._tensor_backend,
        )

        return lptn_kron

    def install_gauge_center(self):
        """
        Install a gauge center to the rightmost site
        of the _AbstractMatrixTN.

        Returns
        -------
        None
        """

        if self.iso_center is not None:
            raise ValueError(
                f"_AbstractMatrixTN already has a gauge center between the sites {self.iso_center}."
            )

        # How to install a gauge center:

        #   |  |  |                                        |     |  |
        # --O--O--O--  --(QR decompose the first one)->  --Q--R--O--O--
        #   |  |  |                                        |     |  |

        #                                              |  |  |
        # --(contract R with tensor on the right)->  --Q--O--O--
        #           (Q is now unitary)                 |  |  |

        # - repeat the same for the next tensor, and so on until all
        #   the tensors except the last one are unitary.

        for ii in range(0, self.num_sites - 1):
            q_mat, r_mat = self.get_tensor_of_site(ii).split_qr([0, 1, 2], [3])

            self[ii] = q_mat
            self[ii + 1] = r_mat @ self.get_tensor_of_site(ii + 1)

        self._iso_center = (self.num_sites - 1, self.num_sites + 1)
        return None

    def apply_one_site_operator(self, op, pos, top=False):
        """
        Applies a one operator `op` to the site `pos` of the _AbstractMatrixTN.

        Parameters
        ----------
        op: numpy array shape (local_dim, local_dim)
            Matrix representation of the quantum gate
        pos: int
            Position of the qubit where to apply `op`.
        top: bool, optional
            If True, apply the two-site operator to the top of the tensor network
            instead of from the bottom, Default to False.

        """
        if top:
            new_tensor = self.get_tensor_of_site(pos).tensordot(op, (2, 1))
            new_tensor.transpose_update([0, 1, 3, 2])
        else:
            new_tensor = self.get_tensor_of_site(pos).tensordot(op, (1, 1))
            new_tensor.transpose_update([0, 3, 1, 2])
        self[pos] = new_tensor

    def apply_two_site_operator(self, op, pos, swap=False, top=False):
        """
        Applies a two-site operator `op` to the site `pos`, `pos+1` of the _AbstractMatrixTN.

        Parameters
        ----------
        op: numpy array shape (local_dim, local_dim, local_dim, local_dim)
            Matrix representation of the quantum gate
        pos: int or list of ints
            Position of the qubit where to apply `op`. If a list is passed,
            the two sites should be adjacent. The first index is assumed to
            be the control, and the second the target. The swap argument is
            overwritten if a list is passed.
        swap: bool, optional
            If True swaps the operator. This means that instead of the
            first contraction in the following we get the second. Defalt to False
        top: bool, optional
            If True, apply the two-site operator to the top of the tensor network
            instead of from the bottom, Default to False.

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
        if np.isscalar(pos):
            pos = (pos, pos + 1)
        if pos[1] - pos[0] != 1:
            raise ValueError(
                (
                    "Apply two site operator can only be used for",
                    " adjacent sites in the _AbstractMatrixTN",
                )
            )
        pos = pos[0]

        op = op.reshape([self._local_dim[pos], self._local_dim[pos + 1]] * 2)

        if swap:
            op = op.transpose([1, 0, 3, 2])

        self.site_canonize(pos, True)
        two_tens = self.get_tensor_of_site(pos).tensordot(
            self.get_tensor_of_site(pos + 1), (3, 0)
        )

        if top:
            contracted = two_tens.tensordot(op, ([2, 4], [2, 3]))
            contracted.transpose_update([0, 1, 2, 4, 5, 3])
        else:
            contracted = two_tens.tensordot(op, ([1, 3], [2, 3]))
            contracted.transpose_update([0, 4, 1, 5, 2, 3])

        tens_left, tens_right, singvals, singvals_cutted = contracted.split_svd(
            [0, 1, 2],
            [3, 4, 5],
            contract_singvals="L",
            conv_params=self.convergence_parameters,
        )
        self[pos] = tens_left
        self[pos + 1] = tens_right
        self._singvals[pos + 1] = singvals
        return singvals_cutted

    def apply_mpo(self, mpo, top=False):
        """
        Apply an _AbstractMatrixTN to the _AbstractMatrixTN on the sites `sites`.
        The MPO should have the following convention for the links:
        0 is left link. 1 is physical link pointing downwards.
        2 is phisical link pointing upwards. 3 is right link.

        The sites are encoded inside the DenseMPO class.

        Parameters
        ----------
        mpo : DenseMPO
            MPO to be applied
        top : bool, optional
            Apply the MPO on the upper legs of the _AbstractMatrixTN.
            Default to False.

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
        lptn_leg = 2 if top else 1
        op_leg = 1 if top else 2

        tot_singvals_cut = []
        # Operator index
        oidx = 0
        next_site = self.get_tensor_of_site(sites[0]).eye_like(
            self.get_tensor_of_site(sites[0]).shape[0]
        )
        for sidx in range(sites[0], sites[-1] + 1):
            tens = self.get_tensor_of_site(sidx)
            if sidx in sites:
                #    |k
                # i -o- l
                #    |j     = T(i,k,l,m,n,p) -> T(i,m,n,k,l,p)
                # m -o- p
                #    |n
                tens = tens.tensordot(operators[oidx], ([lptn_leg], [op_leg]))
                tr_index = (0, 3, 1, 4, 2, 5) if top else (0, 3, 4, 1, 2, 5)
                tens.transpose_update(tr_index)
                # T(i,m,n,k,l,p) -> T(im, n, k, lp)
                tens.reshape_update(
                    (np.prod(tens.shape[:2]), tens.shape[2], tens.shape[3], -1)
                )

                # The matrix next, from the second cycle, is bringing the isometry center in tens
                # next = next.reshape(-1, tens.shape[0])
                #           |k         |k
                # x -o- im -o- lp = x -o- lp
                #           |n         |n
                tens = next_site.tensordot(tens, ([1], [0]))
                oidx += 1

                if sidx + 1 in sites:
                    # Move the isometry when the next site has an MPO (and thus left-dimension kn)
                    #    |k            |k
                    # x -o- lp -->  x -o- y -o- lp
                    #    |n            |n
                    self[sidx], next_site, _, singvals_cut = tens.split_svd(
                        [0, 1, 2],
                        [3],
                        contract_singvals="R",
                        conv_params=self._convergence_parameters,
                        no_truncation=True,
                    )

                    tot_singvals_cut += list(singvals_cut)
                elif sidx == sites[-1]:
                    # End of the procedure
                    self[sidx] = tens
                else:
                    # Move the isometry when the next site does not have an MPO
                    #    |k            |k
                    # x -o- lp -->  x -o- y -o- lp
                    #    |n            |n
                    self[sidx], next_site = tens.split_qr([0, 1, 2], [3])
                    #                p|
                    # y -o- lp --> y -o- l
                    # T(y,kn) -> T(y, k, n) -> T(y, n, k)
                    next_site.reshape_update(
                        (next_site.shape[0], -1, operators[oidx - 1].shape[3])
                    )
                    next_site.transpose_update((0, 2, 1))

            else:
                # Site does not have an operator, just bring the isometry here
                #   p|     |l
                # y -o- i -o- k -> T(y, p, j, l, k) -> T(y, j, p, l, k)
                #          | j
                tens = next_site.tensordot(tens, ([2], [0]))
                tens.transpose_update((0, 2, 3, 1, 4))

                if sidx + 1 in sites:
                    tens.reshape_update(
                        (tens.shape[0], tens.shape[1], tens.shape[2], -1)
                    )
                    self[sidx], next_site, _, singvals_cut = tens.split_svd(
                        [0, 1, 2],
                        [3],
                        contract_singvals="R",
                        conv_params=self._convergence_parameters,
                        no_truncation=True,
                    )
                    tot_singvals_cut += list(singvals_cut)
                else:
                    #   |l|p         |l    |p
                    # y -o- k --> y -o- s -o- k
                    #    |j          |j
                    self[sidx], next_site = tens.split_qr([0, 1, 2], [3, 4])

        self._iso_center = (sites[-1], sites[-1] + 2)
        self.iso_towards(sites[0], trunc=True, keep_singvals=True)

        return tot_singvals_cut

    def swap_qubits(self, sites, conv_params=None, trunc=True):
        """
        This function applies a swap gate to sites,
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
            two_sites = self.get_tensor_of_site(pos).tensordot(
                self.get_tensor_of_site(pos + 1), ([3], [0])
            )
            # Swap the qubits
            two_sites.transpose_update([0, 3, 4, 1, 2, 5])
            if trunc:
                left, right, singvals, singvals_cut = two_sites.split_svd(
                    [0, 1, 2], [3, 4, 5], contract_singvals="R", conv_params=conv_params
                )
                self._singvals[pos + 1] = singvals
                singvals_cut_tot.append(singvals_cut)
            else:
                left, right = two_sites.split_qr([0, 1, 2], [3, 4, 5])

            if pos < sites[1] - 2:
                left.convert(device=self._tensor_backend.memory_device, stream=True)
            # Update tensor and iso center
            self[pos] = left
            self[pos + 1] = right
        self._iso_center = (sites[1], sites[1] + 2)

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
            two_sites = self.get_tensor_of_site(pos - 1).tensordot(
                self.get_tensor_of_site(pos), ([3], [0])
            )
            # Swap the qubits
            two_sites.transpose_update([0, 3, 4, 1, 2, 5])
            if trunc:
                left, right, singvals, singvals_cut = two_sites.split_svd(
                    [0, 1, 2], [3, 4, 5], contract_singvals="L", conv_params=conv_params
                )
                self._singvals[pos] = singvals
                singvals_cut_tot.append(singvals_cut)
            else:
                right, left = two_sites.split_qr(
                    [3, 4, 5],
                    [0, 1, 2],
                    perm_left=[3, 0, 1, 2],
                    perm_right=[1, 2, 3, 0],
                )

            right.convert(device=self._tensor_backend.memory_device, stream=True)
            # Update tensor and iso center
            self[pos - 1] = left
            self[pos] = right
        self._iso_center = (sites[0], sites[0] + 2)

        return singvals_cut_tot

    def to_matrix(self, qiskit_order=False, max_qubit_equivalent=10):
        """
        Return the tensor list representation of the _AbstractMatrixTN.

        Arguments
        ---------

        qiskit_order: bool, optional
            weather to use qiskit ordering or the theoretical one. For
            example the state |011> has 0 in the first position for the
            theoretical ordering, while for qiskit ordering it is on the
            last position.
        max_qubit_equivalent: int, optional
            Maximum number of qubit-equivalents the matrix can have and still be
            transformed into a matrix.
            If the number of qubit-equivalents is greater, it will throw an exception.
            Default to 10.

        Return
        ------
        QteaTensor
            Tensor representation of the _AbstractMatrixTN with
            rank-2 tensor without symmetries and rank-3 tensor
            with symmetries.
        """
        if self.get_tensor_of_site(0).has_symmetry:
            return self._to_matrix_symm(qiskit_order, max_qubit_equivalent)

        if np.prod(self.local_dim) > 2**max_qubit_equivalent:
            raise RuntimeError(
                "Maximum number of sites for the matrix is "
                + f"fixed to the equivalent of {max_qubit_equivalent} qubit sites"
            )
        rho = self.get_tensor_of_site(0)
        for ii in range(1, self.num_sites):
            tensor = self.get_tensor_of_site(ii)
            rho = rho.tensordot(tensor, ([-1], [0]))
        rho.reshape_update(list(self.local_dim) * 2)

        order = list(range(0, 2 * self.num_sites, 2)) + list(
            range(1, 2 * self.num_sites, 2)
        )
        rho.transpose_update(order)

        if qiskit_order:
            order = "F"
        else:
            order = "C"

        return rho.reshape([np.prod(self.local_dim)] * 2, order=order)

    def _to_matrix_symm(self, qiskit_order, max_qubit_equivalent):
        """
        Extract matrix representation of `_AbstractMatrixTN` with symmetries.

        Returns
        -------
        QteaTensor
            Tensor representation of the _AbstractMatrixTN with
            rank-3 tensor, where the links are rows, columns,
            and symmetry sector. The latter should not carry any
            degeneracy in common scenarioes.
        """
        if qiskit_order:
            raise NotImplementedError("Cannot use qiskit order yet with symmetric TN.")

        rho = self.get_tensor_of_site(0)
        dim = rho.shape[1]

        for ii in range(1, self.num_sites):
            tensor = self.get_tensor_of_site(ii)
            dim *= tensor.shape[1]
            if dim > 2**max_qubit_equivalent:
                raise RuntimeError(
                    "Maximum number of sites for the matrix is "
                    + f"fixed to the equivalent of {max_qubit_equivalent} qubit sites"
                )
            c_link = rho.ndim - 1
            rho = rho.tensordot(tensor, ([c_link], [0]))

        # Incoming link from left must be dummy
        rho.remove_dummy_link(0)

        nn = rho.ndim
        perm = list(range(0, nn - 1, 2)) + list(range(1, nn, 2)) + [nn - 1]
        rho = rho.transpose(perm)
        # new leg order: row0, ..., row_n, col_0, ..., col_n, sector

        qlinks = list(range(nn // 2))
        rlinks = list(range(nn // 2, nn))
        _, rho = rho.split_qr(qlinks, rlinks, is_q_link_outgoing=True)
        # new leg order: rows, col_0, ..., col_n, sector

        mm = rho.ndim
        qlinks = list(range(1, mm - 1))
        rlinks = [0, mm - 1]
        _, rho = rho.split_qr(qlinks, rlinks, is_q_link_outgoing=False)
        # new leg order: cols, rows, sector

        # Return leg-order rows, cols, sector
        return rho.transpose([1, 0, 2])

    def get_projector_function(self, pos, pos_links):
        """
        Generates a function which locally projects out the effective projectors.
        Used in the excited state search.
        """
        raise NotImplementedError(
            "The get_projector_function is not implemented for AbstractMatrixTN."
        )
