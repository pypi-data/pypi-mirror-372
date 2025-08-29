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
Tensor class based on numpy / cupy.

Quick programming guide
-----------------------

* numpy versus cupy is resolved as `xp`, which is provide as `_device_checks` function.
  Function acting on the tensors, must use `xp`; calculations on the shape of a tensor
  can be done directly with numpy.
* Multi-GPU support: all functions executing calculations on the GPU must use the
  decorator `gpu_switch` using the corresponding context manager. The decorator does
  not ensure that all input is on the same device. (Easy first-order check: if
  `_device_check` is called, decorator is necessary for all non-static, non-classmethods.)
"""

# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-arguments
# pylint: disable=I1101

import logging
import warnings
from contextlib import nullcontext
from math import ceil

import numpy as np
import scipy as sp
import scipy.linalg as sla
import scipy.sparse.linalg as ssla

# Try to import cupy
try:
    import cupy as cp
    import cupyx.scipy.linalg as cla
    import cupyx.scipy.sparse.linalg as csla
    from cupy_backends.cuda.api.runtime import CUDARuntimeError

    try:
        _ = cp.cuda.Device()
        GPU_AVAILABLE = True
        NUM_GPUS = cp.cuda.runtime.getDeviceCount()

        # for use in isinstance
        _ArrayTypes = (np.ndarray, cp.ndarray)

    except CUDARuntimeError:
        GPU_AVAILABLE = False
        NUM_GPUS = 0

        # for use in isinstance
        _ArrayTypes = np.ndarray

except ImportError:
    cp = None
    GPU_AVAILABLE = False
    NUM_GPUS = 0

    # for use in isinstance
    _ArrayTypes = np.ndarray

from qtealeaves.convergence_parameters import TNConvergenceParameters
from qtealeaves.solvers import EigenSolverH
from qtealeaves.tooling import QTeaLeavesError, read_tensor, write_tensor
from qtealeaves.tooling.devices import _CPU_DEVICE, _GPU_DEVICE, DeviceList
from qtealeaves.tooling.mpisupport import TN_MPI_TYPES

from .abstracttensor import (
    _AbstractDataMover,
    _AbstractQteaBaseTensor,
    _parse_block_size,
)

# pylint: disable-next=invalid-name
_BLOCK_SIZE_BOND_DIMENSION, _BLOCK_SIZE_BYTE = _parse_block_size()

# pylint: disable-next=invalid-name
_USE_STREAMS = False

__all__ = [
    "QteaTensor",
    "DataMoverNumpyCupy",
    "_process_svd_ctrl",
    "set_block_size_qteatensors",
]

logger = logging.getLogger(__name__)


# pylint: disable-next=dangerous-default-value
def logger_warning(*args, storage=[]):
    """Workaround to display warnings only once in logger."""
    if args in storage:
        return

    storage.append(args)
    logger.warning(*args)


# Define decorator allowing multi-GPU support
if NUM_GPUS > 1:

    def gpu_switch(func):
        """
        Used as decorator on functions that executes code on device
        allowing to use `cp.cuda.Device` context magaager.
        """

        def wrapper(*args, **kwargs):
            # As used on non-static methods only, first argument is self
            self = args[0]

            # pylint: disable-next=protected-access
            gpu_idx = self._gpu_idx(self.device)

            do_open_context = gpu_idx is not None
            current = cp.cuda.runtime.getDevice()
            if current == gpu_idx:
                # Current device is target, return function directly
                do_open_context = False

            if not do_open_context:
                return func(*args, **kwargs)

            with cp.cuda.Device(gpu_idx):
                return func(*args, **kwargs)

        return wrapper

else:
    # Either CPU or single-GPU, no wrapper needed
    def gpu_switch(func):
        """Empty decorator on functions that executes code on device."""
        return func


def set_block_size_qteatensors(block_size_bond_dimension=None, block_size_byte=None):
    """
    Allows to overwrite bond dimension decisions to enhance performance
    on hardware by keeping "better" or "consistent" bond dimensions.
    Only one of the two can be used right now.

    **Arguments**

    block_size_bond_dimension : int
        Direct handling of bond dimension.

    block_size_byte : int
        Control dimension of tensors (in SVD cuts) via blocks of bytes.
        For example, nvidia docs suggest multiples of sixteen float64
        or 32 float32 for A100, i.e., 128 bytes.

    **Details**

    There are two options of injecting hardware preferences for tensor.

    1) Call this function and it will set preferences for :class:`QteaTensors`
       via numpy/cupy
    2) Set the environment variables `QTEA_BLOCK_SIZE_BOND_DIMENSION` and/or
       `QTEA_BLOCK_SIZE_BYTE` which will be parsed by all :class:`_AbstractQteaBaseTensors`
       supporting this feature.

    Note that we do not support both options at the same time, only the block
    dimension in bytes will be used if both are available.
    """
    # pylint: disable-next=invalid-name,global-statement
    global _BLOCK_SIZE_BOND_DIMENSION
    # pylint: disable-next=invalid-name,global-statement
    global _BLOCK_SIZE_BYTE

    _BLOCK_SIZE_BOND_DIMENSION = block_size_bond_dimension
    _BLOCK_SIZE_BYTE = block_size_byte

    if (block_size_bond_dimension is not None) and (block_size_byte is not None):
        # We do not want to handle both of them, will be ignored later on,
        # but raise warning as early as possible
        warnings.warn("Ignoring BLOCK_SIZE_BOND_DIMENSION in favor of BLOCK_SIZE_BYTE.")


def set_streams_qteatensors(use_streams):
    """
    Allow to decide if streams are used.

    **Arguments**

    use_streams : bool
        If True, streams will be used, otherwise we return a nullcontext even
        if streams would be possible.

    """
    # pylint: disable-next=invalid-name,global-statement
    global _USE_STREAMS

    _USE_STREAMS = use_streams


# class set_block_size_qteatensors once to resolve if both variables
# are set
set_block_size_qteatensors(_BLOCK_SIZE_BOND_DIMENSION, _BLOCK_SIZE_BYTE)

_CPU_DEVICE = "cpu"
_GPU_DEVICE = "gpu"


# pylint: disable-next=too-many-public-methods
class QteaTensor(_AbstractQteaBaseTensor):
    """
    Dense tensor for Quantum Tea simulations using numpy or cupy as
    underlying arrays and linear algebra.

    **Arguments**

    links : list of integers
        Dimension along each link.

    ctrl : str | scalar, optional
        Initialization of tensor. Valid are "N" (uninitialized array),
        "Z" (zeros) "R", "random" (random), "O" (ones), "1" or "eye"
        for rank-2 identity matrix, "ground" for first element
        equal to one, or `None` (elem completely not set), `scalar`
        (the tensor is filled with that scalar value, must pass
        np.isscalar and np.isreal checks).
        Default to "Z"

    are_links_outgoing : list of bools, optional
        Used in symmetric tensors only

    base_tensor_cls : valid dense quantum tea tensor or `None`, optional
        Used in symmetric tensors only

    dtype : data type, optional
        Data type for numpy or cupy.
        Default to np.complex128

    device : device specification, optional
        Default to `"cpu"`.
        Available: `"cpu", "gpu"`

    **Details**

    Mixed-device mode

    The mixed-device mode is enabled for this class allowing for devices
    like `cpu+gpu:1`. The mixed-device mode can be used for :class:`QteaTensor`.
    Different GPUs can currently not be accessed from within a thread spanned
    inside simulations (other backends might support this). Tensor operation
    on the GPU have to be on the active cupy GPU, which we resolve by a
    decorator setting the active GPU in a context manager for every call.
    Unfortunately, not all operations can be executed on the selected device,
    i.e., if they happen outside the tensors module. Such operations are for
    example in the `qtealeaves.simulation` submodule; return value can be
    cupy-arrays with direct call of GPU kernels on the default GPU. In this case,
    a warning is displayed.
    """

    implemented_devices = DeviceList([_CPU_DEVICE, _GPU_DEVICE])

    def __init__(
        self,
        links,
        ctrl="Z",
        are_links_outgoing=None,  # pylint: disable=unused-argument
        base_tensor_cls=None,  # pylint: disable=unused-argument
        dtype=np.complex128,
        device=None,
    ):
        """

        links : list of ints with shape (links works towards generalization)
        """
        super().__init__(links)
        self._device = device
        xp = self._device_checks()

        with self._gpu_idx_context(device):

            if ctrl is None:
                self._elem = None
            elif ctrl in ["N"]:
                self._elem = xp.ndarray(links, dtype=dtype)
            elif ctrl in ["O"]:
                self._elem = xp.ones(links, dtype=dtype)
            elif ctrl in ["Z"]:
                self._elem = xp.zeros(links, dtype=dtype)
            elif ctrl in ["1", "eye"]:
                if len(links) != 2:
                    raise ValueError("Initialization with identity only for rank-2.")
                if links[0] != links[1]:
                    raise ValueError(
                        "Initialization with identity only for square matrix."
                    )
                self._elem = xp.eye(links[0], dtype=dtype)
            elif (ctrl in ["R", "random"]) and (dtype in [xp.complex64, xp.complex128]):
                # Random numbers and complex
                self._elem = xp.random.rand(*links) + 1j * xp.random.rand(*links)
                self.convert(dtype, device)
            elif ctrl in ["R", "random"]:
                # Random and real numbers
                self._elem = xp.random.rand(*links)
                self.convert(dtype, device)
            elif ctrl in ["ground"]:
                dim = np.prod(links)
                self._elem = xp.zeros([dim], dtype=dtype)
                self._elem[0] = 1.0
                self._elem = self._elem.reshape(links)
            elif np.isscalar(ctrl) and np.isreal(ctrl):
                dim = np.prod(links)
                # NOTE: xp.repeat breaks with python's float and cupy; is
                # there a better way to do this?
                self._elem = xp.ones(dim) * ctrl
                self._elem = self._elem.reshape(links).astype(dtype)
            else:
                raise QTeaLeavesError(f"Unknown initialization {ctrl}.")

    # --------------------------------------------------------------------------
    #                               Properties
    # --------------------------------------------------------------------------

    @property
    def are_links_outgoing(self):
        """Define property of outgoing links as property (always False)."""
        return [False] * self.ndim

    @property
    def device(self):
        """Device where the tensor is stored."""
        return self._device

    @property
    def elem(self):
        """Elements of the tensor."""
        return self._elem

    @property
    def dtype(self):
        """Data type of the underlying arrays."""
        return self._elem.dtype

    @property
    def dtype_eps(self):
        """Data type's machine precision."""
        eps_dict = {
            "float16": 1e-3,
            "float32": 1e-7,
            "float64": 1e-14,
            "complex64": 1e-7,
            "complex128": 1e-14,
        }

        return eps_dict[str(self.dtype)]

    @property
    def linear_algebra_library(self):
        """Specification of the linear algebra library used as string `numpy-cupy``."""
        return "numpy-cupy"

    @property
    def links(self):
        """Here, as well dimension of tensor along each dimension."""
        return self.shape

    @property
    def ndim(self):
        """Rank of the tensor."""
        return self._elem.ndim

    @property
    def shape(self):
        """Dimension of tensor along each dimension."""
        return self._elem.shape

    # --------------------------------------------------------------------------
    #                          Overwritten operators
    # --------------------------------------------------------------------------
    #
    # inherit def __eq__
    # inherit def __ne__

    @gpu_switch
    def __add__(self, other):
        """
        Addition of a scalar to a tensor adds it to all the entries.
        If other is another tensor, elementwise addition if they have the same shape
        """
        new_tensor = self.copy()
        if np.isscalar(other):
            new_tensor._elem += other
        elif isinstance(other, QteaTensor):
            new_tensor._elem += other.elem
        else:
            raise TypeError(
                "Addition for QteaTensor is defined only for scalars and QteaTensor,"
                + f" not {type(other)}"
            )
        return new_tensor

    @gpu_switch
    def __iadd__(self, other):
        """In-place addition of tensor with tensor or scalar (update)."""
        if np.isscalar(other):
            self._elem += other
        elif isinstance(other, QteaTensor):
            self._elem += other.elem
        else:
            raise TypeError(
                "Addition for QteaTensor is defined only for scalars and QteaTensor,"
                + f" not {type(other)}"
            )
        return self

    @gpu_switch
    def __mul__(self, scalar):
        """Multiplication of tensor with scalar returning new tensor as result."""
        return QteaTensor.from_elem_array(
            scalar * self._elem, dtype=self.dtype, device=self.device
        )

    @gpu_switch
    def __imul__(self, scalar):
        """In-place multiplication of tensor with scalar (update)."""
        self._elem *= scalar
        return self

    @gpu_switch
    def __itruediv__(self, scalar):
        """In-place division of tensor with scalar (update)."""
        if scalar == 0 or np.isinf(scalar) or np.isnan(scalar):
            raise QTeaLeavesError("Trying to divide by zero.")
        self._elem /= scalar
        return self

    @gpu_switch
    def __sub__(self, other):
        """
        Subtraction of a scalar to a tensor subtracts it to all the entries.
        If other is another tensor, elementwise subtraction if they have the same shape
        """
        new_tensor = self.copy()
        if np.isscalar(other):
            new_tensor._elem -= other
        elif isinstance(other, QteaTensor):
            new_tensor._elem -= other.elem
        else:
            raise TypeError(
                "Addition for QteaTensor is defined only for scalars and QteaTensor,"
                + f" not {type(other)}"
            )
        return new_tensor

    @gpu_switch
    def __truediv__(self, sc):
        """Division of tensor with scalar."""
        if sc == 0:
            raise QTeaLeavesError("Trying to divide by zero.")
        elem = self._elem / sc
        return QteaTensor.from_elem_array(elem, dtype=self.dtype, device=self.device)

    @gpu_switch
    def __neg__(self):
        """Negative of a tensor returned as a new tensor."""
        # pylint: disable-next=invalid-unary-operand-type
        neg_elem = -self._elem
        return QteaTensor.from_elem_array(
            neg_elem, dtype=self.dtype, device=self.device
        )

    # --------------------------------------------------------------------------
    #                       classmethod, classmethod like
    # --------------------------------------------------------------------------

    @staticmethod
    def convert_operator_dict(
        op_dict,
        params=None,
        symmetries=None,
        generators=None,
        base_tensor_cls=None,
        dtype=np.complex128,
        device=_CPU_DEVICE,
    ):
        """
        Iterate through an operator dict and convert the entries. Converts as well
        to rank-4 tensors.

        **Arguments**

        op_dict : instance of :class:`TNOperators`
            Contains the operators as xp.ndarray.

        params : dict, optional
            To resolve operators being passed as callable.

        symmetries:  list, optional, for compatibility with symmetric tensors.
            Must be empty list.

        generators : list, optional, for compatibility with symmetric tensors.
            Must be empty list.

        base_tensor_cls : None, optional, for compatibility with symmetric tensors.
            No checks on this one here.

        dtype : data type for xp, optional
            Specify data type.
            Default to `np.complex128`

        device : str
            Device for the simulation. Available "cpu" and "gpu"
            Default to "cpu"

        **Details**

        The conversion to rank-4 tensors is useful for future implementations,
        either to support adding interactions with a bond dimension greater than
        one between them or for symmetries. We add dummy links of dimension one.
        The order is (dummy link to the left, old link-1, old link-2, dummy link
        to the right).
        """
        if params is None:
            params = {}

        if symmetries is None:
            symmetries = []

        if generators is None:
            generators = []

        if len(symmetries) != 0:
            raise QTeaLeavesError("Symmetries not supported, but symmetry given.")

        if len(generators) != 0:
            raise QTeaLeavesError("Symmetries not supported, but generators given.")

        def transformation(key, value, op_dict=op_dict, params=params):
            if isinstance(value, QteaTensor):
                tensor = value
            else:
                tensor = op_dict.get_operator(*key, params)
                tensor = QteaTensor.from_elem_array(tensor, dtype=dtype, device=device)

            if tensor.ndim == 2:
                tensor.attach_dummy_link(0)
                tensor.attach_dummy_link(3)

            return tensor

        new_op_dict = op_dict.transform(transformation)
        return new_op_dict

    @gpu_switch
    def copy(self, dtype=None, device=None):
        """Make a copy of a tensor."""
        if dtype is None:
            dtype = self.dtype
        if device is None:
            device = self.device
        tensor = self.from_elem_array(self._elem.copy(), dtype=dtype, device=device)
        return tensor

    @gpu_switch
    def eye_like(self, link):
        """
        Generate identity matrix.

        **Arguments**

        self : instance of :class:`QteaTensor`
            Extract data type etc from this one here.

        link : same as returned by `links` property, here integer.
            Dimension of the square, identity matrix.
        """
        xp = self._device_checks()
        elem = xp.eye(link)

        return self.from_elem_array(elem, dtype=self.dtype, device=self.device)

    @gpu_switch
    def random_unitary(self, links):
        """
        Generate a random unitary matrix via performing a QR on a
        random tensor.

        **Arguments**

        self : instance of :class:`QteaTensor`
            Extract data type etc from this one here.

        links : same as returned by `links` property, here integer.
            Dimension of the tensors as [link[0], .., link[-1],
            link[0], .., link[-1]], random unitary matrix for
            contracting first/last half of legs with itself.
        """
        xp = self._device_checks()
        dim = np.prod(links)
        elem = xp.random.rand(dim, dim)
        elem = xp.linalg.qr(elem)[0].reshape(2 * links)

        return self.from_elem_array(elem, dtype=self.dtype, device=self.device)

    # no gpu_switch necessary, will be handled inside convert / from_elem_array
    @classmethod
    def read(cls, filehandle, dtype, device, base_tensor_cls, cmplx=True, order="F"):
        """Read a tensor from file."""
        elem = read_tensor(filehandle, cmplx=cmplx, order=order)
        return cls.from_elem_array(elem, dtype=dtype, device=device)

    # --------------------------------------------------------------------------
    #                            Checks and asserts
    # --------------------------------------------------------------------------
    #
    # inherit def assert_normalized
    # inherit def assert_unitary
    # inherit def sanity_check

    @gpu_switch
    def are_equal(self, other, tol=1e-7):
        """Check if two tensors are equal."""
        xp = self._device_checks()

        if self.ndim != other.ndim:
            return False

        if np.any(self.shape != other.shape):
            return False

        return xp.isclose(self._elem, other.elem, atol=tol).all()

    @gpu_switch
    def assert_identity(self, tol=1e-7):
        """Check if tensor is an identity matrix."""

        if not self.is_close_identity(tol=tol):
            raise QTeaLeavesError("Tensor not diagonal with ones.", self._elem)

    @gpu_switch
    def is_close_identity(self, tol=1e-7):
        """Check if rank-2 tensor is close to identity."""
        xp = self._device_checks()

        if self.ndim != 2:
            return False

        if self.shape[0] != self.shape[1]:
            return False

        eye = xp.eye(self.shape[0])

        eps = (np.abs(eye - self._elem)).max()

        return eps < tol

    # Overwrite implementation going via char
    def is_dtype_complex(self):
        """Check if data type is complex."""
        xp = self._device_checks()
        return xp.issubdtype(self._elem.dtype, xp.complexfloating)

    def is_implemented_device(self, query):
        """
        Check if argument query is an implemented device.

        Parameters
        ----------

        query : str
            String to be tested if it corresponds to a device
            implemented with this tensor.

        Returns
        -------

        is_implemented : bool
            True if string is available as device.
        """
        return query in self.implemented_devices

    # --------------------------------------------------------------------------
    #                       Single-tensor operations
    # --------------------------------------------------------------------------
    #
    # inherit def flip_links_update

    def attach_dummy_link(self, position, is_outgoing=True):
        """Attach dummy link at given position (inplace update)."""
        # Could use xp.expand_dims
        self.reshape_update(self._attach_dummy_link_shape(position))
        return self

    @gpu_switch
    def conj(self):
        """Return the complex conjugated in a new tensor."""
        return QteaTensor.from_elem_array(
            self._elem.conj(), dtype=self.dtype, device=self.device
        )

    @gpu_switch
    def conj_update(self):
        """Apply the complex conjugated to the tensor in place."""
        xp = self._device_checks()
        xp.conj(self._elem, out=self._elem)

    # pylint: disable-next=too-many-branches
    def convert(self, dtype=None, device=None, stream=None):
        """
        Convert underlying array to the specified data type and device inplace.

        Parameters
        ----------
        dtype : np.dtype, optional
            Type to which you want to convert. If None, no conversion.
            Default to None.
        device : str, optional
            Device where you want to send the QteaTensor. If None, no
            conversion. Default to None.
        stream : None | bool | cp.cuda.Stream | etc
            If None, use default stream for memory communication.
            If boolean, new stream is used for `True`.
            If not None and bool, use a new stream for memory communication.
            Default to None (Use null stream).
        """
        # To simplify syntax below, we use nullcontext if stream is
        # not given
        scontext = nullcontext() if stream is None else stream
        if isinstance(scontext, bool):
            # Some calling methods pass boolean, catch here and generate
            # stream on the fly
            blocking = not scontext

            # cupy's asnumpy() if will not allow stream to be bool
            stream = self.stream() if stream else None
            scontext = self.stream() if scontext else nullcontext()
        else:
            blocking = stream is None

        if device is not None:
            if not self.is_implemented_device(device):
                raise ValueError(
                    f"Device {device} is not implemented. Select from"
                    + f" {self.implemented_devices}"
                )
            if self.is_gpu(query=device) and (not GPU_AVAILABLE):
                raise ImportError("CUDA GPU is not available")

            # Both devices available, figure out what we currently have
            # and start converting
            if isinstance(self._elem, np.ndarray):
                current = _CPU_DEVICE
            elif cp is None:
                current = None
            elif isinstance(self.elem, cp.ndarray):
                current = _GPU_DEVICE
            else:
                current = None

            if device == current:
                # We already are in the correct device
                pass
            elif self.is_gpu() and self.is_gpu(query=device):
                # According to cupy docs, GPU to GPU copy is performed via cp.asarray
                # https://docs.cupy.dev/en/stable/user_guide/basic.html#data-transfer
                # We do not open a stream here, not sure which device would be the
                # correct one to open a stream
                with self._gpu_idx_context(device):
                    self._elem = cp.asarray(self._elem)
            elif self.is_gpu(query=device):
                with self._gpu_idx_context(device):
                    # We run a certain risk here that the stream is not on the
                    # correct device
                    with scontext:
                        # We go from cpu to gpu
                        self._elem = cp.asarray(self._elem)
            elif self.is_cpu(query=device):
                # We run a certain risk here that the stream is not on the
                # correct device; asnumpy supports passing a stream
                # We go from gpu to cpu
                if isinstance(stream, nullcontext):
                    stream = None
                self._elem = cp.asnumpy(self._elem, stream=stream, blocking=blocking)
            self._device = device
        if dtype is not None:
            if dtype != self.dtype:
                self._elem = self._elem.astype(dtype)

        return self

    # pylint: disable-next=too-many-branches
    def convert_singvals(self, singvals, dtype=None, device=None, stream=None):
        """
        Convert the singular values via a tensor.

        Parameters
        ----------
        dtype : np.dtype, optional
            Type to which you want to convert. If None, no conversion.
            Default to None.
        device : str, optional
            Device where you want to send the QteaTensor. If None, no
            conversion. Default to None.
        stream : None | cp.cuda.Stream
            If not None, use a new stream for memory communication.
            Default to None (Use null stream).
        """
        xp = self._device_checks()
        # To simplify syntax below, we use nullcontext if stream is
        # not given
        scontext = nullcontext() if stream is None else stream
        blocking = stream is None

        if device is not None:
            if not self.is_implemented_device(device):
                raise ValueError(
                    f"Device {device} is not implemented. Select from"
                    + f" {self.implemented_devices}"
                )

            if self.is_gpu(query=device) and (not GPU_AVAILABLE):
                raise ImportError("CUDA GPU is not available")

            # Both devices available, figure out what we currently have
            # and start converting
            if isinstance(singvals, np.ndarray):
                current = _CPU_DEVICE
            elif cp is None:
                current = None
            elif isinstance(singvals, cp.ndarray):
                current = _GPU_DEVICE
            else:
                current = None

            if device == current:
                # We already are in the correct device
                pass
            elif self.is_gpu() and self.is_gpu(query=device):
                # According to cupy docs, GPU to GPU copy is performed via cp.asarray
                # https://docs.cupy.dev/en/stable/user_guide/basic.html#data-transfer
                # We do not open a stream here, not sure which device would be the
                # correct one to open a stream
                with self._gpu_idx_context(device):
                    singvals = cp.asarray(singvals)
            elif self.is_gpu(query=device):
                with self._gpu_idx_context(device):
                    # We run a certain risk here that the stream is not on the
                    # correct device
                    with scontext:
                        # We go from cpu to gpu
                        singvals = cp.asarray(singvals)
            elif self.is_cpu(query=device):
                # We run a certain risk here that the stream is not on the
                # correct device; asnumpy supports passing a stream
                # We go from gpu to cpu
                singvals = cp.asnumpy(singvals, stream=stream, blocking=blocking)
        if dtype is not None:
            dtype = dtype(0).real.dtype
            if dtype != singvals.dtype:
                if xp.max(xp.abs(xp.imag(singvals))) > 10 * self.dtype_eps:
                    raise ValueError("Singular values have imaginary part.")
                singvals = xp.real(singvals).astype(dtype)

        return singvals

    @gpu_switch
    def diag(self, real_part_only=False, do_get=False):
        """
        Return either the diagonal of an input rank-2 tensor
        or a rank-2 tensor of an input diagonal.
        """
        xp = self._device_checks()

        if self.ndim not in [1, 2]:
            raise QTeaLeavesError("Can only run on rank-1 or rank-2.")

        diag = xp.diag(self._elem)

        if real_part_only:
            diag = xp.real(diag)

        if self.is_gpu() and do_get:
            diag = diag.get()

        return diag

    # no gpu_switch necessary, only access to data types
    def dtype_from_char(self, dtype):
        """Resolve data type from chars C, D, S, Z and optionally H."""
        xp = self._device_checks()

        data_types = {
            "A": xp.complex128,
            "C": xp.complex64,
            "D": xp.float64,
            "H": xp.float16,
            "S": xp.float32,
            "Z": xp.complex128,
            "I": xp.int32,
        }

        return data_types[dtype]

    # no gpu_switch necessary, only access to eigensolver function
    def eig_api(
        self, matvec_func, links, conv_params, args_func=None, kwargs_func=None
    ):
        """
        Interface to hermitian eigenproblem

        **Arguments**

        matvec_func : callable
            Multiplies "matrix" with "vector"

        links : links according to :class:`QteaTensor`
            Contain the dimension of the problem.

        conv_params : instance of :class:`TNConvergenceParameters`
            Settings for eigenproblem with Arnoldi method.

        args_func : arguments for matvec_func

        kwargs_func : keyword arguments for matvec_func

        **Returns**

        eigenvalues : scalar

        eigenvectors : instance of :class:`QteaTensor`
        """
        _, xsla = self._device_checks(return_sla=True)
        try:
            # pylint: disable-next=invalid-name
            ArpackNoConvergence = xsla.ArpackNoConvergence
            msg_error = (
                "Arpack not converging with new tolerance. Using qtealeaves solver."
            )
        except AttributeError:
            # The definition of the error seems to move every second version of
            # numpy and cupy
            # pylint: disable-next=invalid-name
            ArpackNoConvergence = QTeaLeavesError
            msg_error = (
                "Arpack failed (catching any exception). Using qtealeaves solver."
            )

        kwargs, _, _ = self.prepare_eig_api(conv_params)
        use_qtea_solver = kwargs.pop("use_qtea_solver", False)

        # qtea_solver is fallback solution for Arpack, so try Arpack first
        if not use_qtea_solver:
            try:
                val, vec = self.eig_api_arpack(
                    matvec_func,
                    links,
                    conv_params,
                    args_func=args_func,
                    kwargs_func=kwargs_func,
                )

                return val, vec

            except ArpackNoConvergence:
                # We iterated already over both tolerances, now try qtea_solver
                use_qtea_solver = True
                logger.warning(msg_error)

        # Now, qtea_solver must be either requested or be the fallback

        val, vec = self.eig_api_qtea(
            matvec_func,
            conv_params,
            args_func=args_func,
            kwargs_func=kwargs_func,
        )

        # Half precision had problems with normalization (most likely
        # as eigh is executed on higher precision. Insert `vec /= vec.norm_sqrt()`
        # again if necessary, but general normalization was covering other errors.

        return val, vec

    # no gpu_switch necessary, only resolving abs function
    def eig_api_qtea(self, matvec_func, conv_params, args_func=None, kwargs_func=None):
        """
        Interface to hermitian eigenproblem via qtealeaves.solvers. Arguments see `eig_api`.
        """
        xp = self._device_checks()

        injected_funcs = {
            "abs": xp.abs,
        }

        solver = EigenSolverH(
            self,
            matvec_func,
            conv_params,
            args_func=args_func,
            kwargs_func=kwargs_func,
            injected_funcs=injected_funcs,
        )
        res = solver.solve()

        # Free the allocated device memory that is no longer used (only
        # on the device of this tensor)
        self.free_device_memory(device=self.device)

        return res

    @gpu_switch
    def eig_api_arpack(
        self, matvec_func, links, conv_params, args_func=None, kwargs_func=None
    ):
        """
        Interface to hermitian eigenproblem via Arpack. Arguments see `eig_api`.
        """
        if args_func is None:
            args_func = []

        if kwargs_func is None:
            kwargs_func = {}

        xp, xsla = self._device_checks(return_sla=True)
        kwargs, linear_operator, eigsh = self.prepare_eig_api(conv_params)
        _ = kwargs.pop("injected_funcs")

        _ = kwargs.pop("injected_funcs", None)
        _ = kwargs.pop("use_qtea_solver", None)

        def my_matvec(
            vec,
            func=matvec_func,
            this=self,
            links=links,
            xp=xp,
            args=args_func,
            kwargs=kwargs_func,
        ):
            if isinstance(vec, xp.ndarray):
                tens = this.from_elem_array(vec, dtype=self.dtype, device=self.device)
                tens.reshape_update(links)
            else:
                raise QTeaLeavesError("unknown type")

            tens = -func(tens, *args, **kwargs)

            return tens.elem.reshape(-1)

        ham_dim = int(np.prod(links))
        lin_op = linear_operator((ham_dim, ham_dim), matvec=my_matvec)

        if "v0" in kwargs:
            kwargs["v0"] = self._elem.reshape(-1)

        # Even if this happens we are fine: our approach is iterative, at the next
        # sweep the value should converge
        try:
            eigenvalues, eigenvectors = eigsh(lin_op, **kwargs)
        except xsla.ArpackNoConvergence:
            kwargs["tol"] = conv_params.sim_params["arnoldi_max_tolerance"]
            logger.warning(
                "Arpack solver did not converge. Increasing tolerance to %s.",
                kwargs["tol"],
            )

            # try-except logic is replicated on calling function, we will not try
            # another Arpack call here; kwargs is local, so no need to reset original
            # tolerance
            eigenvalues, eigenvectors = eigsh(lin_op, **kwargs)

        # Free the allocated device memory that is no longer used
        self.free_device_memory(device=self.device)

        return (
            -eigenvalues,
            self.from_elem_array(
                eigenvectors.reshape(links), dtype=self.dtype, device=self.device
            ),
        )

    @gpu_switch
    def einsum(self, einsum_str, *others):
        """
        Call to einsum with `self` as first tensor.

        Arguments
        ---------

        einsum_str : str
            Einsum contraction rule.

        other: List[:class:`QteaTensors`]
            2nd, 3rd, ..., n-th tensor in einsum rule as
            positional arguments.

        Results
        -------

        tensor : :class:`QteaTensor`
            Contracted tensor according to the einsum rules.

        Details
        -------

        The call ``np.einsum(einsum_str, x.elem, y.elem, z.elem)`` translates
        into ``x.einsum(einsum_str, y, z)`` for x, y, and z being
        :class:`QteaTensor`.
        """
        xp = self._device_checks()

        # List of :class:`AbstractQteaTensors
        tensors = [self] + list(others)

        # Check for optimization level, do an educated guess here
        optimization_level = self.einsum_optimization_level(tensors, einsum_str)
        optimize = {
            0: False,
            1: True,
            2: "optimal",
        }[optimization_level]

        # Convert to actual data type of backend
        # pylint: disable-next=no-member
        tensors = [tensor.elem for tensor in tensors]

        elem = xp.einsum(einsum_str, *tensors, optimize=optimize)

        return self.from_elem_array(elem, dtype=self.dtype, device=self.device)

    # pylint: disable-next=unused-argument
    def fuse_links_update(self, fuse_low, fuse_high, is_link_outgoing=True):
        """
        Fuses one set of links to a single link (inplace-update).

        Parameters
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

        self.reshape_update(shape)

    @gpu_switch
    def getsizeof(self):
        """Size in memory (approximate, e.g., without considering meta data)."""
        # Enable fast switch, previously use sys.getsizeof had trouble
        # in resolving size, numpy attribute is only for array without
        # metadata, but metadata like dimensions is only small overhead.
        # (fast switch if we want to use another approach for estimating
        # the size of a numpy array)
        return self._elem.nbytes

    @gpu_switch
    def get_entry(self):
        """Get entry if scalar on host."""
        if np.prod(self.shape) != 1:
            raise QTeaLeavesError("Cannot get entry, more than one.")

        if self.is_gpu():
            return self._elem.get().reshape(-1)[0]

        return self._elem.reshape(-1)[0]

    @gpu_switch
    def kron(self, other, idxs=None):
        """
        Perform the kronecker product between two tensors.
        By default, do it over all the legs, but you can also
        specify which legs should be kroned over.
        The legs over which the kron is not done should have
        the same dimension.

        Parameters
        ----------
        other : QteaTensor
            Tensor to kron with self
        idxs : Tuple[int], optional
            Indexes over which to perform the kron.
            If None, kron over all indeces. Default to None.

        Returns
        -------
        QteaTensor
            The kronned tensor

        Details
        -------

        Performing the kronecker product between a tensor of shape (2, 3, 4)
        and a tensor of shape (1, 2, 3) will result in a tensor of shape (2, 6, 12).

        To perform the normal kronecker product between matrices just pass rank-2 tensors.

        To perform kronecker product between vectors first transfor them in rank-2 tensors
        of shape (1, -1)

        Performing the kronecker product only along **some** legs means that along that
        leg it is an elementwise product and not a kronecker. For Example, if idxs=(0, 2)
        for the tensors of shapes (2, 3, 4) and (1, 3, 2) the output will be of shape
        (2, 3, 8).
        """
        xp = self._device_checks()

        if isinstance(other, xp.ndarray):
            other = QteaTensor.from_elem_array(
                other, dtype=self.dtype, device=self.device
            )
            warnings.warn("Converting tensor on the fly.")

        subscipts, final_shape = self._einsum_for_kron(self.shape, other.shape, idxs)

        elem = xp.einsum(subscipts, self._elem, other._elem).reshape(final_shape)
        tens = QteaTensor.from_elem_array(elem, dtype=self.dtype, device=self.device)
        return tens

    @classmethod
    def mpi_bcast(cls, tensor, comm, tensor_backend, root=0):
        """
        Broadcast tensor via MPI.
        """
        dtype = tensor_backend.dtype
        is_root = comm.Get_rank() == root

        # Broadcast the dim of the shape
        dim = tensor.ndim if is_root else 0
        dim = comm.bcast(dim, root=root)

        # Broadcast shape
        shape = (
            np.array(list(tensor.shape), dtype=int)
            if is_root
            else np.zeros(dim, dtype=int)
        )
        comm.Bcast([shape, TN_MPI_TYPES["<i8"]], root=root)

        # Broadcast the tensor
        if not is_root:
            obj = cls(shape, ctrl="N", dtype=dtype, device=_CPU_DEVICE)
            # bcast will write in every process which is not root, so access _elem
            # pylint: disable-next=protected-access
            elem = obj._elem
        elif tensor.is_cpu():
            obj = tensor
            elem = tensor.elem
        else:
            obj = tensor
            elem = obj.elem.get()

        dtype_mpi = obj.dtype_mpi()
        comm.Bcast([elem, dtype_mpi], root=root)

        obj.convert(device=tensor_backend.device)

        return obj

    def mpi_send(self, to_, comm):
        """
        Send tensor via MPI.

        **Arguments**

        to : integer
            MPI process to send tensor to.

        comm : instance of MPI communicator to be used
        """

        # Send the dim of the shape
        comm.send(self.ndim, to_)

        # Send the shape first
        shape = np.array(list(self.shape), dtype=int)
        comm.Send([shape, TN_MPI_TYPES["<i8"]], to_)

        # Send the tensor
        if hasattr(self._elem, "get"):
            elem = self._elem.get()
        else:
            elem = self._elem

        dtype_mpi = self.dtype_mpi()
        comm.Send([np.ascontiguousarray(elem), dtype_mpi], to_)

    @classmethod
    def mpi_recv(cls, from_, comm, tensor_backend):
        """
        Send tensor via MPI.

        **Arguments**

        from_ : integer
            MPI process to receive tensor from.

        comm : instance of MPI communicator to be used

        tensor_backend : instance of :class:`TensorBackend`
        """
        # Receive the number of legs
        ndim = comm.recv(source=from_)

        # Receive the shape
        shape = np.empty(ndim, dtype=int)
        comm.Recv([shape, TN_MPI_TYPES["<i8"]], from_)

        dtype = tensor_backend.dtype
        obj = cls(shape, ctrl="N", dtype=dtype, device=_CPU_DEVICE)

        # Receive the tensor
        comm.Recv([obj._elem, obj.dtype_mpi()], from_)

        obj.convert(dtype=dtype, device=tensor_backend.memory_device)

        return obj

    @gpu_switch
    def norm(self):
        """Calculate the norm of the tensor <tensor|tensor>."""
        xp = self._device_checks()
        cidxs = np.arange(self.ndim)
        return xp.real(xp.tensordot(self._elem, self._elem.conj(), (cidxs, cidxs)))

    @gpu_switch
    def norm_sqrt(self):
        """
        Calculate the square root of the norm of the tensor,
        i.e., sqrt( <tensor|tensor>).
        """
        xp = self._device_checks()
        norm = self.norm()
        return xp.sqrt(norm)

    @gpu_switch
    def normalize(self):
        """Normalize tensor with sqrt(<tensor|tensor>)."""
        self._elem /= self.norm_sqrt()

    def remove_dummy_link(self, position):
        """Remove the dummy link at given position (inplace update)."""
        # Could use xp.squeeze
        new_shape = self._remove_dummy_link_shape(position)
        self.reshape_update(new_shape)
        return self

    @gpu_switch
    def scale_link(self, link_weights, link_idx, do_inverse=False):
        """
        Scale tensor along one link at `link_idx` with weights.

        **Arguments**

        link_weights : np.ndarray
            Scalar weights, e.g., singular values.

        link_idx : int
            Link which should be scaled.

        do_inverse : bool, optional
            If `True`, scale with inverse instead of multiplying with
            link weights.
            Default to `False`

        **Returns**

        updated_link : instance of :class:`QteaTensor`

        **Details**

        The inverse implementation handles zeros correctly which
        have been introduced due to padding. Therefore, `scale_link`
        should be used over passing `1 / link_weights` to this function.
        """
        xp = self._device_checks()
        key = self._scale_link_einsum(link_idx)

        if do_inverse:
            # Have to handle zeros here ... as we allow padding singular
            # values with zeros, we must also automatically avoid division
            # by zero due to exact zeros. But we can assume it must be at
            # the end of the array
            if link_weights[-1] == 0.0:
                tmp_inv = link_weights.copy()
                inds = xp.where(link_weights == 0.0)
                tmp_inv[inds] = 1.0
                tmp_inv = 1 / link_weights
            else:
                tmp_inv = 1 / link_weights

            tmp = xp.einsum(key, self._elem, tmp_inv)

        else:
            # Non inverse, just regular contraction
            tmp = xp.einsum(key, self._elem, link_weights)

        return self.from_elem_array(tmp, dtype=self.dtype, device=self.device)

    @gpu_switch
    def scale_link_update(self, link_weights, link_idx, do_inverse=False):
        """
        Scale tensor along one link at `link_idx` with weights (inplace update).

        **Arguments**

        link_weights : np.ndarray
            Scalar weights, e.g., singular values.

        link_idx : int
            Link which should be scaled.

        do_inverse : bool, optional
            If `True`, scale with inverse instead of multiplying with
            link weights.
            Default to `False`

        **Details**

        The inverse implementation handles zeros correctly which
        have been introduced due to padding. Therefore, `scale_link_update`
        should be used over passing `1 / link_weights` to this function.
        """
        xp = self._device_checks()

        if do_inverse:
            # Have to handle zeros here ... as we allow padding singular
            # values with zeros, we must also automatically avoid division
            # by zero due to exact zeros. But we can assume it must be at
            # the end of the array
            if link_weights[-1] == 0.0:
                vec = link_weights.copy()
                inds = xp.where(link_weights == 0.0)
                vec[inds] = 1.0
                vec = 1 / link_weights
            else:
                vec = 1 / link_weights
        else:
            vec = link_weights

        if link_idx == 0:
            key = self._scale_link_einsum(link_idx)
            self._einsum_inplace(xp, key, self._elem, vec)
            return self

        if link_idx + 1 == self.ndim:
            # For last link xp.multiply will do the job as the
            # last index is one memory block anyway
            xp.multiply(self._elem, vec, out=self._elem)
            return self

        # Need permutation or einsum, prefer einsum
        key = self._scale_link_einsum(link_idx)
        self._einsum_inplace(xp, key, self._elem, vec)
        return self

    @gpu_switch
    def set_diagonal_entry(self, position, value):
        """Set the diagonal element in a rank-2 tensor (inplace update)"""
        if self.ndim != 2:
            raise QTeaLeavesError("Can only run on rank-2 tensor.")
        self._elem[position, position] = value

    @gpu_switch
    def set_matrix_entry(self, idx_row, idx_col, value):
        """Set one element in a rank-2 tensor (inplace update)"""
        if self.ndim != 2:
            raise QTeaLeavesError("Can only run on rank-2 tensor.")
        self._elem[idx_row, idx_col] = value

    @staticmethod
    def set_seed(seed, devices=None):
        """
        Set the seed for this tensor backend and the specified devices.

        Arguments
        ---------

        seed : list[int]
            List of integers used as a seed; list has length 4.

        devices : list[str] | None, optional
            Can pass a list of devices via a string, e.g., to
            specify GPU by index.
            Default to `None` (CPU seed set, default GPU set if GPU available)
        """
        # Cover all CPU cases
        np.random.seed(seed)

        if not GPU_AVAILABLE:
            return

        # Find single integer as seed
        elegant_pairing = lambda nn, mm: nn**2 + nn + mm if nn >= mm else mm * 2 + nn
        intermediate_a = elegant_pairing(seed[0], seed[1])
        intermediate_b = elegant_pairing(seed[2], seed[3])
        single_seed = elegant_pairing(intermediate_a, intermediate_b)

        if devices is None:
            # GPU available, but not specified via index
            cp.random.seed(single_seed)
            return

        # We have a device list
        devices_set = []
        for device in devices:
            if not QteaTensor.is_gpu_static(device):
                continue

            if ":" in device:
                device_idx = int(device.split(":")[1])
            else:
                device_idx = 0

            if device_idx in devices_set:
                continue

            with cp.cuda.Device(device_idx):
                cp.random.seed(single_seed)

            devices_set.append(device_idx)

    def to_dense(self, true_copy=False):
        """Return dense tensor (if `true_copy=False`, same object may be returned)."""
        if true_copy:
            return self.copy()

        return self

    def to_dense_singvals(self, s_vals, true_copy=False):
        """Convert singular values to dense vector without symmetries."""
        if true_copy:
            return s_vals.copy()

        return s_vals

    @gpu_switch
    def trace(self, return_real_part=False, do_get=False):
        """Take the trace of a rank-2 tensor."""
        xp = self._device_checks()

        if self.ndim != 2:
            raise QTeaLeavesError("Can only run on rank-2 tensor.")

        value = xp.trace(self._elem)

        if return_real_part:
            value = xp.real(value)

        if self.is_gpu() and do_get:
            value = value.get()

        return value

    @gpu_switch
    def transpose(self, permutation):
        """Permute the links of the tensor and return new tensor."""
        tens = QteaTensor(None, ctrl=None, dtype=self.dtype, device=self.device)
        # pylint: disable-next=protected-access
        tens._elem = self._elem.transpose(permutation)
        return tens

    @gpu_switch
    def transpose_update(self, permutation):
        """Permute the links of the tensor inplace."""
        self._elem = self._elem.transpose(permutation)

    @gpu_switch
    def write(self, filehandle, cmplx=None):
        """
        Write tensor in original Fortran compatible way.

        **Details**

        1) Number of links
        2) Line with link dimensions
        3) Entries of tensors line-by-line in column-major ordering.
        """
        xp = self._device_checks()

        if cmplx is None:
            cmplx = xp.sum(xp.abs(xp.imag(self.elem))) > 1e-15

        write_tensor(self.elem, filehandle, cmplx=cmplx)

    # --------------------------------------------------------------------------
    #                         Two-tensor operations
    # --------------------------------------------------------------------------

    @gpu_switch
    def add_update(self, other, factor_this=None, factor_other=None):
        """
        Inplace addition as `self = factor_this * self + factor_other * other`.

        **Arguments**

        other : same instance as `self`
            Will be added to `self`. Unmodified on exit.

        factor_this : scalar
            Scalar weight for tensor `self`.

        factor_other : scalar
            Scalar weight for tensor `other`
        """
        if (factor_this is None) and (factor_other is None):
            self._elem += other.elem
            return

        if factor_this is not None:
            self._elem *= factor_this

        if factor_other is None:
            self._elem += other.elem
            return

        self._elem += factor_other * other.elem

    @gpu_switch
    def dot(self, other):
        """Inner product of two tensors <self|other>."""
        xp = self._device_checks()
        return xp.vdot(self._elem.reshape(-1), other.elem.reshape(-1))

    @gpu_switch
    def split_qr(
        self,
        legs_left,
        legs_right,
        perm_left=None,
        perm_right=None,
        is_q_link_outgoing=True,  # pylint: disable=unused-argument
        disable_streams=False,  # pylint: disable=unused-argument
    ):
        """
        Split the tensor via a QR decomposition.

        Parameters
        ----------

        self : instance of :class:`QteaTensor`
            Tensor upon which apply the QR
        legs_left : list of int
            Legs that will compose the rows of the matrix
        legs_right : list of int
            Legs that will compose the columns of the matrix
        perm_left : list of int, optional
            permutations of legs after the QR on left tensor
        perm_right : list of int, optional
            permutation of legs after the QR on right tensor
        disable_streams : boolean, optional
            No effect here, but in general can disable streams
            to avoid nested generation of streams.

        Returns
        -------

        tens_left: instance of :class:`QteaTensor`
            unitary tensor after the QR, i.e., Q.
        tens_right: instance of :class:`QteaTensor`
            upper triangular tensor after the QR, i.e., R
        """
        xp = self._device_checks()
        is_good_bipartition, is_sorted_l, is_sorted_r = self._split_checks_links(
            legs_left, legs_right
        )

        if is_good_bipartition and is_sorted_l and is_sorted_r:
            d1 = np.prod(np.array(self.shape)[legs_left])
            d2 = np.prod(np.array(self.shape)[legs_right])

            tens_left, tens_right = self._split_qr_dim(d1, d2)

            k_dim = tens_right.shape[0]

            tens_left.reshape_update(list(np.array(self.shape)[legs_left]) + [k_dim])
            tens_right.reshape_update([k_dim] + list(np.array(self.shape)[legs_right]))

        else:
            # Reshaping
            matrix = self._elem.transpose(legs_left + legs_right)
            shape_left = np.array(self.shape)[legs_left]
            shape_right = np.array(self.shape)[legs_right]
            matrix = matrix.reshape(np.prod(shape_left), np.prod(shape_right))
            k_dim = np.min([matrix.shape[0], matrix.shape[1]])

            if self.dtype == xp.float16:
                matrix = matrix.astype(xp.float32)

            # QR decomposition
            mat_left, mat_right = xp.linalg.qr(matrix)

            if self.dtype == xp.float16:
                mat_left = mat_left.astype(xp.float16)
                mat_right = mat_right.astype(xp.float16)

            # Reshape back to tensors
            tens_left = QteaTensor.from_elem_array(
                mat_left.reshape(list(shape_left) + [k_dim]),
                dtype=self.dtype,
                device=self.device,
            )
            tens_right = QteaTensor.from_elem_array(
                mat_right.reshape([k_dim] + list(shape_right)),
                dtype=self.dtype,
                device=self.device,
            )

        if perm_left is not None:
            tens_left.transpose_update(perm_left)

        if perm_right is not None:
            tens_right.transpose_update(perm_right)

        return tens_left, tens_right

    @gpu_switch
    def split_qrte(
        self,
        tens_right,
        singvals_self,
        operator=None,
        conv_params=None,
        is_q_link_outgoing=True,  # pylint: disable=unused-argument
    ):
        """
        Perform an Truncated ExpandedQR decomposition, generalizing the idea
        of https://arxiv.org/pdf/2212.09782.pdf for a general bond expansion
        given the isometry center of the network on  `tens_left`.
        It should be rather general for three-legs tensors, and thus applicable
        with any tensor network ansatz. Notice that, however, you do not have
        full control on the approximation, since you know only a subset of the
        singular values truncated.

        Parameters
        ----------
        tens_left: xp.array
            Left tensor
        tens_right: xp.array
            Right tensor
        singvals_left: xp.array
            Singular values array insisting on the link to the left of `tens_left`
        operator: xp.array or None
            Operator to contract with the tensors. If None, no operator is contracted

        Returns
        -------
        tens_left: ndarray
            left tensor after the EQR
        tens_right: ndarray
            right tensor after the EQR
        singvals: ndarray
            singular values kept after the EQR
        singvals_cutted: ndarray
            subset of thesingular values cutted after the EQR,
            normalized with the biggest singval
        """
        xp = self._device_checks()

        if conv_params is None:
            conv_params = TNConvergenceParameters()
            logger_warning("Using default convergence parameters (QRTE).")
        elif not isinstance(conv_params, TNConvergenceParameters):
            raise ValueError(
                "conv_params must be TNConvergenceParameters or None, "
                + f"not {type(conv_params)}."
            )

        # Trial bond dimension
        eta = ceil((1 + conv_params.min_expansion_qr) * self.shape[0])

        # Contract the two tensors together
        twotensors = xp.tensordot(self._elem, tens_right.elem, (2, 0))
        twotensors = xp.tensordot(xp.diag(singvals_self), twotensors, (1, 0))

        # Contract with the operator if present
        if operator is not None:
            twotensors = xp.tensordot(twotensors, operator.elem, ([1, 2], [2, 3]))
        # For simplicity, transpose in the same order as obtained
        # after the application of the operator
        else:
            twotensors = twotensors.transpose(0, 3, 1, 2)

        # Apply first phase in expanding the bond dimension
        expansor = xp.eye(eta, np.prod(self.shape[:2])).reshape(eta, *self.shape[:2])
        expanded_y0 = xp.tensordot(expansor, twotensors, ([1, 2], [0, 2]))
        expanded_y0 = expanded_y0.transpose([0, 2, 1])

        # Contract with the (i+1)th site dagger
        first_qr = xp.tensordot(twotensors, expanded_y0.conj(), ([1, 3], [2, 1]))
        first_q, _ = xp.linalg.qr(first_qr.reshape(-1, first_qr.shape[2]))
        first_q = first_q.reshape(first_qr.shape)

        # Contract the new q with the i-th site. The we would need a rq decomposition.
        second_qr = xp.tensordot(twotensors, first_q.conj(), ([0, 2], [0, 1]))
        second_qr = second_qr.transpose(2, 1, 0)
        second_q, second_r = xp.linalg.qr(second_qr.reshape(second_qr.shape[0], -1).T)
        second_q = second_q.T.reshape(second_qr.shape)
        # To get the real R matrix I would have to transpose, but to avoid a double
        # transposition I simply avoid that
        # second_r = second_r.T

        # Second phase in the expansor
        eigvl, eigvc = xp.linalg.eigh(second_r.conj() @ second_r.T)
        # Singvals are sqrt of eigenvalues, and sorted in the opposite order
        singvals = xp.sqrt(eigvl)[::-1]

        # Routine to select the bond dimension
        cut, singvals, singvals_cutted = self._truncate_singvals(singvals)
        tens_right = xp.tensordot(eigvc[:cut, ::-1], second_q, ([1], [0]))

        # Get the last tensor
        tens_left = xp.tensordot(twotensors, tens_right.conj(), ([1, 3], [2, 1]))

        tens_left = self.from_elem_array(
            tens_left, dtype=self.dtype, device=self.device
        )
        tens_right = self.from_elem_array(
            tens_right, dtype=self.dtype, device=self.device
        )

        return tens_left, tens_right, singvals, singvals_cutted

    # no gpu_switch necessary, see quick return via super()_split_rq using QR
    def split_rq(
        self,
        legs_left,
        legs_right,
        perm_left=None,
        perm_right=None,
        is_q_link_outgoing=True,  # pylint: disable=unused-argument
        disable_streams=False,  # pylint: disable=unused-argument
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
            No effect here, but in general can disable streams
            to avoid nested generation of streams.

        Returns
        -------

        tens_left: instance of :class:`_AbstractQteaTensor`
            upper triangular tensor after the RQ, i.e., R
        tens_right: instance of :class:`_AbstractQteaTensor`
            unitary tensor after the RQ, i.e., Q.
        """
        xp = self._device_checks()

        # Bug in RQ via scipy although QR via scipy seems to work.
        # pylint: disable-next=using-constant-test
        if True:
            # if xp != np:
            # cupy has no RQ
            # return super().split_rq(...)
            return super().split_rq(
                legs_left,
                legs_right,
                perm_left=perm_left,
                perm_right=perm_right,
                is_q_link_outgoing=is_q_link_outgoing,
            )

        is_good_bipartition, is_sorted_l, is_sorted_r = self._split_checks_links(
            legs_left, legs_right
        )

        if is_good_bipartition and is_sorted_l and is_sorted_r:
            d1 = np.prod(np.array(self.shape)[legs_left])
            d2 = np.prod(np.array(self.shape)[legs_right])

            tens_left, tens_right = self._split_rq_dim(d1, d2)

            k_dim = tens_right.shape[0]

            tens_left.reshape_update(list(np.array(self.shape)[legs_left]) + [k_dim])
            tens_right.reshape_update([k_dim] + list(np.array(self.shape)[legs_right]))

        else:
            # Reshaping
            matrix = self._elem.transpose(legs_left + legs_right)
            shape_left = np.array(self.shape)[legs_left]
            shape_right = np.array(self.shape)[legs_right]
            matrix = matrix.reshape(np.prod(shape_left), np.prod(shape_right))
            k_dim = np.min([matrix.shape[0], matrix.shape[1]])

            if self.dtype == xp.float16:
                matrix = matrix.astype(xp.float32)

            # QR decomposition
            mat_left, mat_right = sla.rq(matrix, mode="economic", check_finite=True)

            if self.dtype == xp.float16:
                mat_left = mat_left.astype(xp.float16)
                mat_right = mat_right.astype(xp.float16)

            # Reshape back to tensors
            tens_left = QteaTensor.from_elem_array(
                mat_left.reshape(list(shape_left) + [k_dim]),
                dtype=self.dtype,
                device=self.device,
            )
            tens_right = QteaTensor.from_elem_array(
                mat_right.reshape([k_dim] + list(shape_right)),
                dtype=self.dtype,
                device=self.device,
            )

        if perm_left is not None:
            tens_left.transpose_update(perm_left)

        if perm_right is not None:
            tens_right.transpose_update(perm_right)

        return tens_left, tens_right

    @gpu_switch
    # pylint: disable-next=unused-argument, too-many-branches
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
        """
        Perform a truncated Singular Value Decomposition by
        first reshaping the tensor into a legs_left x legs_right
        matrix, and permuting the legs of the ouput tensors if needed.
        If the contract_singvals = ('L', 'R') it takes care of
        renormalizing the output tensors such that the norm of
        the MPS remains 1 even after a truncation.

        Parameters
        ----------
        self : instance of :class:`QteaTensor`
            Tensor upon which apply the SVD
        legs_left : list of int
            Legs that will compose the rows of the matrix
        legs_right : list of int
            Legs that will compose the columns of the matrix
        perm_left : list of int, optional
            permutations of legs after the SVD on left tensor
        perm_right : list of int, optional
            permutation of legs after the SVD on right tensor
        contract_singvals: string, optional
            How to contract the singular values.
                'N' : no contraction
                'L' : to the left tensor
                'R' : to the right tensor
        conv_params : :py:class:`TNConvergenceParameters`, optional
            Convergence parameters to use in the procedure. If None is given,
            then use the default convergence parameters of the TN.
            Default to None.
        no_truncation : boolean, optional
            Allow to run without truncation
            Default to `False` (hence truncating by default)
        disable_streams : boolean, optional
            No effect here, but in general can disable streams
            to avoid nested generation of streams.

        Returns
        -------
        tens_left: instance of :class:`QteaTensor`
            left tensor after the SVD
        tens_right: instance of :class:`QteaTensor`
            right tensor after the SVD
        singvals: xp.ndarray
            singular values kept after the SVD
        singvals_cut: xp.ndarray
            singular values cut after the SVD, normalized with the biggest singval
        """
        xp = self._device_checks()
        tensor = self._elem

        # Reshaping
        matrix = tensor.transpose(legs_left + legs_right)
        shape_left = np.array(tensor.shape)[legs_left]
        shape_right = np.array(tensor.shape)[legs_right]
        matrix = matrix.reshape([np.prod(shape_left), np.prod(shape_right)])

        if conv_params is None:
            svd_ctrl = "A"
            max_bond_dimension = min(matrix.shape)
        else:
            svd_ctrl = conv_params.svd_ctrl
            max_bond_dimension = conv_params.max_bond_dimension

        svd_ctrl = _process_svd_ctrl(
            svd_ctrl,
            max_bond_dimension,
            matrix.shape,
            self.device,
            contract_singvals,
        )
        if matrix.dtype == xp.float16:
            matrix = matrix.astype(xp.float32)

        # SVD decomposition
        if svd_ctrl in ("D", "V"):
            mat_left, singvals_tot, mat_right = self._split_svd_normal(matrix)
        elif svd_ctrl in ("E", "X"):
            mat_left, singvals_tot, mat_right = self._split_svd_eigvl(
                matrix,
                svd_ctrl,
                max_bond_dimension,
                contract_singvals,
            )
        elif svd_ctrl in ("E+QR", "X+QR"):
            mat_left, singvals_tot, mat_right = self._split_svd_eigvl_qr(
                matrix,
                svd_ctrl,
                max_bond_dimension,
                contract_singvals,
            )
        elif svd_ctrl == "R":
            mat_left, singvals_tot, mat_right = self._split_svd_random(
                matrix, max_bond_dimension
            )

        if self.dtype == xp.float16:
            mat_left = mat_left.astype(xp.float16)
            mat_right = mat_right.astype(xp.float16)
            singvals_tot = singvals_tot.astype(xp.float16)

        # Truncation
        if not no_truncation:
            cut, singvals, singvals_cut = self._truncate_singvals(
                singvals_tot, conv_params
            )

            if cut < mat_left.shape[1]:
                # Cutting bond dimension
                mat_left = mat_left[:, :cut]
                mat_right = mat_right[:cut, :]
            elif cut > mat_left.shape[1]:
                # Expanding bond dimension to comply with ideal hardware
                # settings
                dim = mat_left.shape[1]
                npad = ((0, 0), (0, cut - dim))
                mat_left = xp.pad(
                    mat_left, npad, mode="constant", constant_values=(0, 0)
                )

                npad = ((0, cut - dim), (0, 0))
                mat_right = xp.pad(
                    mat_right, npad, mode="constant", constant_values=(0, 0)
                )

                npad = (0, cut - dim)
                singvals = xp.pad(
                    singvals, npad, mode="constant", constant_values=(0, 0)
                )
        else:
            singvals = singvals_tot
            singvals_cut = []  # xp.array([], dtype=self.dtype)
            cut = len(singvals_tot)
        mat_left = mat_left[:, :cut]
        mat_right = mat_right[:cut, :]

        # Contract singular values if requested
        if svd_ctrl in ("D", "V", "R"):
            if contract_singvals.upper() == "L":
                mat_left = xp.multiply(mat_left, singvals)
            elif contract_singvals.upper() == "R":
                mat_right = xp.multiply(singvals, mat_right.T).T
            elif contract_singvals.upper() != "N":
                raise ValueError(
                    f"Contract_singvals option {contract_singvals} is not "
                    + "implemented. Choose between right (R), left (L) or None (N)."
                )

        # Reshape back to tensors
        tens_left = mat_left.reshape(list(shape_left) + [cut])
        if perm_left is not None:
            tens_left = tens_left.transpose(perm_left)

        tens_right = mat_right.reshape([cut] + list(shape_right))
        if perm_right is not None:
            tens_right = tens_right.transpose(perm_right)

        # Convert into QteaTensor
        tens_left = self.from_elem_array(
            tens_left, dtype=self.dtype, device=self.device
        )
        tens_right = self.from_elem_array(
            tens_right, dtype=self.dtype, device=self.device
        )
        return tens_left, tens_right, singvals, singvals_cut

    # no gpu_switch necessary, always called from within split_svd
    def _split_svd_normal(self, matrix):
        """
        Normal SVD of the matrix. First try the faster gesdd iterative method.
        If it fails, resort to gesvd.

        Parameters
        ----------
        matrix: xp.array
            Matrix to decompose

        Returns
        -------
        xp.array
            Matrix U
        xp.array
            Singular values
        xp.array
            Matrix V^dagger
        """
        xp = self._device_checks()

        try:
            mat_left, singvals_tot, mat_right = xp.linalg.svd(
                matrix, full_matrices=False
            )
        except np.linalg.LinAlgError:
            logger.error("GESDD SVD decomposition failed. Resorting to gesvd.")
            mat_left, singvals_tot, mat_right = sp.linalg.svd(
                matrix, full_matrices=False, lapack_driver="gesvd"
            )

        return mat_left, singvals_tot, mat_right

    # no gpu_switch necessary, always called from within split_svd
    def _split_svd_eigvl(self, matrix, svd_ctrl, max_bond_dimension, contract_singvals):
        """
        SVD of the matrix through an eigvenvalue decomposition.

        Parameters
        ----------
        matrix: xp.array
            Matrix to decompose
        svd_crtl : str
            If "E" normal eigenvalue decomposition. If "X" use the sparse.
        max_bond_dimension : int
            Maximum bond dimension
        contract_singvals: str
            Whhere to contract the singular values

        Returns
        -------
        xp.array
            Matrix U
        xp.array
            Singular values
        xp.array
            Matrix V^dagger

        Details
        -------

        We use ᵀ*=^†, the adjoint.

        - In the contract-to-right case, which means:
          H = AAᵀ* = USV Vᵀ*SUᵀ* = U S^2 Uᵀ*
          To compute SVᵀ* we have to use:
          A = USVᵀ* -> Uᵀ* A = S Vᵀ*
        - In the contract-to-left case, which means:
          H = Aᵀ*A = VSUᵀ* USVᵀ* = VS^2 Vᵀ*
          First, we are given V, but we want Vᵀ*. However, let's avoid double work.
          To compute US we have to use:
          A = USVᵀ* -> AV = US
          Vᵀ* = right.T.conj()   (with the conjugation done in place)
        """
        xp, xsla = self._device_checks(return_sla=True)
        # The left tensor is unitary
        if contract_singvals == "R":
            herm_mat = matrix @ matrix.conj().T
        # contract_singvals == "L", the right tensor is unitary
        else:
            herm_mat = matrix.conj().T @ matrix

        # We put the condition on the matrix being bigger than 2x2
        # for the sparse eigensolver for stability of the arpack methods
        if svd_ctrl == "E" or (herm_mat.shape[0] - 1) <= 2:
            eigenvalues, eigenvectors = xp.linalg.eigh(herm_mat)
        elif svd_ctrl == "X":
            num_eigvl = min(herm_mat.shape[0] - 1, max_bond_dimension - 1)
            # Added in case bond dimension is 1
            num_eigvl = max(num_eigvl, 1)
            eigenvalues, eigenvectors = xsla.eigsh(herm_mat, k=num_eigvl)
        else:
            raise ValueError(
                f"svd_ctrl = {svd_ctrl} not valid with eigenvalue decomposition"
            )

        # Eigenvalues are sorted ascendingly, singular values descendengly
        # Only positive eigenvalues makes sense. Due to numerical precision,
        # there will be very small negative eigvl. We put them to 0.
        eigenvalues[eigenvalues < 0] = 0
        singvals = xp.sqrt(eigenvalues[::-1][: min(matrix.shape)])
        eigenvectors = eigenvectors[:, ::-1]

        # Taking only the meaningful part of the eigenvectors
        if contract_singvals == "R":
            left = eigenvectors[:, : min(matrix.shape)]
            right = left.T.conj() @ matrix
        else:
            right = eigenvectors[:, : min(matrix.shape)]
            left = matrix @ right
            right = right.T.conj()

        return left, singvals, right

    def _split_svd_eigvl_qr(
        self, matrix, svd_ctrl, max_bond_dimension, contract_singvals
    ):
        """
        SVD of the matrix through an eigenvalue decomposition and a QR (plus
        some contractions).
        """
        xp = self._device_checks()

        svd_ctrl_2 = svd_ctrl.replace("+QR", "")
        contract_singvals_2 = {"L": "R", "R": "L"}[contract_singvals]

        left, singvals, right = self._split_svd_eigvl(
            matrix, svd_ctrl_2, max_bond_dimension, contract_singvals_2
        )

        if contract_singvals == "L":
            # Iso center has to go to the left tensor
            right, r_mat = xp.linalg.qr(right.T)
            right = right.T
            left = xp.tensordot(left, r_mat, [[1], [0]])
        else:
            # Iso center has to go to the right tensor
            left, r_mat = xp.linalg.qr(left)
            right = xp.tensordot(r_mat, right, [[1], [0]])

        return left, singvals, right

    # no gpu_switch necessary, always called from within split_svd
    def _split_svd_random(self, matrix, max_bond_dimension):
        """
        SVD of the matrix through a random SVD decomposition
        as prescribed in page 227 of Halko, Martinsson, Tropp's 2011 SIAM paper:
        "Finding structure with randomness: Probabilistic algorithms for constructing
        approximate matrix decompositions"

        Parameters
        ----------
        matrix: xp.array
            Matrix to decompose
        max_bond_dimension : int
            Maximum bond dimension

        Returns
        -------
        xp.array
            Matrix U
        xp.array
            Singular values
        xp.array
            Matrix V^dagger
        """
        xp = self._device_checks()

        # pylint: disable-next=nested-min-max
        rank = min(max_bond_dimension, min(matrix.shape))
        # This could be parameterized but in the paper they use this
        # value
        n_samples = 2 * rank
        random = xp.random.randn(matrix.shape[1], n_samples).astype(matrix.dtype)
        reduced_matrix = matrix @ random
        # Find orthonormal basis
        ortho, _ = xp.linalg.qr(reduced_matrix)

        # Second part
        to_svd = ortho.T @ matrix
        left_tilde, singvals, right = xp.linalg.svd(to_svd, full_matrices=False)
        left = ortho @ left_tilde

        return left, singvals, right

    @gpu_switch
    def stack_link(self, other, link):
        """
        Stack two tensors along a given link.

        **Arguments**

        other : instance of :class:`QteaTensor`
            Links must match `self` up to the specified link.

        link : integer
            Stack along this link.

        **Returns**

        new_this : instance of :class:QteaTensor`
        """
        newdim_self = list(self.shape)
        newdim_self[link] += other.shape[link]

        d1, d2, d3 = self._shape_as_rank_3(link)
        d4 = other.shape[link]

        new_dim = d2 + d4

        new_this = QteaTensor(
            [d1, new_dim, d3], ctrl="N", dtype=self.dtype, device=self.device
        )

        # pylint: disable=protected-access
        new_this._elem[:, :d2, :] = self.elem.reshape([d1, d2, d3])
        new_this._elem[:, d2:, :] = other.elem.reshape([d1, d4, d3])
        # pylint: enable=protected-access
        new_this.reshape_update(newdim_self)

        return new_this

    @gpu_switch
    def tensordot(self, other, contr_idx, disable_streams=False):
        """Tensor contraction of two tensors along the given indices."""
        xp = self._device_checks()

        tmp_other_device = None
        if isinstance(other, _ArrayTypes):
            # numpy and cupy arrays are copied to device of 'self' as tensors
            other = QteaTensor.from_elem_array(
                other, dtype=self.dtype, device=self.device
            )
            logger.warning("Converting tensor on the fly.")
        elif isinstance(other, QteaTensor):
            # move tensor 'other' to the device of 'self', if needed
            tmp_other_device = other.device
            other.convert(device=self.device)
            if other.device != tmp_other_device:
                logger.warning(
                    "Switching tensor device on the fly. (%s -> %s)",
                    tmp_other_device,
                    other.device,
                )

        elem = xp.tensordot(self._elem, other._elem, contr_idx)
        tens = QteaTensor.from_elem_array(elem, dtype=self.dtype, device=self.device)

        # move 'other' back to original device
        if tmp_other_device is not None:
            other.convert(device=tmp_other_device)

        return tens

    @gpu_switch
    def stream(self, disable_streams=False):
        """
        Define a stream for any operation


        Parameters
        ----------

        disable_streams : bool, optional
            Allows to disable streams to avoid nested creation of
            streams. Globally, streams should be disabled via the
            `set_streams_qteatensors` function of the base tensor module.
            Default to False.

        Returns
        -------

        Context manager, e.g.,
        :class:`to.cuda.Stream` if on GPU
        :class:`nullcontext(AbstractContextManager)` otherwise

        Details
        -------

        For multi-GPU applications, the device of the stream is selected
        as the device of the tensor at the time of the call. If one changes
        the device of the tensor `self` after creating the stream, the
        tensor's device and the stream's device will mismatch.

        """
        if _USE_STREAMS and (not disable_streams) and self.is_gpu():
            return cp.cuda.Stream()
        return nullcontext()

    # --------------------------------------------------------------------------
    #                        Internal methods
    # --------------------------------------------------------------------------
    #
    # inherit _invert_link_selection

    # --------------------------------------------------------------------------
    #                                MISC
    # --------------------------------------------------------------------------

    @staticmethod
    def get_default_datamover():
        """The default datamover compatible with this class."""
        return DataMoverNumpyCupy()

    @gpu_switch
    def mask_to_device(self, mask):
        """
        Send a mask to the device where the tensor is.
        (right now only CPU --> GPU, CPU --> CPU).
        """
        if self.is_cpu():
            return mask

        xp = self._device_checks()
        mask_on_device = xp.array(mask, dtype=bool)
        return mask_on_device

    def mask_to_host(self, mask):
        """
        Send a mask to the host.
        (right now only CPU --> GPU, CPU --> CPU).
        """
        if self.is_cpu():
            return mask

        return cp.asnumpy(mask)

    # no gpu_switch necessary, always called from scale_link_update
    def _einsum_inplace(self, xp, *args):
        """Short-cut to inplace-einsum resolving numpy vs cupy. Sets self._elem."""
        if xp == np:
            xp.einsum(*args, out=self._elem)
        else:
            self._elem = xp.einsum(*args)

    # no gpu_switch necessary, going towards CPU
    def get(self):
        """Get the whole array of a tensor to the host as tensor."""
        if hasattr(self._elem, "get"):
            return self.from_elem_array(self._elem.get())

        return self

    # no gpu_switch necessary, going towards CPU
    def get_of(self, variable):
        """Run the get method to transfer to host on variable (same device as self)."""
        if hasattr(variable, "get"):
            return variable.get()

        return variable

    # no gpu_switch necessary, no direct cupy calls
    def _shift_iso_to_qr(self, target_tens, source_link, target_link):
        """Method to shift isometry center between two tensors."""
        nn = len(self.shape)
        lnk = source_link
        s_perm = list(range(lnk)) + list(range(lnk + 1, nn)) + [lnk]
        q_perm = list(range(lnk)) + [nn - 1] + list(range(lnk, nn - 1))

        tmp = self.transpose(s_perm)
        dim = list(np.arange(tmp.ndim))

        left_mat, right_mat = tmp.split_qr(dim[:-1], dim[-1:], perm_left=q_perm)

        tmp = target_tens.tensordot(right_mat, ([target_link], [1]))

        nn = len(target_tens.shape)
        lnk = target_link
        t_perm = list(range(lnk)) + [nn - 1] + list(range(lnk, nn - 1))

        t_tens = tmp.transpose(t_perm)

        return left_mat, t_tens

    @gpu_switch
    def eigvalsh(self):
        """Calculate eigendecomposition for a rank-2 tensor."""
        xp = self._device_checks()

        if self.ndim != 2:
            raise QTeaLeavesError("Not a matrix, hence no eigvalsh possible.")

        eigvals = xp.linalg.eigvalsh(self._elem)

        return eigvals

    def sqrtm(self):
        """Calculate matrix-square-root for a rank-2 tensor."""

        if self.ndim != 2:
            raise QTeaLeavesError("Not a matrix, hence no sqrtm possible.")

        if self.is_gpu():
            raise QTeaLeavesError("sqrtm not implemented on the GPU through cupy")

        elem = sp.linalg.sqrtm(self._elem)

        return self.from_elem_array(elem, dtype=self.dtype, device=self.device)

    def expm(self, fuse_point=None, prefactor=1):
        """
        Take the matrix exponential with a scalar prefactor, i.e., Exp(prefactor * self).

        Parameters
        ----------
        fuse_point : int, optional
            If given, reshapes the tensor into a matrix by fusing links up to INCLUDING fuse_point
            into one, and links after into the second dimension.
            To compute the exponential of a 4-leg tensor, for example, by fusing (0,1),(2,3),
            set fuse_point=1.
            Default is None.

        prefactor : float, optional
            Prefactor of the tensor to be exponentiated.
            Default to 1.

        Return
        ------
        mat : instance of :class:`QteaTensor`
            Exponential of input tensor.
        """
        xp = self._device_checks()
        xla = sla if xp == np else cla
        mat = self.copy()
        original_shape = mat.shape

        # Fuse the links.
        if fuse_point is not None:
            mat.fuse_links_update(
                fuse_low=0, fuse_high=fuse_point, is_link_outgoing=False
            )
            mat.fuse_links_update(
                fuse_low=1, fuse_high=mat.ndim - 1, is_link_outgoing=True
            )

        # Take the exponent and reshape back into the original shape.
        # pylint: disable-next=protected-access
        mat._elem = xla.expm(prefactor * mat.elem)
        mat.reshape_update(original_shape)
        return mat

    def eig(self):
        """
        Compute eigenvalues and eigenvectors of a two-leg tensor

        Return
        ------
        eigvals, eigvecs : instances of :class:`QteaTensor`
            Eigenvalues and corresponding eigenvectors of input tensor.
        """
        if self.is_gpu():
            # NOTE: 'cupyx.scipy.linalg' has no attribute 'eig'
            # so we handle this case as follows:
            device = self.device
            self.convert(device="cpu")
            eigvals, eigvecs = self.eig()
            self.convert(device=device)
            eigvals.convert(device=device)
            eigvecs.convert(device=device)
            return eigvals, eigvecs

        xp = self._device_checks()
        xla = sla if xp == np else cla

        if self.ndim != 2:
            raise QTeaLeavesError("Works only with two-leg tensor")

        eigvals, eigvecs = xla.eig(
            self.elem
        )  # NOTE: 'cupyx.scipy.linalg' has no attribute 'eig'
        eigvals = self.from_elem_array(eigvals, dtype=self.dtype, device=self.device)
        eigvecs = self.from_elem_array(eigvecs, dtype=self.dtype, device=self.device)
        return eigvals, eigvecs

    @gpu_switch
    def stack_first_and_last_link(self, other):
        """Stack first and last link of tensor targeting MPS addition."""
        newdim_self = list(self.shape)
        newdim_self[0] += other.shape[0]
        newdim_self[-1] += other.shape[-1]

        d1 = self.shape[0]
        d2 = np.prod(self.shape[1:-1])
        d3 = self.shape[-1]
        i1 = other.shape[0]
        i3 = other.shape[-1]

        new_dims = [d1 + i1, d2, d3 + i3]

        new_this = QteaTensor(new_dims, ctrl="Z", dtype=self.dtype, device=self.device)
        # pylint: disable=protected-access
        new_this._elem[:d1, :, :d3] = self.elem.reshape([d1, d2, d3])
        new_this._elem[d1:, :, d3:] = other.elem.reshape([i1, d2, i3])
        # pylint: enable=protected-access
        new_this.reshape_update(newdim_self)

        return new_this

    @staticmethod
    def static_is_gpu_available():
        """Returns flag if GPU is available for this tensor class."""
        return GPU_AVAILABLE

    def is_gpu_available(self):
        """Returns flag if GPU is available for this tensor class."""
        return self.static_is_gpu_available()

    @staticmethod
    def free_device_memory(device=None):
        """
        Free the unused device memory that is otherwise occupied by the cache.
        Otherwise cupy will keep the memory occupied for caching reasons.
        For multi-GPU, all devices will be cleared unless you specify the device.

        Parameters
        ----------

        device : str | None
            If present, i.e., not None, only the corresponding device will
            be freed. The device is a string, e.g., "gpu:0"
        """
        if device is None:
            inds = ["gpu:%d" % (ii) for ii in range(NUM_GPUS)]
        elif QteaTensor.is_cpu_static(device):
            return None
        else:
            inds = [device]

        for device_ii in inds:
            # Use the context provided by the QteaTensor class
            # to catch case of current device with null context
            # pylint: disable-next=protected-access
            with QteaTensor._gpu_idx_context(device_ii):
                mempool = cp.get_default_memory_pool()
                pinned_mempool = cp.get_default_pinned_memory_pool()
                mempool.free_all_blocks()
                pinned_mempool.free_all_blocks()
        return None

    # --------------------------------------------------------------------------
    #                 Methods needed for _AbstractQteaBaseTensor
    # --------------------------------------------------------------------------

    @gpu_switch
    def assert_diagonal(self, tol=1e-7):
        """Check that tensor is a diagonal matrix up to tolerance."""
        xp = self._device_checks()

        if self.ndim != 2:
            raise QTeaLeavesError("Not a matrix, hence not the identity.")

        tmp = xp.diag(xp.diag(self._elem))
        tmp -= self._elem

        if xp.abs(tmp).max() > tol:
            raise QTeaLeavesError("Matrix not diagonal.")

        return

    @gpu_switch
    def assert_int_values(self, tol=1e-7):
        """Check that there are only integer values in the tensor."""
        xp = self._device_checks()

        # .copy() was required as bugfix, although unclear why (dj)
        tmp = xp.round(self.copy().elem)
        tmp -= self._elem

        if xp.abs(tmp).max() > tol:
            raise QTeaLeavesError("Matrix is not an integer matrix.")

        return

    @gpu_switch
    def assert_real_valued(self, tol=1e-7):
        """Check that all tensor entries are real-valued."""
        xp = self._device_checks()

        tmp = xp.imag(self._elem)

        if xp.abs(tmp).max() > tol:
            raise QTeaLeavesError("Tensor is not real-valued.")

    @gpu_switch
    def elementwise_abs_smaller_than(self, value):
        """Return boolean if each tensor element is smaller than `value`"""
        xp = self._device_checks()

        return (xp.abs(self._elem) < value).all()

    @gpu_switch
    def flatten(self):
        """Returns flattened version (rank-1) of dense array in native array type."""
        return self._elem.flatten()

    # no gpu_switch necessary, will be handled inside convert
    @classmethod
    def from_elem_array(cls, tensor, dtype=None, device=None):
        """
        New tensor from array

        **Arguments**

        tensor : xp.ndarray
            Array for new tensor.

        dtype : data type, optional
            Can allow to specify data type.
            If not `None`, it will convert.
            Default to `None`
        """
        if dtype is None and np.issubdtype(tensor.dtype, np.integer):
            logger_warning(
                "Initializing a tensor with integer dtype can be dangerous "
                "for the simulation. Please specify the dtype keyword in the "
                "from_elem_array method if it was not intentional."
            )

        if cp is None:
            current_device = _CPU_DEVICE
        else:
            current_device = (
                _CPU_DEVICE if cp.get_array_module(tensor) == np else _GPU_DEVICE
            )

        if dtype is None:
            dtype = tensor.dtype

        if (device is None) and (cp is None):
            # cupy not available
            device = _CPU_DEVICE
        elif (device is None) and not GPU_AVAILABLE:
            # Well, cupy is there, but no GPU
            device = _CPU_DEVICE
        elif device is None:
            # We can actually check with cp where we are running
            device = current_device

        # __init__ has no convert, it will set the _device attribute
        # without checks, so it has to be true (instead, data type goes via
        # array)
        obj = cls(tensor.shape, ctrl=None, dtype=None, device=current_device)
        obj._elem = tensor

        obj.convert(dtype, device)

        return obj

    def get_attr(self, *args):
        """High-risk resolve attribute for an operation on an elementary array."""
        xp = self._device_checks()

        attributes = []

        for elem in args:
            if elem in ["linalg.eigh", "eigh"]:
                attributes.append(xp.linalg.eigh)
                continue

            if not hasattr(xp, elem):
                raise QTeaLeavesError(
                    f"This tensor's elementary array does not support {elem}."
                )

            attributes.append(getattr(xp, elem))

        if NUM_GPUS > 1:
            attributes = self._get_attr_with_gpu_switch(attributes)

        if len(attributes) == 1:
            return attributes[0]

        return tuple(attributes)

    def _get_attr_with_gpu_switch(self, attributes):
        """
        Wrap functions from get_attr into device of the current tensor.

        Arguments
        ---------

        attributes : list[callable]
            List of requested attribute functions.

        Returns
        -------

        attributes : list[callable]
            List of requested attribute functions running
            on specific GPU of current tensor if needed.
        """
        gpu_idx = self._gpu_idx(self.device)

        if gpu_idx is None:
            # Not on GPU, return attributes directly
            return attributes

        current = cp.cuda.runtime.getDevice()
        if current == gpu_idx:
            # Current device is target, return attributes directly
            return attributes

        attributes_on_device = []
        for elem in attributes:

            def func_on_device(*args, func=elem, gpu_idx=gpu_idx, **kwargs):
                with cp.cuda.Device(gpu_idx):
                    func(*args, **kwargs)

            attributes_on_device.append(func_on_device)

        return attributes_on_device

    @gpu_switch
    def get_diag_entries_as_int(self):
        """Return diagonal entries of rank-2 tensor as integer on host."""
        xp = self._device_checks()

        if self.ndim != 2:
            raise QTeaLeavesError("Not a matrix, cannot get diagonal.")

        tmp = xp.diag(self._elem)
        if self.is_gpu():
            tmp = tmp.get()

        return xp.real(tmp).astype(int)

    @gpu_switch
    def get_submatrix(self, row_range, col_range):
        """Extract a submatrix of a rank-2 tensor for the given rows / cols."""
        if self.ndim != 2:
            raise QTeaLeavesError("Cannot only set submatrix for rank-2 tensors.")

        row1, row3 = row_range
        col1, col2 = col_range

        return self.from_elem_array(
            self._elem[row1:row3, col1:col2], dtype=self.dtype, device=self.device
        )

    @gpu_switch
    def permute_rows_cols_update(self, inds):
        """Permute rows and columns of rank-2 tensor with `inds`. Inplace update."""
        if self.ndim != 2:
            raise QTeaLeavesError("Can only permute rows & cols for rank-2 tensors.")

        tmp = self._elem[inds, :][:, inds]
        self._elem *= 0.0
        self._elem += tmp
        return self

    # no gpu_switch necessary, no actual calls with cupy
    def prepare_eig_api(self, conv_params):
        """
        Return xp variables for eigsh.

        **Returns**

        kwargs : dict
            Keyword arguments for eigs call.
            If initial guess can be passed, key "v0" is
            set with value `None`

        LinearOperator : callable
            Function generating a LinearOperator

        eigsh : callable
            Interface with actual call to eigsh
        """
        xp, xsla = self._device_checks(return_sla=True)

        tolerance = conv_params.sim_params["arnoldi_tolerance"]
        if tolerance is None:
            tolerance = conv_params.sim_params["arnoldi_min_tolerance"]

        kwargs = {
            "k": 1,
            "which": "LA",
            "ncv": None,
            "maxiter": conv_params.arnoldi_maxiter,
            "tol": tolerance,
            "return_eigenvectors": True,
            "use_qtea_solver": False,
        }

        if self.is_cpu():
            kwargs["v0"] = None

        if self.dtype == xp.float16:
            kwargs["use_qtea_solver"] = True

        if self.is_dtype_complex() and (np.prod(self.shape) == 2):
            # scipy eigsh switches for complex data types to eigs and
            # can only solve k eigenvectors of a nxn matrix with
            # k < n - 1. This leads to problems with 2x2 matrices
            # where one can get not even one eigenvector.
            kwargs["use_qtea_solver"] = True

        # abs is no attribute, only function
        kwargs["injected_funcs"] = {"abs": xp.abs}

        return kwargs, xsla.LinearOperator, xsla.eigsh

    @gpu_switch
    def reshape(self, shape, **kwargs):
        """Reshape a tensor."""
        elem = self._elem.reshape(shape, **kwargs)
        tens = QteaTensor.from_elem_array(elem, dtype=self.dtype, device=self.device)
        return tens

    @gpu_switch
    def reshape_update(self, shape, **kwargs):
        """Reshape tensor dimensions inplace."""
        self._elem = self._elem.reshape(shape)

    @gpu_switch
    def set_submatrix(self, row_range, col_range, tensor):
        """Set a submatrix of a rank-2 tensor for the given rows / cols."""

        if self.ndim != 2:
            raise QTeaLeavesError("Cannot only set submatrix for rank-2 tensors.")

        row1, row3 = row_range
        col1, col2 = col_range

        self._elem[row1:row3, col1:col2] = tensor.elem.reshape(row3 - row1, col2 - col1)

    @gpu_switch
    def subtensor_along_link(self, link, lower, upper):
        """
        Extract and return a subtensor select range (lower, upper) for one link.
        """
        d1, d2, d3 = self._shape_as_rank_3(link)

        elem = self._elem.reshape([d1, d2, d3])
        elem = elem[:, lower:upper, :]

        new_shape = list(self.shape)
        new_shape[link] = upper - lower
        elem = elem.reshape(new_shape)

        return self.from_elem_array(elem, dtype=self.dtype, device=self.device)

    @gpu_switch
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

        subtensor : :class:`QteaTensor`
            Subtensor with selected indices.

        Details
        -------

        The numpy equivalent is ``subtensor = tensor[:, :, inds, :]``
        for a rank-4 tensor and ``link=2``.
        """
        d1, d2, d3 = self._shape_as_rank_3(link)

        elem = self._elem.reshape([d1, d2, d3])
        elem = elem[:, inds, :]

        new_shape = list(self.shape)
        new_shape[link] = len(inds)
        elem = elem.reshape(new_shape)

        return self.from_elem_array(elem, dtype=self.dtype, device=self.device)

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
        return self._truncate_decide_chi_static(
            chi_now,
            chi_by_conv,
            chi_by_trunc,
            chi_min,
            _BLOCK_SIZE_BOND_DIMENSION,
            _BLOCK_SIZE_BYTE,
            self.elem.itemsize,
        )

    # no gpu_swicth necessary, only calls from split_qrte and split_svd
    def _truncate_singvals(self, singvals, conv_params=None):
        """
        Truncate the singular values followling the
        strategy selected in the convergence parameters class

        Parameters
        ----------
        singvals : np.ndarray
            Array of singular values
        conv_params : :py:class:`TNConvergenceParameters`, optional
            Convergence parameters to use in the procedure. If None is given,
            then use the default convergence parameters of the TN.
            Default to None.

        Returns
        -------
        cut : int
            Number of singular values kept
        singvals_kept : np.ndarray
            Normalized singular values kept
        singvals_cutted : np.ndarray
            Normalized singular values cutted
        """
        if conv_params is None:
            conv_params = TNConvergenceParameters()
            logger_warning("Using default convergence parameters.")
        elif not isinstance(conv_params, TNConvergenceParameters):
            raise ValueError(
                "conv_params must be TNConvergenceParameters or None, "
                + f"not {type(conv_params)}."
            )

        if conv_params.trunc_method == "R":
            cut = self._truncate_sv_ratio(singvals, conv_params)
        elif conv_params.trunc_method == "N":
            cut = self._truncate_sv_norm(singvals, conv_params)
        else:
            raise QTeaLeavesError(f"Unkown trunc_method {conv_params.trunc_method}")

        # Divide singvals in kept and cut
        singvals_kept = singvals[:cut]
        singvals_cutted = singvals[cut:]
        # Renormalizing the singular values vector to its norm
        # before the truncation
        norm_kept = (singvals_kept**2).sum()
        norm_trunc = (singvals_cutted**2).sum()
        normalization_factor = np.sqrt(norm_kept) / np.sqrt(norm_kept + norm_trunc)
        singvals_kept /= normalization_factor

        # Renormalize cut singular values to track the norm loss
        singvals_cutted /= np.sqrt(norm_trunc + norm_kept)

        return cut, singvals_kept, singvals_cutted

    @gpu_switch
    def vector_with_dim_like(self, dim, dtype=None):
        """Generate a vector in the native array of the base tensor."""
        xp = self._device_checks()

        if dtype is None:
            dtype = self.dtype

        return xp.ndarray(dim, dtype=dtype)

    # --------------------------------------------------------------------------
    #             Internal methods (not required by abstract class)
    # --------------------------------------------------------------------------

    def _device_checks(self, return_sla=False):
        """
        Check if all the arguments of the function where
        _device_checks is called are on the correct device,
        select the correct

        Parameters
        ----------
        device : str
            Device where the computation should take place.
            If called inside an emulator it should be the
            emulator device
        return_sla : bool, optional
            If True, returns the handle to the sparse linear algebra.
            Either sp.sparse.linalg or cp.scipy.sparse.linalg.
            Default to False.

        Returns
        -------
        module handle
            cp if the device is GPU
            np if the device is CPU
        """
        if self.device is None:
            raise QTeaLeavesError("None is only valid device in conversion.")

        if self.is_cpu() or not GPU_AVAILABLE:
            xp = np
            xsla = ssla
        else:
            xp = cp
            xsla = csla

        if return_sla:
            return xp, xsla

        return xp

    def expand_tensor(self, link, new_dim, ctrl="R"):
        """Expand  tensor along given link and to new dimension."""
        newdim = list(self.shape)
        newdim[link] = max(new_dim - newdim[link], 0)

        expansion = QteaTensor(newdim, ctrl=ctrl, dtype=self.dtype, device=self.device)

        return self.stack_link(expansion, link)

    @staticmethod
    def _gpu_idx(device_str):
        """
        Extract the GPU index based on a device string.

        Parameters
        ----------

        device_str : str
            Extract GPU index from this string.

        Returns
        -------

        gpu_idx : int | None
            Returns `None` if device string is no GPU.
            If device string is GPU, returns index or
            index of current device.
        """
        if not QteaTensor.is_gpu_static(device_str):
            return None

        if ":" not in device_str:
            return cp.cuda.runtime.getDevice()

        return int(device_str.split(":")[1])

    @staticmethod
    def _gpu_idx_context(device_str):
        """
        Build a context for the i-th GPU based on a device string.

        Parameters
        ----------

        device_str : str
            Extract GPU index from this string.

        Returns
        -------

        context : :class:`cp.cuda.Device` | :class:`nullcontext`
            Nullcontext is returned if device string is no GPU
            or if the index of the GPU corresponds to the current
            device. If the GPU index does not correspond to the
            current device, the corresponding context manager is
            returned to work on this device.
        """
        # pylint: disable-next=protected-access
        gpu_idx = QteaTensor._gpu_idx(device_str)
        if gpu_idx is None:
            return nullcontext()

        current = cp.cuda.runtime.getDevice()
        if current == gpu_idx:
            return nullcontext()

        return cp.cuda.Device(gpu_idx)

    # no gpu_switch necessary, only calls from split_qr
    def _split_qr_dim(self, rows, cols):
        """Split via QR knowing dimension of rows and columns."""
        xp = self._device_checks()

        if self.dtype == xp.float16:
            matrix = self._elem.astype(xp.float32).reshape(rows, cols)
            qmat, rmat = xp.linalg.qr(matrix)
            qmat = qmat.astype(xp.float16)
            rmat = rmat.astype(xp.float16)
        else:
            qmat, rmat = xp.linalg.qr(self._elem.reshape(rows, cols))

        qtens = QteaTensor.from_elem_array(qmat, dtype=self.dtype, device=self.device)
        rtens = QteaTensor.from_elem_array(rmat, dtype=self.dtype, device=self.device)

        return qtens, rtens

    # no gpu_switch necessary, only calls from split_rq
    def _split_rq_dim(self, rows, cols):
        """Split via RQ knowing dimension of rows and columns."""
        xp = self._device_checks()
        assert xp == np

        if self.dtype == xp.float16:
            matrix = self._elem.astype(xp.float32).reshape(rows, cols)
            rmat, qmat = sla.rq(matrix, mode="economic", check_finite=False)
            rmat = rmat.astype(xp.float16)
            qmat = qmat.astype(xp.float16)
        else:
            rmat, qmat = sla.rq(
                self._elem.reshape(rows, cols), mode="economic", check_finite=False
            )

        rtens = QteaTensor.from_elem_array(rmat, dtype=self.dtype, device=self.device)
        qtens = QteaTensor.from_elem_array(qmat, dtype=self.dtype, device=self.device)

        return rtens, qtens

    # no gpu_switch necessary, only calls from _truncate_singvals
    def _truncate_sv_ratio(self, singvals, conv_params):
        """
        Truncate the singular values based on the ratio
        with the biggest one.

        Parameters
        ----------
        singvals : np.ndarray
            Array of singular values
        conv_params : :py:class:`TNConvergenceParameters`, optional
            Convergence parameters to use in the procedure.

        Returns
        -------
        cut : int
            Number of singular values kept
        """
        xp = self._device_checks()

        # Truncation
        lambda1 = singvals[0]
        cut = xp.nonzero(singvals / lambda1 < conv_params.cut_ratio)[0]
        if self.is_gpu():
            cut = cut.get()

        chi_now = len(singvals)
        chi_by_conv = conv_params.max_bond_dimension
        chi_by_ratio = cut[0] if len(cut) > 0 else chi_now
        chi_min = conv_params.min_bond_dimension

        return self._truncate_decide_chi(chi_now, chi_by_conv, chi_by_ratio, chi_min)

    # no gpu_switch necessary, only calls from _truncate_singvals
    def _truncate_sv_norm(self, singvals, conv_params):
        """
        Truncate the singular values based on the
        total norm cut

        Parameters
        ----------
        singvals : np.ndarray
            Array of singular values
        conv_params : :py:class:`TNConvergenceParameters`, optional
            Convergence parameters to use in the procedure.

        Returns
        -------
        cut : int
            Number of singular values kept
        """
        xp = self._device_checks()

        norm = (singvals[::-1] ** 2).cumsum() / (singvals**2).sum()
        # You get the first index where the constraint is broken,
        # so you need to stop an index before
        cut = xp.nonzero(norm > conv_params.cut_ratio)[0]
        if self.is_gpu():
            cut = cut.get()

        chi_now = len(singvals)
        chi_by_conv = conv_params.max_bond_dimension
        chi_by_norm = len(singvals) - cut[0] if len(cut) > 0 else chi_now
        chi_min = conv_params.min_bond_dimension

        return self._truncate_decide_chi(chi_now, chi_by_conv, chi_by_norm, chi_min)


# pylint: disable-next=too-many-branches
def _process_svd_ctrl(svd_ctrl, max_bond_dim, shape, device, contract_singvals):
    """
    Process the svd_ctrl parameter for an SVD decomposition

    Parameters
    ----------
    svd_ctrl: str
        SVD identifier chosen by the user
    max_bond_dim : int
        Maximum bond dimension
    shape: Tuple[int]
        Shape of the matrix to be split
    device: str
        Device where the splitting is taking place
    contract_singvals: str
        Where to contract the singvals

    Return
    ------
    str
        The svd_ctrl after the double-check
    """
    # First, resolve selection by user
    if svd_ctrl in ("V", "D", "R"):
        return svd_ctrl

    # Previously ratio above 3 were considered good, bond dimension was not considered for X
    ratio_svd_ctrl_r = shape[1] / shape[0] * int(contract_singvals == "R")
    ratio_svd_ctrl_l = shape[0] / shape[1] * int(contract_singvals == "L")
    ratio_chis = min(shape[0], shape[1]) / max_bond_dim

    if svd_ctrl in ["E!", "X!"]:
        # Enforce eigenvalue decompositions
        if (contract_singvals == "L") and (ratio_svd_ctrl_l >= 1.0):
            # Good shape
            return svd_ctrl.replace("!", "")
        if contract_singvals == "L":
            # Bad shape and we need QR
            return svd_ctrl.replace("!", "+QR")
        if (contract_singvals == "R") and (ratio_svd_ctrl_r >= 1.0):
            # Good shape
            return svd_ctrl.replace("!", "")
        if contract_singvals == "R":
            # Bad shape and we need QR
            return svd_ctrl.replace("!", "+QR")

    # An eigenvalue decomposition is nice if we contract the singular values
    # to the right with shape[0] < shape[1] OR
    # contract singular values to the left with shape[1] < shape[0]
    good_svd_ctrl_e = (ratio_svd_ctrl_r >= 3.0) or (ratio_svd_ctrl_l >= 3.0)
    good_svd_ctrl_x = (
        (ratio_svd_ctrl_r >= 3.0) or (ratio_svd_ctrl_l >= 3.0) and (ratio_chis >= 2.0)
    )

    if svd_ctrl == "E" and good_svd_ctrl_e:
        return svd_ctrl

    if svd_ctrl == "X" and good_svd_ctrl_x:
        # The order might be worth discussing, X will never be used if E is
        # okay unless user chooses it.
        return svd_ctrl

    if svd_ctrl in ("E", "X", "E!", "X!"):
        # We could still attempt to calculate more eigen
        # values than we need singular values, which can lead
        # to instabilities. The user was asking for E or X,
        # so we ignored the default bounds

        # Let the autoselect to its job
        logger_warning("Ignoring user input for svd_ctrl.")
        svd_ctrl = "A"

    # Sparse problem, but with no singvals contracted on cpu,
    # use random svd decomposition
    if min(shape) >= 2 * max_bond_dim and QteaTensor.is_cpu_static(device):
        return "R"
    # If none of the above works, go with automatic selection
    # First, if we do not need to compute all the singvals, use
    # sparse eigenvalue decomposition
    if min(shape) >= 4 * max_bond_dim and good_svd_ctrl_x:
        return "X"
    # Non-sparse problem on GPU, with singvals contracted
    # to left or right
    if QteaTensor.is_gpu_static(device) and good_svd_ctrl_e:
        return "E"
    if good_svd_ctrl_e:
        # We should use eigendecomposition approach as well
        # on CPU
        return "E"
    # If everything else fails, we go for normal svd
    return "D"


class DataMoverNumpyCupy(_AbstractDataMover):
    """
    Data mover to move QteaTensor between numpy and cupy.

    Details
    -------

    Streams are linked to device as indicated by the following page:
    https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#stream-and-event-behavior
    and multi-GPU behavior:
    https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#multi-gpu
    """

    tensor_cls = (QteaTensor,)

    def __init__(self):
        if GPU_AVAILABLE:
            self.mover_stream = []
            for ii in range(NUM_GPUS):
                with cp.cuda.Device(ii):
                    self.mover_stream.append(cp.cuda.Stream(non_blocking=True))

            # cupy examples show that mempool depends on the current device
            # upon call time
            # https://docs.cupy.dev/en/stable/user_guide/memory.html#limiting-gpu-memory-usage
            self.mempool = cp.get_default_memory_pool()

            # Seems to be unused
            self.pinned_mempool = cp.get_default_pinned_memory_pool()
        else:
            self.mover_stream = None
            self.mempool = None
            self.pinned_mempool = None

    @property
    def device_memory(self):
        """Current memory occupied in the device."""
        return self.mempool.used_bytes()

    def sync_move(self, tensor, device):
        """
        Move the tensor `tensor` to the device `device`
        synchronously with the main computational stream.

        Parameters
        ----------
        tensor : _AbstractTensor
            The tensor to be moved
        device: str
            The device where to move the tensor
        """
        if GPU_AVAILABLE:
            tensor.convert(dtype=None, device=device)

    def async_move(self, tensor, device, stream=None):
        """
        Move the tensor `tensor` to the device `device`
        asynchronously with respect to the main computational
        stream.

        Parameters
        ----------
        tensor : _AbstractTensor
            The tensor to be moved
        device: str
            The device where to move the tensor
        stream : stream-object
            Stream to be used to move the data if a stream
            different from the data mover's stream should be
            used.
            Default to None (use DataMover's stream)
        """
        # To find the GPU index, we have to know if source or target is on GPU
        if stream is not None:
            # Do not interfere with user suggestion
            pass
        elif tensor.is_gpu():
            # Tensor is on GPU, take the corresponding stream
            # pylint: disable-next=protected-access
            gpu_idx = QteaTensor._gpu_idx(tensor.device)
            stream = self.mover_stream[gpu_idx]
        elif tensor.is_gpu(query=device):
            # Target should be GPU, take the corresponding stream
            # pylint: disable-next=protected-access
            gpu_idx = QteaTensor._gpu_idx(device)
            stream = self.mover_stream[gpu_idx]
        # else:
        # CPU --> CPU, but call anyway in case of new devices (stream is already None)

        tensor.convert(dtype=None, device=device, stream=stream)

    def wait(self, device=None):
        """
        Put a barrier for the streams and wait them.

        Parameters
        ----------

        device : str | None, optional
            If `None`, all streams will be synchronized.
            Default to `None`
        """
        if self.mover_stream is None:
            return

        if device is None:
            # Have to synchronize all of them
            for ii, stream in enumerate(self.mover_stream):
                # pylint: disable-next=protected-access
                with QteaTensor._gpu_idx_context(f"gpu:{ii}"):
                    stream.synchronize()

            return

        # pylint: disable-next=protected-access
        gpu_idx = QteaTensor._gpu_idx(device)
        if gpu_idx is not None:
            # pylint: disable-next=protected-access
            with QteaTensor._gpu_idx_context(f"gpu:{gpu_idx}"):
                self.mover_stream[gpu_idx].synchronize()
