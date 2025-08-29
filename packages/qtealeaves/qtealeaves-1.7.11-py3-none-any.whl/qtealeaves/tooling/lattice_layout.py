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
The lattice layout helps us to support models beyond square lattices
with - to some extent - arbitrary positions in space.
"""
import numpy as np

from .qtealeavesexceptions import QTeaLeavesError

__all__ = ["LatticeLayout"]


class LatticeLayout:
    """
    The LatticeLayout class stores the positions of the (num_x)x(num_y) grid
    which allows for non-square 2D lattices.

    **Arguments**

    num_x : int
        Number of points in x-direction.

    num_y : int
        Number of points in y-direction

    layout_str : str
        Either ``square`` or ``triangle``.
        Default to ``square``
    """

    def __init__(self, num_x, num_y, layout_str="square"):
        self.layout_str = layout_str
        self.num_x = num_x
        self.num_y = num_y

        self.positions = np.zeros((num_x, num_y, 2))
        self.neighbors = {}

        if layout_str == "square":
            self.init_square()
        elif layout_str == "triangle":
            self.init_triangle()
        else:
            raise QTeaLeavesError("Unknown layout `%s`." % (layout_str))

        # Center of the system
        xcenter = np.mean(self.positions[:, :, 0])
        ycenter = np.mean(self.positions[:, :, 1])
        self.center = (xcenter, ycenter)

    def __str__(self):
        return self.layout_str

    def __repr__(self):
        return self.layout_str

    def init_square(self):
        """
        Init a square lattice with lattice spacing 1.
        """
        upper = np.array([self.num_x, self.num_y])

        for ii in range(self.num_x):
            for jj in range(self.num_y):
                self.positions[ii, jj, 0] = ii
                self.positions[ii, jj, 1] = jj

                neighbors_ij = []
                for elem in [(ii - 1, jj), (ii + 1, jj), (ii, jj + 1), (ii, jj - 1)]:
                    if np.any(np.array(elem) < 0) or (np.any(np.array(elem) >= upper)):
                        pass
                    else:
                        neighbors_ij.append(elem)

                self.neighbors[(ii, jj)] = neighbors_ij

    def init_triangle(self):
        """
        Init a hexagonal lattice with spacing 1 on all edges
        of the hexagons.
        """
        for ix in range(self.num_x):
            for iy in range(self.num_y):
                self.positions[ix, iy, 0] = (iy % 2) * 0.5 + ix
                self.positions[ix, iy, 1] = iy * np.sqrt(3.0 / 4.0)

        for ix in range(self.num_x):
            for iy in range(self.num_y):
                neighbors_ij = []
                for jx in range(self.num_x):
                    for jy in range(self.num_y):
                        dist = self.distance((ix, iy), (jx, jy))

                        if abs(dist - 1.0) < 1e-12:
                            neighbors_ij.append((jx, jy))

                self.neighbors[(ix, iy)] = neighbors_ij

    @staticmethod
    def iterate_sites(num_x, num_y):
        """
        Iterate sites of 2D lattice layout.

        **Arguments**

        num_x : int
            Number of points in x-direction.

        num_y : int
            Number of points in y-direction
        """
        for ix in range(num_x):
            for iy in range(num_y):
                yield ix, iy

    def all_distances(self):
        """
        Iterate over all sites to find the all the distances
        for each i,j point in the given lattice.
        """
        if not np.any(self.positions):
            raise QTeaLeavesError("The lattice is not defined yet.")

        dist_ij = np.zeros((self.num_x, self.num_y, self.num_x, self.num_y))
        for ix, iy in self.iterate_sites(self.num_x, self.num_y):
            for jx, jy in self.iterate_sites(self.num_x, self.num_y):
                dist = self.distance((ix, iy), (jx, jy))
                dist_ij[ix, iy, jx, jy] = dist
        return dist_ij

    def unique_distances(self, decimals=10):
        """
        Iterate over all sites to find the unique distances
        for the given lattice within a given decimals precision.

        **Arguments**

        decimals : int
            Round the array with all the distances to the given number
            of decimals.
        """

        # Find all the distances for each i,j site
        dist_ij = np.round(self.all_distances().flatten(), decimals)

        unique_dist = list(set(dist_ij))
        # Remove 0 from the distances list
        unique_dist = list(filter(lambda num: num != 0, unique_dist))

        return np.sort(unique_dist)

    def distance(self, site_a, site_b):
        """
        Calculate the distance between two points.

        **Arguments**

        site_a : tuple of two ints or floats
            Coordinates of the first site, either in the
            grid if integers, or in real-space coordinates
            if floats are passed.

        site_b : tuple of two ints or floats
            Coordinates of the second site.
        """
        if isinstance(site_a[0], int) and isinstance(site_b[0], int):
            dx_dy = (
                self.positions[site_a[0], site_a[1], :]
                - self.positions[site_b[0], site_b[1], :]
            )
        elif isinstance(site_a[0], int):
            dx_dy = self.positions[site_a[0], site_a[1], :] - np.array(site_b)
        elif isinstance(site_b[0], int):
            dx_dy = self.positions[site_b[0], site_b[1], :] - np.array(site_a)
        else:
            dx_dy = np.array(site_a) - np.array(site_b)

        return np.sqrt(np.sum(dx_dy**2))
