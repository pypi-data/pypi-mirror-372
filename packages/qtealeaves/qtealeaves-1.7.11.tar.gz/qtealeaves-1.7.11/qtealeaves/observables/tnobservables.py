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
Observable to recap all the observables that can be measured by the TN
"""

import os
import re
import warnings
from collections import OrderedDict
from copy import deepcopy
from pathlib import Path

import h5py

from qtealeaves import __version__
from qtealeaves.tooling import QTeaLeavesError
from qtealeaves.tooling.parameterized import _ParameterizedClass

from .bond_entropy import TNObsBondEntropy
from .correlation import TNObsCorr, TNObsCorr4
from .custom_correlation import TNObsCustom
from .custom_function_obs import TNCustomFunctionObs
from .distance2pure import TNDistance2Pure
from .local import TNObsLocal
from .log_negativity import TNObsLogNegativity
from .mpo_densempolist import TNObsDenseMPOList
from .probabilities import TNObsProbabilities
from .projective import TNObsProjective
from .state2file import TNState2File
from .tensor_product import TNObsTensorProduct
from .timecorrelator import TNObsTZeroCorr
from .weighted_sum import TNObsWeightedSum

__all__ = ["TNObservables"]


class TNObservables(_ParameterizedClass):
    """
    Organization of all the measurements to be taken during a
    tensor network simulation.
    To add new observables  in the container you should simply
    use the :code:`+=` operator as shown in the example.

    **Example**

    .. code-block:: python

        obs = TNObservables()
        obs += any_other_observable

    **Arguments**

    filename_observables : str
        Base filename of the definition with the observables
        inside the input folder and observables subfolder. A
        postfix might be appended upon need. The file extension
        will be chosen by the backend.

    folder_observables : str
        Subfolder for the observable input files inside
        the input folder.

    num_trajectories : int
        Total number of quantum trajectories.

    **Details**

    Up to now, the class organizes and accepts observables of the
    type :class:`TNObsLocal`, :class:`TNObsCorr`, :class:`TNDistance2Pure`,
    :class:`TNState2File`, :class:`TNObsTensorProduct`, :class:`TNObsWeightedSum`,
    :class:`TNObsProjective`, :class:`TNObsProbabilities`, :class:`TNObsBondEntropy`,
    :class:`TNObsCustom`, :class:`TNObsDenseMPOList`
    """

    def __init__(
        self,
        filename_observables="observables.in",
        folder_observables="observables",
        num_trajectories=1,
        do_write_hdf5=False,
    ):
        self.results_buffer = {}
        self.filename_observables = filename_observables
        self.folder_observables = folder_observables
        self.num_trajectories = num_trajectories
        self.do_write_hdf5 = do_write_hdf5

        self.obs_list = OrderedDict()

        elems = [
            TNObsLocal,
            TNObsCorr,
            TNDistance2Pure,
            TNState2File,
            TNObsTensorProduct,
            TNObsWeightedSum,
            TNObsProjective,
            TNObsProbabilities,
            TNObsBondEntropy,
            TNObsTZeroCorr,
            TNObsCorr4,
            TNObsCustom,
            TNObsDenseMPOList,
            TNObsLogNegativity,
            TNCustomFunctionObs,
        ]

        for elem in elems:
            obj = elem.empty()
            self.obs_list[repr(obj)] = obj

    def get_num_trajectories(self, **kwargs):
        """
        Get number of quantum trajectories

        **Arguments**

        params : keyword argument
            A dictionary with parameters is accepted
            as a keyword argument.
        """
        params = kwargs.get("params", {})
        num_trajectories = self.eval_numeric_param(self.num_trajectories, params)

        # the first entry of the seed list should be <4096
        if num_trajectories > 4095:
            raise QTeaLeavesError("Number of trajectory over the limit for the seed.")

        return num_trajectories

    def add_observable(self, obj):
        """
        Add a specific observable to the measurements. The class
        of the observable added must match the predefined observables
        inside this class.
        """
        if repr(obj) not in self.obs_list:
            raise QTeaLeavesError(f"Observables not of valid type: {repr(obj)}")
        self.obs_list[repr(obj)] += obj

    def __iadd__(self, obj):
        """
        Overwrite operator ``+=`` to simplify syntax.
        """
        self.add_observable(obj)
        return self

    @staticmethod
    def add_trajectories(all_results, new):
        """
        Add the observables for different quantum trajectories.

        **Arguments**

        all_results : dict
            Dictionary with observables.

        new : dict
            Dictionary with new observables to add to all_results.
        """
        for name in ["energy", "norm"]:
            if name not in all_results:
                all_results[name] = new[name]

            else:
                all_results[name] += new[name]

        # `time` is the time of the quench, not the CPU time
        # Must be the same for all simulations if dynamics
        # Do not add, just pick if it is present
        if ("time" not in all_results) and ("time" in new):
            all_results["time"] = new["time"]

        return all_results

    @staticmethod
    def avg_trajectories(all_results, num_trajectories):
        """
        Get the average of quantum trajectories observables.

        **Arguments**

        all_results : dict
            Dictionary with observables.

        num_trajectories : int
            Total number of quantum trajectories.
        """
        # skip time, already not added up since it is the time
        # in the simulation (must be same).
        for name in ["energy", "norm"]:
            all_results[name] /= num_trajectories
        return all_results

    def collect_operators(self):
        """
        Collect all operators with some additional information. This
        function is just collecting the information from all observables
        stored within this class.
        """
        op_lst = []

        for elem in self.obs_list:
            for op_tuple in self.obs_list[elem].collect_operators():
                op_lst.append(op_tuple)

        return list(set(op_lst))

    def write_results(self, filename, params, state_ansatz):
        """
        Write the complete measurement file mocking the fortran
        output. The assumption is that the results buffer of each
        measurement was set with all the required results.

        **Arguments**

        filename : str
            Target location of the file.

        params : dict
            Simulation parameters.

        state_ansatz : str
            Label identifying the state ansatz currently in use.
        """
        # We probably need params in the future - avoid unused argument error
        _ = len(params)

        with open(filename, "w+") as fh:
            # First line is version
            fh.write("PY-" + str(__version__) + "\n")
            # Separator line
            fh.write("-" * 20 + "\n")
            # Energy and norm each in one line
            energy = self.results_buffer["energy"]
            if hasattr(energy, "__len__"):
                # Resolve list via last element
                energy = energy[-1]
            fh.write(str(energy) + "\n")
            fh.write(str(self.results_buffer["norm"]) + "\n")
            if "time" in self.results_buffer:
                fh.write(str(self.results_buffer["time"]) + "\n")
            else:
                fh.write(str(-999e300) + "\n")

            self.results_buffer = {}

            for elem in self.obs_list:
                self.obs_list[elem].write_results(fh, state_ansatz=state_ansatz)

    @staticmethod
    def read_cpu_time_from_log(filename_result, params):
        """
        Read the CPU time if it can be resolved via the log file.

        **Arguments**

        filename_result : str
            Filename to the output file including the path. This filename
            can vary for statics and dynamics and therefore has to be passed.
            Function assumes that the log-file is stored next to it.

        **Returns**

        Iterator returns key, value pair if available.
        """
        regex = re.compile(r"CPU time:?\s*([\d\.]+)")
        log_file = Path(filename_result).parent / params.get("log_file", "sim.log")
        if not log_file.is_file():
            return
        with log_file.open() as log_file:
            for line in reversed(log_file.readlines()):
                match = regex.search(line)
                if match:
                    yield "cpu_time", float(match.group(1))
                    break

    # pylint: disable-next=too-many-locals
    def read_file(self, filename, params):
        """
        Read all the results from a single file and store them
        in a dictionary.

        **Arguments**

        filename : str
            Filename to the output file including the path. This filename
            can vary for statics and dynamics and therefore has to be passed.

        params : dict
            The parameter dictionary, which is required to obtain
            the output folder.
        """
        results = {}

        if self.eval_numeric_param(elem=self.do_write_hdf5, params=params):
            # read from the hdf5 file
            # filename is the same as for text, but with last three chars replaced by hdf5
            hdf5_filename = filename[:-3] + "hdf5"
            with h5py.File(hdf5_filename, "r") as h5f:
                # The structure of the file is:
                # version
                # energy
                # time
                # norm
                # /TNObsLocal/0, 1, 2, ...
                # /TNObsCorr/0/real
                #             /imag

                results["energy"] = h5f["energy"][()]
                results["time"] = h5f["time"][()]
                results["norm"] = h5f["norm"][()]

                for elem in self.obs_list:
                    obs_type_name = elem
                    obs_object = self.obs_list[elem]
                    if type(obs_object) in [TNObsLocal, TNObsCorr]:
                        # Currently only enabled for these two measurements
                        # read if there is a dataset
                        if obs_type_name in h5f:
                            dataset = h5f[obs_type_name]
                            for key, value in obs_object.read_hdf5(
                                dataset, params=params
                            ):
                                results[key] = value

                    else:
                        warnings.warn(
                            f"NOT IMPLEMENTED YET: Instance is {type(obs_object)}. "
                            + "It does not support hdf5 read/writing yet. Use do_write_hdf5=False."
                        )

        else:
            # reading from .dat file
            with open(filename, "r") as fh:
                # First line is IO version (for future use)
                _ = fh.readline()
                # Separator
                _ = fh.readline()

                energy = fh.readline()
                results["energy"] = float(energy)
                norm = fh.readline()
                results["norm"] = float(norm)
                time = fh.readline()
                if "j" in time:
                    # Detect complex number (complex time evolution) via j in string for imag part
                    results["time"] = complex(time)
                elif float(time) > 0.0:
                    results["time"] = float(time)

                for key, value in self.read_cpu_time_from_log(filename, params):
                    results[key] = value

                for elem in self.obs_list:
                    for key, value in self.obs_list[elem].read(fh, params=params):
                        results[key] = value

        return results

    def read(self, filename, folder, params):
        """
        Read all the results and store them in a dictionary.

        **Arguments**

        filename : str
            Filename of the output file (not including the path). This filename
            can vary for statics and dynamics and therefore has to be passed.

        folder : str
            Folder of the output file.

        params : dict
            The parameter dictionary, which is required to obtain
            the output folder.
        """
        num_trajectories = self.get_num_trajectories(params=params)

        if num_trajectories == 1:
            # no quantum trajectories
            folder_name_output = self.eval_str_param(folder, params)

            # get results
            # pylint: disable-next=no-member
            full_file_path = os.path.join(folder_name_output, filename)
            results = self.read_file(full_file_path, params)
        else:
            # read results for quantum trajectories
            results = {}
            for ii in range(num_trajectories):
                # add trajectory id into params
                tmp = deepcopy(params)
                tmp["trajectory_id"] = self.get_id_trajectories(ii)
                tmp["seed"] = self.get_seed_trajectories(tmp)

                folder_name_output = self.get_folder_trajectories(folder, tmp)

                # get results for each quantum trajectory
                # pylint: disable-next=no-member
                full_file_path = os.path.join(folder_name_output, filename)

                name_ii = ("trajectory", tmp["trajectory_id"])
                results[name_ii] = self.read_file(full_file_path, params)
                results[name_ii]["seed"] = tmp["seed"]

                # add the observables
                results = self.add_trajectories(results, results[name_ii])
                for elem in self.obs_list:
                    results = self.obs_list[elem].add_trajectories(
                        results, results[name_ii]
                    )

            # compute the average of the observables
            results = self.avg_trajectories(results, num_trajectories)
            for elem in self.obs_list:
                results = self.obs_list[elem].avg_trajectories(
                    results, num_trajectories
                )

        return results

    @staticmethod
    def get_id_trajectories(val):
        """
        Get the id for the given quantum trajectory.

        **Arguments**

        val : int
            value for id of the quantum trajectory.
        """
        return val

    @staticmethod
    def get_seed_trajectories(params):
        """
        Get the seed for the given quantum trajectory.

        **Arguments**

        params : dict or list of dicts
            The parameter dictionary or dictionaries, which is required
            to obtain the output folder.

        **Returns**

        seed : list
            The seed for the simulation has 4 entries.
            The following rules applies:
                - entries must be smaller than 4096
                - entries must be bigger than 0
                - last entry must be odd
        """
        if "seed" in params:
            raise QTeaLeavesError("The seed cannot be specified by the user.")

        seed = [params["trajectory_id"] + 1, 13, 17, 19]
        return seed

    def get_folder_trajectories(self, folder_name, params):
        """
        Evaluate the folder name and add the trajectory id if running trajectories.

        **Arguments**

        folder_name : str
            Name of the input/output folder for the simulation.

        params : dict or list of dicts
            The parameter dictionary or dictionaries, which is required
            to obtain the output folder.

        **Returns**

        folder_name : str
            Modified folder name with the trajectory id.
        """
        num_trajectories = self.get_num_trajectories(params=params)
        folder_name = self.eval_str_param(folder_name, params)

        if num_trajectories != 1:
            folder_name = folder_name + "/qt_" + str(params["trajectory_id"])

        return folder_name
