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
Generic base class for operators.
"""

# pylint: disable=too-many-locals

# pylint: disable-next=no-name-in-module
from collections import OrderedDict

import numpy as np

from qtealeaves.tooling.operatorstrings import _op_string_mul
from qtealeaves.tooling.parameterized import _ParameterizedClass

__all__ = ["TNOperators"]


class TNOperators(_ParameterizedClass):
    """
    Generic class to write operators. This class contains no pre-defined
    operators. It allows you to start from scratch if no other operator
    class fulfills your needs.

    **Arguments**

    set_names : list of str, optional
        Name of the operators sets.
        Default to `default`

    mapping_func : callable (or `None`), optional
        Mapping the site index to an operator. Arguments
        `site_idx` must be accepted.
        Default to `None` (default mapping to only operator set)
    """

    def __init__(self, set_names="default", mapping_func=None):
        if isinstance(set_names, str):
            set_names = [set_names]

        self._ops_dicts = {}
        for name in set_names:
            if not isinstance(name, str):
                raise TypeError(f"Set names must be str, but got `{type(name)}`.")
            self._ops_dicts[name] = OrderedDict()

        # Trivial mapping as None resolved in property
        self._mapping_func = None
        if mapping_func is not None:
            self._mapping_func = mapping_func

        # Mapping of operators (to avoid equal operators being defined twice)
        # Can be set, e.g., for 2nd order operators.
        self._has_2nd_order = False
        self._mapping_op = {}

    @property
    def one_unique(self):
        """Flag if only one operators set exists (True) or multiple (False)."""
        return len(self) == 1

    @property
    def mapping_func(self):
        """Mapping function for site to operator set name."""
        if self._mapping_func is None:
            default_key = self.set_names[0]

            # pylint: disable-next=unused-argument
            def default_mapping(site_idx, default_key=default_key):
                return default_key

            return default_mapping

        return self._mapping_func

    @property
    def set_names(self):
        """Return operator set names as list of strings."""
        return list(self._ops_dicts.keys())

    def __len__(self):
        """Lenght of TNOperators defined as number of operator sets."""
        return len(self._ops_dicts)

    def __contains__(self, key):
        """Check if a key is inside the operators."""
        key_a, key_b = self._parse_key(key)
        if key_a not in self._ops_dicts:
            return False

        return key_b in self._ops_dicts[key_a]

    def __delitem__(self, key):
        """Delete entry in operators."""
        key_a, key_b = self._parse_key(key)
        del self._ops_dicts[key_a][key_b]

    def __getitem__(self, key):
        """Extract entry by key."""
        key_a, key_b = self._parse_key(key)
        return self._ops_dicts[key_a][key_b]

    def __setitem__(self, key, value):
        """Set entry by key."""
        key_a, key_b = self._parse_key(key, callee_set=True)
        self._ops_dicts[key_a][key_b] = value

    def __iter__(self):
        """Iterate through all keys (of all operators sets)."""
        for key, value in self._ops_dicts.items():
            for subkey in value:
                yield (key, subkey)

    def items(self):
        """Iterate throught all (key, value) pairs of all operators sets."""
        for key, value in self._ops_dicts.items():
            for subkey, subvalue in value.items():
                yield (key, subkey), subvalue

    def _parse_key(self, key, callee_set=False):
        """
        Parse the key and split into operator set key and operator name key.

        **Arguments**

        key : tuple (or str)
            Key as tuple of length two (or operator name).

        callee_set : bool, optional
            Indicate if callee is `__setitem__`.
            Default to `False`.
        """
        if isinstance(key, str) and self.one_unique:
            default_key = self.set_names[0]
            return default_key, key

        if isinstance(key, str):
            raise ValueError("Operators are not unique, indicate index.")

        if len(key) != 2:
            raise ValueError("Operators are not unique, indicate index.")

        if isinstance(key[0], str):
            # str for operator set name
            key_0 = key[0]
        elif isinstance(key[0], (int, np.int64)) and callee_set:
            raise ValueError("Cannot set entry via integer entry (per site).")
        elif isinstance(key[0], (int, np.int64)):
            # int for site, use mapping
            # pylint: disable-next=not-callable
            key_0 = self.mapping_func(key[0])
        else:
            raise ValueError(f"First entry must be set name or int, but `{key[0]}`.")

        if not isinstance(key[1], str):
            raise ValueError(
                f"Second entry must specify operator name, but `{key[1]}`."
            )

        return key_0, key[1]

    def get_operator(self, site_idx_1d, operator_name, params):
        """
        Provide a method to return any operator, either defined via
        a callable or directly as a matrix.

        **Arguments**

        site_idx_1d : int, str
            If int, site where we need the operator. Mapping will evaluate what
            to return.
            If str, name of operator set.

        operator_name : str
            Tag/identifier of the operator.

        params : dict
            Simulation parameters as a dictionary; dict is passed
            to callable.
        """
        if isinstance(site_idx_1d, (int, np.int64)):
            # pylint: disable-next=not-callable
            key_0 = self.mapping_func(site_idx_1d)
        else:
            key_0 = site_idx_1d
        op_mat = self.eval_numeric_param(self[(key_0, operator_name)], params)
        return op_mat

    def get_local_links(self, num_sites, params):
        """
        Extract the local links from the operators.

        **Arguments**

        num_sites : integer
            Number of sites.

        params : dict
            Dictionary with parameterization of the simulation.
        """
        local_links = []
        for ii in range(num_sites):
            eye = self.get_operator(ii, "id", params)

            if hasattr(eye, "links"):
                local_links.append(eye.links[1])
            else:
                # When constructing H, we call this with numpy tensors
                local_links.append(eye.shape[0])

        return local_links

    def transform(self, transformation, **kwargs):
        """
        Generate a new :class:`TNOperators` by transforming the
        current instance.

        **Arguments**

        transformation : callable
            Accepting key and value as arguments plus potential
            keyword arguments.

        **kwargs : key-word arguments
            Will be passed to `transformation`
        """
        new_ops = TNOperators(set_names=self.set_names, mapping_func=self.mapping_func)
        for key, value in self.items():
            new_ops[key] = transformation(key, value, **kwargs)

        return new_ops

    def check_alternative_op(self, set_name, key):
        """
        Check entry for alternative operators, i.e., the sigma_x squared
        is the identity.

        Arguments
        ---------

        set_name : str
            Search in this set name of operators. (Set names allow
            different Hilbert spaces on different sites.)

        key : str
            Operator represented as key. Check if there is an alternative
            key for this key.

        Returns
        -------

        alternative_key : None | str
            If `None`, no alternative key is given or the corresponding
            dictionary for checking is not set. If str, then this operator
            has the same representation as `key`.
        """
        set_dict = self._mapping_op.get(set_name, None)
        if set_dict is None:
            return None

        return self._mapping_op[set_name].get(key, None)

    # pylint: disable-next=too-many-branches
    def generate_products_2nd_order(
        self,
        left_conj=False,
        left_transpose=False,
        right_conj=False,
        right_transpose=False,
    ):
        """
        Generate all possible multiplications (matrix-matrix multiplications) of
        the operator set, i.e., [A, B, ...] generators [A*A, A*B, B*A, B*B, ...].
        Transformation can be taken into account on top.

        Arguments
        ---------

        left_conj : Boolean
            Tells if the left operator needs to be complex conjugated.
            Default is False.

        right_transpose : Boolean
            Tells if the left operator needs to be transposed.
            Default is False.

        right_conj : Boolean
            Tells if the right operator needs to be complex conjugated.
            Default is False.

        right_transpose : Boolean
            Tells if the right operator needs to be transposed.
            Default is False.

        Returns
        -------

        None (in-place update of the operator dictionary)

        """
        if self._has_2nd_order:
            return

        self._has_2nd_order = True

        additional_ops = {}
        for set_name in self.set_names:
            additional_ops[set_name] = {}

            for op_str_a, op_a in self._ops_dicts[set_name].items():
                for op_str_b, op_b in self._ops_dicts[set_name].items():
                    op_str = _op_string_mul("", op_str_a, left_conj, left_transpose)
                    op_str = _op_string_mul(
                        op_str, op_str_b, right_conj, right_transpose
                    )
                    op_str = op_str_a + "*" + op_str_b
                    if (op_str_a == "id") and (op_str_b == "id"):
                        additional_ops[set_name][op_str] = "id"
                    elif (
                        (op_str_a == "id")
                        and (not right_conj)
                        and (not right_transpose)
                    ):
                        additional_ops[set_name][op_str] = op_str_b
                    elif (
                        (op_str_b == "id") and (not left_conj) and (not left_transpose)
                    ):
                        additional_ops[set_name][op_str] = op_str_a
                    elif op_a.has_symmetry:
                        tmp_a = _op_transformation(op_a, left_conj, left_transpose)
                        tmp_b = _op_transformation(op_b, right_conj, right_transpose)

                        op = tmp_a.tensordot(tmp_b, [(2,), (1,)])
                        _, op = op.split_qr([0, 3, 1, 4], [2, 5])
                        op, _ = op.split_rq([0, 1], [2, 3, 4])
                        additional_ops[set_name][op_str] = op
                    else:
                        tmp_a = _op_transformation(op_a, left_conj, left_transpose)
                        tmp_b = _op_transformation(op_b, right_conj, right_transpose)

                        op = tmp_a.einsum("ijkl,akbd->ijbl", tmp_b)
                        additional_ops[set_name][op_str] = op

            # Check they are really new and not identical to existing ones
            # to get the smallest set
            to_be_added = {}
            to_be_reset = {}
            for key, op in additional_ops[set_name].items():
                if isinstance(op, str):
                    continue

                for key_ii, op_ii in self._ops_dicts[set_name].items():
                    if op.are_equal(op_ii, tol=10 * op.dtype_eps):
                        to_be_reset[key] = key_ii
                    else:
                        to_be_added[key] = op
                        continue

            for key, value in to_be_added.items():
                self._ops_dicts[set_name][key] = value

            for key, value in to_be_reset.items():
                additional_ops[set_name][key] = value

        for set_name, set_dict in additional_ops.items():
            if set_name not in self._mapping_op:
                self._mapping_op[set_name] = {}

            for key, value in set_dict.items():
                self._mapping_op[set_name][key] = value


def _op_transformation(op, is_conj, is_transpose):
    """
    Carry out the transformation on an operator.

    Arguments
    ---------

    op : :class:`_AbstractQteaTensor`
        Tensor to be transformed. We assume rank-4 tensors.

    is_conj : bool
        Flag if conjugate is applied.

    is_transpose : bool
        Flag if transpose is applied.

    Returns
    -------

    new_op : :class:`_AbstractQteaTensor`
        Operator after the transformations.
    """
    if is_conj and is_transpose:
        new_op = op.conj().transpose([0, 2, 1, 3])
    elif is_conj:
        new_op = op.conj()
    elif is_transpose:
        new_op = op.transpose([0, 2, 1, 3])
    else:
        new_op = op

    return new_op
