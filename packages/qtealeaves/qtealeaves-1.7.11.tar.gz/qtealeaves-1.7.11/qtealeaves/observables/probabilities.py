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
Observable to measure the probabilities of the final state of the MPS
"""

import logging

import mpmath as mp

from qtealeaves.tooling import QTeaLeavesError

from .tnobase import _TNObsBase

__all__ = ["TNObsProbabilities"]

logger = logging.getLogger(__name__)


class TNObsProbabilities(_TNObsBase):
    r"""
    Observable to measure the probabilities of the state configurations
    at the end of an evolution.

    Parameters
    ----------
    prob_type: str, optional
        The type of probability measure. Available:
        - 'U', unbiased (probabilities and count)
        - 'G', greedy (probabilities only)
        - 'E', even. (probabilities only, also implemented in Fortran backend)
        Default to 'U'
    num_samples: int | None, optional
        "U" only: Number of samples for the unbiased prob_type.
        If a list is passed, the function is called multiple times
        with that list of parameters.
        Default to 100 (via `None`)
    prob_threshold: float | None, optional
        probability treshold for `prob_type=('G', 'E')`.
        Recall that prob_type=E needs lower thresholds to measure  more states while
        prob_type=G needs higher thresholds to measure more states.
        Default to 0.9 for "G", 0.1 for "E" (via `None`)
    precision : int, optional
        Decimal place precision for the mpmath package. It is only
        used inside the function, and setted back to the original after
        the computations. Before processing the intervals with precision
        larger than 15 you need to set mpmath precision again.
        If it is 15 or smaller, it just uses numpy.
        Default to 15.
    qiskit_convention : bool, optional
        If you should use the qiskit convention when measuring, i.e. least significant qubit
        on the right. Default to False.

    Details
    -------

    The probabilities are computed following
    a probability tree, where each node is a site, and has a number of
    childs equal to the local dimension :math:`d` of the site. We keep
    track of the probabilities of the paths from the root to the leaves.
    The leaves identify the final state. For example, a state written as

    .. math::
        |\psi\rangle = \sqrt{N}\left(|00\rangle + |01\rangle
        + 2|11\rangle\right)

    with :math:`N=\frac{1}{6}` will have the following
    probability tree. Branches going left measures :math:`0` while
    branches on the right measures :math:`1`. The ordering here is
    the right-most site being the index-0 site.

    .. code-block::

                   ----o----             # No measure, state s2,s1
            p=1/6/            \p=5/6     # First measure, states s2,0 or s2,1
                o              o
         p=1/6/   \p=0  p=1/6/   \p=4/6  # Second measure, states 0,0 or 0,1 or 1,1
             00   10        01   11

    There are three possible ways of computing the probability:

    - Going down **evenly** on the tree, which means following ALL possible paths
      at the same time, and discarding paths which probability is below an input
      threshold :math:`\epsilon`. You might have no outputs, if all the branches
      has a probability :math:`p<\epsilon`.
    - Going down **greedily** on the tree, which means following each time the path
      with highest probability, until the total probability measured is more then
      a threshold :math:`\mathcal{E}`. This procedure is dangerous, since it can
      take an exponentially-long time if :math:`\mathcal{E}` is too high.
    - Going down **unbiasedly** on the tree, which means drawing a ``num_sumples``
      uniformly distributed random numbers :math:`u\sim U(0,1)` and ending in the
      leaf which probability interval :math:`[p_{\mathrm{low}}, p_{\mathrm{high}}]`
      is such that :math:`u\in [p_{\mathrm{low}}, p_{\mathrm{high}}]`. This is the
      suggested method. See http://arxiv.org/abs/2401.10330 for additional details.

    The result of the observable will be a dictionary where:

    - the keys are the measured state on a given basis
    - the values are the probabilities of measuring the key for the **even** and
      **greedy** approach, while they are the probability intervals for the
      **unbiased** approach and the count of each sample, i.e., a tuple of three
      numbers.
    """

    # pylint: disable-next=too-many-arguments
    def __init__(
        self,
        prob_type="U",
        num_samples=None,
        prob_threshold=None,
        precision=15,
        qiskit_convention=False,
    ):
        self.prob_type = [prob_type.upper()]
        self.qiskit_convention = [qiskit_convention]
        self.precision = [precision]

        if prob_type == "U":
            if num_samples is None:
                num_samples = 100
            if prob_threshold is not None:
                logger.warning("Ignoring `prob_threshold` for prob_type=U")
            self.prob_param = [num_samples]
            name = "unbiased_probability"
        elif prob_type == "E":
            if num_samples is not None:
                logger.warning("Ignoring `num_samples` for prob_type=E")
            if prob_threshold is None:
                prob_threshold = 0.1
            self.prob_param = [prob_threshold]
            name = "even_probability"
        elif prob_type == "G":
            if num_samples is not None:
                logger.warning("Ignoring `num_samples` for prob_type=E")
            if prob_threshold is None:
                prob_threshold = 0.9
            self.prob_param = [prob_threshold]
            name = "greedy_probability"
        else:
            raise ValueError(
                f"Probability types can only be U, G or E. Not {prob_type}"
            )

        _TNObsBase.__init__(self, name)
        self.measurable_ansaetze = ("MPS", "TTN", "TTO", "ATTN")

    def __len__(self):
        """
        Provide appropriate length method
        """
        return len(self.prob_type)

    def __iadd__(self, other):
        """
        Documentation see :func:`_TNObsBase.__iadd__`.
        """
        if isinstance(other, TNObsProbabilities):
            self.prob_type += other.prob_type
            self.prob_param += other.prob_param
            self.name += other.name
            self.qiskit_convention += other.qiskit_convention
            self.precision += other.precision
        else:
            raise QTeaLeavesError("__iadd__ not defined for this type.")

        return self

    @classmethod
    def empty(cls):
        """
        Documentation see :func:`_TNObsBase.empty`.
        """
        obj = cls()
        obj.prob_type = []
        obj.prob_param = []
        obj.name = []
        obj.qiskit_convention = []
        obj.precision = []

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

        for name, prob_type, precision in zip(
            self.name, self.prob_type, self.precision
        ):
            if is_measured:
                num_lines = int(fh.readline().replace("\n", ""))
                measures = {}
                for _ in range(num_lines):
                    line = fh.readline().replace("\n", "")
                    words = line.replace(" ", "").split("|")
                    if prob_type == "U" and precision <= 15:
                        measures[words[0]] = (
                            float(words[1]),
                            float(words[2]),
                            int(words[3]),
                        )
                    elif prob_type == "U" and precision > 15:
                        # Set mpmath precision
                        old_precision = mp.mp.dps
                        mp.mp.dps = precision
                        measures[words[0]] = (
                            mp.mpf(words[1]),
                            mp.mpf(words[2]),
                            int(words[3]),
                        )
                        mp.mp.dps = old_precision
                    else:
                        # "G" and "E" cannot count, count will be -1 to signal
                        # not being valid, but the user should not see
                        measures[words[0]] = float(words[1])
                yield name, measures
            else:
                yield name, None

    # pylint: disable-next=too-many-locals
    def write_results(self, fh, state_ansatz, **kwargs):
        """
        See :func:`_TNObsBase.write_results`.
        """
        is_measured = self.check_measurable(state_ansatz)

        # Write separator first
        fh.write("-" * 20 + "tnobsprobabilities\n")
        # Assignment for the linter
        _ = fh.write("T \n") if is_measured else fh.write("F \n")

        if is_measured:
            for name, prob_type, precision in zip(
                self.name, self.prob_type, self.precision
            ):

                # Set mpmath precision
                old_precision = mp.mp.dps
                mp.mp.dps = precision

                if prob_type in ["E", "G"]:
                    # Logic is different and we do not get any count here anyway
                    # And no boundary, but the probability goes on the first boundary
                    prob_dictionary = self.results_buffer[name]
                    fh.write(str(len(prob_dictionary)) + "\n")
                    for state, value in prob_dictionary.items():
                        fh.write(f"{state} | {value} | -1.0 | {-1}\n")
                    continue

                bounds_dictionary, samples = self.results_buffer[name]
                fh.write(str(len(bounds_dictionary)) + "\n")

                # Comment: might not be the most memory efficient solution
                # as we have another dictionary with all the keys, eventually
                # same thing with the iterator
                counter = {state: 0 for state in bounds_dictionary.keys()}
                states_iterator = iter(sorted(bounds_dictionary.keys()))
                state = next(states_iterator)

                # We can assume `samples` are already sorted ascending
                warning_never_printed = True
                for sampled_num in samples:
                    while sampled_num > bounds_dictionary[state][1]:
                        # Loop over states until we find the right one, this
                        # skips states in the dictionary which have no
                        # sample at all (but are measured in terms of being
                        # a pair with only the last qubit different)
                        try:
                            state = next(states_iterator)
                        except StopIteration:
                            break
                    if (
                        bounds_dictionary[state][1]
                        >= sampled_num
                        > bounds_dictionary[state][0]
                    ):
                        counter[state] += 1
                    elif warning_never_printed:
                        # pylint: disable-next=logging-not-lazy
                        logger.warning(
                            f"{sampled_num} not in {bounds_dictionary[state]}."
                            + " This warning will not be shown again."
                        )
                        warning_never_printed = False

                for state, value in bounds_dictionary.items():
                    fh.write(f"{state} | {value[0]} | {value[1]} | {counter[state]}\n")

                # Reset mpmath precision
                mp.mp.dps = old_precision
