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

__all__ = [
    "get_quantum_ising_1d",
    "get_quantum_ising_2d",
    "get_quantum_ising_3d",
]


def get_quantum_ising_1d(has_obc=True):
    """
    Return quantum Ising model and its operators in one dimension
    for open boundary conditions.

    **Arguments**

    has_obc : bool or list of bools, optional
        Defines the boundary condition along each spatial dimension.
        If scalar is given, the boundary condition along each
        spatial dimension is assumed to be equal.
        Default to True

    **Returns**

    model : instance of :class:`QuantumModel`
        Contains the Hamiltonian of the system.

    ising_ops : instance of :class:`TNOperators`
        Contains the operators required for the quantum
        Ising model.

    **Details**

    The quantum Ising model comes with three parameters to be defined,
    i.e., the system size `L`, the external field `g`, and the
    interaction strength `J`. These need to be defined in the simulation
    dictionary.
    """
    model_name = lambda params: "QIsing_g%2.4f" % (params["g"])

    model = modeling.QuantumModel(1, "L", name=model_name)
    model += modeling.LocalTerm("sz", strength="g", prefactor=-1)
    model += modeling.TwoBodyTerm1D(
        ["sx", "sx"], 1, strength="J", prefactor=-1, has_obc=has_obc
    )

    ising_ops = operators.TNSpin12Operators()

    return model, ising_ops


def get_quantum_ising_2d(has_obc=True):
    """
    Return quantum Ising model and its operators in two dimensions
    for open boundary conditions.

    **Arguments**

    has_obc : bool or list of bools, optional
        Defines the boundary condition along each spatial dimension.
        If scalar is given, the boundary condition along each
        spatial dimension is assumed to be equal.
        Default to True

    **Returns**

    model : instance of :class:`QuantumModel`
        Contains the Hamiltonian of the system.

    ising_ops : instance of :class:`TNOperators`
        Contains the operators required for the quantum
        Ising model.

    **Details**

    The quantum Ising model comes with three parameters to be defined,
    i.e., the system size `L`, the external field `g`, and the
    interaction strength `J`. These need to be defined in the simulation
    dictionary. The interaction `J` is independent of the spatial
    direction.
    """
    model_name = lambda params: "QIsing_g%2.4f" % (params["g"])

    model = modeling.QuantumModel(2, "L", name=model_name)
    model += modeling.LocalTerm("sz", strength="g", prefactor=-1)
    model += modeling.TwoBodyTerm2D(
        ["sx", "sx"], shift=[1, 0], strength="J", prefactor=-1, has_obc=has_obc
    )

    ising_ops = operators.TNSpin12Operators()

    return model, ising_ops


def get_quantum_ising_3d(has_obc=True):
    """
    Return quantum Ising model and its operators in three dimensions
    for open boundary conditions.

    **Arguments**

    has_obc : bool or list of bools, optional
        Defines the boundary condition along each spatial dimension.
        If scalar is given, the boundary condition along each
        spatial dimension is assumed to be equal.
        Default to True

    **Returns**

    model : instance of :class:`QuantumModel`
        Contains the Hamiltonian of the system.

    ising_ops : instance of :class:`TNOperators`
        Contains the operators required for the quantum
        Ising model.

    **Details**

    The quantum Ising model comes with three parameters to be defined,
    i.e., the system size `L`, the external field `g`, and the
    interaction strength `J`. These need to be defined in the simulation
    dictionary. The interaction `J` is independent of the spatial
    direction.
    """
    model_name = lambda params: "QIsing_g%2.4f" % (params["g"])

    model = modeling.QuantumModel(3, "L", name=model_name)
    model += modeling.LocalTerm("sz", strength="g", prefactor=-1)
    model += modeling.TwoBodyTerm3D(
        ["sx", "sx"], shift=[1, 0, 0], strength="J", prefactor=-1, has_obc=has_obc
    )

    ising_ops = operators.TNSpin12Operators()

    return model, ising_ops
