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
Local observable
"""

import numpy as np

from qtealeaves.mpos import ITPO, DenseMPO, DenseMPOList, MPOSite
from qtealeaves.tooling import QTeaLeavesError

from .tnobase import _TNObsBase

__all__ = ["TNObsLocal"]


class TNObsLocal(_TNObsBase):
    """
    The local observable will measure an operator defined on a single site
    across the complete system. This means that, if the single site has
    a dimension :math:`d` we expect the local observable to be a matrix
    of dimension :math:`d\\times d`. For example, if we are working with
    qubits, i.e. :math:`d=2`, a local observable can be the Pauli matrix
    :math:`\\sigma_z`.

    The local observable will be measured on *each* site of the tensor
    network. As such, the output of this measurement will be a dictionary
    where:

    - the key is the `name` of the observable
    - the value is a list of length :math:`n`, with :math:`n` the number
    of sites of the tensor network. The :math:`i`-th element of the
    list will contain the expectation value of the local observable
    on the :math:`i`-th site.

    **Arguments**

    name : str
        Define a label under which we can find the observable in the
        result dictionary.

    operator : str
        Identifier/string for the operator to be measured.
    """

    def __init__(self, name, operator):
        super().__init__(name)
        self.operator = [operator]
        self.measurable_ansaetze = ("MPS", "TTN", "TTO", "ATTN", "LPTN", "STATE")

    @classmethod
    def empty(cls):
        """
        Documentation see :func:`_TNObsBase.empty`.
        """
        obj = cls("x", "x")
        obj.name = []
        obj.operator = []

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
        if isinstance(other, TNObsLocal):
            self.name += other.name
            self.operator += other.operator
        else:
            raise QTeaLeavesError("__iadd__ not defined for this type.")

        return self

    def collect_operators(self):
        """
        Documentation see :func:`_TNObsBase.collect_operators`.
        """
        for elem in self.operator:
            yield (elem, None)

    # pylint: disable-next=too-many-locals
    def to_itpo(self, operators, tensor_backend, num_sites, de_layer):
        """
        For measurements of aTTN when local entries on sites with disentanglers
        are not local anymore, returns an ITPO with these non-local terms for
        measurement. The resulting terms are stored in order of looping
        over observable names and number of sites.

        Parameters
        ----------
        operators: TNOperators
            The operator class
        tensor_backend: instance of `TensorBackend`
            Tensor backend of the simulation
        num_sites: int
            Number of sites of the state
        de_layer : DELayer
            Disentangler layer for which the iTPO layer is created

        Returns
        -------
        ITPO: The `ITPO` class
            iTPO with the non-local terms for measurement.
        """
        dense_mpo_list = DenseMPOList()
        for kk, _ in enumerate(self.name):
            key_loc = self.operator[kk]
            key_id = None

            # get local operator and corresponding identity
            for oset_name in operators.set_names:
                op = operators[(oset_name, key_loc)]

                # the matching identity (is it not always in operators?)
                op_identity = op.eye_like(op.links[1])
                op_identity.attach_dummy_link(0, is_outgoing=False)
                op_identity.attach_dummy_link(3, is_outgoing=True)
                key_id = str(id(op_identity)) if key_id is None else key_id
                operators[(oset_name, key_id)] = op_identity

            # fill the itpo with correct operators on correct sites
            for ii in range(num_sites):
                if ii in de_layer.de_sites:
                    # appropriate identity operator needs
                    # to be added on the other site of the disentangler

                    where = np.where(de_layer.de_sites == ii)
                    # we assume max 1 disentangler per site
                    ind = [where[0][0], where[1][0]]
                    position_identity = de_layer.de_sites[ind[0], abs(ind[1] - 1)]

                    site_a = MPOSite(
                        ii, key_loc, 1.0, 1.0, operators=operators, params={}
                    )
                    site_b = MPOSite(
                        position_identity,
                        key_id,
                        1.0,
                        1.0,
                        operators=operators,
                        params={},
                    )

                    dense_mpo = DenseMPO(
                        [site_a, site_b], tensor_backend=tensor_backend
                    )
                    dense_mpo_list.append(dense_mpo)

        # Sites within dense mpos are not ordered and we have to make links match anyways
        dense_mpo_list = dense_mpo_list.sort_sites()

        itpo = ITPO(num_sites)
        itpo.add_dense_mpo_list(dense_mpo_list)
        itpo.set_meas_status(do_measurement=True)

        return itpo

    def read(self, fh, **kwargs):
        """
        Read local observables from standard formatted fortran output.

        fh : filehandle
            Read the information about the measurements from this filehandle.
        """
        # First line is separator
        _ = fh.readline()
        is_meas = fh.readline().replace("\n", "").replace(" ", "")
        is_measured = is_meas == "T"

        for ii in range(len(self)):
            if is_measured:
                str_values = fh.readline()

                yield self.name[ii], np.array(list(map(float, str_values.split())))
            else:
                yield self.name[ii], None

    def read_hdf5(self, dataset, params):
        """
        Reads the given dataset of observables into a generator.
        The keys of the dataset are (0-based) integers which correspond to
        the names of the observables.

        **Arguments**

        dataset : h5py dataset object
            The dataset to be read out.
        params : params dictionary
            Unused for now.
        """
        _ = params  # unused for now
        for ii, name in enumerate(self.name):
            yield name, dataset[str(ii)][()]

    def write_results(self, fh, state_ansatz, **kwargs):
        """
        See :func:`_TNObsBase.write_results`.
        """
        is_measured = self.check_measurable(state_ansatz)

        # Write separator first
        fh.write("-" * 20 + "tnobslocal\n")
        # Assignment for the linter
        _ = fh.write("T \n") if is_measured else fh.write("F \n")

        if is_measured:
            for name_ii in self.name:
                result_ii = self.results_buffer[name_ii]

                fh.write(" ".join(list(map(str, result_ii))) + "\n")
