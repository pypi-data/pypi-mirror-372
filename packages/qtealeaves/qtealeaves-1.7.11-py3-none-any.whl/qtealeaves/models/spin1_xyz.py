"""
Setup for spin-1 XYZ model.
"""

from qtealeaves import modeling, operators

__all__ = ["get_spin1_xyz_1d"]


def get_spin1_xyz_1d(has_obc=True):
    """
    Spin-1 XYZ chain.

    **Returns**

    model : instance of :class:`QuantumModel`
        Contains the Hamiltonian of the system.

    spin1_ops : instance of :class:`TNOperators`
        Contains the spin-1 operators.
    """

    model_name = lambda params: "XYZ S=1"

    model = modeling.QuantumModel(1, "L", name=model_name)

    model += modeling.TwoBodyTerm1D(
        ["sx", "sx"], shift=1, strength="Jx", prefactor=1, has_obc=has_obc
    )
    model += modeling.TwoBodyTerm1D(
        ["sy", "sy"], shift=1, strength="Jy", prefactor=1, has_obc=has_obc
    )
    model += modeling.TwoBodyTerm1D(
        ["sz", "sz"], shift=1, strength="Jz", prefactor=1, has_obc=has_obc
    )

    spin1_ops = operators.TNSpin1Operators()

    return model, spin1_ops
