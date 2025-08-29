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
The module contains a tensor node.
"""

__all__ = ["TNnode"]


class TNnode:
    """
    Class to encode a node in a tensor network, to work
    with arbitrary tensor network.

    Parameters
    ----------
    layer: int
        Layer of the network where the node lives
    index: int
        Index of the tensor inside the layer
    children: list of TNnode
        Children nodes
    link_idx: int
        Number for the new index for the links
    """

    def __init__(self, layer, index, children, link_idx):
        self.layer = layer
        self.index = index

        if children is not None:
            self.link_idxs = []
            for child in children:
                child.add_parent(self)
                self.link_idxs.append(child.link_idxs[-1])
            self.link_idxs.append(link_idx)
        else:
            self.link_idxs = [link_idx + ii for ii in range(3)]
        self.children = children
        # By default, the parent is None and should be added with
        # the appropriate method
        self.parent = None

    def __repr__(self) -> str:
        return f"({self.layer}, {self.index})"

    def is_child(self, parent_node):
        """
        Check if the class is the child of `parent_node`

        Parameters
        ----------
        parent_node : TNnode
            Potential parent node

        Returns
        -------
        bool
            True if `parent_node` is the parent
        """
        return parent_node == self.parent

    def is_parent(self, child_node):
        """
        Check if the class is the parent of `child_node`

        Parameters
        ----------
        child_node : TNnode
            Potential child node

        Returns
        -------
        bool
            True if `child_node` is the child
        """
        return child_node in self.children

    def add_parent(self, parent):
        """
        Add the node `parent` as parent node of the class

        Parameters
        ----------
        parent : TNnode
            New parent node
        """
        self.parent = parent
