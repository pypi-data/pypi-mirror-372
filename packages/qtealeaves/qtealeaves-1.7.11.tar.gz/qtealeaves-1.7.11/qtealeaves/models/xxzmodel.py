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
Setup of quantum Ising models.
"""

from qtealeaves import modeling, operators

__all__ = ["get_xxz_1d"]


def get_xxz_1d(has_obc=True):
    """
    Return the XXZ model and its operators in one dimension.

    **Arguments**

    has_obc : bool or list of bools, optional
        Defines the boundary condition. Default to True

    **Returns**

    model : instance of :class:`QuantumModel`
        Contains the Hamiltonian of the system.

    xxz_ops : instance of :class:`TNOperators`
        Contains the operators required for the quantum
        Ising model.

    **Details**

    The XXZ models comes with four parameters to be defined,
    i.e., the system size `L`, the external field `g`, and the
    interaction strengths `Jx` and `Jz`. These need to be defined
    in the simulation dictionary.
    """
    model_name = lambda params: "XXZ"

    model = modeling.QuantumModel(1, "L", name=model_name)
    model += modeling.LocalTerm("sz", strength="g", prefactor=-1)
    model += modeling.TwoBodyTerm1D(
        ["splus", "sminus"], shift=1, strength="Jx", prefactor=-0.5, has_obc=has_obc
    )
    model += modeling.TwoBodyTerm1D(
        ["sminus", "splus"], shift=1, strength="Jx", prefactor=-0.5, has_obc=has_obc
    )
    model += modeling.TwoBodyTerm1D(
        ["sz", "sz"], shift=1, strength="Jz", prefactor=-1, has_obc=has_obc
    )

    xxz_ops = operators.TNSpin12Operators()

    return model, xxz_ops
