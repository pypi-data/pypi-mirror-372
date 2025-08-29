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
Idea of CustomSiteTerm:
defining a single n-body interaction term in a d-dimensional system.

Differently from other interaction/local terms, it is not by default applied
to the whole lattice. It is a single term applied to the given set of coordinates.
"""
from copy import deepcopy

from qtealeaves.tooling import QTeaLeavesError
from qtealeaves.tooling.mapping import map_selector

from .baseterm import _ModelTerm

__all__ = ["CustomSiteTerm"]


class CustomSiteTerm(_ModelTerm):
    """
    Single Hamiltonian term on a specified set of coordinates.
    The system can be either 1-, 2-, 3-D.
    The term can be a local term (single operator on a site) or a generic string
    of operators, like a plaquette.

    **Arguments**

    operators : string or list of n strings, where n is the number of operators.
        Each string must be an identifier for the operators.
        Before launching the simulation, the python API will check that the operator is defined.
        CustomSiteTerm can be a 2-body operator (a list of two strings is expected)
        or a generic list of strings (for an n-body term).
        If a single string is passed, it will be first converted into a list (for
        a local term applied to a subset of sites of the lattice).

    coord_list : list of integers, nested list of integers or a callable.
        If coord_list is a list:
            - List of integers: 1-d system is assumed, the length of the list must agree with
            the number of operators.
            - List of lists: a 2d or 3d system is assumed,
            each inner list is the coordinate of a site in the lattice.
            One expects one coordinate for a local term,
            two coordinates for two-body terms and so on.

        If coord_list is a callable it must have the following structure:
            Arguments: params, dictionary.
            Returns: a list in the shape described above depending on the system dimensionality.

    strength : str, callable, numeric (optional).
        It defines the coupling strength of the local terms. It can
        be parameterized via a value in the dictionary for the
        simulation or a function.
        Default to 1.

    prefactor : numeric, scalar (optional).
        Scalar prefactor, e.g., in order to take into account signs etc.
        Default to 1.


    **Attributes**

    map_type : str, optional.
        It selects the mapping from a n-dimensional system to the
        1d system required for the TTN simulations.
    """

    def __init__(self, operators, coord_list, strength=1, prefactor=1):
        super().__init__()

        if isinstance(operators, list):
            self.operators = operators
        elif isinstance(operators, str):
            self.operators = [operators]
        self.strength = strength
        self.prefactor = prefactor

        if isinstance(coord_list, list):
            self.coord_list = deepcopy(coord_list)
        elif hasattr(coord_list, "__call__"):
            self.coord_list = coord_list

        # Will be set when adding Hamiltonian terms
        self.map_type = None

    def get_coord_list(self, params):
        """
        The function get_coord_list returns the list of coordinates a list, independently
        whether the term was defined passing a list or a callable.

        **Arguments**

        params : dictionary
            Contains the simulation parameters.
        """

        if isinstance(self.coord_list, list):
            coord_list = deepcopy(self.coord_list)
        elif hasattr(self.coord_list, "__call__"):
            coord_list = self.coord_list(params)
        else:
            raise QTeaLeavesError(
                f"Unrecognized coord_list type. Expected list or callable, got {type(coord_list)}."
            )

        num_ops = len(self.operators)

        if len(coord_list) != num_ops:
            raise QTeaLeavesError(
                f"Wrong number of coordinates. Expected {num_ops}, got {len(coord_list)}"
            )

        if all(isinstance(coord, int) for coord in coord_list):
            return [[[coord] for coord in coord_list]]

        if all(isinstance(coord, list) for coord in coord_list):
            return [coord_list]

        raise QTeaLeavesError(
            "wrong structure for coord_list. They must be all integers or all lists"
        )

    def check_custom_dim(self, params):
        """
        The function check_custom_dim checks that all the coordinates have the same length.
        """

        coord_list = self.get_coord_list(params)
        test_dim = len(coord_list[0][0])

        res = True

        for term in coord_list:
            for enum_coord, coord in enumerate(term):
                res = len(coord) == test_dim
                if not res:
                    raise QTeaLeavesError(
                        f"Dimension does not match among input coordinates. \
                                          Expected {test_dim}, got {len(coord)} \
                                          on site {enum_coord} with coordinates {coord}"
                    )

    # pylint: disable-next=unused-argument
    def get_entries(self, params):
        """
        Get-entries combines the information about the coordinates with the
        information about the operators.

        **Arguments**

        params : dictionary.
            It Contains the simulation parameters.

        **Returns**

            A generator of dictionaries, one per each term (in this case there is only one term,
            but the structure is kept equal to the stucture of the other Hamiltonian terms, i.e.
            a list of terms).

        **Details**

        To-Do: adding complex conjugates for general case beyond
        b bdagger case.
        """

        coord_list = self.get_coord_list(params)

        for term in coord_list:

            coordinates = deepcopy(term)

            coupl_ii = {"coordinates": coordinates, "operators": self.operators}

            yield coupl_ii

    # pylint: disable-next=too-many-branches
    def get_interactions(self, ll, params, **kwargs):
        """
        These interactions are closest to the TPO description iterating
        over specific sites within the 1d coordinates.

        **Arguments**

        ll : list of ints.
            Number of sites along the dimensions, i.e., not the
            total number of sites. Example: for a 2D system, ll = [L_x, L_y].

        params : dictionary.
            Contains the simulation parameters.

        **Returns**

            a generator of tuples.
            The first element of the tuple is the dictionary
            generated by the function get_entries, the second is a list of the
            1d coordinates obtained from the mapping.
        """

        map_type = self.eval_str_param(self.map_type, params)

        # Here there is a consistency check among all the involved coordinates.
        self.check_custom_dim(params)

        # Here the list of coordinates is defined and
        # the dimensionality of the problem is deduced from the list of coordinates.
        coord_list = self.get_coord_list(params)
        dim = len(coord_list[0][0])

        map_to_1d = map_selector(dim, ll, map_type)

        for term in self.get_entries(params):

            coordinates = [tuple(coord) for coord in term["coordinates"]]

            coords_1d = [map_to_1d[coord] for coord in coordinates]

            yield term, coords_1d
