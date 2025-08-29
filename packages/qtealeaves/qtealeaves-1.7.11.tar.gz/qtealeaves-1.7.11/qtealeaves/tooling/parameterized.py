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
The tooling to have parameterized models and instances.
"""
import typing

__all__ = ["_ParameterizedClass"]


class _ParameterizedClass:
    """
    Abstract base class for any other class which needs to evaluate
    parameterization.
    """

    def eval_numeric_param(self, elem, params):
        """
        Evaluate a numeric parameter which might be defined via the
        parameter dictionary.

        **Arguments**

        elem : callable, string, or int/float
            Defines the parameter either via a function which return
            the value, a string being an entry in the parameter
            dictionary, or directly as the numeric value.

        params : dict
            The parameter dictionary, which will be passed to callables
            and used to evaluate string parameters.
        """
        if isinstance(elem, list):
            return [self.eval_numeric_param(subelem, params) for subelem in elem]

        if hasattr(elem, "__call__"):
            val = elem(params)
        elif isinstance(elem, str):
            val = params[elem]
        else:
            val = elem

        return val

    @staticmethod
    def eval_str_param(elem, params):
        """
        Evaluate a string parameter.

        **Arguments**

        elem : callable, string, or int/float
            Defines the parameter either via a function which return
            the value, or directly as the numeric value.

        params : dict
            The parameter dictionary, which will be passed to callables.
        """
        if hasattr(elem, "__call__"):
            val = elem(params)
        # pylint: disable-next=isinstance-second-argument-not-valid-type
        elif not isinstance(elem, typing.Hashable):
            val = elem
        elif elem in params:
            val = params[elem]
        else:
            val = elem

        return val

    @staticmethod
    def eval_str_param_default(elem, params, default):
        """
        Evaluate a string parameter and allow to set default. It
        sets the default as soon as elem is not callable.

        **Arguments**

        elem : callable, ...
            Defines the parameter via a callable. Any other variable
            will be overwritten by the default.

        params : dict
            The parameter dictionary passed to the callable.

        default : str
            The default value if elem is not callable.
        """
        if hasattr(elem, "__call__"):
            val = elem(params)
        else:
            val = default

        return val

    def _resolve_params_attr(self, params, attr_numeric=None, attr_str=None, idx=None):
        """
        Resolve parameterized values (inplace-update).

        **Arguments**

        params : dict
            Parameter dictionary of the simulation which can be used to
            resolve the parameters.

        attr_numeric : list of strings or `None`
            For a list of strings, `getattr` and `setattr`
            is called for the the class to resolve potential
            parameterization with `eval_numeric_param`

        attr_str : list of strings or `None`
            For a list of strings, `getattr` and `setattr`
            is called for the the class to resolve potential
            parameterization with `eval_str_param`

        idx : int | None, optional
            Resolve and pick entry in list if value is a list.
            We take the last element if list is shorter than idx
            Default to `None` (no value in list is picked)
        """
        if attr_numeric is not None:
            for elem in attr_numeric:
                value = getattr(self, elem)
                value = self.eval_numeric_param(value, params)
                if (idx is not None) and hasattr(value, "__len__"):
                    # Take last element if list shorter than idx
                    value = value[min(idx, len(value) - 1)]

                setattr(self, elem, value)

        if attr_str is not None:
            for elem in attr_str:
                value = getattr(self, elem)
                value = self.eval_str_param(value, params)
                if (
                    (idx is not None)
                    and hasattr(value, "__len__")
                    and (not isinstance(value, str))
                ):
                    value = value[idx]
                setattr(self, elem, value)
