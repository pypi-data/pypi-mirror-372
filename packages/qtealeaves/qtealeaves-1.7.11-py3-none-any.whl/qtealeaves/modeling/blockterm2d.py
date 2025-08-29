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
Block (generic n-body rectangular) interactions in a two-dimensional system.
"""

import numpy as np

from qtealeaves.tooling import QTeaLeavesError, map_selector

from .baseterm import _ModelTerm

__all__ = ["BlockTerm2D"]


class BlockTerm2D(_ModelTerm):
    """
    The block term is applied to sites in a rectangle with shape l_x*l_y
    in a 2d model. If symmetries are used, none of the operators
    is allowed to change a symmetry sector (block diagonal).

    **Arguments**
    operators : 2d np.array of strings
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

        self.op_shape = operators.shape
        self.operators = operators.flatten()
        self.strength = strength
        self.prefactor = prefactor

        if isinstance(mask, np.ndarray):

            # pylint: disable-next=unused-argument
            def mask_function(params, mask=mask):
                return mask

            mask = mask_function
        self.mask = mask

        # If volume is 1 we need to use a local operator instead.
        if operators.shape[0] * operators.shape[1] == 1:
            raise ValueError(
                "The operator volume is 1. Please use modeling.LocalTerm for local operators."
            )

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
        for operator in self.operators:
            yield operator, None

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

        x_coords, y_coords = np.meshgrid(
            range(self.op_shape[0]), range(self.op_shape[1]), indexing="ij"
        )
        if not self.has_obc[0]:
            x_range = range(ll[0])
        else:
            x_range = range(ll[0] - self.op_shape[0] + 1)
        if not self.has_obc[1]:
            y_range = range(ll[1])
        else:
            y_range = range(ll[1] - self.op_shape[1] + 1)

        for x_i in x_range:
            for y_i in y_range:
                coordinate_grid = np.array(
                    [(x_coords + x_i) % ll[0], (y_coords + y_i) % ll[1]]
                )
                if not local_mask[x_i, y_i]:
                    continue
                coords_1d = [
                    map_to_1d[elem]
                    for elem in [
                        tuple(x_y)
                        for x_y in coordinate_grid.reshape(
                            2, self.op_shape[0] * self.op_shape[1]
                        ).T
                    ]
                ]
                yield elem, coords_1d

    def get_fortran_str(self, ll, params, operator_map, param_map):
        """
        Get the string representation needed to write
        a Fortran input file.

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
        """
        str_repr = ""
        param_repr = self.get_param_repr(param_map)

        op_str = [operator_map[(elem, None)] for elem in self.operators]

        l_x, l_y = self.op_shape
        op_volume = l_x * l_y
        counter = 0
        for _, coords in self.get_interactions(ll, params):
            counter += 1
            if len(set(coords)) < op_volume:
                raise QTeaLeavesError("Same site ...")
            inds = np.argsort(np.array(coords))
            for ii in range(op_volume):
                str_repr += "%d %d\n" % (coords[inds[ii]] + 1, op_str[inds[ii]])
            str_repr += param_repr + " %30.15E\n" % (self.prefactor)

        # Now we can write the information for the first lines (order is correct)
        str_repr = "%d\n" % (op_volume) + str_repr
        str_repr = "%d\n" % (counter) + str_repr
        return str_repr
