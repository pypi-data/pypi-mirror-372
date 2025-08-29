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
Observable to measure the logarithmic negativity of the system
"""

from qtealeaves.tooling import QTeaLeavesError

from .tnobase import _TNObsBase

__all__ = ["TNObsLogNegativity"]


class TNObsLogNegativity(_TNObsBase):
    """
    Observable to enable the measurement of the logarithmic negativity.

    The output of the measurement will be a dictionary, where the keys are
    a continous range of sites which form the first bipartition.
    For example, the continuous range (2, 3) has the bipartitions [2, 3] vs
    [0, 1, 4, 5, 6, 7] for a system of 8 sites. Indices are python indices starting at zero.

    There are different measurement modes, dtermining which partitions are measured.
    Available are:
    - "H": only the left (right) half of the system.
    - "L": all available partitions that overlab with the left boundary of the system.
    - "R": all available partitions that overlab with the right boundary of the system
    - "LR": the combination of "L" and "R".
    - "A": all partitons native in the TTO.
    Default to "H".

    """

    def __init__(self, mode="H"):
        _TNObsBase.__init__(self, "log_negativity")
        self.measurable_ansaetze = "TTO"
        self.mode = [mode.upper()]

    def __iadd__(self, other):
        """
        Documentation see :func:`_TNObsBase.__iadd__`.
        If you add another log negativity observable, it will overwrite the previous one.
        """
        if isinstance(other, TNObsLogNegativity):
            self.name = other.name
            self.mode = other.mode
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
        obj.mode = []

        return obj

    def read(self, fh, **kwargs):
        """
        Read the measurement observable.

        Parameters
        ----------

        fh : filehandle
            Read the information about the measurements from this filehandle.
        """
        fh.readline()  # separator
        is_meas = fh.readline().replace("\n", "").replace(" ", "")
        is_measured = is_meas == "T"

        if is_measured:
            num_log_neg = int(fh.readline().replace("\n", ""))
            for ii in range(num_log_neg):
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
            self.results_buffer["lognegativity"] = None

        return list(zip(self.results_buffer.keys(), self.results_buffer.values()))

    def write(self, fh, **kwargs):
        """
        Write observable to file.

        Parameters
        ----------

        fh : filehandle
            Write the information about the measurements to this filehandle.
        """

        str_buffer = "------------------- lognegativity\n"
        str_buffer += "%d\n" % (len(self.name))

        fh.write(str_buffer)

        return

    def write_results(self, fh, state_ansatz, **kwargs):
        """
        See :func:`_TNObsBase.write_results`.
        """
        is_measured = self.check_measurable(state_ansatz)

        # Write separator first
        fh.write("-" * 20 + "lognegativity\n")
        # Assignment for the linter
        _ = fh.write("T \n") if is_measured else fh.write("F \n")
        if is_measured:
            # Number of results
            buffer_str = ""
            num_log_negs = 0

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
                    num_log_negs += 1

                    buffer_str += f"{num_terms}\n"
                    buffer_str += sub_buffer

            fh.write(f"{num_log_negs}\n")
            if num_log_negs > 0:
                fh.write(buffer_str)
