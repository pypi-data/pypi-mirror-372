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
The time correlator measures the correlation ``<A_i(t=0) B_j(t)>`` during
a time evolution. The index `i` is fixed, while `j` is running over the
system size. It cannot be used for fermionic operators.
"""

import numpy as np

from qtealeaves.tooling import QTeaLeavesError

from .tnobase import _TNObsBase

__all__ = ["TNObsTZeroCorr"]


class TNObsTZeroCorr(_TNObsBase):
    """


    **Arguments**

    name : str
        Define a label under which we can finde the observable in
        the result dictionary.

    operator : list of two strings
        Identifiers/strings for the operators to be measured. The
        first operator is applied at `t=0`, the second at all `t`
        during measurements of the time evolution.

    site_idx : int
        Specify on which site the first operator should be measured
        on.
    """

    def __init__(self, name, operators, site_idx):
        super().__init__(name)
        self.measurable_ansaetze = ()
        self.operators = [operators]
        self.site_inds = [site_idx]

    @classmethod
    def empty(cls):
        """
        Documentation see :func:`_TNObsBase.empty`.
        """
        obj = cls(None, None, None)
        obj.name = []
        obj.operators = []
        obj.site_inds = []

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
        if isinstance(other, TNObsTZeroCorr):
            self.name += other.name
            self.operators += other.operators
            self.site_inds += other.site_inds
        else:
            raise QTeaLeavesError("__iadd__ not defined for this type.")

        return self

    def collect_operators(self):
        """
        Documentation see :func:`_TNObsBase.collect_operators`.
        """
        for elem in self.operators:
            yield (elem[0], "l")
            yield (elem[1], "r")

    def read(self, fh, **kwargs):
        """
        Read the measurements of the time correlator obsverable from fortran.

        **Arguments**

        fh : filehandle
            Read the information about the measurements from this filehandle.
        """
        # First line is separator
        _ = fh.readline()
        is_meas = fh.readline().replace("\n", "").replace(" ", "")
        is_measured = is_meas == "T"

        for elem in self.name:
            if not is_measured:
                yield elem, None
                continue

            # Observable was measured
            realcompl = fh.readline()

            if "C" in realcompl:
                str_values_r = fh.readline()
                str_values_c = fh.readline()
                real_val = np.array(list(map(float, str_values_r.split())))
                compl_val = np.array(list(map(float, str_values_c.split())))
                res = real_val + 1j * compl_val

                yield elem, res

            if "R" in realcompl:
                str_values_r = fh.readline()
                res = np.array(list(map(float, str_values_r.split())))

                yield elem, res

    def write_results(self, fh, state_ansatz, **kwargs):
        """
        See :func:`_TNObsBase.write_results`.
        """
        is_measured = self.check_measurable(state_ansatz)

        # Write separator first
        fh.write("-" * 20 + "tnobstzerocorr\n")
        # Assignment for the linter
        _ = fh.write("T \n") if is_measured else fh.write("F \n")

        if is_measured:
            for name_ii in self.name:
                # Write column by column because this is favored
                # by the fortran memory

                corr_mat = self.results_buffer[name_ii]
                real_mat = np.real(corr_mat)
                imag_mat = np.imag(corr_mat)

                if np.any(np.abs(imag_mat) > 1e-12):
                    fh.write("C\n")

                    str_r = " ".join(list(map(str, list(real_mat[:]))))
                    str_c = " ".join(list(map(str, list(imag_mat[:]))))

                    fh.write(str_r + "\n")
                    fh.write(str_c + "\n")

                else:
                    fh.write("R\n")

                    str_r = " ".join(list(map(str, list(real_mat[:]))))

                    fh.write(str_r + "\n")

            self.results_buffer = {}
