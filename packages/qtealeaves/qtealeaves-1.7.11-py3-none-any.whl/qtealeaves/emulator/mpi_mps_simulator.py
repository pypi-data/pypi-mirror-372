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
The module contains a the MPI version of the MPS simulator.

Code for the MPI simulations should be run as:

.. code-block::
   mpiexec -n 4 python my_mpi_script.py

where we used 4 processes as an example.
"""
import numpy as np

from qtealeaves.convergence_parameters import TNConvergenceParameters
from qtealeaves.tensors import TensorBackend
from qtealeaves.tooling.mpisupport import MPI, TN_MPI_TYPES

from .mps_simulator import MPS

__all__ = ["MPIMPS"]


# pylint: disable-next=too-many-instance-attributes
class MPIMPS(MPS):
    """
    MPI version of the MPS emulator that divides the MPS between the different nodes

    Parameters
    ----------
    num_sites: int
        Number of sites
    convergence_parameters: :py:class:`TNConvergenceParameters`
        Class for handling convergence parameters. In particular, in the MPS simulator we are
        interested in:
        - the *maximum bond dimension* :math:`\\chi`;
        - the *cut ratio* :math:`\\epsilon` after which the singular
            values are neglected, i.e. if :math:`\\lamda_1` is the
            bigger singular values then after an SVD we neglect all the
            singular values such that :math:`\\frac{\\lambda_i}{\\lambda_1}\\leq\\epsilon`
    local_dim: int or list of ints, optional
        Local dimension of the degrees of freedom. Default to 2.
        If a list is given, then it must have length num_sites.
    initialize: str, optional
        The method for the initialization. Default to "vacuum"
        Available:
        - "vacuum", for the |000...0> state
        - "random", for a random state at given bond dimension
    tensor_backend : `None` or instance of :class:`TensorBackend`
        Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.

    """

    # pylint: disable-next=too-many-arguments
    def __init__(
        self,
        num_sites,
        convergence_parameters,
        local_dim=2,
        initialize="vacuum",
        tensor_backend=None,
    ):
        if MPI is None:
            raise ImportError("No module mpi4py found in python environment")
        # MPI variables
        # pylint: disable-next=c-extension-no-member
        self.comm = MPI.COMM_WORLD
        self.size = self.comm.Get_size()
        self.rank = self.comm.Get_rank()
        self.tot_sites = num_sites

        # Number of sites in the local MPS
        modulus = num_sites % self.size
        local_num_size = int(np.floor(num_sites // self.size))
        self.indexes = [0] + [
            local_num_size + 1 if ii < modulus else local_num_size
            for ii in range(self.size)
        ]
        local_num_size = self.indexes[self.rank + 1]

        # indexes takes into account which indexes are in each core
        self.indexes = np.cumsum(self.indexes)

        # The par_map is a dicrionary where the index is the position of the
        # sites in the full chain, while the value the position on the
        # subchain in this process
        self.par_map = dict(
            zip(
                np.arange(
                    self.indexes[self.rank], self.indexes[self.rank + 1], dtype=int
                ),
                np.arange(local_num_size, dtype=int),
            )
        )

        # Auxiliary site for the boundaries
        if self.rank < self.size - 1:
            local_num_size += 1

        if not np.isscalar(local_dim):
            local_dim = local_dim[
                self.indexes[self.rank] : self.indexes[self.rank + 1]
                + int(self.rank != (self.size - 1))
            ]

        super().__init__(
            local_num_size,
            convergence_parameters,
            local_dim=local_dim,
            initialize=initialize,
            tensor_backend=tensor_backend,
        )

        # MPS initializetion not aware of device
        self.convert(self.tensor_backend.dtype, self.tensor_backend.memory_device)

    @property
    def mpi_dtype(self):
        """Return the MPI version of the MPS dtype (going via first tensor)"""
        return TN_MPI_TYPES[np.dtype(self[0].dtype).str]

    def get_tensor_of_site(self, idx):
        """Retrieve tensor of specifc site."""
        return self[self.par_map[idx]]

    def apply_one_site_operator(self, op, pos):
        """
        Applies a one operator `op` to the site `pos` of the MPIMPS.
        Instead of communicating the changes on the boundaries we
        perform an additional contraction.

        Parameters
        ----------
        op: numpy array shape (local_dim, local_dim)
            Matrix representation of the quantum gate
        pos: int
            Position of the qubit where to apply `op`.
        """
        # Apply the gate on the right MPS
        if pos in self.par_map:
            super().apply_one_site_operator(op, self.par_map[pos])

        # For one-qubit gates it is more convenient to apply them both to
        # the real and auxiliary qubits if they are on the boundaries
        elif pos - 1 in self.par_map:
            super().apply_one_site_operator(op, self.num_sites - 1)

        return None

    # pylint: disable-next=too-many-arguments
    def apply_two_site_operator(self, op, pos, swap=False, svd=None, parallel=None):
        """
        Applies a two-site operator `op` to the site `pos`, `pos+1` of the MPS.
        Then, perform the necessary communications between the interested
        process and the process

        Parameters
        ----------
        op: numpy array shape (local_dim, local_dim, local_dim, local_dim)
            Matrix representation of the quantum gate
        pos: int or list of ints
            Position of the qubit where to apply `op`. If a list is passed,
            the two sites should be adjacent. The first index is assumed to
            be the control, and the second the target. The swap argument is
            overwritten if a list is passed.
        swap: bool
            If True swaps the operator. This means that instead of the
            first contraction in the following we get the second.
            It is written is a list of pos is passed.
        svd : None
            Required for compatibility. Can be only True.
        parallel: None
            Required for compatibility. Can be only True

        Returns
        -------
        singular_values_cutted: ndarray
            Array of singular values cutted, normalized to the biggest singular value

        """
        if not np.isscalar(pos) and len(pos) == 2:
            pos = min(pos[0], pos[1])
        elif not np.isscalar(pos):
            raise ValueError(
                f"pos should be only scalar or len 2 array-like, not len {len(pos)}"
            )

        # Hardcoded but necessary for compatibility
        svd = True
        parallel = True

        if pos in self.par_map:
            res = super().apply_two_site_operator(
                op, self.par_map[pos], swap, svd=svd, parallel=parallel
            )

            # Send the information back to the auxiliary if it was the first site
            if self.par_map[pos] == 0 and self.rank > 0:
                self.mpi_send_tensor(self[0], to_=self.rank - 1)
                self.comm.Send(
                    [
                        self.singvals[1],
                        TN_MPI_TYPES[self.singvals[1].dtype.str],
                    ],
                    self.rank - 1,
                )

            # Send the information towards the next if it was the last site
            elif self.par_map[pos] == self.num_sites - 2 and self.rank < self.size - 1:
                self.mpi_send_tensor(self[self.num_sites - 1], to_=self.rank + 1)
                self.comm.Send(
                    [
                        self.singvals[self.num_sites - 1],
                        TN_MPI_TYPES[self.singvals[self.num_sites - 1].dtype.str],
                    ],
                    self.rank + 1,
                )

        else:
            res = []
            # Receive the information from the MPS on the right
            if pos == self.indexes[self.rank + 1] and self.rank < self.size - 1:
                tens = self.mpi_receive_tensor(from_=self.rank + 1)

                self[self.num_sites - 1] = tens

                singvals = np.empty(tens.shape[2], self.singvals[self.num_sites].dtype)
                self.comm.Recv(
                    [
                        singvals,
                        TN_MPI_TYPES[self.singvals[self.num_sites].dtype.str],
                    ],
                    self.rank + 1,
                )
                self._singvals[self.num_sites] = singvals

            # Receive the information from the MPS from the left
            if pos == self.indexes[self.rank] - 1 and self.rank > 0:
                tens = self.mpi_receive_tensor(from_=self.rank - 1)
                self[0] = tens

                singvals = np.empty(tens.shape[0], self.singvals[0].dtype)
                self.comm.Recv(
                    [
                        singvals,
                        TN_MPI_TYPES[self.singvals[0].dtype.str],
                    ],
                    self.rank - 1,
                )
                self._singvals[0] = singvals

        return res

    def apply_projective_operator(self, site, selected_output=None, remove=False):
        """
        Apply a projective operator to the site **site**, and give the measurement as output.
        You can also decide to select a given output for the measurement, if the probability is
        non-zero. Finally, you have the possibility of removing the site after the measurement.

        Parameters
        ----------
        site: int
            Index of the site you want to measure
        selected_output: int, optional
            If provided, the selected state is measured. Throw an error if the probability of the
            state is 0
        remove: bool, optional
            If True, the measured index is traced away after the measurement. Default to False.

        Returns
        -------
        meas_state: int | None
            Measured state or None if site not in this part of the MPI-MPS.
        state_prob : float | None
            Probability of measuring the output state or None if site not
            in this part of the MPI-MPS.
        """
        self.reinstall_isometry_serial()
        if site in self.par_map:
            res = super().apply_projective_operator(
                self.par_map[site], selected_output, remove
            )
        else:
            res = (None, None)

        # Move informations to further right
        self.reinstall_isometry_serial(left=False, from_site=site)
        # Move information to the left
        self.reinstall_isometry_serial()

        return res

    # pylint: disable-next=arguments-differ
    def reinstall_isometry_serial(self, left=False, from_site=None):
        """
        Reinstall the isometry center on position 0 of the full MPS.

        This step is serial because we have to serially pass the information
        along the MPS. It cannot be parallelized.

        Parameters
        ----------
        left: bool, optional
            If True, reinstall the isometry to the left.
            If False, to the right. Defaulto to False
        from_site: int, optional
            The site from which the isometrization should start.
            By default None, i.e. the other end of the MPS chain.

        Returns
        -------
        None
        """
        if from_site is None:
            from_site = self.num_sites - 1 if left else 0
        extrem = np.nonzero(from_site <= self.indexes)[0][0]

        if left:
            boundaries = (extrem, -1, -1)
            tidx = 0
            to_ = self.rank - 1
            from_ = self.rank + 1
        else:
            boundaries = (extrem, self.size, 1)
            tidx = self.num_sites - 1
            to_ = self.rank + 1
            from_ = self.rank - 1

        for ii in range(*boundaries):
            if self.rank == ii:
                self._first_non_orthogonal_left = self.num_sites - 1
                self._first_non_orthogonal_right = self.num_sites - 1
                if left:
                    self.right_canonize(0, True, True)
                else:
                    self.left_canonize(self.num_sites - 1, True, True)

                # Send tensor
                if (self.rank > 0 and left) or (self.rank + 1 < self.size and not left):
                    self.mpi_send_tensor(self[tidx], to_=to_)

            elif (self.rank == ii - 1 and left) or (self.rank == ii + 1 and not left):
                # Receive tensor
                tens = self.mpi_receive_tensor(from_=from_)
                self[self.num_sites - 1 - tidx] = tens

    # pylint: disable-next=arguments-differ
    def reinstall_isometry_parallel(self, num_cycles):
        """
        Reinstall the isometry by applying identities to all even sites and
        to all odd sites, and repeating for `num_cycles` cycles.
        The reinstallation is exact for `num_cycles=num_sites/2`.
        Method from https://arxiv.org/abs/2312.02667

        This step is serial because we have to serially pass the information
        along the MPS. It cannot be parallelized.

        Parameters
        ----------
        num_cycles: int
            Number of cycles for reinstalling the isometry

        Returns
        -------
        None
        """
        for _ in range(num_cycles):
            # Apply on all even sites
            for ii in range(0, self.tot_sites - 1, 2):
                self.apply_two_site_operator(
                    self[0].eye_like(4), ii, svd=True, parallel=True
                )
            # Apply on all odd sites
            for ii in range(1, self.tot_sites - 1, 2):
                self.apply_two_site_operator(
                    self[0].eye_like(4), ii, svd=True, parallel=True
                )

    def mpi_gather_tn(self):
        """
        Gather the tensors on process 0.
        We do not use MPI.comm.Gather because we would gather lists of np.arrays
        without using the np.array advantages, making it slower than the single
        communications.

        Returns
        -------
        list on np.ndarray or None
            List of tensors on the rank 0 process, None on the others
        """
        self.comm.Barrier()
        if self.rank != 0:
            num_tensors = (
                self.num_sites if self.rank == self.size - 1 else self.num_sites - 1
            )
            for jj in range(num_tensors):
                self.mpi_send_tensor(self[jj], to_=0)
            tensor_list = None
        else:
            tensor_list = [None for _ in range(self.tot_sites)]
            tensor_list[: self.num_sites - 1] = self.tensors[:-1]

            tidx = self.num_sites - 1
            for ii in range(1, self.size):
                num_tensors = self.indexes[ii + 1] - self.indexes[ii]
                for jj in range(num_tensors):
                    tens = self.mpi_receive_tensor(from_=ii)
                    tensor_list[tidx + jj] = tens
                tidx += num_tensors

        self.comm.Barrier()

        return tensor_list

    def mpi_scatter_tn(self, tensor_list):
        """
        Scatter the tensors on process 0.
        We do not use MPI.comm.Scatter because we would gather lists of np.arrays
        without using the np.array advantages, making it slower than the single
        communications.

        Parameters
        ----------
        tensor_list : list of lists of np.ndarrays
            The index i of the list is sent to the rank i

        Returns
        -------
        list on np.ndarray or None
            List of tensors on the rank 0 process, None on the others
        """
        self.comm.Barrier()
        if self.rank == 0:
            for ridx, sub_tensorlist in enumerate(tensor_list[1:]):
                for idx, tens in enumerate(sub_tensorlist):
                    self.mpi_send_tensor(tens, to_=ridx + 1)

            tensor_list = tensor_list[0]
        else:
            num_tensors = len(tensor_list[self.rank])
            tensor_list = [None for _ in range(num_tensors)]
            for idx in range(num_tensors):
                tens = self.mpi_receive_tensor(from_=0)
                tensor_list[idx] = tens

        self.comm.Barrier()

        return tensor_list

    def to_tensor_list(self):
        """
        Return the tensor list of the full MPS. Thus, here there are
        communications between the different processes and all the tensorlist
        is returned on process 0

        Returns
        -------
        list of np.ndarray or None
            List of tensors on the rank 0 process, None on the others
        """
        return self.mpi_gather_tn()

    def to_statevector(self, qiskit_order=False, max_qubit_equivalent=20):
        """
        Serially compute the statevector

        Parameters
        ----------
        qiskit_order: bool, optional
            weather to use qiskit ordering or the theoretical one. For
            example the state |011> has 0 in the first position for the
            theoretical ordering, while for qiskit ordering it is on the
            last position.
        max_qubit_equivalent: int, optional
            Maximum number of qubit sites the MPS can have and still be
            transformed into a statevector.
            If the number of sites is greater, it will throw an exception.
            Default to 20.

        Returns
        -------
        np.ndarray or None
            Statevector on process 0, None on the others
        """

        tensorlist = self.to_tensor_list()
        if self.rank == 0:
            mps = MPS.from_tensor_list(tensorlist)
            statevect = mps.to_statevector(qiskit_order, max_qubit_equivalent)
        else:
            statevect = None

        return statevect

    @classmethod
    def from_tensor_list(
        cls,
        tensor_list,
        conv_params=None,
        tensor_backend=None,
        target_device=None,
    ):
        """
        Initialize the MPS tensors using a list of correctly shaped tensors

        Parameters
        ----------
        tensor_list : list of ndarrays or cupy arrays
            List of tensor for initializing the MPS
        conv_params : :py:class:`TNConvergenceParameters`, optional
            Convergence parameters for the new MPS. If None, the maximum bond
            bond dimension possible is assumed, and a cut_ratio=1e-9.
            Default to None.
        tensor_backend : `None` or instance of :class:`TensorBackend`
            Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.
        target_device: None | str, optional
            If `None`, take memory device of tensor backend.
            If string is `any`, do not convert. Otherwise,
            use string as device string.

        Returns
        -------
        obj : :py:class:`MPIMPS`
            The MPIMPS class
        """
        mismatches = [
            tensor_list[ii].shape[2] != tensor_list[ii + 1].shape[0]
            for ii in range(len(tensor_list) - 1)
        ]
        if any(mismatches):
            msg = f"Mismatches for tensors equals to True: {mismatches}."
            raise ValueError(f"Dimension mismatch when constructing MPS:{msg}")

        if conv_params is None:
            max_bond_dim = max(elem.shape[2] for elem in tensor_list)
            conv_params = TNConvergenceParameters(max_bond_dimension=int(max_bond_dim))
        if tensor_backend is None:
            # Have to resolve it here in case target device is not given
            tensor_backend = TensorBackend()
        if target_device is None:
            target_device = tensor_backend.memory_device
        elif target_device == "any":
            target_device = None

        local_dim = [elem.shape[1] for elem in tensor_list]
        obj = cls(
            len(tensor_list), conv_params, local_dim, tensor_backend=tensor_backend
        )

        # Convert data type (lateron device if GPU enabled?)
        for elem in tensor_list:
            elem.convert(obj.tensor_backend.dtype, target_device)

        if obj.rank == 0:
            tensorlist = [
                tensor_list[
                    obj.indexes[rank] : obj.indexes[rank + 1]
                    + int(rank != obj.size - 1)
                ]
                for rank in range(obj.size)
            ]
        else:
            list_sizes = obj.indexes[1:] - obj.indexes[:-1] + 1
            list_sizes[-1] -= 1
            tensorlist = [
                [None for _ in range(list_sizes[rank])] for rank in range(obj.size)
            ]

        tensor_list = obj.mpi_scatter_tn(tensorlist)
        obj._tensors = tensor_list

        return obj

    @classmethod
    def from_statevector(
        cls,
        statevector,
        local_dim=2,
        conv_params=None,
        tensor_backend=None,
    ):
        """Serially decompose the statevector and then initialize the MPS"""
        mps = MPS.from_statevector(
            statevector, local_dim, conv_params, tensor_backend=tensor_backend
        )

        return cls.from_tensor_list(
            mps.to_tensor_list(), conv_params, tensor_backend=tensor_backend
        )

    # ---------------------------
    # ----- MEASURE METHODS -----
    # ---------------------------

    def meas_local(self, op_list):
        """
        Measure a local observable along all sites of the MPS

        Parameters
        ----------
        op_list : list of :class:`_AbstractQteaTensor`
            local operator to measure on each site

        Return
        ------
        measures : ndarray, shape (num_sites)
            Measures of the local operator along each site on rank-0
        """
        res = super().meas_local(op_list)

        # Call back on the site 0 the results
        if self.rank != 0:
            self.comm.Send([res, self.mpi_dtype[res.dtype.str]], 0)
            tot_res = None
        else:
            tot_res = np.empty(self.tot_sites, dtype=res.dtype)
            tot_res[: self.num_sites - 1] = res[:-1]

            tidx = self.num_sites - 1
            for ii in range(1, self.size):
                num_tensors = self.indexes[ii] - self.indexes[ii - 1]
                self.comm.Recv(
                    [tot_res[tidx : tidx + num_tensors], self.mpi_dtype[res.dtype.str]],
                    ii,
                )
                tidx += num_tensors

        return tot_res

    def _get_eff_op_on_pos(self, pos):
        """
        Obtain the list of effective operators adjacent
        to the position pos and the index where they should
        be contracted

        Parameters
        ----------
        pos : int
            Index of the tensor w.r.t. which we have to retrieve
            the effective operators

        Returns
        -------
        list of IndexedOperators
            List of effective operators
        list of ints
            Indexes where the operators should be contracted
        """
        raise NotImplementedError("This function has to be overwritten")
