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
Two-body interactions in one-dimensional systems.
"""
import numpy as np

from qtealeaves.tooling import QTeaLeavesError

from .baseterm import _ModelTerm1D

__all__ = ["TwoBodyTerm1D", "TwoBodyAllToAllTerm1D"]


class TwoBodyTerm1D(_ModelTerm1D):
    """
    The term defines an interaction between two sites of the Hilbert space.
    For example, the tunneling term in the Bose-Hubbard model can be
    represented by this term. This class represents the 1d version.

    **Arguments**

    operators : list of two strings
        String identifier for the operators. Before launching the simulation,
        the python API will check that the operator is defined.

    shift : int
        Defines the distance of the interaction in compliance
        with the systems in higher dimensions. In the end,
        we iterate over all sites and apply interactions to
        sites (x,) and (x + shift,)

    strength : str, callable, numeric (optional)
        Defines the coupling strength of the local terms. It can
        be parameterized via a value in the dictionary for the
        simulation or a function.
        Default to 1.

    prefactor : numeric, scalar (optional)
        Scalar prefactor, e.g., in order to take into account signs etc.
        Default to 1.

    add_complex_conjg : bool, optional
        (BUG ticket #1) Aims to automatically add complex conjugated
        terms, e.g., for the tunneling term.

    has_obc : bool or list of bools, optional
        Defines the boundary condition along each spatial dimension.
        If scalar is given, the boundary condition along each
        spatial dimension is assumed to be equal.
        Default to True

    mask : callable or ``None``, optional
        The true-false-mask allows to apply the Hamiltonians terms
        only to specific sites, i.e., with true values. The function
        takes the dictionary with the simulation parameters as an
        argument. The mask is applied to the site where the left
        operator is acting on.
        Default to ``None`` (all sites have the interaction)

    """

    # pylint: disable-next=too-many-arguments
    def __init__(
        self,
        operators,
        shift,
        strength=1,
        prefactor=1,
        add_complex_conjg=False,
        has_obc=True,
        mask=None,
    ):
        super().__init__()

        self.operators = operators
        self.shift = shift
        self.strength = strength
        self.prefactor = prefactor
        self.add_complex_conjg = add_complex_conjg
        self.mask = mask

        if isinstance(has_obc, bool):
            self.has_obc = [has_obc]
        else:
            self.has_obc = has_obc

    def iter_shifts(self):
        """
        Return all possible shifts, which is in the case of the
        1d systems exactly the defined shift.
        """
        yield self.shift

    # pylint: disable-next=unused-argument
    def get_entries(self, params):
        """
        Entries based on two coordinates; one of them is the
        origin (0,).

        **Arguments**

        params : dictionary
            Contains the simulation parameters.

        **Details**

        To-Do: complex-conjugate terms are wrong, i.e., they work
        for sigma_{i}^{+} sigma_{j}^{-} or b_{i}^{dagger} b_{j}, but
        not for terms as b_{j} sigma_{i}^{x}!
        """
        for shift in self.iter_shifts():
            coord_a = 0
            coord_b = shift
            coordinates = [coord_a, coord_b]

            coupl_ii = {"coordinates": coordinates, "operators": self.operators}

            yield coupl_ii

            if self.add_complex_conjg:
                coupl_ii = {
                    "coordinates": coordinates,
                    "operators": self.operators[::-1],
                }

                yield coupl_ii

    def get_interactions(self, ll, params, **kwargs):
        """
        Iterate over all interaction. The iterator yields
        a dictionary with the operator keys and the generic
        shift based on the origin, and a list with the
        coordinates in the 1d system.
        """
        if self.mask is None:
            local_mask = np.ones(ll, dtype=bool)
        else:
            local_mask = self.mask(params)

        for elem in self.get_entries(params):
            for ix in self.iterate_sites(ll):
                coord_a, coord_b = elem["coordinates"]

                if np.sum(np.abs(np.array(coord_a))) != 0:
                    raise QTeaLeavesError("Coordinate A is not the origin.")

                jx = ix + coord_b

                if (jx >= ll[0]) and self.has_obc[0]:
                    continue

                if (jx < 0) and self.has_obc[0]:
                    continue

                if jx >= ll[0]:
                    jx = jx % ll[0]
                if jx < 0:
                    jx += ll[0]

                if (jx >= ll[0]) or (jx < 0):
                    raise QTeaLeavesError("Improve handling.")

                if ix == jx:
                    raise QTeaLeavesError("Same site ...")

                if not local_mask[ix]:
                    continue

                # Still in python indices
                coords_1d = [ix, jx]

                yield elem, coords_1d

    def get_fortran_str(self, ll, params, operator_map, param_map):
        """
        See :func:`_ModelTerm.get_fortran_str_two_body`.
        """
        return self.get_fortran_str_twobody(ll, params, operator_map, param_map)

    # pylint: disable-next=too-many-locals, too-many-arguments
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
        if self.shift != 1:
            raise NotImplementedError(
                "Only nearest neighbor implemented for sparse MPO."
            )

        sp_mat_ops = []
        for ii in range(np.prod(ll)):
            sp_mat_ops.append(sp_ops_cls(ii == 0, ii + 1 == np.prod(ll), True))

        op_id_0 = operator_map[(self.operators[0], "l")]
        op_id_1 = operator_map[(self.operators[1], "r")]

        param_repr = self.get_param_repr(param_map)

        for _, inds in self.get_interactions(ll, params, **kwargs):
            if abs(inds[0] - inds[1]) == np.prod(ll) - 1:
                raise QTeaLeavesError(
                    "Periodic boundary conditions not implemented for spMat."
                )

            if inds[0] == 0:
                shape_l = (1, 3)
            else:
                shape_l = (2, 3)

            if inds[1] + 1 == np.prod(ll):
                shape_r = (3, 1)
            else:
                shape_r = (3, 2)

            sp_mat_l = np.zeros(shape_l, dtype=int)
            sp_mat_r = np.zeros(shape_r, dtype=int)

            prefactor_l = np.zeros(shape_l, dtype=np.complex128)
            prefactor_r = np.zeros(shape_r, dtype=np.complex128)

            params_l = np.zeros(shape_l, dtype=int)
            params_r = np.zeros(shape_r, dtype=int)

            sp_mat_l[-1, 1] = op_id_0
            prefactor_l[-1, 1] = self.prefactor
            params_l[-1, 1] = param_repr

            sp_mat_r[1, 0] = op_id_1
            prefactor_r[1, 0] = 1.0
            params_r[1, 0] = -1

            sp_mat_ops[inds[0]].add_term(sp_mat_l, params_l, prefactor_l)
            sp_mat_ops[inds[1]].add_term(sp_mat_r, params_r, prefactor_r)

        return sp_mat_ops


class TwoBodyAllToAllTerm1D(TwoBodyTerm1D):
    """
    Random all-to-all two-body interaction for a one-dimensional system,
    e.g., as in spin glasses.

    **Arguments**

    operators : list of two strings
        String identifier for the operators. Before launching the simulation,
        the python API will check that the operator is defined.

    coupling_matrix : numpy ndarray of rank-2
        The coupling between the different sites in the all-to-all
        interactions. These values can only be set once and cannot
        be time-dependent in a time-evolution.

    strength : str, callable, numeric (optional)
        Defines the coupling strength of the local terms. It can
        be parameterized via a value in the dictionary for the
        simulation or a function.
        Default to 1.

    prefactor : numeric, scalar (optional)
        Scalar prefactor, e.g., in order to take into account signs etc.
        Default to 1.

    **Details**

    The term adds the following terms:
    ``sum_{i} sum_{j>i} strength * prefactor * coupling_mat[i, j] * A_i * B_j``
    and only the upper triangular matrix of the coupling_mat is accessed.
    The hermiticity of the Hamiltonian is not ensured. Terms of the form
    ``B_j A_i`` with ``j < i`` are also not added.
    """

    add_complex_conjg = False

    def __init__(self, operators, coupling_matrix, strength=1, prefactor=1):
        super().__init__(
            operators=operators, shift=None, strength=strength, prefactor=prefactor
        )
        self.coupling_matrix = coupling_matrix

    def get_interactions(self, ll, params, **kwargs):
        cmat = self.eval_numeric_param(self.coupling_matrix, params)

        for ii in range(ll[0]):
            for jj in range(ii + 1, ll[0]):
                if abs(cmat[ii, jj]) == 0.0:
                    # Coupling will always be zero
                    continue

                coords_1d = [ii, jj]

                yield {"operators": self.operators, "weight": cmat[ii, jj]}, coords_1d

    def get_fortran_str(self, ll, params, operator_map, param_map):
        """
        Get the string representation needed to write
        for Fortran. This method works for any two-body interaction.

        **Arguments**

        ll : int
            Number of sites along one dimension in the system, e.g.,
            number of sites for one side of the square in a 2d system.

        params : dictionary
            Contains the simulation parameters.

        operator_map : OrderedDict
            For operator string as dictionary keys, it returns the
            corresponding integer IDs.

        param_map : dict
            This dictionary contains the mapping from the parameters
            to integer identifiers.

        **Details**

        We cannot use the function :func:`_ModelTerm.get_fortran_str_two_body`
        as we have to modify the prefactor.
        """
        str_repr = ""
        param_repr = self.get_param_repr(param_map)

        cmat = self.eval_numeric_param(self.coupling_matrix, params)
        if isinstance(cmat, np.ndarray):
            if len(cmat.shape) != 2:
                raise QTeaLeavesError("Coupling must be a matrix.")
        else:
            raise QTeaLeavesError("Unknown type for coupling.")

        str_repr = ""
        counter = 0
        for elem in self.get_interactions(ll, params):
            if elem[1][0] == elem[1][1]:
                raise QTeaLeavesError("Same site ...")

            ii = elem[1][0]
            jj = elem[1][1]

            # Increment counter for non-zero term (get_interactions
            # takes care of that)
            counter += 1

            # Ensure order is increasing (if ever enabled in get_interactions)
            if ii < jj:
                op_id_str_0 = operator_map[(self.operators[0], "l")]
                op_id_str_1 = operator_map[(self.operators[1], "r")]

                # Convert from python index to fortran index by
                # adding offset 1
                str_repr += "%d %d\n" % (ii + 1, op_id_str_0)
                str_repr += "%d %d\n" % (jj + 1, op_id_str_1)
            else:
                op_id_str_0 = operator_map[(self.operators[0], "r")]
                op_id_str_1 = operator_map[(self.operators[1], "l")]

                # Convert from python index to fortran index by
                # adding offset 1
                str_repr += "%d %d\n" % (jj + 1, op_id_str_1)
                str_repr += "%d %d\n" % (ii + 1, op_id_str_0)

            prefactor = self.prefactor * cmat[ii, jj]
            str_repr += param_repr + " %30.15E\n" % (prefactor)

        # Insert at the beginning: number of terms and number
        # of operators (later always 2)
        str_repr = "%d\n%d\n" % (counter, 2) + str_repr

        return str_repr
