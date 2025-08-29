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
MPO-like structure defining an uncompressed machine learning data set, which
can be used as effective operator in tensor network sweeps.
"""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-branches
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-locals

import logging

import numpy as np

from qtealeaves.tensors.abstracttensor import _AbstractQteaTensor
from qtealeaves.tooling import QTeaLeavesError

from .abstracteffop import _AbstractEffectiveOperators

__all__ = ["MLDataMPO"]

logger = logging.getLogger(__name__)


class MLDataTerm:
    """

    Arguments
    ---------

    tensor : :class:`_AbstractQteaTensor`
        Rank-5 tensor representing the effective operator in
        the :class:`MLDataMPO`

    Details
    -------

    .. code-block::

       The effective operators look at the moment like this

           2
           |
       0 --o-- 3
           |\
           | \
           1  4

    with 0: left neighbor, 1: label, 2: MPS, 3: right neighbor, 4: sample
    Therefore, the bond dimensions are for each link:

    0) usually one, would have to be equals across all samples.
    1) 1, except for the special effective operator carrying the labels.
    2) dimension of the feature map.
    3) usually one, would have to be equals across all samples.
    4) dimension of the samples.

    """

    def __init__(self, tensor):
        self.tensor = tensor

        if tensor.ndim != 5:
            raise QTeaLeavesError(
                f"Rank error for MLDataTerm tensor with {tensor.ndim}."
            )

    def __iter__(self):
        """Iterate through all the :class:`_AbstractQteaTensors`, here just one."""
        yield self.tensor

    def device(self):
        """Return the device by running query on tensor."""
        return self.tensor.device

    def dtype(self):
        """Return the dtype by running query on tensor."""
        return self.tensor.dtype

    def convert(self, *args, **kwargs):
        """Convert the data type and device of the `MLDataTerm`."""
        self.tensor.convert(*args, **kwargs)


class MLDataMPO(_AbstractEffectiveOperators):
    """
    Uncompressed machine learning data set for labeled data.

    Arguments
    ---------

    data_samples : List[py:class:`MPS`] | dict
        Feature dataset specified as list of MPS samples as in Miles
        Stoudenmire's paper.
        If dict: provide keys `num_sites`, `num_samples`, and `local_dim`.
        The class attribute `site_terms` will be set to None and it is
        up to the calling method to fill it consistently.

    labels : List[int]
        Labels of the dataset; must be range from 0 .. number of labels.
        (not supported: one-hot encoding, non-integer labels, etc.)

    batch_size : int
        Number of samples for a single sweep(epoch)

    tensor_backend : :class:`TensorBackend`
        Setting the backend for linear algebra etc.
    """

    def __init__(self, data_samples, labels, batch_size, tensor_backend):
        if isinstance(data_samples, dict):
            num_sites = data_samples["num_sites"]
            num_samples = data_samples["num_samples"]
            local_dim = data_samples["local_dim"]
        else:
            num_sites = data_samples[0].num_sites
            num_samples = len(data_samples)
            local_dim = data_samples[0][0].shape[1]

        self._num_sites = num_sites
        self._labels = labels
        self._num_labels = len(np.unique(self._labels))
        self._current_labels = None
        self._num_samples = num_samples
        self._batch_size = batch_size
        self._tensor_cls = tensor_backend.tensor_cls
        self._eff_ops = {}

        if self.batch_size > self.num_samples:
            raise ValueError(
                f"Invalid input with {self.batch_size=} > {self.num_samples}."
            )

        if isinstance(data_samples, dict):
            self.site_terms = None
            return

        links = [1, 1, local_dim, 1, num_samples]
        samples = [tensor_backend(links) for ii in range(num_sites)]
        for ii in range(num_samples):
            for jj in range(num_sites):
                samples[jj][:1, :1, :2, :1, ii : ii + 1] = data_samples[ii][jj].reshape(
                    [1, 1, local_dim, 1, 1]
                )

        self.site_terms = samples

    # --------------------------------------------------------------------------
    #                               Properties
    # --------------------------------------------------------------------------

    @property
    def device(self):
        """Device where the tensor is stored."""
        for _, tensor in self._eff_ops.items():
            return tensor.device

        return None

    @property
    def dtype(self):
        """Data type of the underlying arrays."""
        for _, tensor in self._eff_ops.items():
            return tensor.dtype

        return None

    @property
    def num_sites(self):
        """Return the number of sites in the underlying system."""
        return self._num_sites

    @property
    def has_oqs(self):
        """Return if effective operators is open system (if no support, always False)."""
        return False

    # Properties not enforced by parent class ----------------------------------

    @property
    def current_labels(self):
        """Current labels of batch. None before call to `setup_as_eff_ops`."""
        return self._current_labels

    @property
    def eff_ops(self):
        """Dictionary with effective operators."""
        return self._eff_ops

    @property
    def batch_size(self):
        """Batch size for one sweep / epoch."""
        return self._batch_size

    @property
    def num_labels(self):
        """NUmber of unique labels."""
        return self._num_labels

    @property
    def num_samples(self):
        """Number of samples in this training data set."""
        return self._num_samples

    # --------------------------------------------------------------------------
    #                          Overwritten operators
    # --------------------------------------------------------------------------

    def __getitem__(self, key):
        """Get an entry from the effective operators."""
        return self._eff_ops[key]

    def __setitem__(self, key, value):
        """Set an entry from the effective operators."""
        if isinstance(value, MLDataTerm):
            pass
        elif isinstance(value, _AbstractQteaTensor):
            value = MLDataTerm(value)
        else:
            raise TypeError(
                "Effective operator of MLDataMPO must be `_AbstractQteaTensor`, "
                f"but is `{type(value)}`."
            )

        # print("Setting", key, value.tensor.shape)
        self._eff_ops[key] = value

    # --------------------------------------------------------------------------
    #                          Classmethod, classmethod-like
    # --------------------------------------------------------------------------

    @classmethod
    def from_matrix(
        cls,
        data_samples,
        labels,
        batch_size,
        tensor_backend,
        emb_map,
        pad_extra_sites=0,
    ):
        """
        Smart initialization without list of :class:`MPS`.

        Arguments
        ---------

        data_samples : rank-2 with dimensions [samples, sites]
            Represents the data set with the first dimension being the samples
            and the second dimension being translated into sites.
            More generally, it can be a rank-n tensor with the first dimension
            being the samples, but has to be reshaped to [samples, sites, local_dim]
            by the embedding map.

        labels : rank-1 with dimension [samples]
            True labels of the data.

        batch_size : int
            Batch sized used in training. Must be smaller or equal to the
            number of samples.

        tensor_backend : :class:`TensorBackend`
            Choose the tensor backend for the simulation including the
            data type or the device etc.

        emb_map : callable
            Embedding map which encodes the features of the data set into
            qubits or qudits. The map should be able to take the data_samples
            and return a rank-3 tensor with dimensions [samples, sites, local_dim].

        pad_extra_sites : int
            Number of padding sites to be added to the embedded data, i.e. the
            quantum state. This is useful for the TTN ansatz, where the number
            of sites has to be a power of 2. The padding sites are |0>.

        """

        embedded_data = emb_map(data_samples)
        logger.debug("Embedded data shape: %s", embedded_data.shape)

        num_samples, num_sites, local_dim = embedded_data.shape

        links = [1, 1, local_dim, 1, num_samples]
        samples = []
        for ii in range(num_sites):
            tensor = tensor_backend(links)

            tensor = tensor.from_elem_array(
                np.transpose(embedded_data[:, ii], (1, 0)).reshape(
                    1, 1, local_dim, 1, num_samples
                ),
                dtype=tensor_backend.dtype,
                device=tensor_backend.memory_device,
            )
            samples.append(tensor)

        if pad_extra_sites > 0:
            for ii in range(pad_extra_sites):
                samples.append(
                    tensor.from_elem_array(
                        np.concatenate(
                            [
                                np.ones((1, 1, 1, 1, num_samples)),
                                np.zeros((1, 1, local_dim - 1, 1, num_samples)),
                            ],
                            axis=2,
                        ),
                        dtype=tensor_backend.dtype,
                        device=tensor_backend.memory_device,
                    )
                )
            num_sites += pad_extra_sites

        data_samples_dummy = {
            "num_sites": num_sites,
            "num_samples": num_samples,
            "local_dim": local_dim,
        }

        obj = cls(data_samples_dummy, labels, batch_size, tensor_backend)
        obj.site_terms = samples

        return obj

    # --------------------------------------------------------------------------
    #                        Abstract effective operator methods
    # --------------------------------------------------------------------------

    def contr_to_eff_op(self, tensor, pos, pos_links, idx_out):
        """
        Calculate the effective operator along a link.

        Arguments
        ---------

        tensor : :class:`_AbstractQteaTensor`
            Tensor to be contracted to effective operator.

        pos : int, tuple (depending on TN)
            Position of tensor.

        pos_links : list of int, tuple (depending on TN)
            Position of neighboring tensors where the links
            in `tensor` lead to.

        idx_out : int
            Uncontracted link to be used for effective operator.

        Returns
        -------

        None (inplace update)
        """
        rank = tensor.ndim
        if (rank == 3) and (idx_out == 0):
            self._contr_to_eff_op_rank_3_link_0(tensor, pos, pos_links)
        elif (rank == 3) and (idx_out == 1):
            self._contr_to_eff_op_rank_3_link_1(tensor, pos, pos_links)
        elif (rank == 3) and (idx_out == 2):
            self._contr_to_eff_op_rank_3_link_2(tensor, pos, pos_links)
        else:
            raise NotImplementedError(
                f"Case with idx_out={idx_out} and rank={rank} not implmented yet."
            )

    # pylint: disable-next=too-many-arguments
    def contract_tensor_lists(
        self, tensor, pos, pos_links, custom_ops=None, pre_return_hook=None
    ):
        """
        Linear operator to contract all the effective operators
        around the tensor in position `pos`. Used in the optimization.
        Not implemented for machine learning.
        """
        if pre_return_hook is not None:
            raise NotImplementedError(
                f"Trying to pass {pre_return_hook=}. Should be None."
            )
        raise NotImplementedError("Should not be required for machine learning.")

    def convert(self, dtype, device):
        """
        Convert underlying array to the specified data type inplace. Original
        site terms are preserved.
        """
        if (self.dtype == dtype) and (self.device == device):
            return

        for _, tensor in self._eff_ops.items():
            tensor.convert(dtype, device)

    def get_accuracy(self, classificator):
        """
        Calculate the accuracy of a classificator for the data set.

        Arguments
        ---------

        classificator : :class:`_AbstractTN` enabled for TN-ML
            Ansatz trained as predictor.

        Returns
        -------

        accuracy : float
            Number of matches over the number of samples.
        """
        prediction = classificator.ml_predict(self)
        num_matches = np.sum(np.array(prediction) == self._labels)

        return num_matches / self.num_samples

    def _select_training_batch(self, tensor_network):
        """
        Selection of batch.

        Arguments
        ---------

        tensor_network : :class:`_AbstractTN`
            Used to get data type and device.

        Returns
        -------

        current : list[_AbstractQteaTensor]
            List of tensors with one tensor per site.
        """
        if self.batch_size == self.num_samples:
            current = [elem.copy() for elem in self.site_terms]
            self._current_labels = self._tensor_cls.from_elem_array(
                self._labels[:],
                dtype=tensor_network.dtype,
                device=tensor_network.computational_device,
            )
        else:
            indexes = np.random.choice(self.num_samples, self.batch_size, replace=False)
            indexes = indexes[np.argsort(indexes)]
            current = [
                elem.subtensor_along_link_inds(4, indexes) for elem in self.site_terms
            ]
            self._current_labels = self._tensor_cls.from_elem_array(
                self._labels[indexes],
                dtype=tensor_network.dtype,
                device=tensor_network.computational_device,
            )

        return current

    def setup_as_eff_ops(self, tensor_network, measurement_mode=False):
        """Set this sparse MPO as effective ops in TN and initialize."""
        tensor_cls = self._tensor_cls

        # Select the training batch
        current = self._select_training_batch(tensor_network)

        # pylint: disable-next=protected-access
        for ii, key in enumerate(tensor_network._iter_physical_links()):
            current[ii].convert(
                tensor_network.dtype, device=tensor_network.memory_device
            )
            self[key] = current[ii]

        dtype = tensor_network.dtype
        device = tensor_network.memory_device

        # There are some special effective operators needed
        if tensor_network.extension in ["mps"]:
            # Left boundary operator
            chi_l = tensor_network[0].shape[0]
            links = [1, chi_l, chi_l, 1, self.batch_size]
            eff_op = tensor_cls(links, dtype=dtype, device=device)
            eye = tensor_cls(links[1:3], ctrl="1", dtype=dtype, device=device)
            for ii in range(self.batch_size):
                eff_op[:1, :chi_l, :chi_l, :1, ii : ii + 1] = eye

            self[(None, 0)] = eff_op

            # Right boundary operator # LPTN order for labellink=kraus
            chi_r = tensor_network[-1].shape[-1]
            links = [1, chi_r, chi_r, 1, self.batch_size]
            if chi_r > 1:
                eff_op = tensor_cls(links, dtype=dtype, device=device)
                eye = tensor_cls(links[1:3], ctrl="1", dtype=dtype, device=device)
                for ii in range(self.batch_size):
                    eff_op[:1, :chi_l, :chi_l, :1, ii : ii + 1] = eye

            else:
                eff_op = tensor_cls(links, ctrl="O", dtype=dtype, device=device)

            self[(None, self.num_sites - 1)] = eff_op
        elif tensor_network.extension in ["tto"]:
            # Top tensor operator
            if (tensor_network[0][0].shape[2] != 1) and (
                "labelenv" not in tensor_network.tn_ml_mode
            ):
                shape = tensor_network[0][0].shape
                tensor_network[0][0] = tensor_network[0][0].subtensor_along_link_inds(
                    2, [0]
                )
                tensor_network.normalize()
                logging.warning(
                    "Reducing TTO to pure state for ML, previous shape=%s.", str(shape)
                )

            if tensor_network[0][0].ndim == 3:
                # Scalar label
                chi_l = tensor_network[(0, 0)].shape[2]
            else:
                # Vector label + argmax
                chi_l = 1
            links = [1, chi_l, chi_l, 1, self.batch_size]
            eff_op = tensor_cls(links, dtype=dtype, device=device)
            eye = tensor_cls(links[1:3], ctrl="1", dtype=dtype, device=device)
            for ii in range(self.batch_size):
                eff_op[:1, :chi_l, :chi_l, :1, ii : ii + 1] = eye

            self[(None, (0, 0))] = eff_op

        else:
            raise TypeError(f"Ansatz {tensor_network.extension} not yet enabled.")

        # Last chance to change iso center
        if tensor_network.iso_center is None:
            logger.warning("Isometrizing TN on the fly in `build_effective_operators`.")
            tensor_network.isometrize_all()

        if tensor_network.iso_center != tensor_network.default_iso_pos:
            tensor_network.iso_towards(tensor_network.default_iso_pos, trunc=True)

        tensor_network.eff_op = self
        tensor_network.build_effective_operators()

    # --------------------------------------------------------------------------
    #                            Effective operator methods
    # --------------------------------------------------------------------------

    def print_summary(self):
        """Print summary of computational effort (by default no report)."""

    # --------------------------------------------------------------------------
    #                     Methods not required by parent class
    # --------------------------------------------------------------------------

    def _contr_to_eff_op_rank_3_link_0(self, tensor, pos, pos_links):
        """
        Build effective operator for rank-3 and idx_out=0 fixed.

        Arguments
        ---------

        tensor : :class:`_AbstractQteaTensor`
            Tensor to be contracted to effective operator.

        pos : int, tuple (depending on TN)
            Position of tensor.

        pos_links : list of int, tuple (depending on TN)
            Position of neighboring tensors where the links
            in `tensor` lead to.

        Returns
        -------

        None (inplace update)
        """
        idx_out = 0
        ops_list, idx_list, key, ikey = self._helper_contract_to_eff_op(
            pos, pos_links, idx_out, keep_none=True
        )

        if len(ops_list) != 2:
            raise ValueError("MLDataMPO might have None as effective operator.")

        if idx_list[0] > idx_list[1]:
            raise QTeaLeavesError("MLDataMPO currently only for sorted idx_list.")

        eff_op = tensor.einsum(
            "abc,ijbkl,kxcyl->ijxayl", ops_list[0].tensor.conj(), ops_list[1].tensor
        )
        eff_op.fuse_links_update(1, 2)

        assert eff_op.shape[2] == tensor.shape[0]

        self[key] = eff_op
        if ikey in self._eff_ops:
            del self._eff_ops[ikey]

    def _contr_to_eff_op_rank_3_link_1(self, tensor, pos, pos_links):
        """
        Build effective operator for rank-3 and idx_out=1 fixed.

        Arguments
        ---------

        tensor : :class:`_AbstractQteaTensor`
            Tensor to be contracted to effective operator.

        pos : int, tuple (depending on TN)
            Position of tensor.

        pos_links : list of int, tuple (depending on TN)
            Position of neighboring tensors where the links
            in `tensor` lead to.

        Returns
        -------

        None (inplace update)
        """
        idx_out = 1
        ops_list, idx_list, key, ikey = self._helper_contract_to_eff_op(
            pos, pos_links, idx_out, keep_none=True
        )

        if len(ops_list) != 2:
            raise ValueError("MLDataMPO might have None as effective operator.")

        if idx_list[0] > idx_list[1]:
            raise QTeaLeavesError("MLDataMPO currently only for sorted idx_list.")

        eff_op = (
            ops_list[0]
            .tensor.conj()
            .einsum("abcde,cij,xyjae->dbyixe", tensor, ops_list[1].tensor)
        )
        eff_op.fuse_links_update(1, 2)

        self[key] = eff_op
        if ikey in self._eff_ops:
            del self._eff_ops[ikey]

    def _contr_to_eff_op_rank_3_link_2(self, tensor, pos, pos_links):
        """
        Build effective operator for rank-3 and idx_out=2 fixed.

        Arguments
        ---------

        tensor : :class:`_AbstractQteaTensor`
            Tensor to be contracted to effective operator.

        pos : int, tuple (depending on TN)
            Position of tensor.

        pos_links : list of int, tuple (depending on TN)
            Position of neighboring tensors where the links
            in `tensor` lead to.

        Returns
        -------

        None (inplace update)
        """
        idx_out = 2
        ops_list, idx_list, key, ikey = self._helper_contract_to_eff_op(
            pos, pos_links, idx_out, keep_none=True
        )

        if len(ops_list) != 2:
            raise ValueError("MLDataMPO might have None as effective operator.")

        if idx_list[0] > idx_list[1]:
            raise QTeaLeavesError("MLDataMPO currently only for sorted idx_list.")

        eff_op = ops_list[0].tensor.einsum(
            "abcde,cij,dxiye->abxjye", tensor, ops_list[1].tensor.conj()
        )
        eff_op.fuse_links_update(1, 2)

        assert eff_op.shape[2] == tensor.shape[2]

        self[key] = eff_op
        if ikey in self._eff_ops:
            del self._eff_ops[ikey]
