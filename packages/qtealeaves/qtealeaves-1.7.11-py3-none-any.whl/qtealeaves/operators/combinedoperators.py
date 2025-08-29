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
Combined operators.
"""

import numpy as np

from qtealeaves.tooling import QTeaLeavesError

from .tnoperators import TNOperators

__all__ = ["TNCombinedOperators"]


class TNCombinedOperators(TNOperators):
    """
    Combine operators for system a and b.

    **Arguments**

    ops_a : instance of :class:`TNOperators`
        Set of operators for system a.

    ops_b : instance of :class:`TNOperators`
        Set of operators for system b.

    folder_operators : str, optional
        The name of the subfolder inside the input folder, where
        we store operators.
        Default to ``CombinedOps``

    **Details**

    The key of the operators after merging will be ops_a.ops_b.
    """

    def __init__(self, ops_a, ops_b):
        super().__init__()

        if not isinstance(ops_a, TNOperators):
            raise QTeaLeavesError("Operators A are not an instance of TNOperators.")

        if not isinstance(ops_b, TNOperators):
            raise QTeaLeavesError("Operators B are not an instance of TNOperators.")

        self.ops_a = ops_a
        self.ops_b = ops_b
        self.merge_ops()

    def merge_ops(self):
        """
        Merge set of operators.
        """
        for name in self.ops_a.set_names:
            # Identity should go first and must be named "id"
            self[(name, "id")] = self.get_any_operator_function(
                (name, "id"), (name, "id")
            )

        # Brute-force add all other ones
        for key_a in self.ops_a:
            for key_b in self.ops_b:
                if key_a[0] != key_b[0]:
                    # Different set of operators
                    continue

                key = ".".join([key_a[1], key_b[1]])
                self[(key_a[0], key)] = self.get_any_operator_function(key_a, key_b)

    def get_any_operator_function(self, key_a, key_b):
        """
        Get function to compute kronecker product between set of
        operators a and b.

        Parameters
        ----------
        key_a : str
            Operator name of class a.
        key_b : str
            Operator name of class b.
        """

        def get_any_operator(params, self=self, key_a=key_a, key_b=key_b):
            op_a = self.ops_a.get_operator(key_a[0], key_a[1], params)
            op_b = self.ops_b.get_operator(key_b[0], key_b[1], params)
            return np.kron(op_a, op_b)

        return get_any_operator
