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
Local terms in a Hamiltonian or Lindblad equation.
"""

# pylint: disable-msg=too-many-instance-attributes, too-many-arguments

from copy import deepcopy
from warnings import warn

import numpy as np
from scipy.linalg import expm

from qtealeaves.tooling.mapping import QTeaLeavesError, map_selector

from .baseterm import _ModelTerm

__all__ = ["LocalTerm", "LindbladTerm", "RandomizedLocalTerm", "LocalKrausTerm"]


class LocalTerm(_ModelTerm):
    """
    Local Hamiltonian terms are versatile and probably part of any model
    which will be implemented. For example, the external field in the
    quantum Ising model can be represented as a local term.

    **Arguments**

    operator : str
        String identifier for the operator. Before launching the simulation,
        the python API will check that the operator is defined.

    strength : str, callable, numeric (optional)
        Defines the coupling strength of the local terms. It can
        be parameterized via a value in the dictionary for the
        simulation or a function.
        Default to 1.

    prefactor : numeric, scalar (optional)
        Scalar prefactor, e.g., in order to take into account signs etc.
        Default to 1.

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

    def __init__(self, operator, strength=1, prefactor=1, mask=None):
        super().__init__()

        self.operator = operator
        self.strength = strength
        self.prefactor = prefactor
        self.mask = mask

        # Will be set when adding Hamiltonian terms
        self.map_type = None

    def count(self, params):
        """
        Defines length as number of terms in fortran input file,
        which by now depends the presence of a mask.

        **Arguments**

        params : dictionary
            Contains the simulation parameters.
        """
        if self.mask is None:
            return 1

        return np.sum(self.mask(params))

    def get_entries(self, params):
        """
        Return the operator and the strength of this term.

        **Arguments**

        params : dictionary
            Contains the simulation parameters.
        """
        strength = self.eval_strength(params)

        return self.operator, strength

    def collect_operators(self):
        """
        The required operators must be provided through this
        method; thus, we return the operator in the local term.
        """
        yield self.operator, None

    def get_fortran_str(self, ll, params, operator_map, param_map, dim):
        """
        Get the string representation needed to write the
        local terms as an plocal_type for Fortran.

        **Arguments**

        ll : int
            Number of sites along the dimensions, i.e., not the
            total number of sites. Assuming list of sites
            along all dimension.

        params : dictionary
            Contains the simulation parameters.

        operator_map : OrderedDict
            For operator string as dictionary keys, it returns the
            corresponding integer IDs.

        param_map : dict
            This dictionary contains the mapping from the parameters
            to integer identifiers.

        dim : int
            Dimensionality of the problem, e.g., a 2d system.
        """
        str_repr = ""
        op_id_str = str(operator_map[(self.operator, None)])

        has_spatial_dependency = False
        param_repr = self.get_param_repr(param_map)

        if self.mask is not None:
            for _, idx in self.get_interactions(ll, params, dim=dim):
                # Convert from python index to fortran index by
                # adding offset 1
                str_repr += "%d\n" % (idx[0] + 1)
                str_repr += op_id_str + "\n"
                str_repr += param_repr
                str_repr += "%30.15E\n" % (self.prefactor)

        elif has_spatial_dependency:
            # Write for each site
            raise NotImplementedError("To-do ...")
        else:
            str_repr += "-1\n"
            str_repr += op_id_str + "\n"
            str_repr += param_repr
            str_repr += "%30.15E\n" % (self.prefactor)

        return str_repr

    # pylint: disable-next=too-many-branches
    def get_interactions(self, ll, params, **kwargs):
        """
        Iterator returning the local terms one-by-one, e.g., to build
        a Hamiltonian matrix. (In that sense, the "interaction" is
        obviously misleading here.)

        **Arguments**

        ll : int
            Number of sites along the dimension, i.e., not the
            total number of sites. Assuming list of sites
            along all dimension.

        params : dictionary
            Contains the simulation parameters.

        dim : int (as keyword argument!)
            Dimensionality of the problem, e.g., a 2d system.
        """
        if "dim" not in kwargs:
            raise QTeaLeavesError("Local terms needs dim information")
        dim = kwargs["dim"]

        elem = {"coordinates": None, "operators": [self.operator]}

        if self.mask is None:

            def check_mask(*args):
                return True

        else:
            local_mask = self.mask(params)
            if len(local_mask.shape) != dim:
                raise QTeaLeavesError("Mask dimension does not match system dimension.")

            def check_mask(*args, local_mask=local_mask):
                if len(args) == 1:
                    return local_mask[args[0]]
                if len(args) == 2:
                    return local_mask[args[0], args[1]]
                if len(args) == 3:
                    return local_mask[args[0], args[1], args[2]]

                raise QTeaLeavesError("Unknown length of *args.")

        if dim not in [1, 2, 3]:
            raise QTeaLeavesError(f"Dimension unknown: {dim}.")

        if dim == 1:
            for ii in range(ll[0]):
                if not check_mask(ii):
                    continue

                elem_ii = deepcopy(elem)
                elem_ii["coordinates_nd"] = (ii,)

                yield elem_ii, [ii]

            return

        map_to_1d = map_selector(dim, ll, self.map_type)
        if dim == 2:
            idx = 0
            for ii in range(ll[0]):
                for jj in range(ll[1]):
                    idx += 1

                    if not check_mask(ii, jj):
                        continue

                    elem_ii = deepcopy(elem)
                    elem_ii["coordinates_nd"] = (ii, jj)

                    yield elem_ii, [map_to_1d[(ii, jj)]]
        elif dim == 3:
            idx = 0
            for ii in range(ll[0]):
                for jj in range(ll[1]):
                    for kk in range(ll[2]):
                        idx += 1

                        if not check_mask(ii, jj, kk):
                            continue

                        elem_ii = deepcopy(elem)
                        elem_ii["coordinates_nd"] = (ii, jj, kk)

                        yield elem_ii, [map_to_1d[(ii, jj, kk)]]

        return

    def get_sparse_matrix_operators(
        self, ll, params, operator_map, param_map, sp_ops_cls, **kwargs
    ):
        """
        Construct the sparse matrix operator for this term.

        **Arguments**

        ll : int
            System size.

        params : dictionary
            Contains the simulation parameters.

        operator_map : OrderedDict
            For operator string as dictionary keys, it returns the
            corresponding integer IDs.

        param_map : dict
            This dictionary contains the mapping from the parameters
            to integer identifiers.

        sp_ops_cls : callable (e.g., constructor)
            Constructor for the sparse MPO operator to be built
            Has input bool (is_first_site), bool (is_last_site),
            bool (do_vectors).

        kwargs : keyword arguments
            Keyword arguments are passed to `get_interactions`
        """
        op_id = operator_map[(self.operator, None)]
        param_id = self.get_param_repr(param_map)

        sp_mat_ops = []
        for ii in range(np.prod(ll)):
            sp_mat_ops.append(sp_ops_cls(ii == 0, ii + 1 == np.prod(ll), True))

        for _, inds in self.get_interactions(ll, params, **kwargs):
            sp_mat_ops[inds[0]].add_local(op_id, param_id, self.prefactor, self.is_oqs)

        return sp_mat_ops


