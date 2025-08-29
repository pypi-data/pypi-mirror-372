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
Abstract class for tensors. Represents all the functions that should be
implemented in a tensor.

We provide two tensor types:

* :class:`_AbstractQteaTensor` : suitable for simulation
* :class:`_AbstractQteaBaseTensor` : suitable for simulation and
  suitable to be the base tensor type for a symmetric tensor.

"""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-branches
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-lines

import abc
import logging
import os
import string
from typing import Self

import numpy as np

from qtealeaves.tooling import QTeaLeavesError
from qtealeaves.tooling.devices import _CPU_DEVICE, _GPU_DEVICE
from qtealeaves.tooling.mpisupport import MPI

__all__ = [
    "_AbstractQteaTensor",
    "_AbstractQteaBaseTensor",
    "_AbstractDataMover",
    "_parse_block_size",
]

logger = logging.getLogger(__name__)


logger = logging.getLogger(__name__)


class _AbstractQteaTensor(abc.ABC):
    """
    Tensor for Quantum Tea simulations.

    **Arguments**

    links : list
        Type of entries in list depends on tensor type and are either
        integers for dense tensors or some LinkType for symmetric
        tensors.

    ctrl : str, optional
        Initialization of tensor.
        Default to "Z"

    are_links_outgoing : list of bools
        Used in symmetric tensors only: direction of link in tensor.
        Length is same as rank of tensor.

    base_tensor_cls : valid dense quantum tea tensor or `None`
        Used in symmetric tensors only: class representing dense tensor

    dtype : data type, optional
        Valid data type for the underlying tensors.

    device : device specification, optional
        Valid device specification (depending on tensor).
    """

    has_symmetry = False

    @abc.abstractmethod
    def __init__(
        self,
        links,
        ctrl="Z",
        are_links_outgoing=None,
        base_tensor_cls=None,
        dtype=None,
        device=None,
    ):
        pass

    # --------------------------------------------------------------------------
    #                               Properties
    # --------------------------------------------------------------------------

    @property
    @abc.abstractmethod
    def are_links_outgoing(self):
        """Define property of outgoing links as property (always False)."""

    @property
    @abc.abstractmethod
    def base_tensor_cls(self):
        """Base tensor class."""

    @property
    @abc.abstractmethod
    def device(self):
        """Device where the tensor is stored."""

    @property
    @abc.abstractmethod
    def dtype(self):
        """Data type of the underlying arrays."""

    @property
    @abc.abstractmethod
    def dtype_eps(self):
        """Data type's machine precision of the underlying arrays."""

    @property
    @abc.abstractmethod
    def linear_algebra_library(self):
        """Specification of the linear algebra library used as string."""

    @property
    @abc.abstractmethod
    def links(self):
        """Specification of link with full information to reconstruct link."""

    @property
    @abc.abstractmethod
    def ndim(self):
        """Rank of the tensor."""

    @property
    @abc.abstractmethod
    def shape(self):
        """Dimension of tensor along each dimension."""

    # --------------------------------------------------------------------------
    #                    Data type tooling beyond properties
    # --------------------------------------------------------------------------

    @abc.abstractmethod
    def dtype_from_char(self, dtype):
        """Resolve data type from chars C, D, S, Z and optionally H."""

    def dtype_mpi(self, query=None):
        """
        Resolve the dtype for sending tensors via MPI.

        Arguments
        ---------

        query : char | str | None, optional
            Return the MPI data type for the tensor itself or for
            the query passed, i.e., if not `None`. Query must be
            a character or string `real` return the MPI data type
            for the same precision as self, but real arithmetic.
            Default to `None` (`self.dtype_to_char()`)
        """
        if query is None:
            query = self.dtype_to_char()
        elif len(query) > 1:
            dtype_char = self.dtype_to_char()
            query = {"Z": "D", "C": "S"}.get(dtype_char, dtype_char)
        return {
            # pylint: disable=c-extension-no-member
            "Z": MPI.DOUBLE_COMPLEX,
            "C": MPI.COMPLEX,
            "S": MPI.REAL,
            "D": MPI.DOUBLE_PRECISION,
            "I": MPI.INT,
            # pylint: enable=c-extension-no-member
        }[query]

    def dtype_real(self):
        """
        Get the data type at the same precision which represents real numbers.

        Returns
        -------

        dtype : class for corresponding backend.
            The data type will be determined via the mapping of the char data
            types C -> S, D -> D, S -> S, Z -> D, H -> H, I -> I.
        """
        dtype_char = self.dtype_to_char()
        dtype_char = {"Z": "D", "C": "S"}.get(dtype_char, dtype_char)
        return self.dtype_from_char(dtype_char)

    def dtype_to_char(self):
        """
        Translate current data type of the tensor back to char C, D, S, Z, H, or I.

        Returns
        -------

        char : represent data type as a single letter.
        """
        for elem in ["D", "S", "H", "Z", "C", "I"]:
            if self.dtype == self.dtype_from_char(elem):
                return elem

        raise ValueError(f"Could not resolve data type to char with {self.dtype}.")

    # --------------------------------------------------------------------------
    #                Overwritten operators (alphabetically)
    # --------------------------------------------------------------------------

    @abc.abstractmethod
    def __add__(self, other):
        """
        Addition of a scalar to a tensor adds it to all the entries.
        If other is another tensor, elementwise addition if they have the same shape
        """

    def __eq__(self, other):
        """Checking equal tensors up to tolerance."""

        # If the tensors are on separate devices, move other to
        # the device of self for the comparison.
        tmp_other_device = other.device
        other.convert(device=self.device)
        if other.device != tmp_other_device:
            logger.warning(
                "Switching tensor device on the fly in __eq__. (%s -> %s)",
                tmp_other_device,
                other.device,
            )
        compare = self.are_equal(other)

        # move back
        other.convert(device=tmp_other_device)

        return compare

    @abc.abstractmethod
    def __iadd__(self, other):
        """In-place addition of tensor with tensor or scalar (update)."""

    @abc.abstractmethod
    def __imul__(self, scalar):
        """In-place multiplication of tensor with scalar (update)."""

    @abc.abstractmethod
    def __itruediv__(self, sc):
        """In-place division of tensor with scalar (update)."""

    def __matmul__(self, other):
        """Matrix multiplication as contraction over last and first index of self and other."""
        idx = self.ndim - 1
        return self.tensordot(other, ([idx], [0]))

    @abc.abstractmethod
    def __mul__(self, scalar):
        """Multiplication of tensor with scalar returning new tensor as result."""

    def __ne__(self, other):
        """Checking not equal tensors up to tolerance."""
        return not self.are_equal(other)

    @abc.abstractmethod
    def __neg__(self):
        """Negative of a tensor returned as a new tensor."""

    def __rmul__(self, scalar):
        """Multiplication from the right of a scalar"""
        return self * scalar

    def __rsub__(self, other):
        """Subtraction of two tensors "other - self". For efficient method, overwrite."""
        # If both are tensors, the multiplication with (-1) can be saved, but
        # that should be it.
        new = self.copy()
        new *= -1.0
        new += other
        return new

    @abc.abstractmethod
    def __sub__(self, other):
        """Subtraction of two tensors."""

    # --------------------------------------------------------------------------
    #                       classmethod, classmethod like
    # --------------------------------------------------------------------------

    @staticmethod
    @abc.abstractmethod
    def convert_operator_dict(
        op_dict,
        params=None,
        symmetries=None,
        generators=None,
        base_tensor_cls=None,
        dtype=None,
        device=None,
    ):
        """
        Iterate through an operator dict and convert the entries.

        **Arguments**

        op_dict : instance of :class:`TNOperators`
            Contains the operators as xp.ndarray.

        symmetries:  list, optional, for compatability with symmetric tensors.
            For symmetry, contains symmetries.
            Otherwise, must be empty list.

        generators : list, optional, for compatability with symmetric tensors.
            For symmetries, contains generator of the symmetries as str for dict.
            Must be empty list.

        base_tensor_cls : None, optional, for compatability with symmetric tensors.
            For symmetries, must be valid base tensor class.
            Otherwise, no checks on this one here.

        dtype : data type for xp, optional
            Specify data type.

        device : str
            Device for the simulation. Typically "cpu" and "gpu", but depending on
            tensor backend.
        """

    @abc.abstractmethod
    def copy(self, dtype=None, device=None):
        """Make a copy of a tensor."""

    @abc.abstractmethod
    def eye_like(self, link):
        """
        Generate identity matrix.

        **Arguments**

        self : instance of :class:`QteaTensor`
            Extract data type etc from this one here.

        link : same as returned by `links` property.
            Dimension of the square, identity matrix.
        """

    @classmethod
    @abc.abstractmethod
    def mpi_bcast(cls, tensor, comm, tensor_backend, root=0):
        """
        Broadcast tensor via MPI.
        """

    @classmethod
    @abc.abstractmethod
    def mpi_recv(cls, from_, comm, tensor_backend):
        """
        Send tensor via MPI.

        **Arguments**

        from_ : integer
            MPI process to receive tensor from.

        comm : instance of MPI communicator to be used

        tensor_backend : instance of :class:`TensorBackend`
        """

    @abc.abstractmethod
    def random_unitary(self, links):
        """
        Generate a random unitary tensor via performing a SVD on a
        random tensor, where a matrix dimension is specified with
        `links`. Tensor will be of the structure
        [link[0], .., link[-1], link[0], .., link[-1]].
        """

    def unitary_like(self, first_column):
        """
        Generates a unitary tensor of the same shape as self.
        Reshapes self into a rank-2 tensor, and generates
        a corresponding unitary matrix.

        **Arguments**

        first_column : int
            All links up to this one are merged into the first leg,
            the others go to the second.
            For a 4-legged tensor, use first_column=2.

        **Details**

        For complex datatype,
        For real, we cannot rely on the exponent. Thus, we do a QR and
        discard the Q. R is unitary, and related to the inital matrix.
        Actually (by Frobenius norm) the closest unitary to
        a given matrix is obtained through SVD.
        This functionality is not implemented yet.
        """
        if self.is_dtype_complex():
            strfunc = "expm"
            kwargs = {"prefactor": 1j}
        else:
            strfunc = "q_from_qr"
            kwargs = {}

        return self.matrix_function(first_column, strfunc, **kwargs)

    @abc.abstractmethod
    def randomize(self, noise=None):
        """
        Randomizes the entries of self.
        noise : float | None The amount of noise added. None randomizes completely.
        """

    @classmethod
    @abc.abstractmethod
    def read(cls, filehandle, dtype, device, base_tensor_cls, cmplx=True, order="F"):
        """Read a tensor from file."""

    @staticmethod
    @abc.abstractmethod
    def dummy_link(example_link):
        """Construct a dummy link. This method is particularly important for symmetries."""

    @staticmethod
    @abc.abstractmethod
    def set_missing_link(links, max_dim, are_links_outgoing=None, restrict_irreps=None):
        """Calculate the property of a missing link in a list.

        **Arguments**

        links : list
            Contains data like returned by property `links`, except
            for one element being `None`

        max_dim : int
            Maximal dimension of link allowed by convergence parameters
            or similar.

        are_links_outgoing : list of bools
            Indicates link direction for symmetry tensors only.

        restrict_irreps : :class:`IrrepListing` | None
            All irreps from here will remain in the link. Irreps
            which are here but not in the link, will not be added.
            Degeneracies will be calculated based on the minimum
            of the two. Always ignored for tensors without symmetry.
            Default to `None` (no irreps are dropped).
        """

    @abc.abstractmethod
    def zeros_like(self, requires_grad=False):
        """Get a tensor with the same links as `self` but filled with zeros."""

    @abc.abstractmethod
    def stream(self, disable_streams=False):
        """Define a stream for any operation

        Parameters
        ----------

        disable_streams : bool, optional
            Allows to disable streams to avoid nested creation of
            streams. Globally, streams should be disabled via the
            `set_streams_*` function of the corresponding base tensor module.
            Default to False.

        Returns
        -------

        Context manager, e.g.,
        :class:`Stream` if stream exists for tensor backend
        :class:`nullcontext(AbstractContextManager)` otherwise

        """

    # --------------------------------------------------------------------------
    #                            Checks and asserts
    # --------------------------------------------------------------------------

    @abc.abstractmethod
    def are_equal(self, other, tol=1e-7):
        """Check if two tensors are equal."""

    def assert_identical_irrep(self, link_idx):
        """Assert that specified link is identical irreps."""
        if not self.is_identical_irrep(link_idx):
            raise QTeaLeavesError(f"Link at {link_idx} is no identical irrep.")

    @abc.abstractmethod
    def assert_identity(self, tol=1e-7):
        """Check if tensor is an identity matrix."""

    def assert_normalized(self, tol=1e-7):
        """Raise exception if norm is not 1 up to tolerance."""
        norm = self.norm()

        if abs(norm - 1.0) > tol:
            raise QTeaLeavesError("Violating normalization condition.")

    def assert_unitary(self, links, tol=1e-7):
        """Raise exception if tensor is not unitary up to tolerance for given links."""
        ctensor = self.conj().tensordot(self, (links, links))
        # reshape into a matrix to check if identity
        half_links = len(ctensor.links) // 2
        ctensor.fuse_links_update(0, half_links - 1)
        ctensor.fuse_links_update(1, half_links)

        ctensor.assert_identity(tol=tol)

    def assert_rank_2(self):
        """
        Enforce that the matrix is rank 2.
        """
        if self.ndim != 2:
            raise QTeaLeavesError(
                f"Enforcing a rank 2 tensor, but got rank {self.ndim}."
            )

    @abc.abstractmethod
    def is_close_identity(self, tol=1e-7):
        """Check if rank-2 tensor is close to identity."""

    def is_cpu(self, query=None):
        """
        Check if device is CPU or not.

        Parameters
        ----------

        query : str | None, optional
            If given, check for this string. If `None`, self.device
            will be checked.
            Default to None.

        Returns
        -------

        is_cpu : bool
            True if device is a CPU.
        """
        return self.is_cpu_static(self.device if query is None else query)

    @staticmethod
    def is_cpu_static(device_str):
        """
        Check if device is CPU or not.

        Parameters
        ----------

        device_str : str
            Check for this string if it corresponds to a CPU.

        Returns
        -------

        is_cpu : bool
            True if device is a CPU.
        """
        return device_str.startswith(_CPU_DEVICE)

    def is_dtype_complex(self):
        """Check if data type is complex."""
        return self.dtype_to_char() in ["C", "Z"]

    def is_gpu(self, query=None):
        """
        Check if device is GPU or not.

        Parameters
        ----------

        query : str | None, optional
            If given, check for this string. If `None`, self.device
            will be checked.
            Default to None.

        Returns
        -------

        is_gpu : bool
            True if device is a GPU.

        """
        return self.is_gpu_static(self.device if query is None else query)

    @staticmethod
    def is_gpu_static(device_str):
        """
        Check if device is GPU or not.

        Parameters
        ----------

        device_str : str
            Check for this string if it is a GPU device.

        Returns
        -------

        is_gpu : bool
            True if device is a GPU.
        """
        if device_str is None:
            # Device string None is not a GPU as far as we can tell
            # This can happen on empty symmetric tensors returning
            # `None` as device, maybe "cpu" would be better for an
            # empty tensor as device does matters less.
            return False

        return device_str.startswith(_GPU_DEVICE)

    @abc.abstractmethod
    def is_identical_irrep(self, link_idx):
        """Check that the link at `link_idx` is identical irrep."""

    @abc.abstractmethod
    def is_implemented_device(self, query):
        """Check if argument query is an implemented device."""

    @abc.abstractmethod
    def is_link_full(self, link_idx):
        """Check if the link at given index is at full bond dimension."""

    def sanity_check(self):
        """Quick set of checks for tensor."""
        return

    @staticmethod
    # pylint: disable-next=unused-argument
    def free_device_memory(device=None):
        """
        Free the unused device memory that is otherwise occupied by the cache.
        This method SHOULD NOT free memory allocated for the computation.

        Parameters
        ----------

        device : str | None
            If present, i.e., not None, only the corresponding device will
            be freed. The device is a string, e.g., "gpu:0"
        """
        return

    # --------------------------------------------------------------------------
    #                       Single-tensor operations
    # --------------------------------------------------------------------------

    @abc.abstractmethod
    def attach_dummy_link(self, position, is_outgoing=True):
        """Attach dummy link at given position (inplace update)."""

    @abc.abstractmethod
    def conj(self):
        """Return the complex conjugated in a new tensor."""

    @abc.abstractmethod
    def conj_update(self):
        """Apply the complex conjugate to the tensor in place."""

    @abc.abstractmethod
    def convert(self, dtype=None, device=None, stream=None):
        """Convert underlying array to the specified data type inplace."""

    @abc.abstractmethod
    def convert_singvals(self, singvals, dtype=None, device=None, stream=None):
        """Convert the singular values via a tensor."""

    @abc.abstractmethod
    def eig_api(
        self, matvec_func, links, conv_params, args_func=None, kwargs_func=None
    ):
        """Interface to hermitian eigenproblem"""

    @abc.abstractmethod
    def einsum(self, einsum_str, *others):
        """
        Call to einsum with `self` as first tensor.

        Arguments
        ---------

        einsum_str : str
            Einsum contraction rule.

        other: List[:class:`_AbstractQteaTensors`]
            2nd, 3rd, ..., n-th tensor in einsum rule as
            positional arguments. Entries must be of same
            instance as `self`.

        Results
        -------

        tensor : :class:`_AbstractQteaTensor`
            Contracted tensor according to the einsum rules.

        Details
        -------

        The call ``np.einsum(einsum_str, x.elem, y.elem, z.elem)`` translates
        into ``x.einsum(einsum_str, y, z)`` for x, y, and z being
        :class:`QteaTensor`. Similar holds for other derivates and backend
        libraries.
        """

    @abc.abstractmethod
    def fuse_links_update(self, fuse_low, fuse_high, is_link_outgoing=True):
        """Fuses one set of links to a single link (inplace-update)."""

    @abc.abstractmethod
    def get_of(self, variable):
        """Run the get method to transfer to host on variable (same device as self)."""

    @abc.abstractmethod
    def getsizeof(self):
        """Size in memory (approximate, e.g., without considering small meta data)."""

    @abc.abstractmethod
    def get_entry(self):
        """Get entry if scalar on host."""

    # pylint: disable-next=unused-argument
    def flip_links_update(self, link_inds):
        """Flip irreps on given links (symmetric tensors only)."""
        return self

    @abc.abstractmethod
    def mpi_send(self, to_, comm):
        """
        Send tensor via MPI.

        **Arguments**

        to : integer
            MPI process to send tensor to.

        comm : instance of MPI communicator to be used
        """

    @abc.abstractmethod
    def norm(self):
        """Calculate the norm of the tensor <tensor|tensor>."""

    @abc.abstractmethod
    def norm_sqrt(self):
        """Calculate the square root of the norm of the tensor <tensor|tensor>."""

    @abc.abstractmethod
    def normalize(self):
        """Normalize tensor with sqrt(<tensor|tensor>)."""

    @abc.abstractmethod
    def remove_dummy_link(self, position):
        """Remove the dummy link at given position (inplace update)."""

    @abc.abstractmethod
    def restrict_irreps(self, link_idx, sector):
        """Restrict, i.e., project, link to a sector (needed for symmetric tensors)."""

    @abc.abstractmethod
    def scale_link(self, link_weights, link_idx, do_inverse=False):
        """Scale tensor along one link at `link_idx` with weights. Can do inverse, too."""

    @abc.abstractmethod
    def scale_link_update(self, link_weights, link_idx, do_inverse=False):
        """Scale tensor along one link at `link_idx` with weights (inplace update)."""

    @abc.abstractmethod
    def set_diagonal_entry(self, position, value):
        """Set the diagonal element in a rank-2 tensor (inplace update)"""

    @abc.abstractmethod
    def set_matrix_entry(self, idx_row, idx_col, value):
        """Set element in a rank-2 tensor (inplace update)"""

    @abc.abstractmethod
    def split_link_deg_charge(self, link_idx):
        """
        Split a link into two, where one carries the degeneracy, the other the charge.

        Arguments
        ---------

        link_idx : int
            Link to be split.

        Returns
        -------

        :class:`_AbstractQteaTensor`
            New tensor with link at position `link_idx` split into two
            links at `link_idx` (degeneracy) and `link_idx + 1` (charge).
            Links originally after `link_idx` follow shifted by one index.
        """

    @abc.abstractmethod
    def to_dense(self, true_copy=False):
        """Return dense tensor (if `true_copy=False`, same object may be returned)."""

    @abc.abstractmethod
    def to_dense_singvals(self, s_vals, true_copy=False):
        """Convert singular values to dense vector without symmetries."""

    @abc.abstractmethod
    def trace(self, return_real_part=False, do_get=False):
        """Take the trace of a rank-2 tensor."""

    @abc.abstractmethod
    def trace_one_dim_pair(self, links):
        """Trace a pair of links with dimenion one. Inplace update."""

    @abc.abstractmethod
    def transpose(self, permutation):
        """Permute the links of the tensor and return new tensor."""

    @abc.abstractmethod
    def transpose_update(self, permutation):
        """Permute the links of the tensor inplace."""

    @abc.abstractmethod
    def write(self, filehandle, cmplx=None):
        """Write tensor."""

    @abc.abstractmethod
    def matrix_function(self, first_column, function_attr_str, **func_kwargs):
        """
        Apply a matrix function to the rank-n tensor by reshaping it into a bipartition
        of legs. Result of matrix function must be exactly one matrix of the same size.

        **Details**

        Currently, we support the following functions:

        * `expm` to take the matrix exponential
        * `q_from_qr` to generate unitary matrices
        * `randomize` to randomize an existing tensor (on the existing cs in the
          symmetric version here). Randomize as matrix function can create new
          blocks in the block-diagonal blocks which were zero before.
        * `copy` as identity operation.
        """

    # --------------------------------------------------------------------------
    #                         Two-tensor operations
    # --------------------------------------------------------------------------

    @abc.abstractmethod
    def add_update(self, other, factor_this=None, factor_other=None):
        """
        Inplace addition as `self = factor_this * self + factor_other * other`.
        """

    @abc.abstractmethod
    def dot(self, other):
        """Inner product of two tensors <self|other>."""

    @abc.abstractmethod
    def kron(self, other, idxs=None):
        """
        Perform the kronecker product between two tensors.
        By default, do it over all the legs, but you can also
        specify which legs should be kroned over.
        The legs over which the kron is not done should have
        the same dimension.
        """

    @abc.abstractmethod
    def expand_link_tensorpair(self, other, link_self, link_other, new_dim, ctrl="R"):
        """Expand the link between a pair of tensors based on the ctrl parameter. "R" for random"""

    @abc.abstractmethod
    def split_qr(
        self,
        legs_left,
        legs_right,
        perm_left=None,
        perm_right=None,
        is_q_link_outgoing=True,
        disable_streams=False,
    ):
        """Split the tensor via a QR decomposition."""

    @abc.abstractmethod
    def split_qrte(
        self,
        tens_right,
        singvals_self,
        operator=None,
        conv_params=None,
        is_q_link_outgoing=True,
    ):
        """Split via a truncated expanded QR."""

    def split_rq(
        self,
        legs_left,
        legs_right,
        perm_left=None,
        perm_right=None,
        is_q_link_outgoing=True,
        disable_streams=False,
    ):
        """
        Split the tensor via a RQ decomposition. The abstract class defines the RQ
        via a QR and permutation of legs, but we highly recommend overwriting this
        approach with an actual RQ.

        Parameters
        ----------

        self : instance of :class:`_AbstractQteaTensor`
            Tensor upon which apply the RQ
        legs_left : list of int
            Legs that will compose the rows of the matrix (and the R matrix)
        legs_right : list of int
            Legs that will compose the columns of the matrix (and the Q matrix)
        perm_left : list of int | None, optional
            permutations of legs after the QR on left tensor
            Default to `None` (no permutation)
        perm_right : list of int | None, optional
            permutation of legs after the QR on right tensor
            Default to `None` (no permutation)
        is_q_link_outgoing : int, optional
            Direction of link, placeholder for symmetric tensors.
            Default to True.
        disable_streams : boolean, optional
            Can disable streams to avoid nested generation of streams.

        Returns
        -------

        tens_left: instance of :class:`_AbstractQteaTensor`
            upper triangular tensor after the RQ, i.e., R
        tens_right: instance of :class:`_AbstractQteaTensor`
            unitary tensor after the RQ, i.e., Q.
        """
        tens_q, tens_r = self.split_qr(
            legs_right,
            legs_left,
            is_q_link_outgoing=is_q_link_outgoing,
            disable_streams=disable_streams,
        )

        # Permute into RQ order
        perm_r = list(range(1, len(legs_left) + 1)) + [0]
        perm_q = [len(legs_right)] + list(range(len(legs_right)))

        if perm_left is not None:
            # User requests for permutation + RQ order
            nn = len(perm_left)
            perm_left = [0 if ii == nn - 1 else ii + 1 for ii in perm_left]
            tens_r.transpose_update(perm_left)
        else:
            # Permute into RQ order
            tens_r.transpose_update(perm_r)

        if perm_right is not None:
            # User requests for permutation + RQ order
            nn = len(perm_right)
            perm_right = [nn - 1 if ii == 0 else ii - 1 for ii in perm_right]
            tens_q.transpose_update(perm_right)
        else:
            # Permute into RQ order
            tens_q.transpose_update(perm_q)

        return tens_r, tens_q

    @abc.abstractmethod
    def split_svd(
        self,
        legs_left,
        legs_right,
        perm_left=None,
        perm_right=None,
        contract_singvals="N",
        conv_params=None,
        no_truncation=False,
        is_link_outgoing_left=True,
        disable_streams=False,
    ):
        """Split tensor via SVD for a bipartion of links."""

    @abc.abstractmethod
    def stack_link(self, other, link):
        """Stack two tensors along a given link."""

    @abc.abstractmethod
    def stack_first_and_last_link(self, other):
        """
        Stack first and last link of tensor targeting MPS addition.

        Parameters
        ----------

        other : :class:`_AbstractQteaTensor` (same type as self)
            Second tensor to be stacked onto self for first and last link.

        Returns
        -------

        stacked_tensor : :class:`_AbstractQteaTensor` (same type as self)
            New tensor with dimension d1 = s1 + o1, d2 = s2 = o2, d3 = s3 + o3.
            The dimensions of self are (s1, s2, s3) and the dimensions of
            other are (o1, o2, o3).
        """

    @abc.abstractmethod
    def tensordot(self, other, contr_idx, disable_streams=False):
        """Tensor contraction of two tensors along the given indices."""

    # --------------------------------------------------------------------------
    #                        Internal methods
    # --------------------------------------------------------------------------

    def _invert_link_selection(self, links):
        """Invert the selection of links and return them as a list."""
        ilinks = [ii if (ii not in links) else None for ii in range(self.ndim)]
        ilinks = list(filter(_func_not_none, ilinks))
        return ilinks

    @staticmethod
    def _split_checks_links(legs_left, legs_right):
        """
        Check if bipartition is there and if links are sorted.

        **Returns**

        is_good_bipartition : bool
            True if all left legs before right legs

        is_sorted_l : bool
            True if left legs are already sorted

        is_sorted_r : bool
            True if right legs are already sorted.
        """
        legs_l = np.array(legs_left)
        legs_r = np.array(legs_right)
        is_good_bipartition = np.max(legs_l) < np.min(legs_r)
        is_sorted_l = (
            True if (legs_l.ndim < 2) else np.all(legs_l[1:] - legs_l[:-1] > 0)
        )
        is_sorted_r = (
            True if (legs_r.ndim < 2) else np.all(legs_r[1:] - legs_r[:-1] > 0)
        )

        return is_good_bipartition, is_sorted_l, is_sorted_r

    @staticmethod
    def _einsum_for_kron(self_shape, other_shape, idxs):
        """
        Return the einstein notation summation for the
        kronecker operation between two tensors along
        the indeces idxs

        Parameters
        ----------
        self_shape : Tuple[int]
            Shape of the first tensor
        other_shape : Tuple[int]
            Shape of the second tensor
        idxs : Tuple[int]
            Indexes over which to perform the kron.
            If None, kron over all indeces.

        Returns
        -------
        str
            The einstein notation expression for einsum
        Tuple[int]
            The shape of the output
        """
        self_ndim = len(self_shape)
        other_ndim = len(other_shape)

        final_shape = np.array(self_shape) * np.array(other_shape)
        # Getting the maximum number of indexes required for einsum
        alphabet = list(map(chr, range(97, 97 + self_ndim + len(other_shape))))
        # The first ndim letters are for the first tensor
        letters_left = np.array(alphabet[:self_ndim], dtype=str)
        letters_right = np.array(
            alphabet[self_ndim : self_ndim + other_ndim], dtype=str
        )
        # Adjust the letters in case some index should be not kronned over
        if idxs is not None:
            not_idxs = np.setdiff1d(np.arange(self_ndim), idxs)
            letters_right[not_idxs] = letters_left[not_idxs]
            final_shape[not_idxs] = np.array(self_shape)[not_idxs]
        # Create the subscripts. The formula will look something like:
        # ijk,lmn->iljmkn if all the indexes are kronned over
        # ijk,ljn->iljkn if for example only indexes [0, 2] are kronned
        subscripts = "".join(letters_left) + "," + "".join(letters_right) + "->"
        if idxs is not None:
            letters_right[not_idxs] = ""
        subscripts += "".join([ii + jj for ii, jj in zip(letters_left, letters_right)])

        return subscripts, final_shape


