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
Extended json encoder able to encode numpy arrays etc.
"""
import json

import numpy as np

__all__ = ["QteaJsonEncoder"]


class QteaJsonEncoder(json.JSONEncoder):
    """
    A json encoder extended for quantum tea with ability to
    handle common problematic classes.
    """

    # pylint: disable-next=arguments-renamed
    def default(self, obj):
        """
        Default encoding is checking for common classes with no default
        support for encoding.

        Arguments
        ---------

        obj
            Object to be encoded.
        """
        if isinstance(obj, np.floating):
            return obj.astype(np.float64).tolist()

        if isinstance(obj, np.integer):
            return list(map(int, obj))

        if str(obj) in (
            "TTN",
            "MPS",
        ):
            return str(obj)

        return super().default(obj)
