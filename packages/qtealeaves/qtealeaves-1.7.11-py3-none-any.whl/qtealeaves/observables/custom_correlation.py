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
Custom observable
"""

# pylint: disable=too-many-locals
# pylint: disable=too-many-instance-attributes

import numpy as np

from qtealeaves.mpos import ITPO, DenseMPO, DenseMPOList, MPOSite
from qtealeaves.tooling import QTeaLeavesError, map_selector

from .tnobase import _TNObsBase

__all__ = ["TNObsCustom"]


class TNObsCustom(_TNObsBase):
    """
    The custom observable measures the term of arbitrary size over the arbitrary
    positions. Thus, the observable is of type ``<A_i B_j ... C_k>``. The
    results are stored in 1D array, with the order as provided in input.
    All operators in the measured n-body term must be placed on different
    sites, i != j != ... != k".

    If the system is 2d or 3d, user can provide the positions of measurements
    either in the already flattened, i.e. 1d indexing, or as 2d/3d indexing.
    In the latter case, additional arguments (see below) must be provided.


    Arguments
    ---------

    name : str
        Define a label under which we can find the observable in the
        result dictionary.

    operators : list (of length term_size) of strings
        Identifiers/strings for the operators to be measured.

    site_indices : list of lists
        On which sites we want to measure specified operators. E.g.
        if we want to measure 2-body correlators on sites [1,2] and [3,4],
        `site_indices=[[1,2],[3,4]]`.
        REMARK: counting starts at 0.

    batch_size : int | None, optional
        None measures with a single iTPO. Any integer will be interpreted
        as batch size after every batch_size entries a new iTPO is created.
        The batch size addresses the problem of memory needs of the iTPO
        correlation measurement with all terms at once; lower batch sizes
        reduce the memory cost and increasing the computational cost to
        some extent.
        Default to None (Measure all correlations in one iTPO).

    **If working with 2d/3d systems:**

    dim : 1, 2, or 3, optional
        Dimensionality of the lattice (1d, 2d, 3d)
        Default is 1.
    mapping : string or instance of :py:class:`HilbertCurveMap`, optional
        If dim != 1, which 2d/3d to 1d mapping to use. Possible inputs are:
        'HilbertCurveMap', 'SnakeMap', and 'ZigZagMap'.
        Default is 'HilbertCurveMap'.
    lattice : list, optional
        If working with 2d or 3d systems, a lattice size must be given to
        compute the corresponding mapping to 1d.
    """

    # pylint: disable-next=too-many-arguments
    def __init__(
        self,
        name,
        operators,
        site_indices,
        batch_size=None,
        dim=1,
        mapping="HilbertCurveMap",
        lattice=None,
    ):
        super().__init__(name)
        self.measurable_ansaetze = ("MPS", "TTN", "TTO", "ATTN")
        if operators is not None:
            # how many sites per observable term, e.g. two-body or three-body term.
            self.term_size = [len(operators)]
            # max term size if there are more than one custom observable
            # defined in the simulation - look at __iadd__ function
            self.max_term_size = self.term_size[0]
            # run the input checks
            if self.term_size[0] == 1:
                raise ValueError(
                    "We do not measure local terms as a custom correlations."
                )
        else:
            self.term_size = None
            self.max_term_size = None
        self.operators = [operators]
        self.batch_size = [batch_size]

        # handling 2D and 3D
        if (dim is not None) and (site_indices is not None):
            # run the input checks
            if (dim > 1) and (lattice is None):
                raise ValueError(
                    "If lattice dimensionality is >1, the lattice size must "
                    "be given as the input."
                )
            if isinstance(site_indices[0][0], list) and (dim == 1):
                dim_sites = len(site_indices[0][0])
                raise ValueError(
                    f"Dimension of the given site indices input, dim = {dim_sites}, "
                    "does not correspond to the 1d system."
                )

            if dim > 1:
                # if system dimensionality is 2d or 3d, the site indices array needs
                # to be flattened to 1d
                site_indices = self.get_sites_1d(site_indices, dim, lattice, mapping)

        # check if operators match number of specified sites
        if site_indices is not None:
            if any(len(inds) != len(operators) for inds in site_indices):
                raise ValueError(
                    "Must provide one operator per site in measurement positions."
                )
        self.site_indices = site_indices

    @classmethod
    def empty(cls):
        """
        Documentation see :func:`_TNObsBase.empty`.
        """
        obj = cls(None, None, None)
        obj.name = []
        obj.term_size = []
        obj.operators = []
        obj.site_indices = []
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
        if isinstance(other, TNObsCustom):
            self.name += other.name
            if self.max_term_size is not None:
                if other.term_size[0] > self.max_term_size:
                    self.max_term_size = other.term_size[0]
            else:
                self.max_term_size = other.term_size[0]
            self.term_size += other.term_size
            self.operators += other.operators
            self.batch_size += other.batch_size
            self.site_indices.append(other.site_indices)
        else:
            raise QTeaLeavesError("__iadd__ not defined for these types.")

        return self

    def collect_operators(self):
        """
        Documentation see :func:`_TNObsBase.collect_operators`.

        In the case of n-body operators with n>2, we choose that
        the bulk operators have label 'r'. However, note that this has
        limitations if the symmetry number changes.
        """
        for elem in self.operators:
            yield (elem[0], "l")
            for subelem in elem[1:-1]:
                yield (subelem, "r")
            yield (elem[-1], "r")

    def to_itpo(self, operators, tensor_backend, num_sites):
        """
        Return an ITPO representing the custom correlation observable.
        Since custom corr don't handle diagonal terms, the function is same for
        TTN and aTTN.

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
            num_meas = len(self.site_indices[kk])
            for ii in range(num_meas):
                position = self.site_indices[kk][ii]
                if len(position) != len(np.unique(np.array(position))):
                    raise ValueError(
                        "For now cannot measure local (diagonal) terms with "
                        "custom correlations. All sites within a term must "
                        "be different."
                    )
                mpo_sites = []
                for jj, key_op in enumerate(self.operators[kk]):
                    site = MPOSite(
                        position[jj], key_op, 1.0, 1.0, operators=operators, params={}
                    )
                    mpo_sites.append(site)

                dense_mpo = DenseMPO(mpo_sites, tensor_backend=tensor_backend)
                dense_mpo_list.append(dense_mpo)

                # There are two conditions under which we want to yield:
                # 1) If the batch_size is filled.
                # 2) If batch_size is specified, and we are in the last point of the iteration.
                # The second enforces that each custom correlation is measured separately.
                # We assume this makes sense if the user asks for batches.
                condition1 = len(dense_mpo_list) == self.batch_size[kk]
                condition2 = self.batch_size[kk] is not None and ii == num_meas - 1
                if condition1 or condition2:
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

    def get_sites_1d(self, site_indices, dim, lattice, mapping):
        """
        In the case of 2D, or 3D input of the measurement position sites,
        give back the flattened (mapped to 1d) array for measurement position sites.

        Parameters
        ----------
        site_indices : list of measurement positions
            On which sites we want to measure specified operators.
            REMARK: counting starts at 0.
        dim : 2 or 3
            Dimensionality of the lattice (2d, 3d)
        lattice : list, optional
            Lattice size.
        mapping : string or instance of :py:class:`HilbertCurveMap`
            If dim != 1, which 2d/3d to 1d mapping to use. Possible inputs are:
            'HilbertCurveMap', 'SnakeMap', and 'ZigZagMap'.
        """
        # get the mapping
        map_indices = map_selector(dim, lattice, mapping)

        # define the new flattened site index list
        site_indices_flattened = []
        for sites in site_indices:
            # get the sites for each subterm
            sites_ii = []
            for ii in range(self.term_size[0]):
                sites_ii.append(map_indices[tuple(sites[ii])])
            site_indices_flattened.append(sites_ii)

        return site_indices_flattened

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

        ii = 0
        for elem in self.name:
            if is_measured:
                # get how many subterms are measured within each measurement
                num_sites_measured = len(self.site_indices[ii])
                # check if results are real or complex
                realcompl = fh.readline()

                if "C" in realcompl:
                    # first read the results as list of strings
                    str_values_r = []
                    str_values_c = []
                    for _ in range(num_sites_measured):
                        str_values_r.append(fh.readline())
                        str_values_c.append(fh.readline())
                    # convert back to float values
                    real_val = np.array(list(map(float, str_values_r)))
                    compl_val = np.array(list(map(float, str_values_c)))
                    # combine them into the complex array
                    res = real_val + 1j * compl_val

                    yield elem, res

                if "R" in realcompl:
                    # first read the results as list of strings
                    str_values_r = []
                    for _ in range(num_sites_measured):
                        str_values_r.append(fh.readline())
                    # convert back to float values
                    res = np.array(list(map(float, str_values_r)))

                    yield elem, res
                ii += 1
            else:
                yield elem, None

    def write_results(self, fh, state_ansatz, **kwargs):
        """
        See :func:`_TNObsBase.write_results`.
        """
        is_measured = self.check_measurable(state_ansatz)

        # Write separator first
        fh.write("-" * 20 + "tnobscustom\n")
        # Assignment for the linter
        _ = fh.write("T \n") if is_measured else fh.write("F \n")

        if is_measured:
            for name_ii in self.name:
                # get the real and imaginary part of results array
                res = self.results_buffer[name_ii]
                res_real = np.real(res)
                res_imag = np.imag(res)

                num_sites_measured = len(res_real)
                # write if is complex
                if np.any(np.abs(res_imag) > 1e-12):
                    # results are imaginary
                    fh.write("C\n")

                    # write both real and imaginary results term by term
                    for ii in range(num_sites_measured):
                        str_r = str(res_real[ii])
                        str_i = str(res_imag[ii])
                        fh.write(str_r + "\n")
                        fh.write(str_i + "\n")
                else:
                    # results are real
                    fh.write("R\n")
                    # write just the real parts
                    for ii in range(num_sites_measured):
                        str_r = str(res_real[ii])
                        fh.write(str_r + "\n")
            self.results_buffer = {}