class LindbladTerm(LocalTerm):
    """
    Local Lindblad operators acting at one site are defined via this
    term. For the arguments see See :class:`LocalTerm.check_dim`.

    **Details**

    The Lindblad equation is implemented as

    .. math::

        \\frac{d}{dt} \\rho = -i [H, \\rho]
           + \\sum \\gamma (L \\rho L^{\\dagger}
           - \\frac{1}{2} \\{ L^{\\dagger} L, \\rho \\})

    """

    @property
    def is_oqs(self):
        """Status flag if term belongs to Hamiltonian or is Lindblad."""
        return True

    def quantum_jump_weight(self, state, operators, quench, time, params, **kwargs):
        """
        Evaluate the unnormalized weight for a jump with this Lindblad term.

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
            No keyword arguments are parsed for this term.
        """
        if self.mask is None:
            mask = np.ones(state.num_sites, dtype=bool)
        else:
            mask = self.mask(params)

        mask = mask.astype(int).astype(np.float64)

        if self.strength in quench:
            strength = quench[self.strength](time, params)
        else:
            strength = self.eval_numeric_param(self.strength, params)

        total_scaling = strength * self.prefactor

        operator_list = []
        for ii in range(state.num_sites):
            lindblad = operators[(ii, self.operator)]
            operator = lindblad.conj().tensordot(lindblad, ([0, 1, 3], [0, 1, 3]))
            operator_list.append(operator)

        meas_vec = state.meas_local(operator_list)

        return np.sum(meas_vec * mask) * total_scaling

    def quantum_jump_apply(self, state, operators, params, rand_generator, **kwargs):
        """
        Apply jump with this Lindblad. Contains inplace update of state.

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
            No keyword arguments are parsed for this term.
        """
        if self.mask is None:
            mask = np.ones(state.num_sites, dtype=bool)
        else:
            mask = self.mask(params)

        mask = mask.astype(int).astype(np.float64)

        operator_list = []
        for ii in range(state.num_sites):
            lindblad = operators[(ii, self.operator)].copy()
            operator = lindblad.conj().tensordot(lindblad, ([0, 1, 3], [0, 1, 3]))
            operator_list.append(operator)

        meas_vec = state.meas_local(operator_list)

        meas_vec = meas_vec * mask
        meas_vec = np.cumsum(meas_vec)
        meas_vec /= meas_vec[-1]

        rand = rand_generator.random()

        idx = meas_vec.shape[0] - 1
        for ii in range(idx):
            if rand < meas_vec[ii]:
                idx = ii
                break

        if lindblad.ndim not in [2, 4]:
            raise QTeaLeavesError("Operator neither rank-2 nor rank-4.")

        if lindblad.ndim == 4:
            # See if we can reduce rank-4 to rank-3 by removing dummy links
            if lindblad.is_identical_irrep(0) and lindblad.is_identical_irrep(3):
                lindblad = lindblad.remove_dummy_link(3).remove_dummy_link(0)

        if lindblad.ndim == 2:
            state.site_canonize(idx)
            state.apply_one_site_operator(lindblad, idx)
            state.normalize()
            return

        # Remaining with rank-4, but not both identical irreps
        if not lindblad.is_identical_irrep(0):
            # Enforce convention that left link is identical irrep carrying no charge
            raise QTeaLeavesError(
                "By convention, left horizontal link must be identical irrep."
            )

        if lindblad.shape[3] != 1:
            # Need to stay in a pure state, thus enforce dimension one on Kraus link
            raise QTeaLeavesError("By convention, Lindblad cannot introduce mixedness.")

        lindblad = lindblad.remove_dummy_link(0)
        state.site_canonize(idx)
        state.apply_one_site_operator_weak_symmetry(lindblad, idx)
        state.normalize()


