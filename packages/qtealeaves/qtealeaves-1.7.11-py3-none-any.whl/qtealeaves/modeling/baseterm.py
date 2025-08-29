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
Abstract base class for a term in the model.
"""


from itertools import product
from warnings import warn

from qtealeaves.tooling import QTeaLeavesError
from qtealeaves.tooling.parameterized import _ParameterizedClass

__all__ = ["_ModelTerm", "_ModelTerm1D"]


class _ModelTerm(_ParameterizedClass):
    """
    Abstract base class for any term in a model.
    """

    strength = 1
    prefactor = 1

    @property
    def is_oqs(self):
        """Status flag if term belongs to Hamiltonian or is Lindblad."""
        return False

    @staticmethod
    def check_dim(dim):
        """
        By default, do not restrict dimensionality. Overwriting
        this methods, allows to restrict terms to 1d, 2d, or
        3d systems.

        **Arguments**

        dim : int
            Dimensionality of the system, e.g., 3 for a 3-d systems.
        """
        return isinstance(dim, int)

    @staticmethod
    def iterate_sites(ll):
        """
        Iterate sites; trivial in 1d model.

        **Arguments**

        ll : list of one int
            Number of sites in the chain is stored in the
            first entry of the list.
        """
        if len(ll) == 1:
            yield from range(ll[0])
        else:
            ranges = [range(ii) for ii in ll]
            yield from product(*ranges)

    def eval_strength(self, params):
        """
        Evaluate the strength of the parameter.

        **Arguments**

        params : dictionary
            Contains the simulation parameters.
        """
        strength = self.eval_numeric_param(self.strength, params)

        if hasattr(strength, "__len__"):
            raise QTeaLeavesError("Strength cannot be a list.")
        if strength == 0.0:
            warn("Adding term with zero-coupling.")

        return strength

    def get_strengths(self):
        """
        Returns an iterator over the strenghts of the term.
        It is just the strength in most cases, but it can vary
        (for example for the KrausTerm)
        """
        yield self.strength

    def get_param_repr(self, param_map):
        """
        Get the integer identifier as a string to be written into
        the input files for fortran.

        **Arguments**

        param_map : dict
            This dictionary contains the mapping from the parameters
            to integer identifiers.
        """
        if hasattr(self.strength, "__call__"):
            param_repr = str(param_map[repr(self.strength)][0]) + "\n"
        elif isinstance(self.strength, str):
            param_repr = str(param_map[self.strength][0]) + "\n"
        elif self.strength == 1.0:
            # Default
            param_repr = "-1\n"
        else:
            raise QTeaLeavesError("Case not allowed.")

        return param_repr

    def get_interactions(self, ll, params, **kwargs):
        """
        Iterator returning the terms one-by-one, e.g., to build
        a Hamiltonian matrix. Must be overwritten by inheriting
        class.
        """
        raise NotImplementedError("Must be overwritten.")

    def get_fortran_str_twobody(self, ll, params, operator_map, param_map):
        """
        Get the string representation needed to write
        for Fortran. This method works for any two-body interaction.

        **Arguments**

        ll : int
            Number of sites along the dimensions in the system, e.g.,
            number of sites for both sides of the rectangle in a 2d system.

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

        subterms = []
        for elem in self.get_interactions(ll, params):
            subterms.append(elem)

            if elem[1][0] == elem[1][1]:
                raise QTeaLeavesError("Same site ...")

        # Number of terms and number of operators (later always 2)
        str_repr += "%d\n" % (len(subterms))
        str_repr += "%d\n" % (2)

        for elem in subterms:
            # Two "loop" over the operators
            # pylint: disable=no-member
            if elem[1][0] < elem[1][1]:
                op_id_str_0 = operator_map[(self.operators[0], "l")]
                op_id_str_1 = operator_map[(self.operators[1], "r")]

                # Convert from python index to fortran index by
                # adding offset 1
                str_repr += "%d %d\n" % (elem[1][0] + 1, op_id_str_0)
                str_repr += "%d %d\n" % (elem[1][1] + 1, op_id_str_1)
            else:
                op_id_str_0 = operator_map[(self.operators[0], "r")]
                op_id_str_1 = operator_map[(self.operators[1], "l")]

                # Convert from python index to fortran index by
                # adding offset 1
                str_repr += "%d %d\n" % (elem[1][1] + 1, op_id_str_1)
                str_repr += "%d %d\n" % (elem[1][0] + 1, op_id_str_0)

            # pylint: enable=no-member

            str_repr += param_repr + " %30.15E\n" % (self.prefactor)
        return str_repr

    # pylint: disable-next=unused-argument, too-many-arguments
    def quantum_jump_weight(self, state, operators, quench, time, params, **kwargs):
        """Evaluate the unnormalized weight for a jump with this Lindblad term."""
        if self.is_oqs:
            raise NotImplementedError("Must be overwritten for Lindblad.")

        raise ValueError("Trying to evaluate quantum jump on Hamiltonian term.")

    # pylint: disable-next=unused-argument
    def quantum_jump_apply(self, state, operators, params, rand_generator, **kwargs):
        """Apply jump with this Lindblad."""
        if self.is_oqs:
            raise NotImplementedError("Must be overwritten for Lindblad.")

        raise ValueError("Trying to evaluate quantum jump on Hamiltonian term.")


# pylint: disable-next=abstract-method
class _ModelTerm1D(_ModelTerm):
    """
    Abstract base class for any term in a 1D model.
    """

    @staticmethod
    def check_dim(dim):
        """
        See :func:`_ModelTerm.check_dim`
        """
        if dim != 1:
            raise QTeaLeavesError("Dimension does not match.")

    def collect_operators(self):
        """
        All the required operators are returned to ensure that they are
        written by fortran.
        """
        # Take same approach as in 2d/3d system and provide both versions
        # of the operator (although there is no mapping like the Hilbert
        # curve, occasional problem appeared)
        # pylint: disable=no-member
        yield self.operators[0], "l"
        yield self.operators[0], "r"
        yield self.operators[1], "l"
        yield self.operators[1], "r"

        if self.add_complex_conjg:
            # Only works in the b, bdagger or sigma^{+}, sigma^{-}
            # scenario

            yield self.operators[1], "l"
            yield self.operators[0], "r"

        # pylint: enable=no-member
