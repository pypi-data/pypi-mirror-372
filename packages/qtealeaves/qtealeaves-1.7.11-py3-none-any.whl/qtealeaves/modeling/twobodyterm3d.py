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
Two-body interactions in a three-dimensional system.
"""

# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments

import numpy as np

from qtealeaves.tooling import QTeaLeavesError
from qtealeaves.tooling.mapping import map_selector

from .baseterm import _ModelTerm

__all__ = ["TwoBodyTerm3D"]


class TwoBodyTerm3D(_ModelTerm):
    """
    The term defines an interaction between two sites of the Hilbert space.
    For example, the tunneling term in the Bose-Hubbard model can be
    represented by this term. This class represents the 2d version.

    **Arguments**

    operators : list of two strings
        String identifier for the operators. Before launching the simulation,
        the python API will check that the operator is defined.

    shift : list of three ints
        Defines the distance of the interaction. In the end,
        we iterate over all sites and apply interactions to
        sites (x, y, z) and (x + shift[0], y + shift[1], z + shift[2])

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

    **Attributes**

    map_type : str, optional
        Selecting the mapping from a n-dimensional system to the
        1d system required for the TTN simulations.
    """

    def __init__(
        self,
        operators,
        shift,
        strength=1,
        prefactor=1,
        isotropy_xyz=True,
        add_complex_conjg=False,
        has_obc=True,
    ):
        super().__init__()

        self.operators = operators
        self.shift = shift
        self.strength = strength
        self.prefactor = prefactor
        self.isotropy_xyz = isotropy_xyz
        self.add_complex_conjg = add_complex_conjg

        # Will be set when adding Hamiltonian terms
        self.map_type = None

        if isinstance(has_obc, bool):
            self.has_obc = [has_obc] * 3
        else:
            self.has_obc = has_obc

    @staticmethod
    def check_dim(dim):
        """
        See :func:`_ModelTerm.check_dim`
        """
        if dim != 3:
            raise QTeaLeavesError("Dimension does not match.")

    def collect_operators(self):
        """
        All the required operators are returned to ensure that they are
        written by fortran.
        """
        yield self.operators[0], "l"
        yield self.operators[1], "r"

        # Have to always add ... order in sites not guaranteed and
        # could be swapped
        yield self.operators[1], "l"
        yield self.operators[0], "r"

        if self.add_complex_conjg:
            # Only works in the b, bdagger or sigma^{+}, sigma^{-}
            # scenario

            yield self.operators[1], "l"
            yield self.operators[0], "r"

    def iter_shifts(self):
        """
        Return all possible shifts, which depends on the isotropy
        in the 3d case.
        """
        if self.isotropy_xyz:
            n_coord = np.sum(np.array(self.shift) > 0)
            if n_coord not in [1, 2, 3]:
                raise QTeaLeavesError(
                    f"Not implemented. Is this case n_coord={n_coord} useful?"
                )
            if n_coord == 1:
                shifts = [
                    [self.shift[0], self.shift[1], self.shift[2]],
                    [self.shift[1], self.shift[2], self.shift[0]],
                    [self.shift[2], self.shift[0], self.shift[1]],
                ]
            elif n_coord == 2:
                if len(set(self.shift)) != 2:
                    # Can be solved by adding the additional permutation
                    # and then building the set
                    raise QTeaLeavesError("Missing permutations.")
                shifts = [
                    [self.shift[0], self.shift[1], self.shift[2]],
                    [self.shift[0], -self.shift[1], self.shift[2]],
                    [self.shift[1], self.shift[2], self.shift[0]],
                    [self.shift[1], self.shift[2], -self.shift[0]],
                    [self.shift[2], self.shift[0], self.shift[1]],
                    [self.shift[2], -self.shift[0], self.shift[1]],
                ]
            else:
                # Must be n_coords=3 now
                if len(set(self.shift)) != 1:
                    # Can be solved by adding the additional permutation
                    # and then building the set
                    raise QTeaLeavesError("Maybe missing permutations.")
                shifts = [
                    [self.shift[0], self.shift[1], self.shift[2]],
                    [-self.shift[0], self.shift[1], self.shift[2]],
                    [self.shift[0], -self.shift[1], self.shift[2]],
                    [self.shift[0], self.shift[1], -self.shift[2]],
                ]
        else:
            shifts = [self.shift]

        yield from shifts

    def get_entries(self, params):
        """
        Entries are defined based on two coordinates, the origin
        chosen as (0, 0, 0) and the shift. There are no site-dependent
        terms.

        **Arguments**

        params : dictionary
            Contains the simulation parameters.

        **Details**

        To-Do: complex-conjugate terms are wrong, i.e., they work
        for sigma_{i}^{+} sigma_{j}^{-} or b_{i}^{dagger} b_{j}, but
        not for terms as b_{j} sigma_{i}^{x}!
        """
        if (self.has_obc[0] != self.has_obc[1]) or (self.has_obc[0] != self.has_obc[2]):
            raise QTeaLeavesError(
                "Cannot build dictionary with different " + "boundary conditions."
            )

        for shift in self.iter_shifts():
            coord_a = [0, 0, 0]
            coord_b = shift
            coordinates = [coord_a, coord_b]

            coupl_ii = {
                "strength": self.eval_strength(params),
                "operators": self.operators,
                "coordinates": coordinates,
            }

            yield coupl_ii

            if self.add_complex_conjg:
                coupl_ii = {
                    "strength": self.eval_strength(params),
                    "operators": [self.operators[1], self.operators[0]],
                    "coordinates": coordinates,
                }

                yield coupl_ii

    def get_interactions(self, ll, params, **kwargs):
        """
        These interactions are closest to the TPO description iterating
        over specific sites within the 1d coordinates.

        **Arguments**

        ll : int
            Number of sites along each dimension, i.e., not the
            total number of sites. Assuming list of sites
            along all dimension.

        params : dictionary
            Contains the simulation parameters.
        """
        if isinstance(self.map_type, str):
            map_type = self.eval_str_param(self.map_type, params)
        else:
            map_type = self.map_type
        map_to_1d = map_selector(3, ll, map_type)

        for elem in self.get_entries(params):
            for ix, iy, iz in self.iterate_sites(ll):
                coord_a, coord_b = elem["coordinates"]

                if np.sum(np.abs(np.array(coord_a))) != 0:
                    raise QTeaLeavesError("Coordinate A is not the origin.")

                jx = ix + coord_b[0]
                jy = iy + coord_b[1]
                jz = iz + coord_b[2]

                if (jx >= ll[0]) and self.has_obc[0]:
                    continue
                if (jx < 0) and self.has_obc[0]:
                    continue

                if (jy >= ll[1]) and self.has_obc[1]:
                    continue
                if (jy < 0) and self.has_obc[1]:
                    continue

                if (jz >= ll[2]) and self.has_obc[2]:
                    continue
                if (jz < 0) and self.has_obc[2]:
                    continue

                if jx >= ll[0]:
                    jx = jx % ll[0]
                if jx < 0:
                    jx += ll[0]

                if jy >= ll[1]:
                    jy = jy % ll[1]
                if jy < 0:
                    jy += ll[1]

                if jz >= ll[2]:
                    jz = jz % ll[2]
                if jz < 0:
                    jz += ll[2]

                if (jx >= ll[0]) or (jx < 0):
                    raise QTeaLeavesError("Improve handling.")
                if (jy >= ll[1]) or (jy < 0):
                    raise QTeaLeavesError("Improve handling.")
                if (jz >= ll[2]) or (jz < 0):
                    raise QTeaLeavesError("Improve handling.")

                if (ix == jx) and (iy == jy) and (iz == jz):
                    raise QTeaLeavesError(
                        "Same site.", (ix, iy, iz), (jx, jy, jz), coord_a, coord_b
                    )

                # Convert from python to Hilbert space index starting from 1
                coords_1d = [map_to_1d[elem] for elem in [(ix, iy, iz), (jx, jy, jz)]]

                yield elem, coords_1d

    def get_fortran_str(self, ll, params, operator_map, param_map):
        """
        See :func:`_ModelTerm.get_fortran_str_two_body`.
        """
        return self.get_fortran_str_twobody(ll, params, operator_map, param_map)
