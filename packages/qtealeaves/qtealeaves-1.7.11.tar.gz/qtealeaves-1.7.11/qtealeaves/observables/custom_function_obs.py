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
Observable to measure any quantity with a custom function
"""

import json

from qtealeaves.tooling import QTeaLeavesError

from ..simulation.tn_simulation import TN_TYPE_LABEL
from .tnobase import _TNObsBase

__all__ = ["TNCustomFunctionObs"]


class TNCustomFunctionObs(_TNObsBase):
    """
    Custom observable for tensor network measurements
    that are not part of the standard set of observables.
    In addition to the name of the observable, the user
    must provide a custom function to perform the
    measurement. Moreover, this observable is Json serializable.
    """

    def __init__(self, name, function, func_kwargs, measurable_ansaetze=None):
        _TNObsBase.__init__(self, name)
        self.function = [function]
        self.func_kwargs = [func_kwargs]

        if measurable_ansaetze is None:
            # defaults to all the ansaetze
            self.measurable_ansaetze = set(TN_TYPE_LABEL.values())
        else:
            # otherwise, set explicitly
            self.measurable_ansaetze = measurable_ansaetze

    def __iadd__(self, other):
        """
        Documentation see :func:`_TNObsBase.__iadd__`.
        """
        if isinstance(other, TNCustomFunctionObs):
            self.name += other.name
            self.function += other.function
            self.func_kwargs += other.func_kwargs
        else:
            raise QTeaLeavesError("__iadd__ not defined for this type.")

        return self

    @classmethod
    def empty(cls):
        """
        Documentation see :func:`_TNObsBase.empty`.
        """
        obj = cls(None, None, None)
        obj.name = []
        obj.function = []
        obj.func_kwargs = []

        return obj

    def read(self, fh, **kwargs):
        """
        Read the measurements of the observable.

        Parameters
        ----------

        fh : filehandle
            Read the information about the measurements from this filehandle.
        """
        json_dict = json.load(fh)
        self.results_buffer = {}
        for name_ii, res_ii in json_dict["measurements"].items():
            self.name.append(name_ii)
            self.results_buffer[name_ii] = res_ii

        return list(zip(self.results_buffer.keys(), self.results_buffer.values()))

    def write_results(self, fh, state_ansatz, **kwargs):
        """
        Write the actual results to a file mocking the fortran output.
        Therefore, the results have to be stored in the result buffer.

        Parameters
        ----------

        fh : filehandle
            Open filehandle where the results are written to.
        is_measured : bool
            If True, the backend can measure the observable
        """
        is_measured = self.check_measurable(state_ansatz)

        # Dictionary to store the results
        ress = {}
        ress["is_measured"] = is_measured
        ress["measurements"] = {}
        if is_measured:
            for name_ii in self.name:
                ress["measurements"][name_ii] = self.results_buffer[name_ii]

        # Write the results to the file
        json.dump(ress, fh)


def bond_dimension(state, func_kwargs=None):
    """
    Measure any bond dimension in an MPS.
    Default is the maximum bond dimension.

    Parameters
    ----------
    state : MPS
        The MPS state to measure the bond dimension for.
    func_kwargs : dict, optional
        Additional arguments to pass to the function.
        func_kwargs["bond"]: int, optional
            The bond dimension to measure.
            Default is None, which means the maximum bond dimension.

    Returns
    -------
    int
        The requested bond dimension of the MPS.
    """
    if func_kwargs is None:
        return state.current_max_bond_dim
    raise NotImplementedError(
        "The requested bond dimension measurement is not implemented yet."
    )
