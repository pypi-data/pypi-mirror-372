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
Sum of local terms in a Hamiltonian or Lindblad equation.
"""

# pylint: disable=too-many-locals
# pylint: disable=too-many-lines
# pylint: disable=too-many-arguments
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements

from copy import deepcopy

import numpy as np

from qtealeaves.tooling import QTeaLeavesError
from qtealeaves.tooling.mapping import map_selector

from .localterm import LindbladTerm

__all__ = ["SumLindbladTerm"]


class SumLindbladTerm(LindbladTerm):
    """
    Sum of local Lindblad operators acting at one site are defined via this
    term. For the arguments see See :class:`LocalTerm.check_dim`.

    **Details**

    The Lindblad equation with the Lindblad operator $L = \\sum_i L_i$
    is implemented as:

    .. math::

        \\frac{d}{dt} \\rho = -i [H, \\rho]
           + \\sum \\gamma (L \\rho L^{\\dagger}
           - \\frac{1}{2} \\{ L^{\\dagger} L, \\rho \\})

    **Arguments**

    operator : list of two str
        String identifier for the operator. Before launching the simulation,
        the python API will check that the operator is defined.
        The operator should be a list of length 2 and it should contain
        in order L and Ldag.

    strength : str, callable, numeric (optional)
        Defines the coupling strength of the local terms. It can
        be parameterized via a value in the dictionary for the
        simulation or a function.
        Default to 1.

    prefactor : numeric, scalar (optional)
        Scalar prefactor, e.g., in order to take into account signs etc.
        Default to 1.

    coupling_entries : None or parameterized
        Individual coupling for each site. Rank equals dimensionality.
        Default to `None` (equal to unit coupling 1).

    mask : callable or ``None``, optional
        The true-false-mask allows to apply the local Hamiltonians
        only to specific sites, i.e., with true values. The function
        takes the dictionary with the simulation parameters as an
        argument.
        Default to ``None`` (all sites have a local term)

    **Attributes**

    map_type : str, optional
        Selecting the mapping from a n-dimensional system to the
        1d system required for the TTN simulations.
    """

    def __init__(
        self, operator, strength=1, prefactor=1, coupling_entries=None, mask=None
    ):
        if len(operator) != 2:
            raise QTeaLeavesError(
                "The operator should be a list of length 2, i.e. provide L and Ldag in order."
            )

        super().__init__(
            operator=operator, strength=strength, prefactor=prefactor, mask=mask
        )

        self.coupling_entries = coupling_entries

    def get_entries(self, params):
        """
        Entries in the format that works for local term and
        two-body interaction.

        **Arguments**

        params : dictionary
            Contains the simulation parameters.
        """
        coupl_ii = {"coordinates": None, "operators": self.operator}

        yield coupl_ii

    def _get_check_mask_func(self, dim, params):
        """Build the function which returns True/False if site is active."""
        if self.mask is None:

            def check_mask(*args):
                return True

        else:
            local_mask = self.mask(params)
            if len(local_mask.shape) != dim:
                raise QTeaLeavesError("Mask dimension does not match system dimension.")

            def check_mask(*args, local_mask=local_mask):
                # We check masks for 1d, 2d, and 3d systems where mask matches
                # the original system dimensionality. Otherwise, error is raised.
                if len(args) == 1:
                    return local_mask[args[0]]
                if len(args) == 2:
                    return local_mask[args[0], args[1]]
                if len(args) == 3:
                    return local_mask[args[0], args[1], args[2]]

                raise QTeaLeavesError("Unknown length of *args.")

        return check_mask

    def _get_coupl_func(self, dim, params):
        """Build the function which returns coupling."""
        if self.coupling_entries is None:

            def get_coupl(*args):
                return 1.0

        else:
            ctens = self.eval_numeric_param(self.coupling_entries, params)

            def get_coupl(*args, dim=dim, ctens=ctens):
                if (len(args) == 1) and (dim == 1):
                    return ctens[args[0]]
                if (len(args) == 2) and (dim == 2):
                    return ctens[args[0], args[1]]
                if (len(args) == 3) and (dim == 3):
                    return ctens[args[0], args[1], args[2]]

                raise QTeaLeavesError("No match for dimension etc.")

        return get_coupl

    def _get_coupl_matrix(self, dim, params, ll, num_sites):
        """Build vector and matrix is with the couplings."""
        get_coupl = self._get_coupl_func(dim, params)
        vec = np.zeros([num_sites, 1], dtype=np.complex128)
        map_to_1d = map_selector(dim, ll, self.map_type)

        for ii in range(num_sites):
            ix = map_to_1d(ii)
            vec[ii] = get_coupl(*ix)

        return vec, np.tensordot(np.conj(vec), vec, ([1], [1]))

    def get_interactions(self, ll, params, **kwargs):
        """
        Iterate over all interaction. The iterator yields
        the operator and the strength of this term.
        Assuming that the operator is a list [L, Ldag],
        return L for the diagonal (local) case and [L, Ldag] for
        the interaction terms.
        """
        if "dim" not in kwargs:
            raise QTeaLeavesError("SumLocalLindblad term needs dim information")
        dim = kwargs["dim"]

        check_mask = self._get_check_mask_func(dim, params)
        get_coupl = self._get_coupl_func(dim, params)
        map_to_1d = map_selector(dim, ll, self.map_type)

        for elem in self.get_entries(params):
            for ix in self.iterate_sites(ll):
                if isinstance(ix, int):
                    ix = tuple([ix])

                if not check_mask(*ix):
                    continue

                ctens_i = get_coupl(*ix)

                # diagonal (local): return L operator
                elem_ii = deepcopy(elem)
                elem_ii["operators"] = [elem["operators"][0]]
                elem_ii["coordinates_nd"] = ix
                elem_ii["weight"] = ctens_i

                yield elem_ii, [map_to_1d[ix]]

                for jx in self.iterate_sites(ll):
                    if isinstance(jx, int):
                        jx = tuple([jx])

                    if ix == jx:
                        # skip diagonal
                        continue

                    if not check_mask(*jx):
                        continue

                    ctens_j = get_coupl(*jx)
                    elem["weight"] = np.conj(ctens_j) * ctens_i

                    # interaction: return L and Ldag
                    yield elem, [map_to_1d[ix], map_to_1d[jx]]

    def quantum_jump_weight(self, state, operators, quench, time, params, **kwargs):
        """
        Evaluate the unnormalized weight for a jump with this sum of
        Lindblad term. Correlation measurments are performed as a
        trick to compute the weight of the jump.

        **Arguments**

        state : :class:`_AbstractTN`
            Current quantum state where jump should be applied.

        operators : :class:`TNOperators`
            Operator dictionary of the simulation.

        quench : :class:`DynamicsQuench`
            Current quench to evaluate time-dependent couplings.

        time : float
            Time of the time evolution (accumulated dt)

        params :  dict
            Dictionary with parameters, e.g., to extract parameters which
            are not in quench or to build mask.

        kwargs : keyword arguments
            This term requires the following classes to be passed by
            keys of the same name: MPOSite, DenseMPO, DenseMPOList, ITPO
        """
        # pylint: disable-next=invalid-name
        MPOSite = kwargs["MPOSite"]
        # pylint: disable-next=invalid-name
        DenseMPO = kwargs["DenseMPO"]
        # pylint: disable-next=invalid-name
        DenseMPOList = kwargs["DenseMPOList"]
        # pylint: disable-next=invalid-name
        ITPO = kwargs["ITPO"]

        num_sites = state.num_sites
        _, cmat = self._get_coupl_matrix(
            kwargs["dim"], params, kwargs["lvals"], num_sites
        )

        if self.mask is None:
            # it is a 2d array because it should contain the information
            # for both sites i and j
            # (later it is multiplied with the correlation matrix)
            mask = np.ones((num_sites, num_sites), dtype=bool)
        else:
            mask = np.array(self.mask(params))
            mask = np.kron(mask.reshape(mask.shape[0], 1), mask)

        # one could gain some speed by adding using the mask on the iTPO
        # level, not after the iTPO
        mask = mask.astype(int).astype(np.float64)

        if self.strength in quench:
            strength = quench[self.strength](time)
        else:
            strength = self.eval_numeric_param(self.strength, params)

        total_scaling = strength * self.prefactor

        # Measure correlations
        # (trick to compute the weight for the jump, i.e.
        # <L Ldag>_{ij} = <psi_j| Ldag L |psi_i>)
        # --------------------
        key_a = self.operator[1]  # Ldag
        key_b = self.operator[0]  # L

        # raise exception if disentanglers present
        if hasattr(state, "de_layer"):
            raise QTeaLeavesError(
                "Correlation measurements for the weight currently "
                "not implemented if the state has disentanglers."
            )

        # 1) measure diagonal entries
        corr_diag = np.zeros(num_sites, dtype=np.complex128)

        op_ab_list = []
        for ii in range(num_sites):
            op_a = operators[(ii, key_a)]
            op_b = operators[(ii, key_b)]

            if op_a.ndim == 2:
                op_ab = op_a @ op_b
            else:
                # assume rank-4 (but delta charge both times to the right
                op_ab = op_a.tensordot(op_b, ([2], [1]))
                op_ab.flip_links_update([0, 2])
                op_ab.trace_one_dim_pair([0, 3])
                op_ab.trace_one_dim_pair([1, 3])

            op_ab_list.append(op_ab)

        for ii, elem in enumerate(state.meas_local(op_ab_list)):
            corr_diag[ii] = elem

        state.iso_towards(state.default_iso_pos, keep_singvals=True, trunc=True)

        hmpo = state.eff_op

        # 2) create itpo
        dense_mpo_list = DenseMPOList()
        for ii in range(num_sites):
            for jj in range(num_sites):
                if ii == jj:
                    continue

                site_a = MPOSite(ii, key_a, 1.0, 1.0, operators=operators, params={})
                site_b = MPOSite(jj, key_b, 1.0, 1.0, operators=operators, params={})

                dense_mpo = DenseMPO([site_a, site_b])
                dense_mpo_list.append(dense_mpo)

        # sites are not ordered and we have to make links match anyways
        dense_mpo_list = dense_mpo_list.sort_sites()

        itpo = ITPO(num_sites)
        itpo.add_dense_mpo_list(dense_mpo_list)

        itpo.set_meas_status(do_measurement=True)
        state.eff_op = None
        itpo.setup_as_eff_ops(state, measurement_mode=True)

        # 3) measure non-diagonal entries from itpo measurement
        dict_by_tpo_id = itpo.collect_measurements()
        idx = -1

        corr_mat = np.diag(corr_diag)

        for ii in range(num_sites):
            for jj in range(num_sites):
                if ii == jj:
                    continue
                idx += 1
                corr_mat[ii, jj] = dict_by_tpo_id[idx]

        state.eff_op = hmpo

        return np.sum(corr_mat * mask * cmat) * total_scaling

    def quantum_jump_apply(self, state, operators, params, rand_generator, **kwargs):
        """
        Apply jump with this sum of Lindblad. Contains inplace update of state.

        **Arguments**

        state : :class:`_AbstractTN`
            Current quantum state where jump should be applied.

        operators : :class:`TNOperators`
            Operator dictionary of the simulation.

        params :  dict
            Dictionary with parameters, e.g., to extract parameters which
            are not in quench or to build mask.

        rand_generator : random number generator
            Needs method `random()`, used to decide on jump within
            the sites.

        kwargs : keyword arguments
            This term requires the following classes to be passed by
            keys of the same name: MPOSite, DenseMPO
        """
        if operators[self.operator[0]].has_symmetry:
            # raise an error if the tensor is symmetric
            raise QTeaLeavesError("Symmetric Lindblad operator not supported.")

        # pylint: disable-next=invalid-name
        MPOSite = kwargs["MPOSite"]
        # pylint: disable-next=invalid-name
        DenseMPO = kwargs["DenseMPO"]

        num_sites = state.num_sites
        dtype = state.dtype
        device = state.device

        if self.mask is None:
            mask = np.ones(num_sites, dtype=bool)
        else:
            mask = self.mask(params)

        mask = mask.astype(int).astype(np.float64)
        cvec, _ = self._get_coupl_matrix(
            kwargs["dim"], params, kwargs["lvals"], num_sites
        )

        # append the index of the sites that are not masked
        # in a list
        not_masked_sites = []
        for ii in range(num_sites):
            # apply mask
            if not mask[ii]:
                continue
            not_masked_sites.append(ii)

        # build sum of lindblad operator in dense mpo
        # form for bulk, left and right
        # remind that sparse MPO matrix have the form
        #       ( 1 0 )     ( 1 0 ) ( 1 )
        # (L 1) ( L 1 ) ... ( L 1 ) ( L )
        # where 1 is the identity matrix, and L the Lindblad operator

        # create list of MPO sites
        mpo_list = []
        for idx, ii in enumerate(not_masked_sites):
            # copy of operator dictionary
            new_ops = deepcopy(operators)

            # get local dimension of site ii
            local_dim = state.local_dim[ii]

            if idx == 0:
                # left boundary

                # the identity is set inside the loop to enable
                # not equal hilbert space size
                # (the same applies in "right" and "bulk" cases)

                op_left = state.tensor_backend.tensor_cls(
                    [1, local_dim, local_dim, 2], ctrl="Z", dtype=dtype, device=device
                )
                op_left[:1, :local_dim, :local_dim, :1] = (
                    operators[self.operator[0]] * cvec[ii]
                )

                op_left[:1, :local_dim, :local_dim, 1:2] = operators[(ii, "id")]

                # pylint: disable-next=protected-access
                set_name, key_op = new_ops._parse_key((ii, str(id(op_left))))
                new_ops[(set_name, key_op)] = op_left

            elif idx == (len(not_masked_sites) - 1):
                # right boundary

                op_right = state.tensor_backend.tensor_cls(
                    [2, local_dim, local_dim, 1], ctrl="Z", dtype=dtype, device=device
                )
                op_right[1:2, :local_dim, :local_dim, :1] = (
                    operators[self.operator[0]] * cvec[ii]
                )

                op_right[:1, :local_dim, :local_dim, :1] = operators[(ii, "id")]

                # pylint: disable-next=protected-access
                set_name, key_op = new_ops._parse_key((ii, str(id(op_right))))
                new_ops[(set_name, key_op)] = op_right

            else:
                # bulk case
                op_bulk = state.tensor_backend.tensor_cls(
                    [2, local_dim, local_dim, 2], ctrl="Z", dtype=dtype, device=device
                )
                op_bulk[1:2, :local_dim, :local_dim, :1] = (
                    operators[self.operator[0]] * cvec[ii]
                )

                op_bulk[:1, :local_dim, :local_dim, :1] = operators[(ii, "id")]

                op_bulk[1:2, :local_dim, :local_dim, 1:2] = operators[(ii, "id")]

                # pylint: disable-next=protected-access
                set_name, key_op = new_ops._parse_key((ii, str(id(op_bulk))))
                new_ops[(set_name, key_op)] = op_bulk

            site = MPOSite(ii, key_op, 1.0, 1.0, operators=new_ops, params={})
            mpo_list.append(site)

        # build dense MPO
        dense_mpo = DenseMPO(mpo_list, is_oqs=self.is_oqs)

        # apply MPO to the state
        state.apply_mpo(dense_mpo)
        state.normalize()
