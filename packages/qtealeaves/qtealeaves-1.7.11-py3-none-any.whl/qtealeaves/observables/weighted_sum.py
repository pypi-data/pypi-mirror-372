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
Observable to measure the weighted sum of tensor product observables
"""

import warnings

import numpy as np

from qtealeaves.mpos import ITPO, DenseMPO, DenseMPOList, MPOSite
from qtealeaves.tooling import QTeaLeavesError

from .tensor_product import TNObsTensorProduct
from .tnobase import _TNObsBase

__all__ = ["TNObsWeightedSum"]


class TNObsWeightedSum(_TNObsBase):
    r"""
    Class to measure observables which is the weighted sum of tensor product,
    which means of the type

    .. math::

        O = \sum_{i=0}^m \alpha_i\left( o_1^i\otimes o_2^i \otimes \dots \otimes o_n^i
        \right)

    where :math:`m` is the number of addends and :math:`n` the number of sites.
    For further informations about the single observable
    :math:`O_i=o_1^i\otimes o_2^i \otimes \dots \otimes o_n^i` see the documentation
    of :class:`TNObsTensorProduct`.

    The output of the measurement will be a dictionary where:

    - The key is the `name` of the observable
    - The value is its expectation value

    An example of this observable are Pauli decompositions of Hamiltonian, i.e.
    Hamiltonians written as a weighted sum of tensor product operators formed
    by Pauli matrices.
    They are usually used in the Quantum chemistry applications, such as
    the Variational Quantum Eigensolver.

    Parameters
    ----------
    name: str
        Name to identify the observable
    tp_operators: :class:`TNObsTensorProduct`
        Tensor product observables. Its length, i.e. the number of tensor product
        observables contained in it, should be the same of the number of complex
        coefficients.
    coeffs: list of complex
        Coefficients of the weighted sum for each tp_operators
    use_itpo: bool, optional
        If True, measure using ITPO. Default to False. Consumed in python.

    """

    def __init__(self, name, tp_operators, coeffs, use_itpo=False):
        if np.isscalar(coeffs):
            coeffs = [coeffs]
        self.tp_operators = [tp_operators]
        self.coeffs = [coeffs]
        self.use_itpo = use_itpo

        _TNObsBase.__init__(self, name)
        self.measurable_ansaetze = ("MPS", "TTN", "TTO", "ATTN")

    @classmethod
    def empty(cls):
        """
        Documentation see :func:`_TNObsBase.empty`.
        """
        obj = cls(None, None, None)
        obj.name = []
        obj.tp_operators = []
        obj.coeffs = []
        obj.use_itpo = True

        return obj

    def __len__(self):
        """
        Provide appropriate length method
        """
        return len(self.name)

    def __iadd__(self, other):
        """
        Documentation see :func:`_TNObsBase.__iadd__`.
        """
        if isinstance(other, TNObsWeightedSum):
            self.name += other.name
            self.tp_operators += other.tp_operators
            self.coeffs += other.coeffs
            self.use_itpo = self.use_itpo and other.use_itpo
        else:
            raise QTeaLeavesError("__iadd__ not defined for this type.")

        return self

    @classmethod
    def from_pauli_string(cls, name, pauli_string, use_itpo=False):
        """
        Initialize the observable from a qiskit chemistry pauli string format.
        First, outside of the function use the WeightedPauliOperator method to_dict()
        and then give that dict as input to this function

        Parameters
        ----------
        name: str
            Name of the observable
        pauli_string: dict
            Dictionary of pauli strings
        use_itpo: bool, optional
            If True, measure using ITPO. Default to False. Consumed in python.

        Returns
        -------
        TNObsWeightedSum
            The weighted sum observable initialized from the pauli dictionary
        """
        assert (
            "paulis" in pauli_string.keys()
        ), "Dictionary is not in pauli string format"

        addends = pauli_string["paulis"]

        coeffs = []
        tp_operators = TNObsTensorProduct.empty()
        # First, we look at each term in the weighted sum
        for term in addends:
            string = term["label"]
            coef = term["coeff"]["real"] + 1j * term["coeff"]["imag"]
            operators = []
            sites = []
            for idx, pauli in enumerate(string):
                if pauli != "I":
                    operators.append(pauli)
                    sites.append([idx])
            if len(sites) == 0:
                operators.append("I")
                sites.append([0])
            tp_operators += TNObsTensorProduct(string, operators, sites)

            coeffs += [coef]

        obs_wt = cls(name, tp_operators, coeffs, use_itpo)

        return obs_wt

    def to_itpo(self, operators, tensor_backend, num_sites):
        """
        Return an ITPO represented the weighted sum observable

        Parameters
        ----------
        operators: TNOperators
            The operator class
        tensor_backend: instance of `TensorBackend`
            Tensor backend of the simulation
        num_sites: int
            Number of sites in the state to be measures

        Returns
        -------
        ITPO
            The ITPO class
        """
        dense_mpo_list = DenseMPOList()

        # Cycle over weighted sum observables
        for coeffs, tp_ops in zip(self.coeffs, self.tp_operators):
            if isinstance(tp_ops, list):
                tp_ops = tp_ops[0]
            # Cycle over the TPO of a single weighted sum
            for ops, sites, coef in zip(tp_ops.operators, tp_ops.sites, coeffs):
                mpo_sites_list = []
                # Cycle over the different operators in a single TPO
                for op_ii, site_ii in zip(ops, sites):
                    mpo_sites_list.append(
                        MPOSite(
                            site_ii[0], op_ii, 1.0, coef, operators=operators, params={}
                        )
                    )

                    # iTPO has local weights, need to set to one after first term
                    coef = 1.0
                dense_mpo = DenseMPO(mpo_sites_list, tensor_backend=tensor_backend)
                dense_mpo_list.append(dense_mpo)
                if len(dense_mpo) > 0:
                    warnings.warn("Adding length zero MPO to dense MPO list.")

        # Sites are not ordered and we have to make links match anyways
        dense_mpo_list = dense_mpo_list.sort_sites()
        itpo = ITPO(num_sites)
        itpo.add_dense_mpo_list(dense_mpo_list)
        itpo.set_meas_status(do_measurement=True)

        return itpo

    def read(self, fh, **kwargs):
        """
        Read the measurements of the correlation observable from fortran.

        Parameters
        ----------

        fh : filehandle
                Read the information about the measurements from this filehandle.
        """
        fh.readline()  # separator
        is_meas = fh.readline().replace("\n", "").replace(" ", "")
        is_measured = is_meas == "T"

        for name in self.name:
            if is_measured:
                value = fh.readline().replace("\n", "").replace(" ", "")
                value = np.array(value.split(","), dtype=float)

                yield name, value[0] + 1j * value[1]
            else:
                yield name, None

    def write_results(self, fh, state_ansatz, **kwargs):
        """
        See :func:`_TNObsBase.write_results`.
        """
        is_measured = self.check_measurable(state_ansatz)

        # Write separator first
        fh.write("-" * 20 + "tnobsweightedsum\n")
        # Assignment for the linter
        _ = fh.write("T \n") if is_measured else fh.write("F \n")

        if is_measured:
            for name_ii in self.name:
                fh.write(f"{np.real(self.results_buffer[name_ii])}, ")
                fh.write(f"{np.imag(self.results_buffer[name_ii])} \n")
