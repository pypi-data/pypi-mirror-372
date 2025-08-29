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
Observable to save the tensors forming the final MPS
"""

from qtealeaves.tooling import QTeaLeavesError

from .tnobase import _TNObsBase

__all__ = ["TNState2File"]


class TNState2File(_TNObsBase):
    """
    Write the state to a file.

    We stress that saving the state to a file will enable to
    further measure observables, since you will have available
    all the informations you had at the end of the simulation.

    .. warning::
        While saving the state can be useful, it can really slow
        down the evolution when it is saved at each time-step of
        a time evolution. Please use this observable carefully!
        Reference to the description on the backend for more
        specific informations.

    **Arguments**

    name : str
        Filename to save the state.

    formatting : char
        Specifies format, i.e., 'F' for formatted, 'U' for
        unformatted, or 'D' for formatted without symmetries.
        On the python backend, U is pickled, F is formatted
        D is converted to dense tensor and pickled (especially
        the last on is different from fortran, where the dense
        TN is stored as formatted file).
    """

    def __init__(self, name, formatting):
        super().__init__(name)
        self.formatting = [formatting]
        self.measurable_ansaetze = ("MPS", "TTN", "TTO", "ATTN", "LPTN", "STATE")

    @classmethod
    def empty(cls):
        """
        Documentation see :func:`_TNObsBase.empty`.
        """
        obj = cls("x", "F")
        obj.name = []
        obj.formatting = []

        return obj

    def __len__(self):
        """
        Provide an appropriate length method.
        """
        return len(self.name)

    def __iadd__(self, other):
        """
        Documentation see :func:`_TNObsBase.__iadd__`.
        """
        if isinstance(other, TNState2File):
            self.name += other.name
            self.formatting += other.formatting
        else:
            raise QTeaLeavesError("__iadd__ not defined for this type.")

        return self

    def add_trajectories(self, all_results, new):
        """
        Documentation see :func:`_TNObsBase.add_trajectories`.
        Here, we generate a list of filenames.
        """
        for name in self.name:
            if name not in all_results:
                all_results[name] = [new[name]]
            else:
                all_results[name].append(new[name])
        return all_results

    def avg_trajectories(self, all_results, num_trajectories):
        """
        Documentation see :func:`_TNObsBase.avg_trajectories`.
        Here, we return the list of filenames as is, no action possible
        for averaging.
        """
        return all_results

    def write_results(self, fh, state_ansatz, **kwargs):
        """
        See :func:`_TNObsBase.write_results`.
        """
        is_measured = self.check_measurable(state_ansatz)

        # Write separator first
        fh.write("-" * 20 + "tnstate2file\n")
        # Assignment for the linter
        _ = fh.write("T \n") if is_measured else fh.write("F \n")

        for name_ii in self.name:
            fh.write(self.results_buffer[name_ii] + "\n")

        self.results_buffer = {}

    def read(self, fh, **kwargs):
        """
        Read file observable from standard formatted fortran output.

        **Arguments**

        fh : filehandle
            Read the information about the measurements from this filehandle.

        params : dict (in kwargs)
            The parameter dictionary, which is required to obtain
            the output folder. It is required to evaluate
            callable etc. used in ``self.name``.
        """
        params = kwargs.get("params")

        # First line is separator
        _ = fh.readline()
        is_meas = fh.readline().replace("\n", "").replace(" ", "")
        is_measured = is_meas == "T"

        for elem in self.name:
            if is_measured:
                filename = self.eval_str_param(elem, params)
                filename_final = fh.readline().strip()

                yield filename, filename_final

            else:
                filename = self.eval_str_param(elem, params)
                yield filename, None
