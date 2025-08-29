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
Restricted classes, e.g., a list restricted to instances of a certain type
"""

from .qtealeavesexceptions import QTeaLeavesError

__all__ = ["_RestrictedList"]


class _RestrictedList(list):
    """
    List allowing only instances of a certain class (here :class:`object` true
    for anything as example).
    """

    class_allowed = object

    def __init__(self, *args):
        super().__init__(*args)

        for elem in self:
            self._check_class(elem)

    def _check_class(self, elem):
        """Internal function raising error if entry is not of given class."""
        if not isinstance(elem, self.class_allowed):
            raise QTeaLeavesError(
                f"List only accepts `{self.class_allowed}` as entries."
            )

        return elem

    def __setitem__(self, index, elem):
        """Overwriting setting items."""
        super().__setitem__(index, self._check_class(elem))

    def insert(self, index, elem):
        """Overwriting inserting an item."""
        super().insert(index, self._check_class(elem))

    def append(self, elem):
        """Overwriting appending an item."""
        super().append(self._check_class(elem))

    def extend(self, other):
        """Overwriting extending a list."""
        if isinstance(other, type(self)):
            super().extend(other)
        else:
            super().extend(self._check_class(elem) for elem in other)
