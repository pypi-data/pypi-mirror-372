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
Plaquette (4-body) interactions in a two-dimensional system.
"""
import numpy as np

from qtealeaves.tooling import QTeaLeavesError, map_selector

from .baseterm import _ModelTerm

__all__ = ["PlaquetteTerm2D"]


class PlaquetteTerm2D(_ModelTerm):
    """
    The plaquette term is applied to 2x2 nearest-neighbor sites
    in a 2d model. If symmetries are used, none of the operators
    is allowed to change a symmetry sector (block diagonal).

    **Arguments**
    operators : list of two strings
        String identifier for the operators. Before launching the simulation,
        the python API will check that the operator is defined.

    strength : str, callable, numeric (optional)
        Defines the coupling strength of the local terms. It can
        be parameterized via a value in the dictionary for the
        simulation or a function.
        Default to 1.

    prefactor : numeric, scalar (optional)
        Scalar prefactor, e.g., in order to take into account signs etc.
        Default to 1.

    has_obc : bool or list of bools, optional
        Defines the boundary condition along each spatial dimension.
        If scalar is given, the boundary condition along each
        spatial dimension is assumed to be equal.
        Default to True
        If [False, True], the topology is a strip on the x axis
        If [True, False], the topology is a strip on the y axis
        If [False,False], the topology is a thorus

    mask : callable or ``None``, optional
        The true-false-mask allows to apply the Hamiltonians terms
        only to specific plaquettes,
        i.e., with true values. The function
        takes the dictionary with the simulation parameters as an
        argument. The mask is applied to the site where the lower-left
        corner of the plaquette operator is acting on.
        Default to ``None`` (all sites have the interaction)


    The order of the operators is for the shifts (0,0), (0,1), (1,0), (1,1)
    """

    # pylint: disable-next=too-many-arguments
    def __init__(self, operators, strength=1, prefactor=1, has_obc=True, mask=None):
        super().__init__()

        self.operators = operators
        self.strength = strength
        self.prefactor = prefactor
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
        Only available in 2d systems.
        """
        if dim != 2:
            raise QTeaLeavesError("Dimension does not match.")

    def collect_operators(self):
        """
        All the required operators are returned to ensure that they are
        written by fortran.
        """
        yield self.operators[0], None
        yield self.operators[1], None
        yield self.operators[2], None
        yield self.operators[3], None

    # pylint: disable-next=too-many-locals
    def get_interactions(self, ll, params, **kwargs):
        """
        Description of interactions close to the TPO formulation.
        It works for both Periodic and Open Boundary conditions,
        depending on the argument has_obc.
        NOTE the order of the operators is
                (x2,y2) ---- (x4,y4)
                   |            |
                   |            |
                (x1,y1) ---- (x3,y3)

        **Arguments**

        ll : list of ints
            Number of sites along the dimensions, i.e., not the
            total number of sites. Assuming list of sites
            along all dimension.

        params : dictionary
            Contains the simulation parameters.
        """
        map_to_1d = map_selector(2, ll, self.map_type)

        if self.mask is None:
            local_mask = np.ones(ll, dtype=bool)
        else:
            local_mask = self.mask(params)

        elem = {"operators": self.operators}

        for x1 in range(ll[0]):
            for y1 in range(ll[1]):
                if x1 < ll[0] - 1:
                    x2 = x1
                    x3 = x1 + 1
                    x4 = x1 + 1
                else:
                    if not self.has_obc[0]:
                        # Periodic boundary conditions on x.
                        # The right part of the plaquette is on the left side of the lattice,
                        # i.e. x3=x4=0
                        x2 = x1
                        x3 = 0
                        x4 = 0
                    else:
                        continue
                if y1 < ll[1] - 1:
                    y2 = y1 + 1
                    y3 = y1
                    y4 = y1 + 1
                else:
                    if not self.has_obc[1]:
                        # Periodic boundary conditions on y.
                        # The upper part of the plaquette is on the lower side of the lattice,
                        # i.e. y2=y4=0
                        y2 = 0
                        y3 = y1
                        y4 = 0
                    else:
                        continue

                if not local_mask[x1, y1]:
                    continue
                coords_1d = [
                    map_to_1d[elem] for elem in [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
                ]

                yield elem, coords_1d

    def get_fortran_str(self, ll, params, operator_map, param_map):
        """
        Get the string representation needed to write
        a Fortran input file.
        """
        str_repr = ""
        param_repr = self.get_param_repr(param_map)

        op_str = [operator_map[(elem, None)] for elem in self.operators]

        counter = 0
        for _, coords in self.get_interactions(ll, params):
            counter += 1

            if coords[0] == coords[1]:
                raise QTeaLeavesError("Same site ...")
            if coords[0] == coords[2]:
                raise QTeaLeavesError("Same site ...")
            if coords[0] == coords[3]:
                raise QTeaLeavesError("Same site ...")
            if coords[1] == coords[2]:
                raise QTeaLeavesError("Same site ...")
            if coords[1] == coords[3]:
                raise QTeaLeavesError("Same site ...")
            if coords[2] == coords[3]:
                raise QTeaLeavesError("Same site ...")

            inds = np.argsort(np.array(coords))

            for ii in range(4):
                str_repr += "%d %d\n" % (coords[inds[ii]] + 1, op_str[inds[ii]])

            str_repr += param_repr + " %30.15E\n" % (self.prefactor)

        # Now we can write the information for the first lines (order is correct)
        str_repr = "%d\n" % (4) + str_repr
        str_repr = "%d\n" % (counter) + str_repr

        return str_repr
