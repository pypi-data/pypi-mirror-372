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
Two-body interactions in a two-dimensional system.
"""
import numpy as np

from qtealeaves.tooling import QTeaLeavesError
from qtealeaves.tooling.mapping import map_selector

from .baseterm import _ModelTerm

__all__ = ["TwoBodyTerm2D", "TwoBodyTerm2DLatticeLayout"]


# pylint: disable-next=too-many-instance-attributes
class TwoBodyTerm2D(_ModelTerm):
    """
    The term defines an interaction between two sites of the Hilbert space.
    For example, the tunneling term in the Bose-Hubbard model can be
    represented by this term. This class represents the 2d version.

    **Arguments**

    operators : list of two strings
        String identifier for the operators. Before launching the simulation,
        the python API will check that the operator is defined.

    shift : list of two ints
        Defines the distance of the interaction. In the end,
        we iterate over all sites and apply interactions to
        sites (x, y) and (x + shift[0], y + shift[1])

    strength : str, callable, numeric (optional)
        Defines the coupling strength of the local terms. It can
        be parameterized via a value in the dictionary for the
        simulation or a function.
        Default to 1.

    prefactor : numeric, scalar (optional)
        Scalar prefactor, e.g., in order to take into account signs etc.
        Default to 1.

    isotropy_xyz : bool, optional
        If False, the defined shift will only be applied as is. If true,
        we permute the defined shift to cover all spatial directions.
        Default to True.

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

    **Attributes**

    map_type : str, optional
        Selecting the mapping from a n-dimensional system to the
        1d system required for the TTN simulations.
    """

    # pylint: disable-next=too-many-arguments
    def __init__(
        self,
        operators,
        shift,
        strength=1,
        prefactor=1,
        isotropy_xyz=True,
        add_complex_conjg=False,
        has_obc=True,
        mask=None,
    ):
        super().__init__()

        self.operators = operators
        self.shift = shift
        self.strength = strength
        self.prefactor = prefactor
        self.isotropy_xyz = isotropy_xyz
        self.add_complex_conjg = add_complex_conjg
        self.mask = mask

        # Will be set when adding Hamiltonian terms
        self.map_type = None

        if isinstance(has_obc, bool):
            self.has_obc = [has_obc] * 2
        else:
            self.has_obc = has_obc

    @staticmethod
    def check_dim(dim):
        """
        See :func:`_ModelTerm.check_dim`
        """
        if dim != 2:
            raise QTeaLeavesError("Dimension does not match.")

    def collect_operators(self):
        """
        All the required operators are returned to ensure that they are
        written by fortran.
        """
        yield self.operators[0], "l"
        yield self.operators[1], "r"

        # Hilbert curvature could swap order of sites
        yield self.operators[0], "r"
        yield self.operators[1], "l"

    def iter_shifts(self):
        """
        Return all possible shifts, which depends on the isotropy
        in the 2d case.
        """
        if self.isotropy_xyz:
            n_coord = np.sum(np.abs(np.array(self.shift)) > 0)
            if n_coord == 0:
                raise QTeaLeavesError("Not implemented. Is this case useful?")
            if n_coord == 1:
                shifts = [
                    [self.shift[0], self.shift[1]],
                    [self.shift[1], self.shift[0]],
                ]
            elif n_coord == 2:
                shifts = [
                    [self.shift[0], self.shift[1]],
                    [self.shift[0], -self.shift[1]],
                ]

                # This takes into account unequal shifts leading
                # to four terms, e.g, (1, 2), (1, -2), (2, 1),
                # and (2, -1)
                if self.shift[0] != self.shift[1]:
                    shifts.append([self.shift[1], self.shift[0]])
                    shifts.append([self.shift[1], -self.shift[0]])
        else:
            shifts = [self.shift]

        yield from shifts

    # pylint: disable-next=unused-argument
    def get_entries(self, params):
        """
        Entries combine the information about possible shifts based
        on the origin coordination (0, 0) and the shift with the
        information about the operators and couplings.

        **Arguments**

        params : dictionary
            Contains the simulation parameters.

        **Details**

        To-Do: adding complex conjugates for general case beyond
        b bdagger case.
        """
        for shift in self.iter_shifts():
            coord_a = [0, 0]
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

    # pylint: disable-next=too-many-branches
    def get_interactions(self, ll, params, **kwargs):
        """
        These interactions are closest to the TPO description iterating
        over specific sites within the 1d coordinates.

        **Arguments**

        ll : list of ints
            Number of sites along the dimensions, i.e., not the
            total number of sites. Assuming list of sites
            along all dimension.

        params : dictionary
            Contains the simulation parameters.
        """
        if isinstance(self.map_type, str):
            map_type = self.eval_str_param(self.map_type, params)
        else:
            map_type = self.map_type
        map_to_1d = map_selector(2, ll, map_type)

        if self.mask is None:
            local_mask = np.ones(ll, dtype=bool)
        else:
            local_mask = self.mask(params)

        for elem in self.get_entries(params):
            for ix, iy in self.iterate_sites(ll):
                coord_a, coord_b = elem["coordinates"]

                if np.sum(np.abs(np.array(coord_a))) != 0:
                    raise QTeaLeavesError("Coordinate A is not the origin.")

                jx = ix + coord_b[0]
                jy = iy + coord_b[1]

                if (jx >= ll[0]) and self.has_obc[0]:
                    continue
                if (jx < 0) and self.has_obc[0]:
                    continue

                if (jy >= ll[1]) and self.has_obc[1]:
                    continue
                if (jy < 0) and self.has_obc[1]:
                    continue

                if jx >= ll[0]:
                    jx = jx % ll[0]
                if jx < 0:
                    jx += ll[0]

                if jy >= ll[1]:
                    jy = jy % ll[1]
                if jy < 0:
                    jy += ll[1]

                if (jx >= ll[0]) or (jx < 0):
                    raise QTeaLeavesError("Improve handling.")
                if (jy >= ll[1]) or (jy < 0):
                    raise QTeaLeavesError("Improve handling.")

                if (ix == jx) and (iy == jy):
                    raise QTeaLeavesError("Same site ...")

                if not local_mask[ix, iy]:
                    continue

                # Convert from python to Hilbert space index starting from 1
                coords_1d = [map_to_1d[elem] for elem in [(ix, iy), (jx, jy)]]

                yield elem, coords_1d

    def get_fortran_str(self, ll, params, operator_map, param_map):
        """
        See :func:`_ModelTerm.get_fortran_str_two_body`.
        """
        return self.get_fortran_str_twobody(ll, params, operator_map, param_map)


class TwoBodyTerm2DLatticeLayout(TwoBodyTerm2D):
    """
    The term defines an interaction between two sites of the Hilbert space,
    for an arbitrary lattice layout. For example, the tunneling term in the
    Bose-Hubbard model can be represented by this term. This class represents
    the 2d version.

    **Arguments**

    operators : list of two strings
        String identifier for the operators. Before launching the simulation,
        the python API will check that the operator is defined.

    distance : float
        Defines the distance of the interaction.

    layout : :class:`LatticeLayout`, str, callable
        Instance of the :class:`LatticeLayout`. The `LatticeLayout` class stores
        the positions of the (nx)x(ny) grid for an arbitrary lattice layout.

    strength : str, callable, numeric (optional)
        Defines the coupling strength of the local terms. It can
        be parameterized via a value in the dictionary for the
        simulation or a function.
        Default to 1.

    prefactor : numeric, scalar (optional)
        Scalar prefactor, e.g., in order to take into account signs etc.
        Default to 1.

    tolerance : float, optional
        Tolerance for the distance of the interaction,
        i.e., the absolute distance must be smaller than the tolerance
        to consider the sites interacting.

    **Attributes**

    map_type : str, optional
        Selecting the mapping from a n-dimensional system to the
        1d system required for the TTN simulations.
    """

    # pylint: disable-next=too-many-arguments
    def __init__(
        self, operators, distance, layout, strength=1, prefactor=1, tolerance=1e-8
    ):
        super().__init__(operators, 1, strength=strength, prefactor=prefactor)
        self.distance = distance
        self.tolerance = tolerance
        self.layout = layout

        # Delete unused terms
        del self.shift
        del self.isotropy_xyz
        del self.add_complex_conjg
        del self.mask
        del self.has_obc

        # Will be set when adding Hamiltonian terms
        self.map_type = None

    def iter_shifts(self):
        """
        The function is inherited, but we overwrite it since it
        has no meaning in this context.
        """
        raise QTeaLeavesError("This function is not available.")

    def get_entries(self, params):
        """
        The function is inherited, but we overwrite it since it
        has no meaning in this context.
        """
        raise QTeaLeavesError("This function is not available.")

    # pylint: disable-next=too-many-locals
    def get_interactions(self, ll, params, **kwargs):
        """
        These interactions are closest to the TPO description iterating
        over specific sites within the 1d coordinates.

        **Arguments**

        ll : int
            Number of sites along the dimensions, i.e., not the
            total number of sites. Assuming equal number of sites
            along all dimension.

        params : dictionary
            Contains the simulation parameters.
        """
        map_to_1d = map_selector(2, ll, self.map_type)

        layout = self.eval_numeric_param(self.layout, params)

        for ix, iy in self.iterate_sites(ll):
            coord_ix, coord_iy = layout.positions[ix, iy, :]

            for jx, jy in self.iterate_sites(ll):
                coord_jx, coord_jy = layout.positions[jx, jy, :]
                dist = layout.distance((coord_ix, coord_iy), (coord_jx, coord_jy))

                coords_1d_i = map_to_1d[(ix, iy)]
                coords_1d_j = map_to_1d[(jx, jy)]

                if coords_1d_i < coords_1d_j:
                    if np.abs(dist - self.distance) <= self.tolerance:
                        coupl_ij = {
                            "coordinates": [(ix, iy), (jx, jy)],
                            "operators": self.operators,
                        }
                        yield coupl_ij, (coords_1d_i, coords_1d_j)

    def get_fortran_str(self, ll, params, operator_map, param_map):
        """
        See :func:`_ModelTerm.get_fortran_str_two_body`.
        """
        return self.get_fortran_str_twobody(ll, params, operator_map, param_map)
