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
The organization of modeling a physical system in 1, 2, or 3 spatial dimensions.
"""

# pylint: disable-msg=too-many-locals, too-many-arguments, too-many-branches

import os

# pylint: disable-next=no-name-in-module
import os.path
from collections import OrderedDict

import numpy as np
import scipy.sparse as sp

from qtealeaves.tooling import QTeaLeavesError
from qtealeaves.tooling.parameterized import _ParameterizedClass

from .baseterm import _ModelTerm

__all__ = ["QuantumModel"]


class QuantumModel(_ParameterizedClass):
    """
    The class represents a physical model, e.g., how to build the
    Hamiltonian. Therefore, multiple instances of the class
    :class:`_ModelTerm` can be added.

    **Arguments**

    dim : int
        number of spatial dimensions, i.e., the information if we have
        a 1d, 2d, or 3d system.

    lvals : int, str, callable
        Information about the number of sites; at the moment regarding
        one spatial dimension. For example, it is the length of the side
        of the cube in 3d systems.

    name : str, callable
        (deprecated) Name tag for the model. Only use for v1 of the
        input processor when writing json files. It can be parameterized
        via a callable returning the filename or a string-key in
        the parameters dictionary.
        Default to ``Rydberg``

    input_file : str
        Name of the input file within the input folder.

    map_type : str, optional
        Selecting the mapping from a n-dimensional system to the
        1d system required for the TTN simulations.
        Default to ``HilbertCurveMap``
    """

    def __init__(
        self,
        dim,
        lvals,
        name="Rydberg",
        input_file="model.in",
        map_type="HilbertCurveMap",
    ):
        self.hterms = []
        self.coupl_params = OrderedDict()
        self.name = name
        self.dim = dim

        self.input_file = input_file

        # Will be set when adding Hamiltonian terms
        self.map_type = map_type

        if isinstance(lvals, str):
            self.lvals = lvals
        elif isinstance(lvals, (int)):
            self.lvals = [lvals] * self.dim
        else:
            if len(lvals) != self.dim:
                raise ValueError("Problems with dimensions.")
            self.lvals = list(lvals)

    def __iadd__(self, new_term):
        """
        Add additional terms to the model

        **Arguments**

        term : instance of :class:`_ModelTerm`
            Represents the additional term in the model.
        """
        self.add_hterm(new_term)
        return self

    def __iter__(self):
        """Iterate over the terms in the model."""
        yield from self.hterms

    def collect_operators(self):
        """
        The required operators must be provided through this
        method. It relies on the same method of each
        :class:`_ModelTerm`.
        """
        op_lst = []
        for elem in self.hterms:
            for op_tuple in elem.collect_operators():
                op_lst.append(op_tuple)

        return list(set(op_lst))

    def eval_lvals(self, params):
        """
        Evaluate the system size via a parameter dictionary and
        `eval_numeric_params`.

        **Arguments**

        params : dict
            The parameter dictionary for the simulation.
        """
        lvals = self.eval_numeric_param(self.lvals, params)

        if isinstance(lvals, int):
            lvals = [lvals] * self.dim
        elif len(lvals) != self.dim:
            raise ValueError("Problems with dimensions.")
        else:
            lvals = list(lvals)

        return lvals

    def get_number_of_sites_xyz(self, params):
        """
        Returns a scalar (integer), which is the dimensions in x-, y-,
        and z-direction. Equal dimensions along a dimensions are assumed
        and only the dimension in x-direction is returned.

        **Arguments**

        params : dict
            The parameter dictionary for the simulation.
        """
        nx = self.get_number_of_sites(params)
        return [nx]

    def get_number_of_sites(self, params):
        """
        Return the total number of sites in the system, i.e., the
        product along all dimensions.

        **Arguments**

        params : dict
            The parameter dictionary for the simulation.
        """
        return int(np.prod(np.array(self.eval_lvals(params))))

    def add_hterm(self, term):
        """
        Add a new term to the model.

        **Arguments**

        term : instance of :class:`_ModelTerm`
            Represents the additional term in the model.
        """
        if not isinstance(term, _ModelTerm):
            raise ValueError("Term in model must be _ModelTerm.")

        term.check_dim(self.dim)

        # Check that the mapping to the 1d system is consistent
        if hasattr(term, "map_type"):
            term.map_type = self.map_type

        self.hterms.append(term)

        for strength in term.get_strengths():
            # Give an index to string parameters
            if hasattr(strength, "__call__"):
                tmp_key = repr(strength)
            elif isinstance(strength, str):
                tmp_key = strength
            elif strength != 1.0:
                raise QTeaLeavesError("Use prefactor for this purpose.")
            else:
                return

            if tmp_key not in self.coupl_params:
                self.coupl_params[tmp_key] = [len(self.coupl_params) + 1, term]

    def build_ham(self, ops, params, qubit_limit=None):
        """
        Build Hamiltonian as a matrix, which only works for very small
        system sizes. Moreover, the underlying terms need to support
        building the Hamiltonian as a matrix.

        **Arguments**

        ops : instance of :class:`TNOperators`
            To build the Hamiltonian, we need the actual operators which
            are passed within this variable.

        params : dict
            The parameter dictionary for the simulation.

        qubit_limit : int, optional
            Prevent memory issues when `build_ham` accidentally used
            for many-body systems.
            Default to `None`, i.e., 16-qubit-equivalents for dense matrices.
        """
        if params.get("ed_sparse", False):
            return self.build_ham_sparse(ops, params, qubit_limit=qubit_limit)
        if qubit_limit is None:
            qubit_limit = 16

        lx_ly_lz = self.eval_lvals(params)
        nsites = int(np.prod(np.array(lx_ly_lz)))
        local_dims = ops.get_local_links(nsites, params)
        dim = int(np.prod(local_dims))
        if np.log2(dim) > qubit_limit:
            raise QTeaLeavesError("Modify `qubit_limit` if dim > 65536 needed.")

        get_id = lambda: np.reshape(np.eye(dim), local_dims + local_dims)
        ham_matrix = get_id() * 0.0

        for elem in self.hterms:
            for subelem, coords_1d in elem.get_interactions(
                lx_ly_lz, params, dim=self.dim
            ):
                tmp = get_id()

                for ii, op_str in enumerate(subelem["operators"]):
                    # coords_1d indices are as well python and start at 0
                    xpos = coords_1d[ii]

                    op_mat = ops.get_operator(xpos, op_str, params)
                    tmp = np.tensordot(op_mat, tmp, ([1], [xpos]))

                    perm = (
                        list(range(1, xpos + 1))
                        + [0]
                        + list(range(xpos + 1, 2 * nsites))
                    )
                    tmp = np.transpose(tmp, perm)

                total_scaling = elem.prefactor * elem.eval_strength(params)
                if "weight" in subelem:
                    total_scaling *= subelem["weight"]

                # Cannot use += when requiring type cast from real to complex
                ham_matrix = ham_matrix + total_scaling * tmp

        return np.reshape(ham_matrix, [dim, dim])

    def build_ham_sparse(self, ops, params, qubit_limit=None):
        """
        Build Hamiltonian as a sparse matrix, which only works for very small
        system sizes. Moreover, the underlying terms need to support
        building the Hamiltonian as a matrix.

        **Arguments**

        ops : instance of :class:`TNOperators`
            To build the Hamiltonian, we need the actual operators which
            are passed within this variable.

        params : dict
            The parameter dictionary for the simulation.
        """
        xp = sp

        if qubit_limit is None:
            qubit_limit = 16

        lx_ly_lz = self.eval_lvals(params)
        nsites = int(np.prod(np.array(lx_ly_lz)))
        local_dims = ops.get_local_links(nsites, params)
        dim = int(np.prod(local_dims))
        if np.log2(dim) > qubit_limit:
            raise QTeaLeavesError("Modify `qubit_limit` if dim > 65536 needed.")

        ham_matrix = xp.csr_matrix((dim, dim))

        for elem in self.hterms:
            for subelem, coords_1d in elem.get_interactions(
                lx_ly_lz, params, dim=self.dim
            ):
                hsite_list = []
                is_eye = [True] * nsites
                for jj in range(nsites):
                    hsite_list.append(xp.eye(local_dims[jj]))

                for ii, op_str in enumerate(subelem["operators"]):
                    # coords_1d indices are as well python and start at 0
                    xpos = coords_1d[ii]

                    op_mat = ops.get_operator(xpos, op_str, params)
                    op_csr = sp.csr_matrix(op_mat)

                    hsite_list[xpos] = op_csr
                    is_eye[xpos] = False

                n_leading_eye = 0
                for is_eye_ii in is_eye:
                    if not is_eye_ii:
                        break
                    n_leading_eye += 1

                n_trailing_eye = 0
                for is_eye_ii in is_eye[::-1]:
                    if not is_eye_ii:
                        break
                    n_trailing_eye += 1

                tmp_a = xp.eye(int(np.prod(local_dims[:n_leading_eye])))
                tmp_b = xp.eye(1)
                if n_trailing_eye > 0:
                    tmp_c = xp.eye(int(np.prod(local_dims[-n_trailing_eye:])))
                else:
                    tmp_c = xp.eye(1)

                jj = nsites - n_leading_eye - n_trailing_eye
                kk = n_leading_eye

                for ii in range(jj):
                    tmp_b = xp.kron(tmp_b, hsite_list[kk])
                    kk += 1

                if n_leading_eye > n_trailing_eye:
                    tmp_b = xp.kron(tmp_b, tmp_c)
                    tmp = xp.kron(tmp_a, tmp_b)
                else:
                    tmp_b = xp.kron(tmp_a, tmp_b)
                    tmp = xp.kron(tmp_b, tmp_c)

                total_scaling = elem.prefactor * elem.eval_strength(params)
                if "weight" in subelem:
                    total_scaling *= subelem["weight"]

                tmp *= total_scaling

                # Cannot use += when requiring type cast from real to complex
                ham_matrix = ham_matrix + tmp

        return ham_matrix

    def apply_ham_to_state(self, state, ops, params):
        """
        Apply the Hamiltonian to a state by contracting all
        operators to it, without constructing the matrix.

        **Arguments**

        state : instance of :class:`StateVector` or `numpy.ndarray`
            The input state.

        ops : instance of :class:`TNOperators`
            The operators consisting the Hamiltonian.

        params : dict
            The parameter dictionary for the simulation.
        """
        lx_ly_lz = self.eval_lvals(params)
        nsites = int(np.prod(np.array(lx_ly_lz)))

        local_dim = ops.get_operator("id", params).shape[0]

        # get the vector from the StateVector object
        if hasattr(state, "state"):
            if isinstance(state.state, np.ndarray):
                psi = state.state
                original_shape = psi.shape
            else:
                raise QTeaLeavesError(
                    f"""The object state has an attribute state.state,
                    but it is not a numpy array but type {type(state.state)}."""
                )
        elif isinstance(state, np.ndarray):
            psi = state
            original_shape = psi.shape
            # if not a N-legged tensor but 1D vector, reshape into N-legged.
            if original_shape != [local_dim] * nsites:
                if original_shape == (local_dim**nsites,):
                    psi.reshape([local_dim] * nsites)
                else:
                    raise QTeaLeavesError(
                        f"""The shape of the input file must be 1D: {local_dim**nsites}
                        or N-legged tensor: {[local_dim]*nsites}, but is {original_shape}."""
                    )
        else:
            raise QTeaLeavesError(
                f"Input state has to be either numpy array or StateVector type, is {type(state)}."
            )

        # the array to add the H|psi> terms into
        final_psi = np.zeros(shape=psi.shape, dtype=psi.dtype)
        # iterate over all terms in H
        for elem in self.hterms:
            for subelem, coords_1d in elem.get_interactions(
                lx_ly_lz, params, dim=self.dim
            ):
                # total_scaling is the prefactor of the operators in this subelem

                total_scaling = elem.prefactor * elem.eval_strength(params)
                if "weight" in subelem:
                    total_scaling *= subelem["weight"]

                # op_psi will be the state with the op applied. Initialize as the initial psi.
                op_psi = np.copy(psi)
                # iterate over all operators in the term
                for ii, op_str in enumerate(subelem["operators"]):
                    # get the operator matrix representation and multiply by its prefactor
                    # (assumes total_scaling is scalar)
                    op_mat = ops.get_operator(op_str, params)
                    op_mat = op_mat * total_scaling
                    # now set total_scaling to 1,
                    # as only the first operator has to be multiplied by it
                    total_scaling = 1

                    # coords_1d indices are as well python and start at 0
                    xpos = coords_1d[ii]

                    # apply the op to the state
                    # tensordot can be understood as contracting the two tensors
                    # by the legs given in axes
                    op_psi = np.tensordot(op_mat, op_psi, axes=(1, xpos))

                    # however, this pushes the resulting leg to first place,
                    # and it has to be permuted back.
                    # This is achieved by transposing the result accoring to the
                    # permutation rule.
                    # There is space for improvement here:
                    # Instead of transposing every time, keep track of the permutations
                    # in a separate list and only permute once at the end.

                    perm = (
                        list(range(1, xpos + 1)) + [0] + list(range(xpos + 1, nsites))
                    )
                    op_psi = np.transpose(op_psi, perm)

                # add the current ops into the final state
                final_psi += op_psi

        # finally reshape psi into a 1D array
        final_psi = np.reshape(final_psi, original_shape)

        if hasattr(state, "state"):
            # update the state
            setattr(state, "state", final_psi)
            return state

        return final_psi

    def density_matrix(
        self, ops, params, temp, return_vec=False, k_b=1, eps_p=1e-8, max_prob=None
    ):
        """
        Diagonalize a Hamiltonian and compute its density matrix at
        finite temperature.

        Parameters
        ----------
        ops : instance of :class:`TNOperators`
            To build the Hamiltonian, we need the actual operators which
            are passed within this variable.

        params : dict
            The parameter dictionary for the simulation.

        temp : float
            Temperature.

        return_vec : Boolean, optional
            If True, return eigenvectors instead
            of density matrix. \\
            Default to False.

        k_b : float, optional
            Value for the Boltzmann constant.\\
            Default to 1.

        eps_p : float, optional
            Value after which the finite temperature state
            probabilities are cut off. \\
            Default to 1e-8.

        max_prob : int or None, optional
            Maximum number of finite temperature probabilities
            left after truncating. If None, there is no limit
            on number of probabilities.
            Default to None.

        Return
        ------
        if return_vec is False:
            rho : 2D np.ndarray
                Density matrix.

        if return_vec is True:
            2D np.ndarray :
                Array with eigenstates of a Hamiltonian as
                columns. Note that this array contains only the
                eigenstates whose corresponding finite temperature
                probabilities are larger than eps_p.

        prob : 1D np.ndarray
            Finite temperature probabilities.
        """
        ham = self.build_ham(ops=ops, params=params)

        # diagonalize the Hamiltonian
        val, vec = np.linalg.eigh(ham)
        l_ind = np.argsort(val)
        ene = val[l_ind]
        psi = vec[:, l_ind]

        # compute the finite temperature probabilities
        part_func = np.sum(np.exp(-ene / (k_b * temp) + ene[0] / (k_b * temp)))
        prob = np.exp(-ene / (k_b * temp) + ene[0] / (k_b * temp)) / part_func

        # cut off all the probabilities smaller than eps_p
        mask = prob > eps_p
        prob = prob[mask]

        k_0 = len(prob)
        if max_prob is not None:
            if k_0 > max_prob:
                raise RuntimeError(
                    f"Too small truncation. {k_0} finite"
                    " temperature probabilities left"
                    f" after truncation, {max_prob}"
                    " is allowed."
                )

        # if return_vec is True, return eigenstates instead of density matrix
        if return_vec:
            return psi[:, :k_0], prob

        # compute the density matrix
        rho = np.matmul(prob * psi[:, :k_0], psi[:, :k_0].T)

        return rho, prob

    # pylint: disable-next=too-many-statements
    def parameterization_write(self, folder_name_input, params, idx=0):
        """
        Write the parameterization of the model into a file and
        return the filename.

        **Arguments**

        folder_name_input : str
            Name of the input folder, where the parameterization file
            will be stored.

        params : dict
            The parameter dictionary for the simulation.

        idx : int, optional
            The parameterization file allows to be indexed to
            support multiple files.
            Default to 0.
        """
        parameterization_file = "parameterization_%03d.dat" % (idx)
        # pylint: disable-next=no-member
        full_file = os.path.join(folder_name_input, parameterization_file)
        str_buffer = ""
        is_real = True

        # Number of parameters
        str_buffer += str(len(self.coupl_params)) + "\n"

        # Number of data points depends on dynamics present or not
        if "Quenches" in params:
            number_time_steps = 0
            for elem in params["Quenches"]:
                number_time_steps += elem.get_length(params)

            str_buffer += "%d\n" % (number_time_steps)
        else:
            str_buffer += "0\n"

        # Parameters for statics
        # ----------------------

        required_params = OrderedDict()

        # Do both options real and complex
        str_buffer_r = ""
        str_buffer_c = ""

        for key, elem in self.coupl_params.items():
            example = elem[1]
            val = example.eval_strength(params)
            if hasattr(val, "__call__"):
                val = val(params)
                if isinstance(val, np.ndarray):
                    unique = np.array(list(set(list(val.flatten()))))
                    if np.sum(np.abs(unique) > 1e-14) > 1:
                        raise QTeaLeavesError(
                            "No support yet of site-dependent "
                            + "couplings with more than one "
                            + "non-zero coupling."
                        )
                    val = 0
                    for entry in unique:
                        if np.abs(entry) > np.abs(val):
                            val = entry

            str_buffer_r += "%30.15E\n" % (np.real(val))
            str_buffer_c += "(%30.15E, %30.15E)\n" % (np.real(val), np.imag(val))
            is_real = is_real and (np.imag(val) == 0)

            # Store default values in case of quenches
            required_params[key] = val

        # Parameters for dynamics
        # -----------------------

        if "Quenches" in params:
            time_offset = 0.0

            str_buffer_1_r = ""
            str_buffer_1_c = ""
            str_buffer_2 = ""

            for next_quench in params["Quenches"]:
                for val in next_quench.iter_params(
                    required_params, params, time_at_start=time_offset
                ):
                    str_buffer_1_r += "%30.15E\n" % (np.real(val))
                    str_buffer_1_c += "(%30.15E, %30.15E)\n" % (
                        np.real(val),
                        np.imag(val),
                    )
                    is_real = is_real and (np.imag(val) == 0)

                for val in next_quench.iter_params_dts(params):
                    if val > 0.0:
                        time_offset += val
                    str_buffer_2 += "%30.15E\n" % (val)

            if is_real:
                str_buffer_r += str_buffer_1_r
                str_buffer_r += str_buffer_2
            else:
                str_buffer_c += str_buffer_1_c
                str_buffer_c += str_buffer_2

        if is_real:
            str_buffer += str_buffer_r
        else:
            str_buffer += str_buffer_c

        with open(full_file, "w+") as fh:
            # Are numbers real? 0=Complex, 1=Real
            # Only real for now ...
            if is_real:
                fh.write("1\n")
            else:
                fh.write("0\n")

            fh.write(str_buffer)

        return parameterization_file

    def timedependent_parameter_to_dict(self, params):
        """
        Return a dictionary with all the time dependent parameters
        of the simulation.

        **Arguments**

        params : dict
            The parameter dictionary for the simulation.
        """

        # Number of data points depends on dynamics present or not
        if "Quenches" in params:
            number_time_steps = 0
            for elem in params["Quenches"]:
                number_time_steps += elem.get_length(params)

        # Parameters for statics
        # ----------------------

        required_params = OrderedDict()

        for key, elem in self.coupl_params.items():
            example = elem[1]
            val = example.eval_strength(params)
            if hasattr(val, "__call__"):
                val = val(params)
                if isinstance(val, np.ndarray):
                    unique = np.array(list(set(list(val.flatten()))))
                    if np.sum(np.abs(unique) > 1e-14) > 1:
                        raise QTeaLeavesError(
                            "No support yet of site-dependent "
                            + "couplings with more than one "
                            + "non-zero coupling."
                        )
                    val = 0
                    for entry in unique:
                        if np.abs(entry) > np.abs(val):
                            val = entry

            # Store default values in case of quenches
            required_params[key] = val

        # Parameters for dynamics
        # -----------------------
        if "Quenches" in params:
            param_dict = {}
            param_dict["time_grid"] = []

            for next_quench in params["Quenches"]:
                # Construct a mask, where entries with value
                # ``True`` refer to time evolution steps (dt > 0) and
                # entries with ``False`` correspond to measurements
                # (dt == 0.0) or skipped measurements (dt < 0.0)
                mask = []

                if len(param_dict["time_grid"]) > 0:
                    time_offset = param_dict["time_grid"][-1]
                else:
                    time_offset = 0.0

                time_ii = time_offset
                for val in next_quench.iter_params_dts(params):
                    if val > 0.0:
                        time_ii += val
                        param_dict["time_grid"].append(time_ii)
                        mask.append(True)
                    else:
                        mask.append(False)

                ii = 0
                # time_offset = 0.0
                # iter_params yields blocks of len(required_params)
                # values, where each time step contains one block
                # for the values at mid time-step and one time step
                # for the values at the end of the time step
                for val in next_quench.iter_params(
                    required_params, params, time_at_start=time_offset
                ):
                    if not mask[ii // len(required_params)]:
                        ii += 1
                        continue

                    jj = ii % len(required_params)
                    key = list(required_params.keys())[jj]
                    if key not in param_dict:
                        param_dict[key] = []

                    param_dict[key].append(val)
                    ii += 1

        return param_dict
