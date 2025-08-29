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
Observable to perform the final projective measurements on the system
"""

from qtealeaves.tooling import QTeaLeavesError

from .tnobase import _TNObsBase

__all__ = ["TNObsProjective"]


class TNObsProjective(_TNObsBase):
    """
    Observable to enable the final projective measurements after the evolution.
    This observable is meant to give single-shot measurements: the system is
    **projectively** measured a number of times equal to `num_shots`, such that
    the user can observe a statistic of the distribution of the state.

    The result of the observable will be a dictionary where:

    - the keys are the measured state on a given basis
    - the values are the number of occurrences of the keys in the `num_shots`
      single shots measurements

    As an example, if we work with qubits, we measure on the computational base
    and we end up with the state :math:`\\frac{1}{\\sqrt{2}}(|00\\rangle+|11\\rangle)`,
    requesting 1000 `num_shots` we will end up with the following result:
    :code:`{'00' : 505, '11' : 495}`. Take into account that the measurement is probabilistic
    and such is will only be an approximation of the true probability distribution,
    that in the example case would be :math:`p_{00}=p_{11}=0.5`.

    Parameters
    ----------
    num_shots : int
        Number of projective measurements
    qiskit_convention : bool, optional
        If you should use the qiskit convention when measuring, i.e. least significant qubit
        on the right. Default to False.
    """

    def __init__(self, num_shots, qiskit_convention=False):
        self.num_shots = num_shots
        self.qiskit_convention = [qiskit_convention]
        self._measures = {}
        _TNObsBase.__init__(self, "projective_measurements")
        self.measurable_ansaetze = ("MPS", "TTN", "TTO", "ATTN")

    def __iadd__(self, other):
        """
        Documentation see :func:`_TNObsBase.__iadd__`.
        """
        if isinstance(other, TNObsProjective):
            self.num_shots += other.num_shots
            self.qiskit_convention += other.qiskit_convention
        else:
            raise QTeaLeavesError("__iadd__ not defined for this type.")

        return self

    @classmethod
    def empty(cls):
        """
        Documentation see :func:`_TNObsBase.empty`.
        """
        obj = cls(0)
        obj.qiskit_convention = []

        return obj

    def add_trajectories(self, all_results, new):
        """
        Documentation see :func:`_TNObsBase.add_trajectories`.
        """
        for name in self.name:
            if name not in all_results:
                all_results[name] = new[name]
            else:
                if len(new[name]) > 0:
                    for key in new[name]:
                        if key not in all_results[name]:
                            all_results[name][key] = new[name][key]
                        else:
                            all_results[name][key] += new[name][key]
        return all_results

    def avg_trajectories(self, all_results, num_trajectories):
        """
        Documentation see :func:`_TNObsBase.avg_trajectories`.
        """
        # the average is not performed for projective measurements
        return all_results

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
            num_lines = int(fh.readline().replace("\n", ""))
            for _ in range(num_lines):
                line = fh.readline()
                words = line.replace(" ", "").split("|")
                self._measures[words[0]] = int(words[1])

            yield self.name[0], self._measures

        else:
            yield self.name[0], {}

    def write_results(self, fh, state_ansatz, **kwargs):
        """
        See :func:`_TNObsBase.write_results`.
        """
        is_measured = self.check_measurable(state_ansatz)

        # Write separator first
        fh.write("-" * 20 + "tnobsfinalmeas\n")
        # Assignment for the linter
        _ = fh.write("T \n") if is_measured else fh.write("F \n")

        if is_measured:
            # Number of results
            if len(self.results_buffer.values()) > 0:
                for res in self.results_buffer.values():
                    fh.write(str(len(res)) + "\n")
                    for key, value in res.items():
                        fh.write(f"{key} | {value} \n")
            else:
                fh.write("0\n")
