# This code is part of tn_py_fronted.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
Observable to measure the bond entropy of the system
"""
import numpy as np

from qtealeaves.tooling import QTeaLeavesError

from .tnobase import _TNObsBase

__all__ = ["TNObsBondEntropy"]


class TNObsBondEntropy(_TNObsBase):
    """
    Observable to enable the measurement of the
    Von Neumann bond entropy at the end
    of a circuit. If the state is pure, than this
    measurement is equal to the entanglement. Otherwise
    it is not well defined.
    Given a quantum state of :math:`n` sites :math:`|\\psi\\rangle` the
    Von Neumann entropy of the bipartition :math:`A(B)` with :math:`n_{A(B)}`
    sites is defined as:

    .. math::
        S_V(\\rho_A) = -\\mathrm{Tr} \\rho_A\\ln(\\rho_A),
            \\quad \\rho_A=\\mathrm{Tr}_B\\left( |\\psi\\rangle\\langle\\psi|\\right)

    This value should be computed using the natural logarithm, i.e. the logarithm in
    base :math:`e`.

    The output of the measurement will be a dictionary, where:

    - As keys, we report on continous range of site which form the first bipartition.
      For example, the continuous range (4, 5) has the bipartitions [4, 5] vs
      [0, 1, 2, 3, 6, 7]. An MPS will define the first bipartitions in the
      different cuts as (0, 0), (0, 1), (0, 2), (0, 3), etc.
    - Indices are python indices starting at zero in the keys.
    - As value the result of :math:`S_V`. Natural log is used for both MPS and TTN.

    The expression above for the computation of the bond entropy is quite complex. Using
    tensor network we can strongly simplify it, using the singular values :math:`s_i`
    "stored" in the link. This is equivalent to look at the eigenvalues :math:`\\lambda_i`
    of the reduced density matrix :math:`\\rho_A` for a pure system like MPS and TTN:

    .. math::
        S_V(\\rho_A) = -\\sum_{i} \\lambda_i \\ln(\\lambda_i) = -\\sum_{i} s_i^2 \\ln(s_i^2)

    """

    def __init__(self):
        _TNObsBase.__init__(self, "bond_entropy")
        self.measurable_ansaetze = ("MPS", "TTN", "TTO", "ATTN")

    def __iadd__(self, other):
        """
        Documentation see :func:`_TNObsBase.__iadd__`.
        If you add another bond entropy observable, the observable that
        performs measurements more often is kept.
        """
        if isinstance(other, TNObsBondEntropy):
            self.name = list(np.unique(self.name + other.name))
        else:
            raise QTeaLeavesError("__iadd__ not defined for this type.")

        return self

    @classmethod
    def empty(cls):
        """
        Documentation see :func:`_TNObsBase.empty`.
        """
        obj = cls()
        obj.name = []

        return obj

    def read(self, fh, **kwargs):
        """
        Read the measurements of the projective measurement
        observable from fortran.

        Parameters
        ----------

        fh : filehandle
            Read the information about the measurements from this filehandle.
        """
        fh.readline()  # separator
        is_meas = fh.readline().replace("\n", "").replace(" ", "")
        is_measured = is_meas == "T"

        if is_measured:
            num_bond_entropy = int(fh.readline().replace("\n", ""))
            for ii in range(num_bond_entropy):
                res_key = self.name[0] + str(ii)
                self.results_buffer[res_key] = {}

                num_terms = int(fh.readline().replace("\n", ""))
                for _ in range(num_terms):
                    # Term written as
                    # Index of the first tensor, index of the second tensor, value
                    term = fh.readline().replace("\n", "").split(",")
                    term_idx = tuple((int(term[0]), int(term[1])))
                    term_value = float(term[2])
                    self.results_buffer[res_key][term_idx] = term_value
        else:
            self.results_buffer["bondentropy"] = None

        return list(zip(self.results_buffer.keys(), self.results_buffer.values()))

    def write_results(self, fh, state_ansatz, **kwargs):
        """
        See :func:`_TNObsBase.write_results`.
        """
        is_measured = self.check_measurable(state_ansatz)

        # Write separator first
        fh.write("-" * 20 + "tnobsbondentropy\n")
        # Assignment for the linter
        _ = fh.write("T \n") if is_measured else fh.write("F \n")
        if is_measured:
            # Number of results
            buffer_str = ""
            num_bond_entropies = 0

            for value in self.results_buffer.values():
                if value is None:
                    continue

                num_terms = 0
                sub_buffer = ""

                for subkey, subvalue in value.items():
                    if subvalue is None:
                        continue

                    num_terms += 1

                    # Index of the first tensor, index of the second tensor, value
                    sub_buffer += f"{subkey[0]}, {subkey[1]}, {subvalue}\n"

                if num_terms > 0:
                    num_bond_entropies += 1

                    buffer_str += f"{num_terms}\n"
                    buffer_str += sub_buffer

            fh.write(f"{num_bond_entropies}\n")
            if num_bond_entropies > 0:
                fh.write(buffer_str)
