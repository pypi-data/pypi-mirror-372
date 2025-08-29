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
String (generic n-body) interactions in a 1-dimensional system.
"""

# pylint: disable-msg=too-many-arguments
# pylint: disable-msg=invalid-name

import numpy as np

from qtealeaves.tooling import QTeaLeavesError

from .baseterm import _ModelTerm

__all__ = ["StringTerm1D"]


class StringTerm1D(_ModelTerm):
    """
    The string term is applied to sites in a string with length l_x
    in a 1d model. If symmetries are used, none of the operators
    is allowed to change a symmetry sector (block diagonal).

    **Arguments**
    operators : list of strings
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

    has_obc : bool, optional
        Defines the boundary condition.
        Default to True.

    mask : callable or ``None``, optional
        The true-false-mask allows to apply the Hamiltonians terms
        only to specific plaquettes,
        i.e., with true values. The function
        takes the dictionary with the simulation parameters as an
        argument. The mask is applied to the site where the lower-left
        corner of the plaquette operator is acting on.
        Default to ``None`` (all sites have the interaction)

    """

    def __init__(self, operators, strength=1, prefactor=1, has_obc=True, mask=None):
        self.str_len = len(operators)
        self.operators = operators
        self.strength = strength
        self.prefactor = prefactor

        if isinstance(mask, np.ndarray):
            # pylint: disable=unused-argument
            def mask_function(params, mask=mask):
                return mask

            # pylint: enable=unused-argument

            mask = mask_function
        self.mask = mask

        # If volume is 1 we need to use a local operator instead.
        if self.str_len == 1:
            raise ValueError(
                "The operator volume is 1. Please use modeling.LocalTerm for local operators."
            )

        # Will be set when adding Hamiltonian terms
        self.map_type = None

        self.has_obc = has_obc

    @staticmethod
    def check_dim(dim):
        """
        Only available in 1d systems.
        """
        if dim != 1:
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

        **Arguments**

        ll : [int]
            Number of sites of the 1d lattice.

        params : dictionary
            Contains the simulation parameters.
        """

        if self.mask is None:
            local_mask = np.ones(ll[0], dtype=bool)
        else:
            local_mask = self.mask(params)

        elem = {"operators": self.operators}

        x_coords = np.arange(self.str_len)

        if not self.has_obc:
            x_range = range(ll[0])
        else:
            x_range = range(ll[0] - self.str_len + 1)

        for x_i in x_range:
            coordinates = (x_coords + x_i) % ll[0]
            if not local_mask[x_i]:
                continue
            yield elem, coordinates.tolist()

    def get_fortran_str(self, ll, params, operator_map, param_map):
        """
        Get the string representation needed to write
        a Fortran input file.
        """

        if len(ll) != 1:
            raise ValueError("StringTerm1D only available for 1d lattices.")

        str_repr = ""
        param_repr = self.get_param_repr(param_map)

        op_str = [operator_map[(elem, None)] for elem in self.operators]

        op_volume = self.str_len
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
