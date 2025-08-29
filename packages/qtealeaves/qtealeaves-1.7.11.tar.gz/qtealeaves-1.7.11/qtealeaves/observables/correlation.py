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
The correlation observable measures the correlation between
two operators. It cannot be used for fermionic operators which
require a Jordan-Wigner transformation. Thus, the correlation
is of type ``<A_i B_j>``. The index ``i`` is running over
the rows of a matrix, the index ``jj`` over the columns.

( <A_1 B_1>   <A_1 B_2>   <A_1 B_3>   ... )
( <A_2 B_1>   <A_2 B_2>   <A_2 B_3>   ... )
( <A_3 B_1>   <A_3 B_2>   <A_3 B_3>   ... )
(    ...         ...         ...      ... )
"""

# pylint: disable=too-many-locals

import numpy as np

from qtealeaves.mpos import ITPO, DenseMPO, DenseMPOList, MPOSite
from qtealeaves.tooling import QTeaLeavesError

from .tnobase import _TNObsBase

__all__ = ["TNObsCorr", "TNObsCorr4"]


class TNObsCorr(_TNObsBase):
    """
    The correlation observable measures the correlation between
    two operators. It cannot be used for fermionic operators which
    require a Jordan-Wigner transformation. Thus, the correlation
    is of type ``<A_i B_j>``. The index ``i`` is running over
    the rows of a matrix, the index ``jj`` over the columns.

    .. code-block::

        ( <A_1 B_1>   <A_1 B_2>   <A_1 B_3>   ... )
        ( <A_2 B_1>   <A_2 B_2>   <A_2 B_3>   ... )
        ( <A_3 B_1>   <A_3 B_2>   <A_3 B_3>   ... )
        (    ...         ...         ...      ... )

    **Arguments**

    name : str
        Define a label under which we can find the observable in the
        result dictionary.

    operators : list of two strings
        Identifiers/strings for the operators to be measured.

    batch_size : int | None, optional
        None measures with a single iTPO. Any integer will be interpreted
        as batch size after every batch_size entries a new iTPO is created.
        The batch size addresses the problem of memory needs of the iTPO
        correlation measurement with all terms at once; lower batch sizes
        reduce the memory cost and increasing the computational cost to
        some extent.
        Default to None (Measure all correlations in one iTPO).
    """

    def __init__(self, name, operators, batch_size=None):
        super().__init__(name)
        self.operators = [operators]
        self.batch_size = [batch_size]
        self.measurable_ansaetze = ("MPS", "TTN", "TTO", "ATTN", "STATE")

    @classmethod
    def empty(cls):
        """
        Documentation see :func:`_TNObsBase.empty`.
        """
        obj = cls(None, None)
        obj.name = []
        obj.operators = []
        obj.batch_size = []

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
        if isinstance(other, TNObsCorr):
            self.name += other.name
            self.operators += other.operators
            self.batch_size += other.batch_size
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

    def to_itpo(self, operators, tensor_backend, num_sites, de_layer=None):
        """
        Return an ITPO or ITPOs as iterator representing alltogether the
        correlation observables. In the case of the aTTN the function takes
        care of diagonal terms of corr matrix with the disentanglers on them.
        These diagonal terms are stored in the order of looping over ii and jj.
        The number of ITPOs can be tuned indirectly via the batch size, i.e.,
        after each batch_size terms an ITPO is constructed and yielded plus
        one with the potentially remaining terms.

        Parameters
        ----------
        operators: TNOperators
            The operator class
        tensor_backend: instance of `TensorBackend`
            Tensor backend of the simulation
        num_sites: int
            Number of sites of the state
        de_layer : DELayer or `None`, optional
            Disentangler layer for which the iTPO layer is created
            Default to `None` (standard TN with no disentanglers)

        Returns
        -------
        ITPO
            The ITPO class

        Details
        -------

        ITPOs can be costly in memory and we are able to tune their memory
        footprint. The batch size purely counts terms and can for example
        contain contributions for two correlation measurements. An example
        how to parse the output can be found in the `tn_simulations.py`.
        """

        if de_layer is None:
            yield from self._to_itpo(operators, tensor_backend, num_sites)
        else:
            yield from self._to_itpo_de_layer(
                operators, tensor_backend, num_sites, de_layer
            )

    def _to_itpo(self, operators, tensor_backend, num_sites):
        """
        Return an ITPO or ITPOs as iterator representing alltogether the
        correlation observables.
        The number of ITPOs can be tuned indirectly via the batch size, i.e.,
        after each batch_size terms an ITPO is constructed and yielded plus
        one with the potentially remaining terms.

        Parameters
        ----------
        operators: TNOperators
            The operator class
        tensor_backend: instance of `TensorBackend`
            Tensor backend of the simulation
        num_sites: int
            Number of sites of the state

        Returns
        -------
        ITPO
            The ITPO class
        """
        dense_mpo_list = DenseMPOList()
        for kk, _ in enumerate(self.name):
            key_a = self.operators[kk][0]
            key_b = self.operators[kk][1]

            for ii in range(num_sites):
                for jj in range(num_sites):
                    if ii == jj:
                        continue

                    site_a = MPOSite(
                        ii, key_a, 1.0, 1.0, operators=operators, params={}
                    )
                    site_b = MPOSite(
                        jj, key_b, 1.0, 1.0, operators=operators, params={}
                    )

                    dense_mpo = DenseMPO(
                        [site_a, site_b], tensor_backend=tensor_backend
                    )
                    dense_mpo_list.append(dense_mpo)

                    if len(dense_mpo_list) == self.batch_size[kk]:
                        dense_mpo_list = dense_mpo_list.sort_sites()

                        itpo = ITPO(num_sites)
                        itpo.add_dense_mpo_list(dense_mpo_list)
                        yield itpo

                        # Start with new empty
                        dense_mpo_list = DenseMPOList()

        if len(dense_mpo_list) == 0:
            # We finished exactly on the last term
            return

        # Sites are not ordered and we have to make links match anyways
        dense_mpo_list = dense_mpo_list.sort_sites()

        itpo = ITPO(num_sites)
        itpo.add_dense_mpo_list(dense_mpo_list)

        yield itpo

    def _to_itpo_de_layer(self, operators, tensor_backend, num_sites, de_layer):
        """
        Return an ITPO or ITPOs as iterator representing alltogether the
        correlation observables. In the case of the aTTN the function takes
        care of diagonal terms of corr matrix with the disentanglers on them.
        These diagonal terms are stored in the order of looping over ii and jj.
        The number of ITPOs can be tuned indirectly via the batch size, i.e.,
        after each batch_size terms an ITPO is constructed and yielded plus
        one with the potentially remaining terms.

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
        ITPO
            The ITPO class
        """
        # only if aTTN
        dense_mpo_list = DenseMPOList()
        for kk, _ in enumerate(self.name):
            key_a = self.operators[kk][0]
            key_b = self.operators[kk][1]

            # get all operators.ops[]
            key_ab = None
            key_id = None
            for oset_name in operators.set_names:
                op_a = operators[(oset_name, key_a)]
                op_b = operators[(oset_name, key_b)]

                # get the operator a x b for the diag entries
                if op_a.ndim == 2:
                    op_ab = op_a @ op_b
                else:
                    # Assume rank-4 (but delta charge both times to the right
                    # Assume that tensor_a and tensor_b have same link dimensions
                    op_ab = op_a.tensordot(op_b, ([2], [1]))
                    op_ab = op_ab.transpose([3, 0, 1, 4, 2, 5])
                    op_ab.fuse_links_update(4, 5)
                    op_ab.fuse_links_update(0, 1, False)
                key_ab = str(id(op_ab)) if key_ab is None else key_ab
                operators[(oset_name, key_ab)] = op_ab

                # get the matching identity (is it not always in operators?)
                op_identity = op_a.eye_like(op_a.links[1])
                op_identity.attach_dummy_link(0, is_outgoing=False)
                op_identity.attach_dummy_link(3, is_outgoing=True)
                key_id = str(id(op_identity)) if key_id is None else key_id
                operators[(oset_name, key_id)] = op_identity

            # fill the itpo with correct operators on correct sites
            for ii in range(num_sites):
                for jj in range(num_sites):
                    if ii == jj and (ii in de_layer.de_sites):
                        # Diagonal entries of correlation matrix for sites that have
                        # a disentangler attached to it cannot longer be measured as
                        # local terms, and thus the appropriate identity operator needs
                        # to be added on the other site of the disentangler
                        # (Warning: if we add them here, we should more or less have control
                        # over the TPO-id, if they are added by the contract-DE-layer logic,
                        # the TPO-id will be added at the end messing up our loop)

                        where = np.where(de_layer.de_sites == ii)
                        # we assume max 1 disentangler per site
                        ind = [where[0][0], where[1][0]]
                        site_identity = de_layer.de_sites[ind[0], abs(ind[1] - 1)]

                        site_a = MPOSite(
                            ii, key_ab, 1.0, 1.0, operators=operators, params={}
                        )
                        site_b = MPOSite(
                            site_identity,
                            key_id,
                            1.0,
                            1.0,
                            operators=operators,
                            params={},
                        )
                    elif ii == jj:
                        continue
                    else:
                        site_a = MPOSite(
                            ii, key_a, 1.0, 1.0, operators=operators, params={}
                        )
                        site_b = MPOSite(
                            jj, key_b, 1.0, 1.0, operators=operators, params={}
                        )

                    dense_mpo = DenseMPO(
                        [site_a, site_b], tensor_backend=tensor_backend
                    )
                    dense_mpo_list.append(dense_mpo)

                    if len(dense_mpo_list) == self.batch_size[kk]:
                        dense_mpo_list = dense_mpo_list.sort_sites()

                        itpo = ITPO(num_sites)
                        itpo.add_dense_mpo_list(dense_mpo_list)
                        yield itpo

                        # Start with new empty
                        dense_mpo_list = DenseMPOList()

        if len(dense_mpo_list) == 0:
            # We finished exactly on the last term
            return

        # Sites within dense mpos are not ordered and we have to make links match anyways
        dense_mpo_list = dense_mpo_list.sort_sites()

        itpo = ITPO(num_sites)
        itpo.add_dense_mpo_list(dense_mpo_list)
        itpo.set_meas_status(do_measurement=True)

        yield itpo

    def read(self, fh, **kwargs):
        """
        Read the measurements of the correlation observable from fortran.

        **Arguments**

        fh : filehandle
            Read the information about the measurements from this filehandle.
        """
        # First line is separator
        _ = fh.readline()
        is_meas = fh.readline().replace("\n", "").replace(" ", "")
        is_measured = is_meas == "T"

        for elem in self.name:
            if is_measured:
                realcompl = fh.readline()

                if "C" in realcompl:
                    str_values_r = fh.readline()
                    str_values_c = fh.readline()
                    real_val = np.array(list(map(float, str_values_r.split())))
                    compl_val = np.array(list(map(float, str_values_c.split())))
                    vect = real_val + 1j * compl_val
                    numlines = real_val.shape[0]

                    # Build numpy matrix
                    res = np.zeros((numlines, numlines), dtype=vect.dtype)
                    res[:, 0] = vect

                    # Now we now the number of entries after reading the
                    # first line and (numlines - 1) lines are left
                    for ii in range(1, numlines):
                        str_values_r = fh.readline()
                        str_values_c = fh.readline()
                        real_val = np.array(list(map(float, str_values_r.split())))
                        compl_val = np.array(list(map(float, str_values_c.split())))
                        res[:, ii] = real_val + 1j * compl_val

                    yield elem, res

                if "R" in realcompl:
                    str_values_r = fh.readline()
                    real_val = np.array(list(map(float, str_values_r.split())))
                    numlines = real_val.shape[0]

                    # Build numpy matrix
                    res = np.zeros((numlines, numlines), dtype=real_val.dtype)
                    res[:, 0] = real_val

                    for ii in range(1, numlines):
                        str_values_r = fh.readline()
                        real_val = np.array(list(map(float, str_values_r.split())))
                        res[:, ii] = real_val

                    yield elem, res

            else:
                yield elem, None

    def read_hdf5(self, dataset, params):
        """
        The data is written into groups, each containing the dataset real,
        and complex variables also containing a dataset imag.
        Check if imag exists and sum them up.
        The names of the groups are (0-based) integers which correspond to
        the names of the observables.

        **Arguments**

        dataset : h5py dataset
            The dataset to be read out of.
        params  : parameter dictionary
            Unused for now (Dec 2023)
        """
        _ = params  # unused for now
        for ii, name in enumerate(self.name):
            real = dataset[str(ii) + "/real"][()]
            if "imag" in dataset[str(ii)]:
                imag = dataset[str(ii) + "/imag"][()]
                yield name, real + 1j * imag
            else:
                yield ii, real

    def write_results(self, fh, state_ansatz, **kwargs):
        """
        See :func:`_TNObsBase.write_results`.
        """
        is_measured = self.check_measurable(state_ansatz)

        # Write separator first
        fh.write("-" * 20 + "tnobscorr\n")
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

                    for jj in range(real_mat.shape[1]):
                        str_r = " ".join(list(map(str, list(real_mat[:, jj]))))
                        str_c = " ".join(list(map(str, list(imag_mat[:, jj]))))

                        fh.write(str_r + "\n")
                        fh.write(str_c + "\n")

                else:
                    fh.write("R\n")

                    for jj in range(real_mat.shape[1]):
                        str_r = " ".join(list(map(str, list(real_mat[:, jj]))))

                        fh.write(str_r + "\n")

            self.results_buffer = {}


class TNObsCorr4(TNObsCorr):
    """
    Measure the correlation of four operators. This measurement
    does not do any projections. We skip entries where two
    or more of the four indices match, e.g., `i1 = i2`.

    **Arguments**

    name : str
        Define a label under which we can find the observable in the
        result dictionary.

    operator : list of four strings
        Identifiers / strings for the operators to be measured.

    **Details**

    Restrictions apply in the case of symmetric tensor, where the
    measurement might not be available even if it is available
    without symmetries.
    """

    measurable_ansaetze = ()

    @classmethod
    def empty(cls):
        """
        Documentation see :func:`_TNObsBase.empty`.
        """
        obj = cls(None, None)
        obj.name = []
        obj.operators = []

        return obj

    def collect_operators(self):
        """
        Documentation see :func:`_TNObsBase.collect_operators`.
        """
        for elem in self.operators:
            for operator in elem:
                yield (operator, None)

    def read(self, fh, **kwargs):
        """
        Read the measurements of the correlation observable from fortran.

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

            str_values_r = fh.readline()
            str_values_c = fh.readline()
            real_val = np.array(list(map(float, str_values_r.split())))
            compl_val = np.array(list(map(float, str_values_c.split())))
            vect = real_val + 1j * compl_val
            dim = real_val.shape[0]

            # Build numpy matrix
            res = np.zeros((dim, dim, dim, dim), dtype=vect.dtype)
            res[:, 0, 0, 0] = vect
            first_line = True

            # Now we now the number of entries after reading the
            # first line and (dim - 1) lines are left
            for j4 in range(dim):
                for j3 in range(dim):
                    for j2 in range(dim):
                        if first_line:
                            # We have already read this line
                            first_line = False
                            continue

                        str_values_r = fh.readline()
                        str_values_c = fh.readline()
                        real_val = np.array(list(map(float, str_values_r.split())))
                        compl_val = np.array(list(map(float, str_values_c.split())))
                        res[:, j2, j3, j4] = real_val + 1j * compl_val

            yield elem, res

    def read_hdf5(self, dataset, params):
        """
        Documentation see :func:`_TNObsBase.read_hdf5`.
        """
        raise QTeaLeavesError("This observables cannot read HDF5 files yet.")

    def write_results(self, fh, state_ansatz, **kwargs):
        """
        See :func:`_TNObsBase.write_results`.
        """
        is_measured = self.check_measurable(state_ansatz)

        # Write separator first
        fh.write("-" * 20 + "tnobscorr4\n")
        # Assignment for the linter
        _ = fh.write("T \n") if is_measured else fh.write("F \n")

        if is_measured:
            for name_ii in self.name:
                # Write column by column because this is favored
                # by the fortran memory

                corr_mat = self.results_buffer[name_ii]
                real_mat = np.real(corr_mat)
                imag_mat = np.imag(corr_mat)

                dim = real_mat.shape[1]
                for j4 in range(dim):
                    for j3 in range(dim):
                        for j2 in range(dim):
                            map_r = map(str, list(real_mat[:, j2, j3, j4]))
                            map_c = map(str, list(imag_mat[:, j2, j3, j4]))

                            str_r = " ".join(list(map_r))
                            str_c = " ".join(list(map_c))

                            fh.write(str_r + "\n")
                            fh.write(str_c + "\n")

            self.results_buffer = {}
