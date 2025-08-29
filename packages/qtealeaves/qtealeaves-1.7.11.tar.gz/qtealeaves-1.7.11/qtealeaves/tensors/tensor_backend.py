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
Tensor backend specification.
"""

# pylint: disable=too-many-arguments
# pylint: disable=too-few-public-methods

import logging

import numpy as np

from .tensor import DataMoverNumpyCupy, QteaTensor

__all__ = ["TensorBackend"]

logger = logging.getLogger(__name__)


# pylint: disable-next=dangerous-default-value
def logger_warning(*args, storage=[]):
    """Workaround to display warnings only once in logger."""
    if args in storage:
        return

    storage.append(args)
    logger.warning(*args)


class TensorBackend:
    """
    Defines the complete tensor backend to be used. Contains the tensor class,
    the base tensor class in case it is needed for symmetric tensors, the
    target device, and the data type.

    Parameters
    ----------
    tensor_cls: _AbstractTensor, optional
        Tensor class. Might be dense or symmetric.
        Default to `QteaTensor`
    base_tensor_cls: _AbstractTensor, optional
        The dense tensor class if `tensor_cls` was symmetric.
        Same as `tensor_cls` for dense tensors.
        Default to `QteaTensor`.
    device: str, optional
        Device of the tensors. Devices available depend on `tensor_cls`.
        The possible device available are:
        - "cpu"
        - "gpu"
        - "cpu+gpu", where the tensor network will be stored in the "cpu",
          but all the computational demanding tasks will be executed on
          the "gpu".
        Default to "cpu".
    dtype: np.dtype, optional
        Type of the tensor network. Available types depends on 'tensor_cls`.
        Default to `np.complex128`.
    symmetry_injector : class similar to `AbelianSymmetryInjector` or `None`
        Provides `inject_parse_symmetries`, `inject_trivial_symmetry`,
        and `inject_parse_sectors` for parsing symmetries and sectors
        as well as providing the trivial symmetry representation.
        Default to `None` (only valid for no symmetries).
    datamover : instance of :class:`_AbstractDataMover`
        Data mover compatible with the base_tensor_cls
        Default to :class:`DataMoverNumpyCupy`
    """

    # pylint: disable-next=too-many-arguments
    def __init__(
        self,
        tensor_cls=QteaTensor,
        base_tensor_cls=QteaTensor,
        device="cpu",
        dtype=np.complex128,
        symmetry_injector=None,
        datamover=DataMoverNumpyCupy(),
    ):
        self.tensor_cls = tensor_cls
        self.base_tensor_cls = base_tensor_cls
        self.device = device
        self.dtype = dtype
        self.datamover = datamover

        # Check the compatibility between datamover and tensor class
        self.datamover.check_tensor_cls_compatibility(base_tensor_cls)

        self._symmetry_injector = symmetry_injector

    @property
    def computational_device(self):
        """Device where the computations are done"""
        if self.device == "cgpu":
            logger_warning("Deprecation mixed-device `cgpu`, use `cpu+gpu` instead.")
            return "gpu"

        if "+" in self.device:
            return self.device.split("+")[-1]

        return self.device

    @property
    def memory_device(self):
        """Device where the tensor is stored"""
        if self.device == "cgpu":
            logger_warning("Deprecation mixed-device `cgpu`, use `cpu+gpu` instead.")
            return "cpu"

        if "+" in self.device:
            return self.device.split("+")[0]

        return self.device

    def __call__(self, *args, create_base_tensor_cls=False, **kwargs):
        """
        The call method is an interface to initialize tensors of the `tensor_cls`

        Parameters
        ----------

        links : link as requested by tensor class.
            Specifies the link in the tensor.

        create_base_tensor_cls : bool, optional
            If `True`, create base tensor class instead of tensor class.
            Default to `False`.

        kwargs: optional
            All optional arguments of the tensor's init method are allowed, e.g.,
            ctrl, are_links_outgoing, base_tensor_cls, dtype, device. If
            base_tensor_cls, device, and dtype are not given, they will be taken
            from the attributes of the this class instead of using default
            arguments.

        """
        auto = {}
        for key, value in self.tensor_cls_kwargs().items():
            if key not in kwargs:
                auto[key] = value

        if create_base_tensor_cls:
            return self.base_tensor_cls(*args, **kwargs, **auto)

        return self.tensor_cls(*args, **kwargs, **auto)

    def from_elem_array(self, array, **kwargs):
        """
        Call the `from_elem_array` method of the underlying base_tensor_cls.

        Parameters
        ----------

        array : tensor
            Tensor to be converted into :class:`_AbstractQteaBaseTensor`.
            Can be numpy or native native type of base tensor's library.

        Returns
        -------

        tensor : :class:`_AbstractBaseTensorClass`
            Tensor/array as Quantum Tea tensor.
        """
        auto = {}
        for key in ["dtype", "device"]:
            if key not in kwargs:
                auto[key] = self.tensor_cls_kwargs()[key]

        return self.base_tensor_cls.from_elem_array(array, **kwargs, **auto)

    def __getstate__(self):
        """Method used to save a pickle"""
        obj = self.__dict__.copy()
        obj["datamover"] = self.datamover.__class__
        obj["_symmetry_injector"] = self._symmetry_injector.__class__
        return obj

    def __setstate__(self, state):
        """Method to load pickleed the object"""
        self.__dict__ = state
        self.datamover = self.datamover()
        self._symmetry_injector = self._symmetry_injector()

    def eye_like(self, link):
        """
        Create identity, unlike version in `_AbstractQteaTensor`, no existing
        tensor is required.

        **Arguments**

        link : same as returned by `links` property, here integer.
            Dimension of the square, identity matrix.
        """
        tmp = self.tensor_cls(
            [link, link],
            are_links_outgoing=[True, False],
            base_tensor_cls=self.base_tensor_cls,
            dtype=self.dtype,
            device=self.memory_device,
            ctrl="Z",
        )
        return tmp.eye_like(link)

    def set_seed(self, seed):
        """
        Set the seed for numpy and the tensor backend if different from numpy.
        (tensor backend still depends on if it is available for now).

        Arguments
        ---------

        seed : list[int]
            List of integers used as a seed; list has length 4.
        """
        devices = [self.memory_device, self.computational_device]
        self.base_tensor_cls.set_seed(seed, devices=devices)

        # We might set numpy seed twice, but that is okay
        np.random.seed(seed)

    def tensor_cls_kwargs(self):
        """
        Returns the keywords arguments for an `_AbstractQteaTensor`.
        """
        return {
            "base_tensor_cls": self.base_tensor_cls,
            "device": self.computational_device,
            "dtype": self.dtype,
        }

    def parse_symmetries(self, params):
        """Parse the symmetry via a function which has to be passed by the user to `__init__`."""
        if self._symmetry_injector is None:
            raise ValueError("Tensor backend is not providing parsing for symmetries.")

        return self._symmetry_injector.inject_parse_symmetries(params)

    def trivial_symmetry(self):
        """Get trivial symmetry via a function which has to be passed by the user to `__init__`."""
        if self._symmetry_injector is None:
            raise ValueError("Tensor backend is not providing trivial symmetry.")

        return self._symmetry_injector.inject_trivial_symmetry()

    def parse_sectors(self, params, sym):
        """Parse the sectors via a function which has to be passed by the user to `__init__`."""
        if self._symmetry_injector is None:
            raise ValueError("Tensor backend is not providing parsing for sectors.")

        return self._symmetry_injector.inject_parse_sectors(params, sym)
