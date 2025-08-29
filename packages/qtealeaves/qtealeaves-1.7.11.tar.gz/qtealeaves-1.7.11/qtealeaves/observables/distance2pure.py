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
Distance observable will measure the distance of the quantum system
to one or more pure states defined within this observable as filenames.
We measure the overlap and return a complex number <phi | psi>.
"""


import numpy as np

from qtealeaves.tooling import QTeaLeavesError

from .tnobase import _TNObsBase

__all__ = ["TNDistance2Pure"]


class TNDistance2Pure(_TNObsBase):
    """
    Distance observable will measure the distance of the quantum system
    to one or more pure states defined within this observable as filenames.
    We measure the overlap and return a complex number
    :math:`\\rangle\\phi | \\psi\\langle`.

    **Arguments**

    name : str
        Define a label under which we can find the observable in the
        result dictionary.

    path_to_state : str
        Filename to the state. The default extension for formatted
        Fortran TTNs is ``.ttn`` and for unformatted Fortran TTNs
        is ``.ttnbin``. Other file extension might be added.
    """

    def __init__(self, name, path_to_state):
        super().__init__(name)
        self.path_to_state = [path_to_state]

        self.check_extension(path_to_state)

        self.measurable_ansaetze = ("MPS", "TTN", "TTO", "ATTN", "STATE")

    @classmethod
    def empty(cls):
        """
        Documentation see :func:`_TNObsBase.empty`.
        """
        obj = cls("x", "x.ttn")
        obj.name = []
        obj.path_to_state = []

        return obj

    def __len__(self):
        """
        Provide appropriate length method.
        """
        return len(self.name)

    def __iadd__(self, other):
        """
        Documentation see :func:`_TNObsBase.__iadd__`.
        """
        if isinstance(other, TNDistance2Pure):
            self.name += other.name
            self.path_to_state += other.path_to_state
        else:
            raise QTeaLeavesError("__iadd__ not defined for this type.")

        return self

    def write_results(self, fh, state_ansatz, **kwargs):
        """
        See :func:`_TNObsBase.write_results`.
        """
        is_measured = self.check_measurable(state_ansatz)

        # Write separator first
        fh.write("-" * 20 + "tndistance2pure\n")
        # Assignment for the linter
        _ = fh.write("T \n") if is_measured else fh.write("F \n")

        if is_measured:
            for name_ii in self.name:
                real_part = np.real(self.results_buffer[name_ii])
                imag_part = np.imag(self.results_buffer[name_ii])
                fh.write(str(real_part) + "," + str(imag_part) + "\n")

            self.results_buffer = {}

    def read(self, fh, **kwargs):
        """
        Read distance observables from standard formatted fortran output.

        fh : filehandle
            Read the information about the measurements from this filehandle.
        """
        # First line is separator
        _ = fh.readline()
        is_meas = fh.readline().replace("\n", "").replace(" ", "")
        is_measured = is_meas == "T"

        for name_ii in self.name:
            if is_measured:
                str_value = fh.readline()
                value_real, value_complex = str_value.split(",")

                yield name_ii, float(value_real) + 1j * float(value_complex)
            else:
                yield name_ii, None

    @staticmethod
    def check_extension(path_to_state):
        """
        Check that the file uses a valid file extension at least readable
        by some simulation.
        """
        if "." not in path_to_state:
            raise QTeaLeavesError("No file extension detected.")

        file_extension = path_to_state.split(".")[-1]

        if file_extension not in ["ttn", "ttnbin", "pklttn", "mps", "pklmps"]:
            raise QTeaLeavesError(
                f"Unknown extension for pure state: {file_extension}."
            )
