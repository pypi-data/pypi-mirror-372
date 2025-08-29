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
Setup of Bose-Hubbard models.
"""

from qtealeaves import modeling, operators

__all__ = ["get_bose_hubbard_1d", "get_bose_hubbard_2d"]


def get_bose_hubbard_1d():
    """
    Return the Bose-Hubbard model and its operators in one dimension
    for open boundary conditions.

    **Returns**

    model : instance of :class:`QuantumModel`
        Contains the Hamiltonian of the system.

    bose_ops : instance of :class:`TNOperators`
        Contains the operators required for the quantum
        Ising model.

    **Details**

    The Bose-Hubbard model comes with three parameters to be defined,
    i.e., the system size `L`, the tunneling strength `J`, and the
    on-site interaction `U`.
    """
    model_name = lambda params: "BoseHubbard_J%2.4f" % (params["J"])

    model = modeling.QuantumModel(1, "L", name=model_name)
    model += modeling.LocalTerm("nint", strength="U")
    model += modeling.TwoBodyTerm1D(["bdagger", "b"], 1, strength="J", prefactor=-1)
    model += modeling.TwoBodyTerm1D(["b", "bdagger"], 1, strength="J", prefactor=-1)

    bose_ops = operators.TNBosonicOperators()

    return model, bose_ops


def get_bose_hubbard_2d():
    """
    Return the Bose-Hubbard model and its operators in one dimension
    for open boundary conditions.

    **Returns**

    model : instance of :class:`QuantumModel`
        Contains the Hamiltonian of the system.

    bose_ops : instance of :class:`TNOperators`
        Contains the operators required for the quantum
        Ising model.

    **Details**

    The Bose-Hubbard model comes with three parameters to be defined,
    i.e., the system size `L`, the tunneling strength `J`, and the
    on-site interaction `U`. The tunneling in x-direction and
    y-direction are equally strong.
    """
    model_name = lambda params: "BoseHubbard_J%2.4f" % (params["J"])

    model = modeling.QuantumModel(2, "L", name=model_name)
    model += modeling.LocalTerm("nint", strength="U")
    model += modeling.TwoBodyTerm2D(
        ["bdagger", "b"], [1, 0], strength="J", prefactor=-1
    )
    model += modeling.TwoBodyTerm2D(
        ["b", "bdagger"], [1, 0], strength="J", prefactor=-1
    )

    bose_ops = operators.TNBosonicOperators()

    return model, bose_ops