class LocalKrausTerm(LindbladTerm):
    """
    Local Kraus operators acting at one site are defined via this
    term.
    The term is mapped at **first order** to a Linblad term for performing
    the jump.

    The close-to-identity Kraus operator MUST BE THE FIRST OPERATOR.
    If that is not the case, an error will be raised at the first jump.

    Notice that for numerical stability the `delta_t` used to define
    the Kraus operator should be of the same order of the timestep
    in the time evolution. This might lead to numerical instabilities.

    **Arguments**

    kraus_operators : List[str]
        String identifier for the Kraus operators.
        Before launching the simulation,
        the python API will check that the operator is defined.

    delta_t : float
        The time discretization used in the Kraus definition. It is needed
        to translate Kraus operators in Linbland operators.

    strength : List[str], List[callable], List[numeric] (optional)
        Defines the coupling strength of the local terms. It can
        be parameterized via a value in the dictionary for the
        simulation or a function.
        Default to 1.

    prefactor : numeric, scalar (optional)
        Scalar prefactor, e.g., in order to take into account signs etc.
        Default to 1.

    mask : callable or ``None``, optional
        The true-false-mask allows to apply the local Hamiltonians
        only to specific sites, i.e., with true values. The function
        takes the dictionary with the simulation parameters as an
        argument.
        Default to ``None`` (all sites have a local term)

    mode : str, optional
        How the LocalKrausTerm should be handled, if by mapping it to
        a linbland (`"L"`) or using it as Kraus (`"K"`). Default to `"L"`.

    **Details**

    The mapping between Kraus :math:`M_k` and linbland :math:`L_k` is:

    .. math::

        L_k = M_{k>0}/\\sqrt{\\Delta t}


    """

    def __init__(
        self, kraus_operators, delta_t, strength=None, prefactor=1, mask=None, mode="L"
    ):
        warn(
            "KrausTerm are unstable with small enough timestep. Please directly use Lindbland"
            "when possible."
        )
        if strength is None:
            strength = [1] * len(kraus_operators)

        # NOTICE: the mapping between Kraus and linbland at first order is done HERE through
        # the prefactor!! Since it is just a rescaling it is the best thing we can do
        super().__init__(
            kraus_operators[1],
            strength=strength[1],
            prefactor=prefactor,
            mask=mask,
        )

        self.prefactor = prefactor / delta_t
        self.kraus_operators = kraus_operators
        self.kraus_strengths = strength
        self.mode = mode.upper()
        self.evol_op = None

        # Set the helper attribute to None to be sure nothing goes wrong
        self.strength = None
        self.operator = None

        # Flag for initialization. Only run once.
        self.is_initialized = False

    def get_kraus_tensor(self, operators, params):
        """
        Get the Kraus tensor. Used in density matrix evolution algorithms (LPTN, TTO)

        **Arguments**

        operators : TNOperators
            The operators class for the simulation
        params : dict
            The parameters of the simulation

        **Returns**

        QteaTensor
            The rank-3 tensor representing the Kraus operators. The last axis is the
            channel axis
        """
        strength = self.eval_numeric_param(self.kraus_strengths[0], params)
        kraus = strength * operators[self.kraus_operators[0]].copy()
        # Remove the dummy indexes due to the MPO formalism here
        if kraus.shape[0] == 1:
            kraus = kraus.remove_dummy_link(0)
        if kraus.shape[-1] == 1:
            kraus = kraus.remove_dummy_link(kraus.ndim - 1)

        kraus_tensor = kraus.reshape([*kraus.shape, 1])

        for idx, kraus in enumerate(self.kraus_operators[1:]):
            strength = self.eval_numeric_param(self.kraus_strengths[idx + 1], params)
            kraus = strength * operators[kraus]
            if kraus.shape[0] == 1:
                kraus = kraus.remove_dummy_link(0)
            if kraus.shape[-1] == 1:
                kraus = kraus.remove_dummy_link(kraus.ndim - 1)
            kraus_tensor = kraus_tensor.stack_link(kraus.reshape([*kraus.shape, 1]), -1)

        return kraus_tensor

    def get_evol_op(self, operators, params):
        """
        Return the non-unitary evolution operator from the Kraus operators for a single
        timestep. For further information see
        https://ocw.mit.edu/courses/
        22-51-quantum-theory-of-radiation-interactions-fall-2012
        /b24652d7f4f647f05174797b957bd3bf_MIT22_51F12_Ch8.pdf, pages 69-70.

        **Details**

        The :math:`\\sqrt{\\Delta t}` is assumed to be constant and the one we used
        to define the Kraus operators to begin with.
        Here we do not divide by :math:`\\sqrt{\\Delta t}` because we would later
        on multiply the operator by :math:`\\Delta t` when we take the `expm`.
        Thus, we avoid the multiplication completely.
        """
        if self.evol_op is None:
            evol_op = operators[self.kraus_operators[0]].zeros_like()
            # We skip the first because it is the identity-like operator
            for idx, operator in enumerate(self.kraus_operators[1:]):
                strength = self.eval_numeric_param(
                    self.kraus_strengths[idx + 1], params
                )
                kraus = operators[operator] * strength
                evol_op += kraus.conj().tensordot(kraus, ([1], [0]))

            self.evol_op = evol_op.from_elem_array(expm(evol_op.elem))

        return self.evol_op

    def get_interactions(self, ll, params, **kwargs):
        """
        The `get_interactions` is a wrapper around the different
        Kraus (linbland) operators we have here
        """
        # Kraus mode should not go to the Hamiltonian
        if self.mode == "K":
            return

        # We skip the first because it is the identity-like operator
        for idx, operator in enumerate(self.kraus_operators[1:]):
            self.operator = operator
            self.strength = self.kraus_strengths[idx + 1]
            yield from super().get_interactions(ll, params, **kwargs)

        self.operator = None
        self.strength = None

    def get_strengths(self):
        """Return the strengths of the Kraus operators as an iterator"""
        yield from self.kraus_strengths

    def quantum_jump_weight(self, state, operators, quench, time, params, **kwargs):
        """
        The `quantum_jump_weight` is a wrapper around the different
        Kraus (linbland) operators we have here.
        See `LindbladTerm.quantum_jump_weight` for the description of the parameters.
        """
        # Kraus mode should not be used for quantum jumps (i.e. 0-prob jump)
        if self.mode == "K":
            return 0

        # Check that everything is ok in the operator ordering. Actually carried
        # out only in the first pass
        self._assert_first_identity(operators, params)
        weights = 0
        # We skip the first because it is the identity-like operator
        for idx, operator in enumerate(self.kraus_operators[1:]):
            self.operator = operator
            self.strength = self.kraus_strengths[idx + 1]
            weights += super().quantum_jump_weight(
                state, operators, quench, time, params, **kwargs
            )
        self.operator = None
        self.strength = None
        return weights

    def quantum_jump_apply(self, state, operators, params, rand_generator, **kwargs):
        """
        The `quantum_jump_apply` is a wrapper to select the correct Kraus (linbland) operator
        that caused a jump.
        We use the Kraus and not the linbland since they are the same up to a constant, which
        will be lost after renormalization.
        See `LindbladTerm.quantum_jump_apply` for the description of the parameters.
        """
        # Select which of the kraus operators jumped
        weights = []
        # We skip the first because it is the identity-like operator
        for idx, operator in enumerate(self.kraus_operators[1:]):
            self.operator = operator
            self.strength = self.kraus_strengths[idx + 1]
            weights.append(
                super().quantum_jump_weight(state, operators, params=params, **kwargs)
            )
        weights = np.cumsum(np.array(weights))
        weights /= weights[-1]
        # throw a random number to decide which term in the
        # list of lindblad terms will jump
        rand = rand_generator.random()
        idx = weights.shape[0] - 1
        for ii in range(idx):
            if rand < weights[ii]:
                idx = ii
                break

        # The +1 is due to the first operator being the close-to-identity
        self.operator = self.kraus_operators[idx + 1]
        self.strength = self.kraus_strengths[idx + 1]
        super().quantum_jump_apply(state, operators, params, rand_generator, **kwargs)
        self.operator = None
        self.strength = None

    def _assert_first_identity(self, operators, params):
        """
        Assert that the first operator in the Kraus operators list is the one close to the identity.

        **Arguments**

        operators : TNOperators
            The operators class for the simulation
        params : dict
            The parameters of the simulation
        """
        # If the check was passed already, don't do it anymore
        if self.is_initialized:
            return

        for idx, operator in enumerate(self.kraus_operators):
            strength = self.eval_numeric_param(self.kraus_strengths[idx], params)
            kraus = strength * operators[operator].copy()

            # Remove the dummy indexes due to the MPO formalism here
            if kraus.shape[0] == 1:
                kraus = kraus.remove_dummy_link(0)
            if kraus.shape[-1] == 1:
                kraus = kraus.remove_dummy_link(kraus.ndim - 1)

            identity = -1 * kraus.eye_like(kraus.shape[0])
            # A bit dangerous here: I suppose the elem has both the abs and sum
            # interfaces defined.
            diff = abs((kraus + identity).elem).sum()
            if idx == 0:
                diff0 = diff
            else:
                if diff < diff0:
                    raise ValueError(
                        (
                            f"The first operator {self.kraus_operators[0]} of the KrausTerm is"
                            f" not the closet to the identity. Operator {kraus} at index {idx} is."
                        )
                    )

        self.is_initialized = True


