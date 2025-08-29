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
Abstract base class for observables.
"""

from qtealeaves.tooling import QTeaLeavesError
from qtealeaves.tooling.parameterized import _ParameterizedClass

__all__ = ["_TNObsBase"]


class _TNObsBase(_ParameterizedClass):
    """
    Abstract base class for observables.

    Attributes
    ----------
    name: str
        Name to identify the observable
    results_buffer : dict
        Store the results of the measurement of the observable
    measurable_ansaetze : tuple(str)
        Tuple of ansatzes for which this observable is measurable
    """

    measurable_ansaetze = ()

    def __init__(self, name, *args, **kwargs):
        self.name = [name]
        self.results_buffer = {}

    def check_measurable(self, tn_type_label):
        """
        Checks wether or not the observable can be measured for a given ansatz.

        Args:
            tn_type_label (str): Label of the TN ansatz
        """
        assert isinstance(tn_type_label, str), "tn_type_label must be a string"
        return tn_type_label in self.measurable_ansaetze

    @classmethod
    def empty(cls):
        """
        Constructor of the class without any content.
        """
        raise NotImplementedError("Must be implemented by actual class.")

    def __iadd__(self, other):
        """
        Overwrite operator ``+=`` to simplify syntax.
        """
        raise NotImplementedError("Must be implemented by actual class.")

    def add_trajectories(self, all_results, new):
        """
        Add the observables for different quantum trajectories.

        **Arguments**

        all_results : dict
            Dictionary with observables.

        new : dict
            Dictionary with new observables to add to all_results.
        """
        for name in self.name:
            if name not in all_results:
                all_results[name] = new[name]

                if isinstance(new[name], dict):
                    raise QTeaLeavesError("Dictionary addition not implemented.")
            else:
                all_results[name] += new[name]
        return all_results

    def avg_trajectories(self, all_results, num_trajectories):
        """
        Get the average of quantum trajectories observables.

        **Arguments**

        all_results : dict
            Dictionary with observables.

        num_trajectories : int
            Total number of quantum trajectories.
        """
        for name in self.name:
            if isinstance(all_results[name], dict):
                raise QTeaLeavesError("Dictionary addition not implemented.")
            all_results[name] /= num_trajectories
        return all_results

    def write_results(self, fh, state_ansatz, **kwargs):
        """
        Write the actual results to a file mocking the fortran output.
        Therefore, the results have to be stored in the result buffer.

        **Arguments**

        fh : filehandle
            Open filehandle where the results are written to.
        state_ansatz : str
            Label identifying the state ansatz currently in use.
        """
        is_measured = self.check_measurable(state_ansatz)

        # Write separator line
        fh.write("-" * 20 + "\n")
        # Assignment for the linter
        _ = fh.write("T \n") if is_measured else fh.write("F \n")

        if is_measured:
            if len(self) == 0:
                self.results_buffer = {}
                return None
        else:
            return None

        raise QTeaLeavesError("Must be implemented by actual class for len > 0.")

    def read(self, fh, **kwargs):
        """
        The measurement outcomes are written by fortran and we read them
        within this method. If the format how the measurements are written
        changes on the fortran side, this method must be adapted.
        """
        fh.readline()  # separator

        raise NotImplementedError("Must be implemented by actual class.")

    def read_hdf5(self, dataset, params):
        """
        Documentation see :func:`_TNObsBase.read_hdf5`.

        **Arguments**

        dataset : h5py dataset
            The dataset to be read out of.
        params  : parameter dictionary
            Unused for now (Dec 2023)
        """
        raise QTeaLeavesError("This observables cannot read HDF5 files yet.")

    def __repr__(self):
        """
        Return the class name as representation.
        """
        return self.__class__.__name__

    def collect_operators(self):
        """
        Observables which require operators must provide this method,
        because operators with symmetries might not be written
        otherwise.

        **Details**

        The problems are, for example, correlations with equal operators
        because they cannot be contracted over their third link.
        """
        return
        yield self

    def get_id(self):
        """
        Get the address in memory, which is useful instead of hashing
        the complete object or for comparisons.
        """
        return hex(id(self))
