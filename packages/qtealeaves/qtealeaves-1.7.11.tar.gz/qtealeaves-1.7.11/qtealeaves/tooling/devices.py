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
The tooling to have accelerator devices recognized.
"""

_CPU_DEVICE = "cpu"
_GPU_DEVICE = "gpu"
_XLA_DEVICE = "xla"


class DeviceList(list):
    """List of devices testing contains as startswith."""

    def __contains__(self, value):
        return any(value.startswith(elem) for elem in self)