class RandomizedLocalTerm(LocalTerm):
    """
    Randomized local Hamiltonian terms are useful to model spinglass systems
    where the coupling of the local term is different for each site.

    **Arguments**

    operator : string
        String identifier for the operators. Before launching the simulation,
        the python API will check that the operator is defined.

    coupling_entries : numpy ndarray of rank-1,2,3
        The coupling for the different sites.
        These values can only be set once and cannot
        be time-dependent in a time-evolution. The rank depends
        on the usage in 1d, 2d, or 3d systems.

    strength : str, callable, numeric (optional)
        Defines the coupling strength of the local terms. It can
        be parameterized via a value in the dictionary for the
        simulation or a function.
        Default to 1.

    prefactor : numeric, scalar (optional)
        Scalar prefactor, e.g., in order to take into account signs etc.
        Default to 1.
    """

    mask = None

    def __init__(self, operator, coupling_entries, strength=1, prefactor=1):
        super().__init__(operator=operator, strength=strength, prefactor=prefactor)
        self.coupling_entries = coupling_entries

    def count(self, params):
        """
        Defines length as number of terms in fortran input file,
        which by now depends the presence of the coupling entries.

        **Arguments**

        params : dictionary
            Contains the simulation parameters.
        """
        ctens = self.eval_numeric_param(self.coupling_entries, params)
        return np.sum(np.abs(ctens) != 0)

    def get_interactions(self, ll, params, **kwargs):
        """
        See :class:`LocalTerm`
        """
        ctens = self.eval_numeric_param(self.coupling_entries, params)

        for elem, coords_1d in super().get_interactions(ll, params, **kwargs):
            elem["weight"] = ctens[elem["coordinates_nd"]]

            if elem["weight"] == 0.0:
                continue

            yield elem, coords_1d

    def get_fortran_str(self, ll, params, operator_map, param_map, dim):
        """
        Get the string representation needed to write the
        local terms as an plocal_type for Fortran.

        **Arguments**

        ll : int
            Number of sites along one dimension, i.e., not the
            total number of sites. Assuming equal number of sites
            along all dimension.

        params : dictionary
            Contains the simulation parameters.

        operator_map : OrderedDict
            For operator string as dictionary keys, it returns the
            corresponding integer IDs.

        param_map : dict
            This dictionary contains the mapping from the parameters
            to integer identifiers.

        dim : int
            Dimensionality of the problem, e.g., a 2d system.
        """
        str_repr = ""
        op_id_str = str(operator_map[(self.operator, None)])

        param_repr = self.get_param_repr(param_map)

        ctens = self.eval_numeric_param(self.coupling_entries, params)
        if isinstance(ctens, np.ndarray):
            if len(ctens.shape) != dim:
                raise QTeaLeavesError(
                    "Coupling %d and " % (len(ctens.shape))
                    + "dimensionality %d do not match." % (dim)
                )
        else:
            raise QTeaLeavesError("Unknown type for coupling.")

        for meta_info, idx in self.get_interactions(ll, params, dim=dim):
            if abs(ctens[meta_info["coordinates_nd"]]) == 0.0:
                # Skip entries with 0 coupling from randomization
                continue

            # Convert from python index to fortran index by
            # adding offset 1
            str_repr += "%d\n" % (idx[0] + 1)
            str_repr += op_id_str + "\n"
            str_repr += param_repr
            prefactor = self.prefactor * ctens[meta_info["coordinates_nd"]]
            str_repr += "%30.15E\n" % (prefactor)

        return str_repr
