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
The tooling to skip unittests in a nice way, e.g., for missing hardware like GPUs.
As we need it in multiple places, it is now in the tooling.
"""

# pylint: disable=too-few-public-methods

import inspect


def decallmethods(decorator, prefix="test_"):
    """
    Class decorator, to apply decorators to all the methods that starts
    with 'test_' in the class
    """

    def dectheclass(cls):
        for name, m in inspect.getmembers(cls, inspect.isfunction):
            if name.startswith(prefix):
                setattr(cls, name, decorator(m))
        return cls

    return dectheclass
