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
The module contains a light-weight aTTN class.
"""
import logging
from copy import deepcopy
from itertools import chain

import numpy as np

from qtealeaves.emulator.state_simulator import StateVector
from qtealeaves.mpos.disentangler import DELayer
from qtealeaves.tensors.abstracttensor import _AbstractQteaTensor
from qtealeaves.tooling import QTeaLeavesError

from .ttn_simulator import TTN

# pylint: disable=protected-access
# pylint: disable=too-many-arguments
# pylint: disable=too-many-lines

__all__ = ["ATTN"]

logger = logging.getLogger(__name__)


# pylint: disable-next=too-many-public-methods
class ATTN(TTN):
    """
    Augmented tree tensor network class = TTN + disentangler gates.

    Parameters
    ----------

    num_sites : int
        Number of sites

    convergence_parameters: :py:class:`TNConvergenceParameters`
        Class for handling convergence parameters. In particular,
        in the aTTN simulator we are interested in:
        - the *maximum bond dimension* :math:`\\chi`;
        - the *cut ratio* :math:`\\epsilon` after which the singular
            values are neglected, i.e. if :math:`\\lamda_1` is the
            bigger singular values then after an SVD we neglect all the
            singular values such that
            :math:`\\frac{\\lambda_i}{\\lambda_1}\\leq\\epsilon`

    local_dim: int, optional
        Local Hilbert space dimension. Default to 2.

    requires_singvals : boolean, optional
        Allows to enforce SVD to have singular values on each link available
        which might be useful for measurements, e.g., bond entropy (the
        alternative is traversing the whole TN again to get the bond entropy
        on each link with an SVD).

    tensor_backend : `None` or instance of :class:`TensorBackend`, optional
        Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.

    initialize : string, optional
        Define the initialization method. For random entries use
        'random', for empty aTTN use 'empty'.
        Default to 'random'.

    sectors : dict, optional
        [Not Implemented for aTTN] For restricting symmetry sector and/or bond dimension
        in initialization. If empty, no restriction.
        Default to empty dictionary.

    de_sites : 2d np.array, optional
        Array with disentangler positions with n rows and 2
        columns, where n is the number of disentanglers. Counting starts from 0
        and indices are passed as in the mapped 1d system.
        If set to 'auto', the disentangler positions are automatically selected
        to fit as much disentanglers as possible.
        Default to 'random'.

    de_initialize : string, optional
        Define the initialization method. For identities use 'identity',
        for random entries use 'random'.
        Default to 'identity'.

    check_unitarity : Boolean, optional
        If True, all the disentangler tensors are checked for unitarity and
        an error is raised if the check fails.
        Default to True.


    Details
    -------
    Notation: the last layer in TTN contains the local Hilbert spaces and the
    most tensors.
    The order of legs in TTN is:
        |2
       (X)
      0| |1
    The order of legs in disentanglers is: 0,1 are attached to <psi|, and 2,3 are
    attached to |psi>, so that it matches the notation DE|psi>.
    """

    extension = "attn"
    has_de = True

    # pylint: disable-next=too-many-arguments
    def __init__(
        self,
        num_sites,
        convergence_parameters,
        local_dim=2,
        requires_singvals=False,
        tensor_backend=None,
        initialize="random",
        sectors=None,
        de_sites=None,
        de_initialize="identity",
        check_unitarity=True,
    ):

        if sectors is None:
            sectors = {}

        # Pre-process local_dim to be a vector
        if np.isscalar(local_dim):
            local_dim = [
                local_dim,
            ] * num_sites

        self.eff_op_no_disentanglers = None

        if de_sites is None:
            raise ValueError("de_sites have to be passed as they are model-dependent.")

        self.de_sites = np.array(de_sites)
        if len(de_sites) > 0:
            if self.de_sites.shape[1] != 2:
                raise ValueError(
                    f"Disentanglers must have 2 sites. {self.de_sites.shape[1]}"
                    "-site disentanglers not supported."
                )
            if np.max(self.de_sites) >= num_sites:
                raise ValueError(
                    f"Cannot place disentangler on site {np.max(self.de_sites)}"
                    f" in system of {num_sites} sites."
                )
        self.de_layer = DELayer(
            num_sites,
            de_sites,
            convergence_parameters,
            local_dim=local_dim,
            tensor_backend=tensor_backend,
            initialize=de_initialize,
            check_unitarity=check_unitarity,
        )

        super().__init__(
            num_sites,
            convergence_parameters,
            local_dim=local_dim,
            requires_singvals=requires_singvals,
            tensor_backend=tensor_backend,
            initialize=initialize,
            sectors=sectors,
        )

        # convert to the appropriate device because the aTTN initialization is
        # not aware of it
        self.convert(self._tensor_backend.dtype, self._tensor_backend.device)

    # --------------------------------------------------------------------------
    #                       classmethod, classmethod like
    # --------------------------------------------------------------------------

    @classmethod
    # pylint: disable-next=arguments-differ
    # pylint: disable-next=too-many-arguments
    def from_statevector(
        cls,
        statevector,
        local_dim=2,
        conv_params=None,
        tensor_backend=None,
        check_unitarity=True,
    ):
        """
        Initialize an aTTN by decomposing a statevector into TTN form with 0
        disentanglers.

        Parameters
        ----------

        statevector : ndarray of shape( [local_dim]*num_sites, )
            Statevector describing the interested state for initializing the TTN

        device : str, optional
            Device where the computation is done. Either "cpu" or "gpu".

        tensor_cls : type for representing tensors.
            Default to :class:`QteaTensor`
        """

        obj_ttn = TTN.from_statevector(
            statevector, local_dim, conv_params, tensor_backend
        )
        obj = ATTN.from_ttn(obj_ttn, de_sites=[], check_unitarity=check_unitarity)

        return obj

    @classmethod
    def from_density_matrix(
        cls, rho, n_sites, dim, conv_params, tensor_backend=None, prob=False
    ):
        """Create an aTTN from a density matrix, which is not implemented yet."""
        raise NotImplementedError("Feature not yet implemented.")

    @classmethod
    def from_lptn(cls, lptn, conv_params=None, **kwargs):
        """Create an aTTN from LPTN, which is not implemented yet."""
        raise NotImplementedError("Feature not yet implemented.")

    @classmethod
    def from_mps(cls, mps, conv_params=None, **kwargs):
        """Create an aTTN from MPS, which is not implemented yet."""
        raise NotImplementedError("Feature not yet implemented.")

    @classmethod
    def from_ttn(
        cls,
        ttn,
        conv_params=None,
        de_sites=None,
        de_initialize="identity",
        check_unitarity=True,
        **kwargs,
    ):
        """
        Create aTTN from an existing TTN.

        Parameters
        ----------
        ttn : :py:class:`TTN`
            TTN part of the new aTTN
        de_sites : list or np.array
            Positions of disentanglers.
        de_initialize : str
            Method of disentangler initialization.
        kwargs : additional keyword arguments
            They are accepted, but not passed to calls in this function.
        """
        if de_sites is None:
            de_sites = []
            logger.warning("Creating ATTN without disentanglers.")
        args = deepcopy(ttn.__dict__)
        if conv_params is None:
            conv_params = args["_convergence_parameters"]
        new_attn = cls(
            num_sites=args["_num_sites"],
            convergence_parameters=conv_params,
            tensor_backend=ttn.tensor_backend,
            de_sites=de_sites,
            de_initialize=de_initialize,
            check_unitarity=check_unitarity,
        )
        for key in args:
            new_attn.__dict__[key] = args[key]

        return new_attn

    @classmethod
    def from_tto(cls, tto, conv_params=None, **kwargs):
        """Create an aTTN from , which is not implemented yet."""
        raise NotImplementedError("Feature not yet implemented.")

    def from_attn(self, include_disentanglers=True):
        """
        NOTE: For now works only for `include_disentanglers` = `False`.

        Create TTN from aTTN.

        Parameters
        ----------
        include_disentanglers : Boolean, optional
            If True, TTN will be constructed by contracting the disentanglers
            to the TTN part of aTTN. If False, only the TTN part of the aTTN
            is returned, regardless of the disentanglers.
            Default to True.
        truncation : Boolean
            Whether to truncate throughout the process of applying the
            disentangler.

        Return
        ------
        new_ttn : :py:class:`TTN`
            Resulting TTN.
        """
        # contracting the disentangler will increase the max bond dim by a factor of 4
        # new_max_bond_dim = 4 * self.convergence_parameters.max_bond_dimension
        # ttn_conv_params = TNConvergenceParameters(max_bond_dimension=new_max_bond_dim)
        # initialize the TTN from the aTTN's atributes
        args = deepcopy(self.__dict__)
        new_ttn = TTN(
            num_sites=args["_num_sites"],
            convergence_parameters=self.convergence_parameters.max_bond_dimension,
        )
        for key in args:
            if key in ["de_sites", "de_layer", "de_initialize", "check_unitarity"]:
                continue
            new_ttn.__dict__[key] = args[key]

        # contract the disentanglers if needed
        if include_disentanglers:
            raise NotImplementedError(
                "Contracting the disentanglers into TTN not yet implemented."
            )
            # for ii, disentangler in enumerate(self.de_layer):
            #     new_ttn.apply_two_site_operator(disentangler, self.de_layer.de_sites[ii])
            # new_ttn._requires_singvals = True
            # new_ttn.iso_towards([0, 0])

        return new_ttn

    # --------------------------------------------------------------------------
    #                               other methods
    # --------------------------------------------------------------------------

    def to_statevector(self, qiskit_order=False, max_qubit_equivalent=20):
        """
        Decompose a given aTTN into statevector form.

        Parameters
        ----------
        qiskit_order : bool, optional
            If true, the order is right-to-left. Otherwise left-to-right
            (which is the usual order in physics). Default to False.
        max_qubit_equivalent : int, optional
            Maximum number of qubits for which the statevector is computed.
            i.e. for a maximum hilbert space of 2**max_qubit_equivalent.
            Default to 20.

        Returns
        -------

        psi : instance of :class:`_AbstractQteaTensor`
            The statevector of the system
        """
        # get the statevector out of TTN
        statevect = super().to_statevector(qiskit_order, max_qubit_equivalent)
        statevect = StateVector(self.num_sites, self.local_dim, statevect)

        # apply the disentanglers to statevector as gates
        for ii, disentangler in enumerate(self.de_layer):
            statevect.apply_two_site_operator(disentangler, self.de_layer.de_sites[ii])

        return statevect.state

    ######### DISENTANGLER METHODS ###############################################################

    def apply_des_to_hamiltonian(self, params):
        """
        Contracts the disentanglers to the hamiltonian.
        Updates the eff_op of self in place.
        **Parameters**
        ----------
        params : dict
            Needed for the creation of the DenseMpo representation
            of the disentangler in contract_de_layer().
        **Returns**
        ----------
        None (eff_op updated in place)
        """

        # get a list of identity operators for each site
        # (for the case of symmetries, this can depend on the site)
        list_of_identities = [
            self._tensor_backend.eye_like(link) for link in self.local_links
        ]

        # contract the disentanglers with the eff_ops
        # pylint: disable=access-member-before-definition
        new_eff_op = self.de_layer.contract_de_layer(
            itpo=self.eff_op, tensor_backend=self._tensor_backend, params=params
        )

        # Local terms are not local anymore when contracted with disentanglers.
        # Here we fill sites without local with 0 * identity
        for ii, term_ii in enumerate(new_eff_op.site_terms):
            if term_ii._local is None:
                # now append identity with weight zero
                term_ii._local = 0.0 * list_of_identities[ii]
                term_ii._local_prefactors = [0.0]

        # update the eff_op
        # pylint: disable=attribute-defined-outside-init
        self.eff_op = None
        self.iso_towards(self.default_iso_pos)
        new_eff_op.setup_as_eff_ops(self)

        return

    def optimize_disentanglers(self):
        """
        Finds the optimal set of disentanglers for a given aTTN
        and Hamiltonian model.
        Used in the aTTN groundstate search.

        **Returns**
        ----------
        None (the aTTN is updated in-place)
        """
        # Many contractions here assume binary trees.
        # Should be reworked for non-binaries.
        self.assert_binary_tree()

        # pylint: disable-next=fixme
        # TODO Disentanglers are independent (if positioned correctly).
        # This loop could be trivially parallellized.
        for ii, de_site in enumerate(self.de_sites):
            self.optimize_de_site(de_site=de_site, de_index=ii)
        return

    # pylint: disable=too-many-branches, too-many-locals
    def optimize_de_site(self, de_site, de_index):
        """
        Optimize the disentangler on a given site.
        See the aTTN cookbook for details.
        For optimizing a given disentangler, we contract its environment
        (the full <psi|H|psi> network excluding the disentangler),
        and then set the disentagler to one which minimizes the energy.

        **Parameters**
        ----------
        de_site : 2d np.array
            Position of the disentangler to be optimized.

        de_index : int
            The index of the disentangler in the list of disentanglers.
            Its tensor is then as self.de_layer[de_index].

        **Returns**
        ----------
        None (the aTTN disentangler is updated in-place)

        """
        # The procedure is:
        #    - obtain the environment (env), which is the full network
        #      excluding the disentangler, the conjugated disentangler
        #      and the two terms of the Hamiltonian that couple to it.
        #    - optimize the disentangler (this is repeated multiple times):
        #        - contract the conjugated disentangler to env
        #        - contract the two hamiltonian terms to env
        #        - the result is now the complete environment of
        #          the disentangler, on which we perform a svd
        #        - set the disentagler to -U*V (this comes from the MERA paper),
        #          the energy is given by the sum of singular values.
        #        - repeat until the energy is converged

        # For the disentangler optimization, we care only about the
        # hamiltonian terms that act on the two disentangler sites.
        # Get the TPO-IDs of these operators here.
        # All contractions will be filtered to only include these terms.

        # get the indices and links to the disentangler site
        ndx_l, link_l, ndx_r, link_r = self.get_indices_from_de_position(de_site)
        last_layer = self.num_layers - 1

        # get the two MPOs coupled to the DE site (they are also used below)
        mpo_left = self.eff_op[
            (last_layer + 1, 2 * ndx_l + link_l), (last_layer, ndx_l)
        ]
        mpo_right = self.eff_op[
            (last_layer + 1, 2 * ndx_r + link_r), (last_layer, ndx_r)
        ]

        # save all unique TPO-IDs into a list
        relevant_tpo_ids = []
        for mpo in (mpo_left, mpo_right):
            for tpo_id in mpo.iter_tpo_ids():
                if tpo_id not in relevant_tpo_ids:
                    relevant_tpo_ids.append(tpo_id)

        # get the left and right environment
        # The left and right are separate due to historical reasons
        # originating in the Fortran code.
        # There might be space for optimization in picking point that separates them.
        env_l, env_r = self.get_environment(de_site, relevant_tpo_ids)

        # contract the environments along the non-disentangler indices

        # first extract the local operators to use them as identities
        local_l = env_l._local
        local_r = env_r._local
        env_l._local = None
        env_r._local = None

        # contract locals separately
        local_lr = local_l.tensordot(other=local_r, contr_idx=[[0, 1], [0, 1]])

        env = env_l.matrix_multiply(
            other=env_r,
            cidx_self=[1, 2],
            cidx_other=[1, 2],
            eye_a=local_l,
            eye_b=local_r,
        )

        # resulting leg order:
        # 0, 5 - horizontal indices
        # 1 - conj left disentangler site
        # 2 - left disentangler site
        # 3 - conj right disentangler site
        # 4 - right disentangler site

        if self.convergence_parameters.de_opt_strategy == "mera":
            self.optimize_disentangler_standard(
                de_index, env, local_lr, mpo_left, mpo_right
            )
        elif self.convergence_parameters.de_opt_strategy == "backpropagation":
            self.optimize_disentangler_backpropagation(
                de_index, env, local_lr, mpo_left, mpo_right
            )
        else:
            raise ValueError(
                "Unknown de_opt_strategy "
                + f"{self.convergence_parameters.de_opt_strategy}. "
                + "Should be 'mera' or 'backpropagation'."
            )
        return

    def optimize_disentangler_standard(
        self, de_index, env, local_lr, mpo_left, mpo_right
    ):
        """
        Optimize the disentangler using the standard MERA-inspired procedure.
        While the energy depends on both D and D*, here we linearize the optimization and
        optimize self-consistently.
        In each iteration assume constant D*, optimize D, and feed the result back.
        Repeat until num_iterations, or convergence of energy (it is given by the sum of the
        singular values of the SVD).

        **Parameters**
        ----------
        de_index : int
            The index of the disentangler we optimize.
        env : `QTeaTensor`
            The environment, not inlucding the two disentanglers and the MPOs.
        local_lr : `QTeaTensor`
            The local term of the environment. Passed here separately for historical
            Fortran-related reasons.
        mpo_left: `ITPO`
            The Hamiltonian term coupled to the left D site.
        mpo_right: `ITPO`
            The Hamiltonian term coupled to the right D site.

        **Returns**
        ----------
        None (The disentangler is optimized in-place.)
        """

        for ii in range(self.convergence_parameters.de_opt_max_iter):
            disentangler = self.de_layer[de_index]
            eff_env = self.contract_env_de_mpo(
                disentangler, env, local_lr, mpo_left, mpo_right
            )

            # compute the SVD on the effective enviromnent
            u_mat, v_conj, singvals, _ = eff_env.split_svd(
                legs_left=[2, 3],
                legs_right=[0, 1],
                no_truncation=True,  # We do not want to truncate.
                conv_params=None,
            )

            u_conj = u_mat.conj()
            v_mat = v_conj.conj()

            res = -1.0 * v_mat.tensordot(other=u_conj, contr_idx=[[0], [2]])
            self.de_layer[de_index] = res
            ##################################################################

            # sum up the energy and check convergence

            # For symmetric tensors, the energy is a list of energies for each sector.
            # Singvals is an instance of AbelianSymLinkWeight.
            tsum = res.get_attr("sum")
            if eff_env.has_symmetry:
                # use the sum attribute obtained from the appropriate tensor class
                new_energy = [-1 * float(tsum(xx)) for xx in singvals.link_weights]
            else:
                new_energy = -1 * float(tsum(singvals))

            # Check for relative convergence
            if ii > 0:
                if self.check_disentangler_convergence(energy, new_energy):
                    break
            else:
                energy = new_energy

        return

    def optimize_disentangler_backpropagation(
        self, de_index, env, local_lr, mpo_left, mpo_right
    ):
        """ "
        Optimize the disentangler using the backpropagation ML procedure.
        The energy depends on both D and D*. D (and thus D*) are passed
        to the optimization function complete_energy_contraction() which
        is optimized with the SGD optimizer from torch. Available for torch
        backend only.

        **Parameters**
        ----------
        de_index : int
            The index of the disentangler we optimize.
        env : `QTeaTensor`
            The environment, not including the two disentanglers and the MPOs.
        local_lr : `QTeaTensor`
            The local term of the environment. Passed here separately for historical Fortran-related
            reasons.
        mpo_left: `ITPO`
            The Hamiltonian term coupled to the left D site.
        mpo_right: `ITPO`
            The Hamiltonian term coupled to the right D site.

        ** Returns ***
        ----------
            None (Disentangler optimized in-place.)
        """
        logger.warning(
            "Using backpropagation for disentangler optimization. This is an"
            " experimental feature."
        )

        # Idea: in order to enforce unitarity of the disentanglers through the optimization, we
        # do not actually optimize the disentangler itself, but the h_matrix, where
        # disentangler = exp(i*h_matrix). This is generalized for symmetric tensors and complex
        # valued cases using the disentangler = h_matrix.unitary_like() calls.
        h_matrix = self.de_layer.h_matrices[de_index]

        # A small random correction seems to help with stability.
        # We could allow to adaptively turn this on/off.
        # optimal_de = optimal_de.matrix_function(first_column=2,
        # function_attr_str="add_random", prefactor=0.001)

        # The learning rate is set by the lr_setter function. If None, use the default strategy.
        lr_setter = self.convergence_parameters.de_opt_learning_rate_strategy
        if lr_setter is None:

            def lr_setter(ii):
                """
                The default strategy for changing the learning rate.
                ** Arguments **
                    ii : int, index of the iteration step.
                ** Returns **
                    lr : float, the learning rate.
                """
                warmup_steps = 20
                warmdown_steps = (
                    self.convergence_parameters.de_opt_max_iter - warmup_steps
                )
                min_lr_log = -8
                max_lr_log = -1
                dif = abs(min_lr_log - max_lr_log)

                # In the warmup exponentially increase the learning rate.
                if ii < warmup_steps:
                    lr = 10 ** (min_lr_log + dif * ((ii + 1) / warmup_steps))
                # Later, exponentially decrease the learning rate.
                else:
                    ii_no_warmup = ii - warmup_steps + 1
                    lr = 10 ** (max_lr_log - dif * (ii_no_warmup / warmdown_steps))
                return lr

        # turn on requires grad for all subtensors of optimal_de
        # This relies on the pyTorch grad functionality.
        all_subtensors = h_matrix.get_all_subtensors()
        for tt in all_subtensors:
            tt.requires_grad_(True)

        # Define the optimizer and gradient_clipper from torch.
        optimizer = h_matrix.get_optimizer(
            "SGD", all_subtensors, lr=1e-2, momentum=0.9, nesterov=True
        )
        # Another option is: optimizer = h_matrix.get_optimizer("AdamW", all_subtensors)
        gradient_clipper = h_matrix.get_gradient_clipper()

        # Actually do the iteration.
        for ii in range(self.convergence_parameters.de_opt_max_iter):

            # propagate backwards
            optimizer.zero_grad()

            # Call the optimization function:
            energy = self.complete_energy_contraction(
                h_matrix, env, local_lr, mpo_left, mpo_right
            )

            energy.backward(retain_graph=False)

            # If the gradients are too large, clip their value.
            # This seems to help in the initial steps.
            gradient_clipper(
                all_subtensors, self.convergence_parameters.de_opt_grad_clipping_value
            )

            # iterate the optimizer forward
            optimizer.step()

            # adjust the learning rate
            lr = lr_setter(ii)
            for param_group in optimizer.param_groups:
                param_group["lr"] = lr

            # Extract the energy as a Python float
            if self.has_symmetry:
                # Everything is contracted. If there is more than one
                # degeneracy_tensor, something has gone wrong.
                if len(energy.degeneracy_tensors) > 1:
                    raise QTeaLeavesError(
                        "There should be just one symmetry sector,"
                        + f"but found {len(energy.degeneracy_tensors)}."
                    )
                energy = energy.degeneracy_tensors[0].elem.item()
            else:
                energy = energy.elem.item()

            # Check for relative convergence
            if ii > 0:
                # to be inspected: ii > 10 should be ii > warmup steps, but this depends on
                # the lr function.
                if ii > 10 and self.check_disentangler_convergence(old_energy, energy):
                    break
                energy_diff = old_energy - energy
                old_energy = energy
            else:
                old_energy = energy
                energy_diff = 0.0

            message = (
                f"Iter {ii}, E : {energy}, dE : {energy_diff}, "
                f"lr: {optimizer.param_groups[0]['lr']}"
            )
            logger.warning(message)

        # turn of the requires_grad() and detach
        for tens in h_matrix.get_all_subtensors():
            tens.requires_grad_(False)
            tens = tens.detach().clone()

        # Check that it is unitary one last time.
        optimal_de = h_matrix.unitary_like(2)
        optimal_de.assert_unitary([2, 3])

        # Set the new h_matrix and the new de_layer.
        self.de_layer[de_index] = optimal_de
        self.de_layer.h_matrices[de_index] = h_matrix

        return

    def check_disentangler_convergence(self, old_energy, new_energy):
        """
        Checks if the disentanglers are converged.
        old_energy and new_energy are lists for symmetric tensors.
        In that case, check that all of them are converged.

        **Parameters**
        ----------
            old_energy : float | list[QTeaTensor]
                Energy in the previous iteration.
            new_energy : float | list[QTeaTensor]
                Energy in the current iteration.
        **Returns**
        ----------
            bool: whether we have reached convergence.
        """
        if isinstance(old_energy, list) and isinstance(new_energy, list):
            relative_convergence = all(
                abs((new_energy[kk] - old_energy[kk]) / new_energy[kk])
                < self.convergence_parameters.de_opt_rel_deviation
                for kk in range(len(new_energy))
            )
        else:
            relative_convergence = (
                abs((new_energy - old_energy) / new_energy)
                < self.convergence_parameters.de_opt_rel_deviation
            )

        return relative_convergence

    def contract_env_de_mpo(self, disentangler, env, local_lr, mpo_left, mpo_right):
        """
        Contracts the conjugate disentangler, the environment and the mpos.
        Used both in optimize_disentangler_standard() and optimize_disentangler_backpropagation().

        **Parameters**
        ----------
            disentangler : QTeaTensor
                The disentangler.
            env : QTeaTensor
                The environment.
            local_lr : QTeaTensor
                The local part of the environment.
            mpo_left : QTeaTensor
                The mpo acting on the left disentangler site.
            mpo_right : QTeaTensor
                The mpo acting on the right disentangler site.
        **Returns**
        ----------
            eff_env : QTeaTensor
            The effective environment.
        """
        # contract the conjugated disentangler along the legs going into the tree!
        de_conj = disentangler.conj()

        env_de = env.tensordot_with_tensor_left(
            tensor=de_conj, cidx_self=[1, 3], cidx_tensor=[2, 3]
        )
        # env is now a circle, with 4 vertical legs:
        # 1 - conj leg pointing up to the left MPO of H
        # 2 - conj leg pointing up to the right MPO of H
        # 3 - leg pointing down to the left DE site
        # 4 - leg pointing down to the right DE site

        # contract the conjugated disentangler to the local term
        local_lr_dec = de_conj.tensordot(other=local_lr, contr_idx=[[2, 3], [0, 2]])

        ##################################################################
        # contract the two MPOs coupled to the DE site

        # left MPO into env
        # permutation is required here to set the leg order in local_left
        env_de = env_de.matrix_multiply(
            other=mpo_left,
            cidx_self=[1],
            cidx_other=[1],
            eye_a=local_lr_dec,
            perm_local_out=[3, 0, 1, 2],
        )

        # Leg order BEFORE THE PERMUTATION
        # 0, 5 - horizontal links
        # 1 - conj link up to the right MPO
        # 2 - link down to the left DE site
        # 3 - link down to the right DE site
        # 4 - conj link up from the mpo_left up to DE site

        # After the permutation the order corresponds to
        # the disentangler leg order:
        # 0, 5 - horizontal links
        # 1, 2 - conj left and right DE sites (pointing up)
        # 3, 4 - left and right DE sites (pointing down)

        # extract the local result and save it
        local_after_left_exists = env_de._local is not None
        if local_after_left_exists:
            local_left = env_de._local
            env_de._local = None

        # right MPO into env
        env_de = env_de.matrix_multiply(
            other=mpo_right,
            cidx_self=[2],
            cidx_other=[1],
            eye_a=local_lr_dec,
            perm_local_out=[0, 3, 1, 2],
        )
        # BEFORE PERMUTATION, the legs are:
        # 0, 3 - left and right DE sites (pointing up)
        # 1, 2 - conj left and right DE sites (pointing down)

        # After the permutation, the legs match the disentangler leg order:
        # 0, 1 - conj left and right DE sites (pointing up)
        # 2, 3 - left and right DE sites (pointing down)

        ##################################################################
        # At this point everything should contract into a local term and no
        # horizontal legs should remain.
        if len(env_de._operators) > 0:
            raise QTeaLeavesError(
                """env_de does not contract to local.
                            Probably bad disentangler positions."""
            )

        # get the local tensor and add the local of the left
        eff_env = env_de._local
        if local_after_left_exists:
            eff_env.add_update(local_left)

        return eff_env

    def complete_energy_contraction(self, h_matrix, env, local_lr, mpo_left, mpo_right):
        """
        Perform the complete contraction: the environment, the disentangler,
        the mpos and the conjugated disentangler.

        **Parameters**
        ----------
            h_matrix : QTeaTensor
                A representation of the disentangler.
            env : QTeaTensor
                The environment.
            local_lr : QTeaTensor
                The local part of the environment.
            mpo_left : QTeaTensor
                The mpo acting on the left disentangler site.
            mpo_right : QTeaTensor
                The mpo acting on the right disentangler site.
        **Returns**
        ----------
            energy : float
        """

        disentangler = h_matrix.unitary_like(first_column=2)
        disentangler.assert_unitary([0, 1])

        # Get the effective environment. The legs match the disentangler leg order.
        eff_env = self.contract_env_de_mpo(
            disentangler, env, local_lr, mpo_left, mpo_right
        )

        # Contract the disentangler to the effective environment.
        energy = disentangler.tensordot(
            other=eff_env, contr_idx=[[0, 1, 2, 3], [0, 1, 2, 3]]
        )

        return energy

    # pylint: disable:=too-many-locals
    def get_environment(self, de_site, relevant_tpo_ids):
        """
        Gets the left and right environment for the DE optimization
        by partially contracting the network of <psi|H|psi>.

        First, we pick an 'anchor', the tensor which separates
        the left and right environment.
        Then, we iteratively contract into env_left everything
        between the tensor attached to the first de_site and
        the anchor, and similarly into the right.

        **Parameters**
        ----------
        de_site : 2d np.array
            Position of the disentangler which is to be optimized.
            A list of two ints, corresponding to the position of
            the two tensors in the lowest layer of the ttn that
            are attached to it.

        relevant_tpo_ids : list[ int ]
            List of TPO-IDs we care about, because they are present
            at the disentangler sites.
            All contraction are filtered to only include these IDs.

        **Returns**
        ------
        env_l, env_r : iTPO
            Left and right environment
        """

        ndx1, link1, ndx2, link2 = self.get_indices_from_de_position(de_site)

        last_layer = self.num_layers - 1
        pos_1 = [last_layer, ndx1]
        pos_2 = [last_layer, ndx2]

        if ndx1 == ndx2:
            raise ValueError("Disentangler attached to the same tensor.")

        # The path logic:
        # Pass the whole path to both left and right env contractions.
        # Pick the anchor as the tensor on the path with the smallest layer.
        # For env_l specify to include the anchor,
        # so stop the loop after the anchor is contracted
        # for env_r specify NOT to include the anchor,
        # and stop the loop before the anchor is contracted
        # Also, the path for env_r has to be reversed.

        # Get the path between the DE positions for the left and right contractions
        full_path_left = self.get_path(target=pos_2, start=pos_1)
        full_path_right = self.get_path(target=pos_1, start=pos_2)

        # for now pick as the anchor the tensor on the path with the lowest
        # layer (read from x[0])
        anchor_point = min(full_path_left, key=lambda x: x[0])
        anchor = tuple(anchor_point[:2])
        # Isometrising towards the anchor enables
        # the separation of the network into two environments.
        self.iso_towards(anchor)

        # Caution: these paths are in different format than the get_path()!
        path_left = self.get_iterative_contraction_path(
            full_path_left, anchor, include_anchor=True
        )
        path_right = self.get_iterative_contraction_path(
            full_path_right, anchor, include_anchor=False
        )

        # pylint: disable-next=fixme
        # TODO: ANCHOR SELECTION (Luka May 2024) the anchor does not have to be the top tensor -
        # this means that the cut between the environments will have the largest bond dimension.
        # It could be reduced if the cut is at some lower layer.
        # WARNING:
        # playing with the anchor position might introduce problems with 4-legged MPO tensors.
        # Or put differently: a given position of disentanglers might only work for a certain
        # anchor selection.
        # You could iteratively try all possible anchors along the path with try - except.

        # From Timo Felser's thesis, page 129 (p. 141 of the pdf):
        # We hereby define the anchor of a causal cone as the topmost tensor (with respect to
        # the hierarchical TTN structure), which is still included in the causal cone.
        # Thus, isometrising the internal TTN towards the anchor node of the causal cone for
        # uk and Hp results in all tensors outside of the causal cone vanishing to
        # identities due to their enforced isometry.
        # Consequently, the complete contraction of the network can be
        # reduced to the tensors within the causal cone only.

        # But this holds for any tensor on the path, so there is freedom in picking the anchor.

        # first is the initial environment contraction
        # see the comments in the function for index order
        env_left = self.start_environment_contraction_for_de_optimization(
            index=ndx1, de_link=link1, relevant_tpo_ids=relevant_tpo_ids
        )

        # now iteratively contract
        # env_left has the same index order as it started with.
        env_left = self.iteratively_contract_along_path(
            env=env_left, path=path_left, relevant_tpo_ids=relevant_tpo_ids
        )

        # now the right environement
        env_right = self.start_environment_contraction_for_de_optimization(
            index=ndx2, de_link=link2, relevant_tpo_ids=relevant_tpo_ids
        )

        # contracted along the reverse of the path downwards
        env_right = self.iteratively_contract_along_path(
            env=env_right, path=path_right, relevant_tpo_ids=relevant_tpo_ids
        )

        return env_left, env_right

    # pylint: disable:=too-many-locals
    def get_iterative_contraction_path(self, path, anchor, include_anchor):
        """
        Collects the information required for an iterative contraction along
        a path, which is slightly different than what get_path() provides.
        At each step of the contraction, you need:
            - this_position : the position of the tree tensor
            - incoming_link : the link where the path comes into the tree
                This is the link along which the tensor is contracted into env.
            - outgoing_link : the link where the path continues
                This link becomes the outgoing link of the new env.

            - offpath_link  : the link pointing away from the path
                This is where the eff_op of the rest of the network is contracted.
            - offpath_position : the position of the tree tensor away from the path
                This is required for the identification of the effective operator.

        The path for contraction ends at the anchor (including it or not), which is set
        by the anchor and include_anchor arguments.

        **Parameters**
        ----------
        path : list[ list[] ]
            The path as it comes from the get_path() method.
        anchor : tuple[ int ]
            Position of the anchor as (layer, index).
        include_anchor : bool
            Whether to include the anchor as the last element or not.

        **Returns**
        ----------
            result : list[ tuple[ int | tuple[int] ] ]
            The list of tuples of integers.
            this_position and offpath_position are tuples of (layer, index),
            the rest are integers.
        """

        # In particular, offpath_link calculation assumes a binary structure.
        # For a non-binary tree, there are multiple offpath_links and multiple
        # effective operators would have to be contracted.
        self.assert_binary_tree()

        result = []
        for count, (this_layer, this_index, this_link, _, _, _) in enumerate(path):
            # Skip the first step
            if count == 0:
                continue

            # the position of the tensor is easy
            this_position = (this_layer, this_index)

            # break when arriving to the anchor
            if not include_anchor and this_position == anchor:
                break

            # incoming link is next_link of the previous element
            incoming_link = path[count - 1][5]
            outgoing_link = this_link

            # offpath link is the third option from [0, 1, 2]
            offpath_link = 3 - (incoming_link + outgoing_link)

            if offpath_link not in (0, 1, 2):
                raise QTeaLeavesError(
                    f"offpath_link is not 0, 1, or 2, but: {offpath_link}."
                )

            # Find the position from where the eff_op is coming.
            # If offpath_link is not 2 but 0 or 1, this will always
            # be one layer lower. But if it is 2, it is going to be
            # one layer higher, OR equal if we are at the top, where
            # link 2 goes sideways!
            if offpath_link == 2:
                if this_layer == 0:
                    # there are only two tensors in this layer (binary tree)
                    offpath_layer = this_layer
                    offpath_ndx = 0 if this_index == 1 else 1
                else:
                    offpath_layer = this_layer - 1
                    offpath_ndx = this_index // 2
            elif offpath_link in [0, 1]:
                offpath_layer = this_layer + 1
                offpath_ndx = (2 * this_index) + offpath_link
            else:
                raise QTeaLeavesError(
                    f"offpath_link is not in (0, 1, 2), but is {offpath_link}."
                )
            offpath_position = (offpath_layer, offpath_ndx)

            result.append(
                [
                    this_position,
                    offpath_position,
                    incoming_link,
                    outgoing_link,
                    offpath_link,
                ]
            )

            # break after arriving to the anchor
            if include_anchor and this_position == anchor:
                break

        return result

    # pylint: disable:=too-many-locals
    def iteratively_contract_along_path(self, env, path, relevant_tpo_ids):
        """
        Given the initial object env, iteratively contracts the tree network
        along the specified path.
        In each step takes contracts a tree tensor on the path with its effective
        operator on the link not on the path, and contracts this object into env.
        Then contracts the conjugate of the tree tensor into env.
        The resulting object has the same leg ordering as the input env.

        **Parameters**
        ----------
        env : ITPO
            The initial point of the iteration.
            Contracted first TTN tensor, MPO, and conj(tensor).

        path : list[ list[] ]
            Path along which to perform the iterative contraction.

        relevant_tpo_ids : list[ int ]
            List of TPO-IDs we care about, because they are present
            at the disentangler sites.
            All contraction are filtered to only include these IDs.

        **Returns**
        ----------
            env : ITPO
            The full object representing the environment of a disentangler
            contracted along the given path.
        """

        # iterate through the path, always considering the next tensor in the tree
        for (
            this_position,
            offpath_position,
            incoming_link,
            outgoing_link,
            offpath_link,
        ) in path:
            # get the tree tensor
            layer, index = this_position
            tree_tensor = self[layer][index]

            # get the eff_op
            this_eff_op = self.eff_op[(offpath_position, this_position)]
            # copy the eff op and remove its local, it does not matter for
            # disentangler optimization
            # this is the object we use
            tree_eff_op = this_eff_op.filter_tpo_ids(relevant_tpo_ids)
            tree_eff_op._local = None

            # for now do the optimization on the memory device
            tree_tensor.convert(self.dtype, self.tensor_backend.memory_device)
            this_eff_op.convert(self.dtype, self.tensor_backend.memory_device)

            # get the local tensor of env separately and remove
            # it from the env
            env_local = env._local
            env._local = None

            ####################
            # Now the contractions:

            # contract the tree tensor into the env

            # There is a nasty edge case:
            # Below we will contract the eff_op to the offpath_link
            # of the tree tensor. This is mostly 0 or 1, and thus
            # the ordering of links is as below.
            # HOWEVER, it might happen (eg. in the top layer) that
            # offpath_link == 2. Then it will become link 4, while
            # link 5 would be pointing down.
            # We have to take care of this here with the permutation.

            edgecase_perm = None  # just in case
            if this_position == (0, 0):
                # additionally the (0,0) tensor has four legs, so take care of this
                edgecase_perm = (
                    (0, 1, 2, 4, 3, 5) if offpath_link > outgoing_link else None
                )
            else:
                edgecase_perm = (
                    [0, 1, 2, 4, 3] if offpath_link > outgoing_link else None
                )

            env = env.tensordot_with_tensor(
                tensor=tree_tensor,
                cidx_self=[2],
                cidx_tensor=[incoming_link],
                perm_local_out=edgecase_perm,
            )

            # resulting indices:
            # 0, 6 - horizontal legs
            # 1 - down to the cojugate tree
            # 2 - up to the conjugate disentangler
            # 3 - down to the disentangler
            # 4 - from tree tensor to its effective op
            # 5 - from tree tensor up to the next layer

            # now use the env_local to define a temporary identity
            # local does not have the first and last link, so
            # contract with tensor along 1
            temp_id = env_local.tensordot(
                other=tree_tensor,
                contr_idx=[[1], [incoming_link]],
            )
            if edgecase_perm is not None:
                temp_id.transpose_update(permutation=edgecase_perm)

            # contract the effective operator into the env
            env = env.matrix_multiply(
                other=tree_eff_op,
                cidx_self=[4],
                cidx_other=[2],
                eye_a=temp_id,
            )
            # resulting indices:
            # 0, 6 - horizontal legs
            # 1 - down to the cojugate tree
            # 2 - up to the conjugate disentangler
            # 3 - down to the disentangler
            # 4 - from tree tensor up to next layer
            # 5 - from eff_op down (to be contracted with conjugate tree tensor)

            # remove local again, it does not matter for disentangler optimization
            env._local = None

            # contract the conjugate tree tensor
            conj_tensor = tree_tensor.conj()
            # The (0, 0) tensor is a special case, as it has the fourth leg!
            # It has to be contracted with the conjugate tensor leg.
            if this_position == (0, 0):
                contr_self = [1, 6, 5]
                contr_tens = [incoming_link, offpath_link, 3]
                perm_final = [3, 2, 0, 1]
            else:
                contr_self = [1, 5]
                contr_tens = [incoming_link, offpath_link]
                perm_final = [3, 2, 0, 1]

            env = env.tensordot_with_tensor(
                tensor=conj_tensor,
                cidx_self=contr_self,
                cidx_tensor=contr_tens,
                perm_local_out=perm_final,
            )
            # leg order BEFORE the permutation:
            # 0, 5 - horizontal legs
            # 1 - conj disentangler leg
            # 2 - disentangler leg down
            # 3 - up into the tree
            # 4 - down into the conj tree

            # the final result, AFTER the permutation:
            # 0, 5 - horizontal legs
            # 1 - down into the conj tree
            # 2 - up into the tree
            # 3 - conj disentangler leg
            # 4 - down to the disentangler

            # now provide a special local in env

            # CAREFUL: contraction indices are 0, 3, not the same as for the
            # env contraction. This is because eff_op is contracted into the env,
            # which permutes the indices of env.
            if this_position == (0, 0):
                contr_self = [0, 3, 5]
                contr_tens = [incoming_link, offpath_link, 3]
            else:
                contr_self = [0, 3]
                contr_tens = [incoming_link, offpath_link]

            tmp = temp_id.tensordot(conj_tensor, contr_idx=[contr_self, contr_tens])
            # now permute the legs of local to match the legs of env
            tmp.transpose_update(permutation=[3, 2, 0, 1])

            # and assign to local of env
            env._local = tmp

        return env

    def start_environment_contraction_for_de_optimization(
        self, index, de_link, relevant_tpo_ids
    ):
        """
        Implementation of the pre_contr_dopt_binary_tree() fortran routine.
        Does the first step of contracting the environment for the
        disentangler optimization: contracts the tensor where the disentangler is
        attached to the MPO operator on the OTHER leg, and then with the
        complex conjugate of the same tensor.
        An iterative contraction of the tree along the path can
        then be performed on this object.

        Order of legs documented at the end of the function.

        See the aTTN cookbook.
        Assumes a binary tree.

        **Parameters**
        ----------

        index   : int
            Index of the tensor coupled to the disentangler in the lowest layer.
            It will be contracted with the mpo on the leg without the disentangler.

        de_link : int
        The link of the tensor at index that attaches to the disentangler.

        relevant_tpo_ids : list[ int ]
            List of TPO-IDs we care about, because they are present
            at the disentangler sites.
            All contraction are filtered to only include these IDs.

        **Returns**
        -------

        result : iTPO
            The result of the contraction.
            With this object you can start the iterative contraction of the tree,
            which leads to obtaining the left/right_environment.
        """

        # in particular
        self.assert_binary_tree()

        layer = self.num_layers - 1

        # this is the tensor with one physical leg attached to the disentangler
        tensor = self[layer][index]

        # the mpo to contract is the eff_op on the leg which is NOT
        # coupled to the disentangler
        mpo_link = 0 if de_link == 1 else 1

        mpo = self.eff_op[((layer + 1, 2 * index + mpo_link), (layer, index))]
        mpo = mpo.filter_tpo_ids(filter_tpo_ids=relevant_tpo_ids)

        # contract the tensor to the mpo. The result is an iTPO
        # indices are 0-left, 1-down, 2-up, 3-right, so cidx_self=2
        result = mpo.tensordot_with_tensor_left(
            tensor=tensor, cidx_self=[2], cidx_tensor=[mpo_link]
        )
        # the result is a 5-legged tensor:
        # 0, 4 - horizontal MPO indices,
        # 1 - right physical index,
        # 2 - up index to next layer,
        # 3 - down MPO index

        # Now contract the conjugate tensor
        tensor_conj = tensor.conj()
        result = result.tensordot_with_tensor(
            tensor=tensor_conj,
            cidx_self=[3],
            cidx_tensor=[mpo_link],
            perm_local_out=[3, 1, 2, 0],
        )
        # the result without the permutation is a 6-legged tensor:
        # 0, 5 - horizontal MPO indices,
        # 1 - ttn physical index down to the disentangler site,
        # 2 - ttn index to next layer up,
        # 3 - conjugate of 1, ttn physical to the disentangler site
        # 4 - conjugate of 2, index to next layer down
        # HOWEVER, we want to have the disentangler legs (above 1, 3) as (3, 4) and
        # the legs pointing up and down to next layers as 1 and 2.

        # The final output now has legs:
        # 0, 5 - horizontal MPO indices,
        # 1 - conjugate of 2, ttn index to next layer down
        # 2 - ttn index to next layer up,
        # 3 - conjugate of 4, ttn physical up to the conj disentangler site
        # 4 - ttn physical index down to the disentangler site,

        # remove local

        # The logic of removing the local terms and contracting them separately
        # exists in the Fortran version of the code.
        # It is not completely clear to me why this is necesary, but the logic
        # is copied here, and in other related functions. (Luka, July 2024)
        result._local = None
        # set the contration of tree * tree.conj() as the new local
        new_local = tensor.tensordot(
            other=tensor_conj, contr_idx=[[mpo_link], [mpo_link]]
        )
        # do the same permutation as above.
        new_local.transpose_update(permutation=[3, 1, 2, 0])
        result._local = new_local

        return result

    def get_indices_from_de_position(self, de_position):
        """
        Given the position of a disentangler, returns
        the indices and links of the two tensors that
        couple to it.

        Parameters
        ----------

        de_position : list[int]
            position of the disentangler

        Returns
        -------

        ndx1, ndx2 : int
            indices of the two tensors that couple to the DE

        link1, link2 : int
            links at which the DE is attached
        """
        # The division by 2 assumes binary trees.
        self.assert_binary_tree()
        ndx1 = de_position[0] // 2  # these for the 'left' environment
        link1 = de_position[0] % 2
        ndx2 = de_position[1] // 2  # these for the 'right'
        link2 = de_position[1] % 2

        return ndx1, link1, ndx2, link2

    def convert(self, dtype, device):
        """Convert data type and device inplace."""
        super().convert(dtype, device)
        # handle converting eff ops without disentanglers
        if self.eff_op_no_disentanglers is not None:
            self.eff_op_no_disentanglers.convert(dtype, device)

    #########################################################################
    ############################# ABSTRACT METHODS ##########################
    #########################################################################

    def meas_local(self, op_list):
        """
        Measure a local observable along sites of the aTTN,
        excluding the sites with the disentangler (because there the
        measurement is not local anymore)

        Parameters
        ----------
        op_list : list of :class:`_AbstractQteaTensor`
            local operator to measure on each site

        Return
        ------
        measures : ndarray, shape (num_sites)
            Measures of the local operator along each site except
            sites with the disentanglers. At the disentangler sites
            `measures` is set to zero.
        """
        if isinstance(op_list, _AbstractQteaTensor):
            if len(set(self.local_dim)) != 1:
                raise QTeaLeavesError(
                    "Trying to use single operator for non-unique Hilbert spaces."
                )
            op_list = [op_list for _ in range(self.num_sites)]

        # Always store on host
        measures = np.zeros(self.num_sites)

        # This subroutine can be parallelized if the singvals are stored using
        # joblib
        for ii in range(self.num_sites):
            # skip disentangler sites
            if ii in self.de_layer.de_sites:
                measures[ii] = np.nan
            else:
                rho_i = self.get_rho_i(ii)
                op = op_list[ii]
                if op.ndim != 2:
                    op = op.copy()
                    op.trace_one_dim_pair([0, 3])

                expectation = rho_i.tensordot(op, ([0, 1], [1, 0]))
                measures[ii] = np.real(expectation.get_entry())

        return measures

    def get_rho_i(self, idx):
        """
        Get the reduced density matrix of the site at index idx.

        Parameters
        ----------
        idx : int
            Index of the site
        """
        # for sites without disentanglers, ingerit from TTN
        if idx not in self.de_layer.de_sites:
            return super().get_rho_i(idx)

        raise NotImplementedError(
            "get_rho_i not yet implemented for sites with disentanglers."
        )

    def set_cache_rho(self):
        """Cache the reduced density matrices for faster access."""
        for ii in range(self.num_sites):
            self.site_canonize(ii)
            if ii not in self.de_layer.de_sites:
                self._cache_rho[ii] = self.get_rho_i(ii)

    def _iter_de(self):
        """Iterate over all disentanglers (for convert etc)."""
        yield from self.de_layer

    def _iter_tensors(self):
        """Iterate over all tensors forming the tensor network (for convert etc)."""
        return chain(super()._iter_tensors(), self._iter_de())

    def _deprecated_get_eff_op_on_pos(self, pos):
        """
        Obtain the list of effective operators adjacent
        to the position pos and the index where they should
        be contracted

        Parameters
        ----------
        pos :
            key to the desired tensor

        Returns
        -------
        list of IndexedOperators
            List of effective operators
        list of ints
            Indexes where the operators should be contracted
        """
        raise NotImplementedError("Not implemented yet for aTTN.")

    def _get_children_magic(self, *args, **kwargs):
        raise NotImplementedError(" Function not implemented yet")

    def get_substate(self, first_site, last_site, truncate=True):
        """
        Returns the smaller TN built of tensors from the subtree. `first_site` and
        `last_site` (where sites refer to physical sites) define the subtree.
        """
        # If disentangler reaches out of substate, it has to be applied ...
        raise NotImplementedError("Substate not implemented for aTTN.")

    def kron(self, other, inplace=False, fill_identity=True, install_iso=False):
        """
        Concatenate two aTTN, taking the kronecker/outer product
        of the two states. The bond dimension assumed is the maximum
        between the two bond dimensions. For now, the restriction is
        that self and other must have the same number of layers.
        Idea for future implementation : allow other to be a TTN.

        Parameters
        ----------
        other : :py:class:`aTTN`
            aTTN to concatenate
        inplace : bool, optional
            If True apply the kronecker product in place. Instead, if
            inplace=False give as output the product. Default to False.
        fill_identity : Bool
            If True, uppermost layer tensors are simply set to identity tensors.
            Otherwise, constructs last layer by QR-ing the top tensors of self and other.
            Defatult to True
        install_iso : bool, optional
            If true, the isometry center will be installed in the resulting
            tensor network. The isometry centers of `self` and `other` might
            be shifted in order to do so. For `False`, the isometry center
            in the new TTO is not set.
            Default to `False`.

        Returns
        -------
        :py:class:`aTTN`
            Concatenation of the first aTTN with the second.
        """
        # Implementation possible, but many good disentangler positions
        # might be blocked for the new halves by the old disentanglers.
        raise NotImplementedError(
            "Not implemented yet for aTTN, but implementation is possible."
        )