class _AbstractQteaBaseTensor(_AbstractQteaTensor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._elem = None

    # --------------------------------------------------------------------------
    #                Overwritten operators (alphabetically)
    # --------------------------------------------------------------------------
    def __getitem__(self, item) -> Self:
        """Get a slice from tensor. If the underlying algebra library supports it,
        the slice will be a view of the original tensor. Otherwise, a copy will be returned.

        **Arguments**
        item : slice
            Slice to be applied to the tensor.

        **Returns**

        """

        # this can be a view or a copy. For numpy and cupy, it is a view
        # when using basic indexing and a copy when using advanced indexing.
        # Check https://numpy.org/doc/stable/user/basics.indexing.html
        # Ellipse is added to always return an array (when specifying all
        # indexes numpy would return a scalar)

        if isinstance(item, int):
            item = (item,)
        if isinstance(item, tuple):
            item += (...,)
        new_elem = self._elem[item]
        new_tensor = self.from_elem_array(
            new_elem, dtype=self.dtype, device=self.device
        )

        return new_tensor

    def __setitem__(self, item, value):
        """Set a slice from tensor.

        **Arguments**
        item : slice
            Slice to be applied to the tensor.
        value : array-like, _AbstractQteaBaseTensor
            Value to be set to the slice.
        """
        if isinstance(value, _AbstractQteaBaseTensor):
            value = value.elem

        if value.dtype != self.dtype:
            logger.warning(
                "Setting value(s) with dtype '%s' different from tensor dtype '%s'. "
                + "Truncation may happen",
                value.dtype,
                self.dtype,
            )

        self._elem[item] = value

    # --------------------------------------------------------------------------
    #                          Printing functions
    # --------------------------------------------------------------------------

    def __str__(self):
        """
        Output of print() function.
        """

        return (
            f"{self.__class__.__name__}(\n{self._elem}, "
            f"shape={self.shape}, dtype={self.dtype}, device={self.device})"
        )

    def _repr_html_(self):
        """
        Fancy print of tensor for Jupyter Notebook.
        """
        markdown_str = (
            f"<details><summary>"
            f'<b style="color:#f5b642; font-size:110%; font-family: helvetica">'
            f"{self.__class__.__name__} </b>"
        )
        markdown_str += f'<b style="color:#9c9c9c"> shape=</b>{self.shape},'
        markdown_str += f'<b style="color:#9c9c9c"> shape=</b>{self.shape},'
        markdown_str += f'<b style="color:#9c9c9c"> dtype=</b>{self.dtype},'
        markdown_str += f'<b style="color:#9c9c9c"> device=</b>{self.device}</summary>'
        markdown_str += str(self._elem).replace(chr(10), "<br>").replace(" ", "&nbsp;")

        return markdown_str + "</details>"

    # --------------------------------------------------------------------------
    #                               Properties
    # --------------------------------------------------------------------------

    @property
    def elem(self):
        """The array representing the tensor entries."""
        return self._elem

    @property
    def base_tensor_cls(self):
        """Base tensor class."""
        return type(self)

    # --------------------------------------------------------------------------
    #          Implementations of abstract _AbstractQteaTensor methods
    # --------------------------------------------------------------------------

    @staticmethod
    # pylint: disable-next=unused-argument
    def dummy_link(example_link):
        """Return a dummy link which is always an int for base tensors."""
        return 1

    def expand_link_tensorpair(self, other, link_self, link_other, new_dim, ctrl="R"):
        """
        Expand the link between a pair of tensors. If ctrl="R", the expansion is random

        **Arguments**

        other : instance of :class`QteaTensor`

        link_self : int
            Expand this link in `self`

        link_other : int
            Expand this link in `other`. Link must be a match (dimension etc.)

        ctrl : str, optional
            How to fill the extension. Default to "R" (random)

        **Returns**

        new_this : instance of :class`QteaTensor`
            Expanded version of `self`

        new_other : instance of :class`QteaTensor`
            Expanded version of `other`
        """
        new_this = self.expand_tensor(link_self, new_dim, ctrl=ctrl)
        new_other = other.expand_tensor(link_other, new_dim, ctrl=ctrl)

        return new_this, new_other

    def is_identical_irrep(self, link_idx):
        """Check that the link at `link_idx` is identical irrep."""
        return self.shape[link_idx] == 1

    def is_link_full(self, link_idx):
        """Check if the link at given index is at full bond dimension."""
        links = list(self.links)
        links[link_idx] = None

        links = self.set_missing_link(links, None)

        return self.links[link_idx] >= links[link_idx]

    def randomize(self, noise=None):
        """
        Randomizes the entries of self.

        Parameters
        ----------
        noise : float | None
            The amount of noise added. None randomizes completely.
        """
        obj = self.base_tensor_cls(
            self.shape, ctrl="R", dtype=self.dtype, device=self.device
        )
        if noise is None:
            self._elem = obj.elem
        else:
            self._elem += noise * obj.elem

    def restrict_irreps(self, link_idx, sector):
        """Restrict, i.e., project, link to a sector (needed for symmetric tensors)."""
        if sector is not None:
            raise ValueError("Tensor without symmetries requires sector to be `None`.")

        return self

    @staticmethod
    def set_missing_link(links, max_dim, are_links_outgoing=None, restrict_irreps=None):
        """
        Calculate the property of a missing link in a list.

        **Arguments**

        links : list
            Contains data like returned by property `links`, except
            for one element being `None`

        max_dim : int
            Maximal dimension of link allowed by convergence parameters
            or similar.

        are_links_outgoing : list of bools
            Indicates link direction for symmetry tensors only.

        restrict_irreps : :class:`IrrepListing` | None
            Always ignored for tensors without symmetry.
            Default to `None`.
        """
        dim = 1
        idx = None

        for ii, elem in enumerate(links):
            if elem is None:
                idx = ii
            else:
                dim *= elem

        if max_dim is not None:
            links[idx] = min(dim, max_dim)
        else:
            links[idx] = dim

        return links

    def split_link_deg_charge(self, link_idx):
        """Split a link into two, where one carries the degeneracy, the other the charge."""
        shape = list(self.shape)
        new_shape = shape[: link_idx + 1] + [1] + shape[link_idx + 1 :]
        return self.reshape(new_shape)

    def trace_one_dim_pair(self, links):
        """Trace a pair of links with dimenion one. Inplace update."""
        if len(links) != 2:
            raise QTeaLeavesError("Can only run on pair of links")

        ii = min(links[0], links[1])
        jj = max(links[1], links[0])

        if ii == jj:
            raise QTeaLeavesError("Same link.")

        self.remove_dummy_link(jj)
        self.remove_dummy_link(ii)

        return self

    def zeros_like(self, requires_grad=False):
        """Get a tensor same as `self` but filled with zeros."""
        return type(self)(self.shape, ctrl="Z", dtype=self.dtype, device=self.device)

    # --------------------------------------------------------------------------
    #                       Other base tensor tooling
    # --------------------------------------------------------------------------

    @abc.abstractmethod
    def assert_diagonal(self, tol=1e-7):
        """Check that tensor is a diagonal matrix up to tolerance."""

    @abc.abstractmethod
    def assert_int_values(self, tol=1e-7):
        """Check that there are only integer values in the tensor."""

    @abc.abstractmethod
    def assert_real_valued(self, tol=1e-7):
        """Check that all tensor entries are real-valued."""

    def get_all_subtensors(self):
        """
        Returns a list of subtensors of self.
        For non-symmetric tensors this is just self.elem.
        """
        return [
            self.elem,
        ]

    def _attach_dummy_link_shape(self, position):
        """Calculate the new shape when attaching a dummy link to a dense tensor."""
        new_shape = list(self.shape)[:position] + [1] + list(self.shape)[position:]
        return new_shape

    def concatenate_vectors(self, vectors, dtype, dim=None):
        """
        Concatenate vectors of the underlying numpy / cupy / torch / etc tensors.

        **Arguments***

        vectors : list
            List of one-dimensional arrays.

        dtype : data type
            Data type of concatenated vectors.

        dim : int | None
            Total dimension of concatenated vectors.
            If `None`, calculated on the fly.
            Default to `None`

        **Returns**

        vec : one-dimensional array of corresponding backend library, e.g., numpy ndarray
            The elements in the list are concatenated in order, e.g.,
            input [[1, 2], [6, 5, 3]] will result in [1, 2, 6, 5, 3].

        mapping : dict
            Keys are the index of the individual vectors in the list `vectors`.
            Values are tuples with two integers with the lower and
            higher bound, e.g., `{0 : (0, 2), 1: (2, 5)}` for the example
            in `vec` in the previous return variable.

        **Details**

        Used to concatenate singular values for symmetric tensors
        in SVD, which is needed as jax and tensorflow do not support
        `x[:]` assignments.
        """
        if dim is None:
            dim = 0
            for elem in vectors:
                dim += elem.shape[0]

        vec = self.vector_with_dim_like(dim, dtype=dtype)

        i2 = 0
        mapping = {}
        for ii, elem in enumerate(vectors):
            i1 = i2
            i2 += elem.shape[0]

            vec[i1:i2] = elem
            mapping[ii] = (i1, i2)

        return vec, mapping

    @staticmethod
    def einsum_optimization_level(tensors, einsum_str):
        """
        Heuristic to get an optimization level for einsum contractions. The
        integer has to be translated into the backend specific strings.

        Parameters
        ----------

        tensors : list[:class:`_AbstractQteaTensors`]
            Tensors involved in the einsum contraction.

        einsum_str : str
            Summation rule for einsum.

        Returns
        -------

        optimization_level : int
            Integer being 0, 1, or 2 with 0 the lowest need
            for optimization. The cost is calculated via
            the product of each unique link. Starting from
            three tensors, cost of 1e8 has level 1, cost of
            1e12 has level 2.
        """
        # Check for optimization level, do an educated guess here

        optimization_level = 0
        if len(tensors) <= 2:
            return optimization_level

        dims = []
        for tensor in tensors:
            dims += list(tensor.shape)

        keys = einsum_str.split("->")[0].replace(",", "")

        cost = 1
        for ii, char in enumerate(keys):
            if char not in keys[:ii]:
                cost *= dims[ii]

        if cost > 1e12:
            # Equivalent to three 1000x1000 matrices multiplied,
            # force numpy or other backend to find optimal way to
            # contract
            optimization_level = 2
        elif cost > 1e8:
            # 1e8 is equivalent to multiply three 100x100 matrices
            # equivalent to "ij,jk,kl->il" (two indices kept, two
            # contracted away
            optimization_level = 1

        return optimization_level

    @abc.abstractmethod
    def elementwise_abs_smaller_than(self, value):
        """Return boolean if each tensor element is smaller than `value`"""

    @abc.abstractmethod
    def expand_tensor(self, link, new_dim, ctrl="R"):
        """Expand  tensor along given link and to new dimension."""

    @abc.abstractmethod
    def get_diag_entries_as_int(self):
        """Return diagonal entries of rank-2 tensor as integer on host."""

    @abc.abstractmethod
    def get_submatrix(self, row_range, col_range):
        """Extract a submatrix of a rank-2 tensor for the given rows / cols."""

    @abc.abstractmethod
    def flatten(self):
        """Returns flattened version (rank-1) of dense array in native array type."""

    @abc.abstractmethod
    def diag(self, real_part_only=False, do_get=False):
        """
        Return either the diagonal of an input rank-2 tensor
        or a rank-2 tensor of an input diagonal.
        """

    @abc.abstractmethod
    def expm(self, fuse_point=None, prefactor=1):
        """
        Take the matrix exponential with a scalar prefactor, i.e., Exp(prefactor * self).
        Self should be a rank 2 tensor.

        **Parameters**
        ----------
        fuse_point : int
            The point at which to fuse the links. fuse_point=1 will fuse links 0, 1 into one,
            and links 2, 3, ... into the other link.
        prefactor : float
            The scalar prefactor to multiply the matrix with.
        """

    @abc.abstractmethod
    def eig(self):
        """Compute eigenvalues and eigenvectors of a two-leg tensor"""

    @abc.abstractmethod
    def eigvalsh(self):
        """Compute eigenvalues and eigenvectors of a two-leg hermitian tensor"""

    @classmethod
    @abc.abstractmethod
    def from_elem_array(cls, tensor, dtype=None, device=None):
        """New tensor from array."""

    def _fuse_links_update_shape(self, fuse_low, fuse_high):
        """
        Calculates shape for dense tensor for fusing one set of links
        to a single link.

        **Parameters**
        ----------
        fuse_low : int
            First index to fuse
        fuse_high : int
            Last index to fuse.

        Example: if you want to fuse links 1, 2, and 3, fuse_low=1, fuse_high=3.
        Therefore the function requires links to be already sorted before in the
        correct order.
        """
        shape = list(self.shape[:fuse_low])
        shape += [np.prod(self.shape[fuse_low : fuse_high + 1])]
        shape += list(self.shape[fuse_high + 1 :])
        return shape

    @abc.abstractmethod
    def mask_to_device(self, mask):
        """Send a mask to the device where the tensor is."""

    @abc.abstractmethod
    def mask_to_host(self, mask):
        """Send a mask to the host."""

    def pad(self, link, new_dim, ctrl="R"):
        """
        Pad a tensor along given link and to new dimension.
        It is a wapper around `self.expand_tensor`.
        The padding is added at the end.

        Parameters
        ----------
        link : int
            Link to expand
        new_dim : int
            New dimension of the tensor
        ctrl : str | scalar
            Value for the padding

        Returns
        -------
        _AbstractQteaTensor
            The padded tensor
        """
        return self.expand_tensor(link, new_dim, ctrl=ctrl)

    @abc.abstractmethod
    def permute_rows_cols_update(self, inds):
        """Permute rows and columns of rank-2 tensor with `inds`. Inplace update."""

    @abc.abstractmethod
    def prepare_eig_api(self, conv_params):
        """Return variables for eigsh."""

    def _remove_dummy_link_shape(self, position):
        """Return shape for removing the dummy link at given position."""
        if self.shape[position] != 1:
            raise QTeaLeavesError(
                "Can only remove links with dimension 1. "
                + f"({self.shape[position]} at {position})"
            )
        new_shape = list(self.shape)[:position] + list(self.shape)[position + 1 :]

        return new_shape

    @abc.abstractmethod
    def reshape(self, shape, **kwargs):
        """Reshape a tensor."""

    @abc.abstractmethod
    def reshape_update(self, shape, **kwargs):
        """Reshape tensor dimensions inplace."""

    def _scale_link_einsum(self, link_idx):
        """Generate einsum-string notation for scale_link."""
        ndim = self.ndim
        if self.ndim > 26:
            raise QTeaLeavesError("Not sure how to support einsum here")

        key_a = string.ascii_lowercase[:ndim]
        key_b = key_a[link_idx]
        key = key_a + "," + key_b + "->" + key_a

        return key

    @abc.abstractmethod
    def set_submatrix(self, row_range, col_range, tensor):
        """Set a submatrix of a rank-2 tensor for the given rows / cols."""

    @staticmethod
    @abc.abstractmethod
    def set_seed(seed, devices=None):
        """
        Set the seed for this tensor backend and the specified devices.

        Arguments
        ---------

        seed : list[int]
            List of integers used as a seed; list has length 4.

        devices : list[str] | None, optional
            Can pass a list of devices via a string, e.g., to
            specify GPU by index. This allows the backend to resolve
            the device index if necessary.
            Default to `None` (CPU seed set, at least default GPU set
            if available)
        """

    def _shape_as_rank_3(self, link):
        """Calculate the shape as rank-3, i.e., before-link, link, after-link."""
        if link > 0:
            dim1 = int(np.prod(list(self.shape)[:link]))
        else:
            dim1 = 1

        dim2 = self.shape[link]

        if link == self.ndim - 1:
            dim3 = 1
        else:
            dim3 = int(np.prod(list(self.shape)[link + 1 :]))

        return dim1, dim2, dim3

    @abc.abstractmethod
    def subtensor_along_link(self, link, lower, upper):
        """Extract and return a subtensor select range (lower, upper) for one line."""

    @abc.abstractmethod
    def subtensor_along_link_inds(self, link, inds):
        """
        Extract and return a subtensor via indices for one link.

        Arguments
        ---------

        link : int
            Select only specific indices along this link (but all indices
            along any other link).

        inds : list[int]
            Indices to be selected and stored in the subtensor.

        Returns
        -------

        subtensor : :class:`_AbstractQteaTensor`
            Subtensor with selected indices.

        Details
        -------

        The numpy equivalent is ``subtensor = tensor[:, :, inds, :]``
        for a rank-4 tensor and ``link=2``.
        """

    def matrix_function(self, first_column, function_attr_str, **func_kwargs):
        """
        Apply a matrix function to the rank-n tensor by reshaping it into a bipartition
        of legs. Result of matrix function must be exactly one matrix of the same size.

        **Details**

        Currently, we support the following functions:

        * `expm` to take the matrix exponential
        * `q_from_qr` to generate unitary matrices
        * `copy` as identity operation.
        """

        if function_attr_str not in [
            "copy",
            "expm",
            "q_from_qr",
        ]:
            warn_str = f"Matrix function `{function_attr_str}` not recognized; you are on your own."
            logger.warning(warn_str)

        original_shape = self.shape

        tensor = self.copy()
        ########################################
        # fuse the second leg
        # pylint: disable=protected-access
        shape_fuse_second = tensor._fuse_links_update_shape(
            fuse_low=first_column, fuse_high=len(original_shape) - 1
        )
        tensor.reshape_update(shape_fuse_second)

        # fuse the first leg
        # pylint: disable=protected-access
        shape_fuse_first = tensor._fuse_links_update_shape(
            fuse_low=0, fuse_high=first_column - 1
        )
        tensor.reshape_update(shape_fuse_first)

        ########################################
        # apply function

        # The getattr gets the attribute of the specific object
        # tensor, with the self already included.
        func = getattr(tensor, function_attr_str)
        result = func(**func_kwargs)

        ########################################
        # reshape back
        result.reshape_update(original_shape)

        return result

    def add_random(self, prefactor):
        """
        Adds random noise with the strength prefactor to all entries.
        Self should be a rank 2 tensor.
        """
        self.assert_rank_2()
        random_tens = prefactor * self.copy().randomize()
        self += random_tens
        return self

    def q_from_qr(self):
        """
        Does a qr and returns the unitary q matrix.
        Self should be a rank 2 tensor.
        """
        self.assert_rank_2()
        tens_left, _ = self.split_qr(
            legs_left=[
                0,
            ],
            legs_right=[
                1,
            ],
        )
        return tens_left

    @abc.abstractmethod
    def _truncate_decide_chi(
        self,
        chi_now,
        chi_by_conv,
        chi_by_trunc,
        chi_min,
    ):
        """
        Decide on the bond dimension based on the various values chi and
        potential hardware preference indicated.

        **Arguments**

        chi_now : int
            Current value of the bond dimension

        chi_by_conv : int
            Maximum bond dimension as suggested by convergence parameters.

        chi_by_trunc : int
            Bond dimension suggested by truncating (either ratio or norm).

        chi_min : int
            Minimum bond dimension under which we do not want to go below.
            For example, used in TTN algorithms.
        """

    @staticmethod
    def _truncate_decide_chi_static(
        chi_now,
        chi_by_conv,
        chi_by_trunc,
        chi_min,
        block_size_bond_dimension,
        block_size_byte,
        data_type_byte,
    ):
        """
        Decide on the bond dimension based on the various values chi and
        potential hardware preference indicated.

        **Arguments**

        chi_now : int
            Current value of the bond dimension

        chi_by_conv : int
            Maximum bond dimension as suggested by convergence parameters.

        chi_by_trunc : int
            Bond dimension suggested by truncating (either ratio or norm).

        chi_min : int
            Minimum bond dimension under which we do not want to go below.
            For example, used in TTN algorithms.

        block_size_bond_dimension : int, `None`
            Ideal block size for the bond dimension. Chi should be a
            multiple of block_size_bond_dimension

        block_size_byte : int, `None`
            Ideal block size for memory in terms of bytes. Chi should be a
            multiple of (block_size_byte / data_type_bytes)

        data_type_byte : int
            Number of bytes for the current data type of the tensor, e.g.,
            8 bytes for a real float64.

        **Returns**

        chi_new : int
            Suggestion for the new bond dimension taking into account the
            current bond dimension, truncation criteria, convergence parameters
            and - if given - hardware preferences.
        """
        if block_size_byte is not None:
            block_size = block_size_byte // data_type_byte
        elif block_size_bond_dimension is not None:
            block_size = block_size_bond_dimension
        else:
            # fall-back is always block-size one; quick return not
            # possible to ensure minimal bond dimension
            block_size = 1

        if chi_by_conv % block_size != 0:
            chi_by_conv = (chi_by_conv // block_size + 1) * block_size
        if chi_by_conv < chi_min:
            # 2nd if-case outside first one to cover cases with block_size=1
            for _ in range(1000):
                chi_by_conv += block_size
                if chi_by_conv >= chi_min:
                    break

            if chi_by_trunc < chi_min:
                logger.warning("Could not reach min_bond_dimension in 1000 iterations.")

        if chi_by_trunc % block_size != 0:
            chi_by_trunc = (chi_by_trunc // block_size + 1) * block_size
        if chi_by_trunc < chi_min:
            for _ in range(1000):
                chi_by_trunc += block_size
                if chi_by_trunc >= chi_min:
                    break

            if chi_by_trunc < chi_min:
                logger.warning("Could not reach min_bond_dimension in 1000 iterations.")

        if chi_now % block_size != 0:
            chi_now = (chi_now // block_size + 1) * block_size
        if chi_now < chi_min:
            for _ in range(1000):
                chi_now += block_size
                if chi_now >= chi_min:
                    break

            if chi_now < chi_min:
                logger.warning("Could not reach min_bond_dimension in 1000 iterations.")

        # pylint: disable-next=nested-min-max
        return min(chi_now, min(chi_by_conv, chi_by_trunc))

    @abc.abstractmethod
    def _truncate_singvals(self, singvals, conv_params=None):
        """Truncate the singular values followling the given strategy."""

    @abc.abstractmethod
    def _truncate_sv_ratio(self, singvals, conv_params):
        """
        Truncate the singular values based on the ratio
        with the biggest one.
        """

    @abc.abstractmethod
    def _truncate_sv_norm(self, singvals, conv_params):
        """
        Truncate the singular values based on the
        total norm cut.
        """

    @abc.abstractmethod
    def vector_with_dim_like(self, dim, dtype=None):
        """Generate a vector in the native array of the base tensor."""

    @staticmethod
    @abc.abstractmethod
    def get_default_datamover():
        """The default datamover compatible with this class."""


class _AbstractDataMover(abc.ABC):
    """
    Abstract class for moving data between different devices

    Class attributes
    ----------------
    tensor_cls : Tuple[_AbstractTensor]
        Tensor classes handled by the datamover
    """

    tensor_cls = (None,)

    @abc.abstractmethod
    def sync_move(self, tensor, device):
        """
        Move the tensor `tensor` to the device `device`
        synchronously with the main computational stream

        Parameters
        ----------
        tensor : _AbstractTensor
            The tensor to be moved
        device: str
            The device where to move the tensor
        """

    @abc.abstractmethod
    def async_move(self, tensor, device, stream=None):
        """
        Move the tensor `tensor` to the device `device`
        asynchronously with respect to the main computational
        stream

        Parameters
        ----------
        tensor : _AbstractTensor
            The tensor to be moved
        device: str
            The device where to move the tensor
        """

    @abc.abstractmethod
    def wait(self):
        """
        Put a barrier for the streams and wait them
        """

    def move(self, tensor, device, sync=True):
        """
        Move the tensor `tensor` to the device `device`

        Parameters
        ----------
        tensor : _AbstractTensor
            The tensor to be moved
        device: str
            The device where to move the tensor
        sync : bool | stream, optional
            If True, move synchronously with the default cuda stream.
            If False, move asynchronously with additional stream in data mover.
            Otherwise, assume argument is the stream to be used. Stream argument
            might differ for backends.
        """
        if not isinstance(sync, bool):
            self.async_move(tensor, device, stream=sync)
        elif sync:
            self.sync_move(tensor, device)
        else:
            self.async_move(tensor, device)

    def check_tensor_cls_compatibility(self, tensor_cls):
        """
        Check if a tensor_cls can be handled by the datamover

        Parameters
        ----------
        tensor_cls : _AbstractTensor
            The tensor class to check
        """
        if tensor_cls not in self.tensor_cls:
            raise TypeError(
                (
                    f"Tensor class {str(tensor_cls)} cannot be handled by "
                    f"datamover {str(self)}"
                )
            )


def _parse_block_size():
    """Parse block size from environment variables and return in 2 ints."""
    block_size_bond_dimension = os.environ.get("QTEA_BLOCK_SIZE_BOND_DIMENSION", None)
    block_size_byte = os.environ.get("QTEA_BLOCK_SIZE_BYTE", None)

    if block_size_bond_dimension is not None:
        block_size_bond_dimension = int(block_size_bond_dimension)
    if block_size_byte is not None:
        block_size_byte = int(block_size_byte)

    return block_size_bond_dimension, block_size_byte


# for invert link selection (avoid creating lambda function
# on every call)
_func_not_none = lambda arg: arg is not None
