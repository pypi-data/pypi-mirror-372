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
Setup of singlet fission model.
"""

import numpy as np

import qtealeaves as qtl
from qtealeaves.modeling import LindbladTerm, LocalTerm, QuantumModel, TwoBodyTerm1D
from qtealeaves.operators import TNOperators

__all__ = ["get_singlet_fission_1d", "get_singlet_fission_1d_phonons"]


def get_singlet_fission_1d(has_obc=True):
    """
    Return singlet fission model and its operators in one dimension
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

    sf_ops : instance of :class:`TNOperators`
        Contains the operators required for the singlet fission model.

    **Details**

    The singlet fission model comes with 7 parameters to be defined,
    - the system size `L`,
    - the local singlet energy `Es`,
    - the local triplet energy `Et`,
    - the singlet hopping coupling `Js`,
    - the triplet hopping coupling `Jt`,
    - the triplet-triplet exchange interaction `chi`,
    - the singlet-triplet coupling `gamma`.
    These need to be defined in the simulation dictionary.
    """

    # ----- operators -----

    # create singlet fission operators
    sf_ops = TNOperators()

    # identity matrix
    sf_ops["id"] = np.eye(3)

    # singlet and triplet dagger
    sf_ops["sd"] = np.array([[0, 0, 0], [1.0, 0, 0], [0, 0, 0]])
    sf_ops["td"] = np.array([[0, 0, 0], [0, 0, 0], [1.0, 0, 0]])

    # singlet and triplet annihilation
    sf_ops["sa"] = np.transpose(sf_ops["sd"])
    sf_ops["ta"] = np.transpose(sf_ops["td"])

    # triplet dagger - triplet annihilation and h.c.
    sf_ops["tdta"] = np.dot(sf_ops["td"], sf_ops["ta"])
    sf_ops["tatd"] = np.dot(sf_ops["ta"], sf_ops["td"])

    # singlet dagger - triplet annihilation and h.c.
    sf_ops["sdta"] = np.array([[0, 0, 0], [0, 0, 1], [0, 0, 0.0]])
    sf_ops["tdsa"] = np.array([[0, 0, 0], [0, 0, 0], [0, 1, 0.0]])

    # number operator singlet and triple
    sf_ops["ns"] = np.diag([0, 1.0, 0])
    sf_ops["nt"] = np.diag([0, 0, 1.0])

    # symmetry generator 2ns + nt (never used)
    sf_ops["sym_gen"] = 2 * sf_ops["ns"] + sf_ops["nt"]

    # ----- model -----

    # model name
    model_name = "singlet_fission_1d"

    # create quantum model with length L
    model = QuantumModel(1, "L", name=model_name)

    # local singlet energy
    model += LocalTerm("ns", strength="Es")

    # local triplet energy
    model += LocalTerm("nt", strength="Et")

    # hopping singlets and h.c.
    model += TwoBodyTerm1D(
        ["sd", "sa"], 1, strength="Js", prefactor=+1, has_obc=has_obc
    )
    model += TwoBodyTerm1D(
        ["sa", "sd"], 1, strength="Js", prefactor=+1, has_obc=has_obc
    )

    # hopping triplets and h.c.
    model += TwoBodyTerm1D(
        ["td", "ta"], 1, strength="Jt", prefactor=+1, has_obc=has_obc
    )
    model += TwoBodyTerm1D(
        ["ta", "td"], 1, strength="Jt", prefactor=+1, has_obc=has_obc
    )

    # triplet-triplet interaction and h.c.
    model += TwoBodyTerm1D(
        ["tdta", "tdta"], 1, strength="chi", prefactor=-1, has_obc=has_obc
    )

    # singlet-triplet conversion and h.c.
    model += TwoBodyTerm1D(
        ["td", "tdsa"], 1, strength="gamma", prefactor=+1, has_obc=has_obc
    )
    model += TwoBodyTerm1D(
        ["tdsa", "td"], 1, strength="gamma", prefactor=+1, has_obc=has_obc
    )
    model += TwoBodyTerm1D(
        ["sdta", "ta"], 1, strength="gamma", prefactor=+1, has_obc=has_obc
    )
    model += TwoBodyTerm1D(
        ["ta", "sdta"], 1, strength="gamma", prefactor=+1, has_obc=has_obc
    )

    return model, sf_ops


def get_singlet_fission_1d_phonons(has_obc=True):
    # pylint: disable=anomalous-backslash-in-string
    """
    Return singlet fission model accounting for exciton-phonon interactions
    and its operators in one dimension for open boundary conditions.

    exciton-phonon arrangement:

    ei = exciton virtual site i
    pj = phonon virtual site j

    .. code-block::

        e1 - e2 - e3 - ..... - eN -
         \   /\   /\   /   \  /  \  /
           p1   p2   p3 ... pN-1  pN

    **Arguments**

    has_obc : bool or list of bools, optional
        Defines the boundary condition along each spatial dimension.
        If scalar is given, the boundary condition along each
        spatial dimension is assumed to be equal.
        Default to True

    **Returns**

    model : instance of :class:`QuantumModel`
        Contains the Hamiltonian of the system.

    sf_ops : instance of :class:`TNOperators`
        Contains the operators required for the singlet fission model.

    **Details**

    The singlet fission model comes with 13 parameters to be defined,
    - the system size `L`,
    - the local singlet energy `Es`,
    - the local triplet energy `Et`,
    - the singlet hopping coupling `Js`,
    - the triplet hopping coupling `Jt`,
    - the triplet-triplet exchange interaction `chi`,
    - the phonons local energy `w0`,
    - the singlet-phonon coupling `gs`,
    - the triplet-phonon coupling `gt`,
    - the singlet-triplet-phonon `gamma`,
    - the phonon displacement offset x0 multiplied by gamma `gamma_x0`,
    - the phonon excitation rate `k_plus`,
    - the phonon relaxation rate `k_minus`,
    These need to be defined in the simulation dictionary.

    The model also inherits the following parameters from TNBosonicOperators()
    - the minimum fock space dimension `fock_space_nmin`,
    - the maximum fock space dimension `fock_space_nmax`,
    """

    # ----- operators -----

    # create exciton operators
    ex_ops = TNOperators()

    # identity matrix
    ex_ops["id"] = np.eye(3)

    # singlet and triplet dagger
    ex_ops["sd"] = np.array([[0, 0, 0], [1.0, 0, 0], [0, 0, 0]])
    ex_ops["td"] = np.array([[0, 0, 0], [0, 0, 0], [1.0, 0, 0]])

    # singlet and triplet annihilation
    ex_ops["sa"] = np.transpose(ex_ops["sd"])
    ex_ops["ta"] = np.transpose(ex_ops["td"])

    # triplet dagger - triplet annihilation and h.c.
    ex_ops["tdta"] = np.dot(ex_ops["td"], ex_ops["ta"])
    ex_ops["tatd"] = np.dot(ex_ops["ta"], ex_ops["td"])

    # singlet dagger - triplet annihilation and h.c.
    ex_ops["sdta"] = np.array([[0, 0, 0], [0, 0, 1], [0, 0, 0.0]])
    ex_ops["tdsa"] = np.array([[0, 0, 0], [0, 0, 0], [0, 1, 0.0]])

    # number operator singlet and triple
    ex_ops["ns"] = np.diag([0, 1.0, 0])
    ex_ops["nt"] = np.diag([0, 0, 1.0])

    # symmetry generator 2ns + nt (never used)
    ex_ops["sym_gen"] = 2 * ex_ops["ns"] + ex_ops["nt"]

    # define phonon (bosonic) operators
    # ---------------------------
    ph_ops = qtl.operators.TNBosonicOperators()

    # combine exciton-boson operators
    # every operator will have the key ex_ops.ph_ops
    sf_ops = qtl.operators.TNCombinedOperators(ex_ops, ph_ops)

    # ----- model -----

    # model name
    model_name = "singlet_fission_1d_with_phonons"

    # create quantum model with length L
    model = QuantumModel(1, "L", name=model_name)

    # local singlet energy
    model += LocalTerm("ns.id", strength="Es")

    # local triplet energy
    model += LocalTerm("nt.id", strength="Et")

    # hopping singlets and h.c.
    model += TwoBodyTerm1D(
        ["sd.id", "sa.id"], 1, strength="Js", prefactor=+1, has_obc=has_obc
    )
    model += TwoBodyTerm1D(
        ["sa.id", "sd.id"], 1, strength="Js", prefactor=+1, has_obc=has_obc
    )

    # hopping triplets and h.c.
    model += TwoBodyTerm1D(
        ["td.id", "ta.id"], 1, strength="Jt", prefactor=+1, has_obc=has_obc
    )
    model += TwoBodyTerm1D(
        ["ta.id", "td.id"], 1, strength="Jt", prefactor=+1, has_obc=has_obc
    )

    # triplet-triplet interaction and h.c.
    model += TwoBodyTerm1D(
        ["tdta.id", "tdta.id"], 1, strength="chi", prefactor=-1, has_obc=has_obc
    )

    # phonons local energy
    model += LocalTerm("id.n", strength="w0")

    # exciton-phonon couplings

    # singlet i with phonon i
    model += TwoBodyTerm1D(
        ["ns.bdagger", "id.id"], 1, strength="gs", prefactor=+1, has_obc=has_obc
    )
    model += TwoBodyTerm1D(
        ["ns.b", "id.id"], 1, strength="gs", prefactor=+1, has_obc=has_obc
    )
    # singlet i with phonon i+1
    model += TwoBodyTerm1D(
        ["id.bdagger", "ns.id"], 1, strength="gs", prefactor=+1, has_obc=has_obc
    )
    model += TwoBodyTerm1D(
        ["id.b", "ns.id"], 1, strength="gs", prefactor=+1, has_obc=has_obc
    )
    # triplet i with phonon i
    model += TwoBodyTerm1D(
        ["nt.bdagger", "id.id"], 1, strength="gt", prefactor=+1, has_obc=has_obc
    )
    model += TwoBodyTerm1D(
        ["nt.b", "id.id"], 1, strength="gt", prefactor=+1, has_obc=has_obc
    )
    # triplet i with phonon i+1
    model += TwoBodyTerm1D(
        ["id.bdagger", "nt.id"], 1, strength="gt", prefactor=+1, has_obc=has_obc
    )
    model += TwoBodyTerm1D(
        ["id.b", "nt.id"], 1, strength="gt", prefactor=+1, has_obc=has_obc
    )

    # singlet-triplet coupling mediated by phonons
    model += TwoBodyTerm1D(
        ["td.bdagger", "tdsa.id"], 1, strength="gamma", prefactor=+1, has_obc=has_obc
    )
    model += TwoBodyTerm1D(
        ["td.b", "tdsa.id"], 1, strength="gamma", prefactor=+1, has_obc=has_obc
    )
    model += TwoBodyTerm1D(
        ["td.id", "tdsa.id"], 1, strength="gamma_x0", prefactor=+1, has_obc=has_obc
    )
    model += TwoBodyTerm1D(
        ["tdsa.bdagger", "td.id"], 1, strength="gamma", prefactor=+1, has_obc=has_obc
    )
    model += TwoBodyTerm1D(
        ["tdsa.b", "td.id"], 1, strength="gamma", prefactor=+1, has_obc=has_obc
    )
    model += TwoBodyTerm1D(
        ["tdsa.id", "td.id"], 1, strength="gamma_x0", prefactor=+1, has_obc=has_obc
    )
    model += TwoBodyTerm1D(
        ["sdta.bdagger", "ta.id"], 1, strength="gamma", prefactor=+1, has_obc=has_obc
    )
    model += TwoBodyTerm1D(
        ["sdta.b", "ta.id"], 1, strength="gamma", prefactor=+1, has_obc=has_obc
    )
    model += TwoBodyTerm1D(
        ["sdta.id", "ta.id"], 1, strength="gamma_x0", prefactor=+1, has_obc=has_obc
    )
    model += TwoBodyTerm1D(
        ["ta.bdagger", "sdta.id"], 1, strength="gamma", prefactor=+1, has_obc=has_obc
    )
    model += TwoBodyTerm1D(
        ["ta.b", "sdta.id"], 1, strength="gamma", prefactor=+1, has_obc=has_obc
    )
    model += TwoBodyTerm1D(
        ["ta.id", "sdta.id"], 1, strength="gamma_x0", prefactor=+1, has_obc=has_obc
    )

    # incoherent phonon exciatation and relaxation
    model += LindbladTerm("id.bdagger", strength="k_plus")
    model += LindbladTerm("id.b", strength="k_minus")

    return model, sf_ops
