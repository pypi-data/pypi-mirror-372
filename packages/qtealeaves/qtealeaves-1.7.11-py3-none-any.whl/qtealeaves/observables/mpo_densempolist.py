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
The observable for the energy variance.
"""

from qtealeaves.mpos import DenseMPOList
from qtealeaves.tooling import QTeaLeavesError

from .tnobase import _TNObsBase

__all__ = ["TNObsDenseMPOList", "TNObsVarE"]


class TNObsDenseMPOList(_TNObsBase):
    """
    The measurement of an MPO defined via the iterators of :class:`DenseMPOList`s.

    Arguments
    ---------

    name : str
        Name of how to find the observable in the result dictionary.

    iterator : iterator
        Yields one or multiple :class:`DenseMPOList`s which represent together
        the MPO. The iteration option is given to reduce the memory costs of
        large MPOs. Iterators has to be able to take the params dictionary
        and the operators as arguments. No other arguments will be given.
    """

    def __init__(self, name, iterator):
        super().__init__(name)
        self.measurable_ansaetze = ("MPS", "TTN", "TTO", "ATTN")
        self.iterators = [iterator]
        self.is_energy_var = [False]

    @classmethod
    def empty(cls):
        """
        Documentation see :func:`_TNObsBase.empty`.
        """
        obj = cls(None, None)
        obj.name = []
        obj.iterators = []
        obj.is_energy_var = []

        return obj

    def __iadd__(self, other):
        """
        Documentation see :func:`_TNObsBase.__iadd__`.
        """
        if isinstance(other, TNObsDenseMPOList):
            self.name += other.name
            self.iterators += other.iterators
            self.is_energy_var += other.is_energy_var
        else:
            raise QTeaLeavesError("__iadd__ not defined for this type.")

        return self

    def read(self, fh, **kwargs):
        """
        Read the measurements of the MPO observable from result file.

        **Arguments**

        fh : filehandle
            Read the information about the measurements from this filehandle.
        """
        # First line is separator
        _ = fh.readline()
        is_meas = fh.readline().replace("\n", "").replace(" ", "")
        is_measured = is_meas == "T"

        if is_measured:
            for result_key in self.name:
                self.results_buffer[result_key] = float(fh.readline())
                yield result_key, self.results_buffer[result_key]
        else:
            for result_key in self.name:
                yield result_key, None

    def write_results(self, fh, state_ansatz, **kwargs):
        """
        See :func:`_TNObsBase.write_results`.
        """
        is_measured = self.check_measurable(state_ansatz)

        # Write separator first
        fh.write("-" * 20 + "tnobsmpo\n")
        # Assignment for the linter
        _ = fh.write("T \n") if is_measured else fh.write("F \n")

        if is_measured:
            for res_key in self.name:
                fh.write(str(self.results_buffer[res_key]) + "\n")
            self.results_buffer = {}


class TNObsVarE(TNObsDenseMPOList):
    """
    The variance observable measures the energy variance
    VarE = <H^2> - <H>^2. The observable vanishes when a given state
    is the eigenstate of the Hamiltonian, therefore it is used to estimate
    how close a given state is to an eigenstate of a Hamiltonian.
    For example, it can estimate how correct is the DMRG groundstate with
    respect to an actual (unknown) groundstate.

    The result is stored in the output result dictionary under the key "var".

    Arguments
    ---------

    model : :class:`QuantumModel`
        Contains the Hamiltonian. We assume it is equal to the system's
        Hamiltonian which is used when subtracting the energy of the current
        state to calculate the variance. If you need to calculate the variance
        of any Hamiltonian, calculate `<H^2>` and `<H>^2` via two MPO
        measurements.

    tensor_backend : :class:`TensorBackend`
        Tensor backend needed to instantiate DenseMPOList.

    batch_size : int | None, optional
        Due to heavy memory requirements, the batch size can specify how
        many MPO terms go into a sub MPO.
        Default to None (all at once)

    print_progress : bool, optional
        Allows to print progress before starting a batch. For monitoring progress
        due to heavy computation.
        Default to False

    Warning
    -------

    This measurement is expensive as it goes via the iTPO. If there are `N`
    terms in the Hamiltonian, there are `N**2` terms necessary for the measurement
    of the variance.
    """

    def __init__(self, model, tensor_backend, batch_size=None, print_progress=False):

        # pylint: disable-next=too-many-arguments
        def var_iterator(
            params,
            operators,
            model=model,
            tensor_backend=tensor_backend,
            batch_size=batch_size,
            print_progress=print_progress,
        ):
            # We will need all combinations of the operators (can be called
            # multiple times without generating 4th order etc).
            operators.generate_products_2nd_order()

            ham = DenseMPOList.from_model(model, params, tensor_backend=tensor_backend)
            ham.initialize(operators, params)

            # pylint: disable-next=protected-access
            yield from ham._mpo_product_iter(
                ham, operators, batch_size=batch_size, print_progress=print_progress
            )

        super().__init__("var", var_iterator)
        self.measurable_ansaetze = ("MPS", "TTN", "TTO", "ATTN")
        self.is_energy_var = [True]

    def __repr__(self):
        return TNObsDenseMPOList.empty().__class__.__name__
