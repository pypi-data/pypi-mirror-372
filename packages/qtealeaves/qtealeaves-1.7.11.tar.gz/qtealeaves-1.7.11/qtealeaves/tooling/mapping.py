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
The Hilbert curve map takes care of the mapping of higher dimensional systems
to a 1d system.
"""

# pylint: disable=too-many-lines
import math
import sys
from collections import OrderedDict
from itertools import product

import numpy as np

from .qtealeavesexceptions import QTeaLeavesError

__all__ = [
    "HilbertCurveMap",
    "GeneralizedHilbertCurveMap",
    "SnakeMap",
    "ZigZagMap",
    "map_selector",
]


class HilbertCurveMap(OrderedDict):
    """
    The map reads the input file and is organized as an ordered
    dictionary. The tuple of the coordinates returns the
    index in the 1d chain.

    **Arguments**

    The class creator takes the following arguments

    dim : integer
        system dimensionality (1d, 2d, or 3d)

    size : int, list
        Dimensionality in each spatial direction [Lx, Ly, Lz]. If only
        an integer is given, square or cube is assumed.

    **Attributes**

    The class attributes are now all in python indices, i.e., the
    dictionary keys and the index in the 1d system.
    """

    def __init__(self, dim, size):
        super().__init__()
        self.keys_list = None

        if dim == 1:
            self.init_1d(size)
        elif dim == 2:
            self.init_2d(size)
        elif dim == 3:
            self.init_3d(size)
        else:
            raise QTeaLeavesError("No Hilbert curve beyond 3d supported.")

    def init_1d(self, size):
        """
        Init the Hilbert curve for a 1d system. Raises an exception.
        ZigZag is the only one providing a mapping for 1d.

        **Arguments**

        size : int or list of two ints
            Defines the shape of the square or rectangle.
        """
        raise QTeaLeavesError(str(self) + ": no mapping needed for 1d case.")

    def init_2d(self, size):
        """
        Init the Hilbert curve for a 2d system.

        **Arguments**

        size : int or list of two ints
            Defines the shape of the square or rectangle.
        """
        if isinstance(size, int):
            size = [size] * 2

        if len(size) != 2:
            raise QTeaLeavesError("Dimension is 2d, but size is not of length 2.")

        hilbert_curve = hilbert_curve_2d(*size)

        ind_list = []
        for ii in range(size[0] * size[1]):
            ind_list.append([])

        for ii in range(size[0]):
            for jj in range(size[1]):
                ind_list[hilbert_curve[ii, jj]] = (ii, jj)

        for ii, elem in enumerate(ind_list):
            self[elem] = ii

        return

    def init_3d(self, size):
        """
        Init the Hilbert curve for a 3d system.

        **Arguments**

        size : int or list of two ints
            Defines the shape of the square or rectangle.
        """
        if isinstance(size, int):
            size = [size] * 3

        if len(size) != 3:
            raise QTeaLeavesError("Dimension is 3d, but size is not of length 3.")

        hilbert_curve = hilbert_curve_3d(*size)

        idx = 0
        for elem in hilbert_curve:
            # All the Hilbert curves in 3d are written in fortran indices
            # Change them here once instead of all lines below
            elem_py_idx = tuple(ii for ii in elem)
            self[elem_py_idx] = idx
            idx += 1

        return

    def __call__(self, coord):
        """
        The call method returns the tuple representing the indices
        of the n-dimension system for one index in the 1-dimensional
        system

        **Arguments**

        coord : int
            Index in the 1d system.
        """
        if not isinstance(coord, int):
            raise QTeaLeavesError("Call method expects integer since v0.2.22.")

        if self.keys_list is None:
            self.keys_list = list(self.keys())

        return self.keys_list[coord]

    def __str__(self):
        """
        The string representation of the Hilbert curve is defined
        as a list of all tuples.
        """
        return str(list(self.keys()))

    def calculate_size(self):
        """
        The system is defined as an n-dimensional system, i.e., 1d, 2d or 3d.
        We return a tuple of length n with the system size along each dimension,
        which we determine from the keys. For example, for a rectangle
        of 8 by 4 sites, the tuple `(8, 4)` is returned as the lattice size.
        """
        dim = len(list(self.keys())[0])

        if dim == 1:
            max_value = 0
            for key in self.keys():
                max_value = max(max_value, key[0])

            return (max_value + 1,)

        if dim == 2:
            max_x = 0
            max_y = 0

            for key in self.keys():
                max_x = max(max_x, key[0])
                max_y = max(max_y, key[1])

            return (max_x + 1, max_y + 1)

        if dim == 3:
            max_x = 0
            max_y = 0
            max_z = 0

            for key in self.keys():
                max_x = max(max_x, key[0])
                max_y = max(max_y, key[1])
                max_z = max(max_z, key[2])

            return (max_x + 1, max_y + 1, max_z + 1)

        raise QTeaLeavesError("Dimensionality not implemented.")

    def backmapping_vector_observable(self, vec):
        """
        We assume an n-dimensional system, e.g., n=2 for a 2d system.
        Takes a vector with the index of the "flattened" as input and
        transforms it into a n-dimensional tensor representing the
        original indices of the system.

        **Arguments**

        vec : np.ndarray with rank 1
            Result to be mapped from the indices of a TTN into their
            original indices.

        **Returns**

        result : np.ndarray with dimension n
            The first indices contain the indices of the original
            n-dimensional system.
        """
        dim = len(list(self.keys())[0])
        size = self.calculate_size()

        if dim == 1:
            result = np.zeros(size[0], vec.dtype)
            for key, src_idx in self.items():
                i1 = key[0]

                result[i1] = vec[src_idx]

            return result

        if dim == 2:
            result = np.zeros((size[0], size[1]), vec.dtype)
            for key, src_idx in self.items():
                i1, i2 = key

                result[i1, i2] = vec[src_idx]

            return result

        if dim == 3:
            result = np.zeros((size[0], size[1], size[2]), vec.dtype)
            for key, src_idx in self.items():
                i1, i2, i3 = key

                result[i1, i2, i3] = vec[src_idx]

            return result

        raise QTeaLeavesError("Dimensionality not implemented.")

    def backmapping_matrix_observable(self, mat):
        """
        We assume an n-dimensional system, e.g., n=2 for a 2d system.
        Takes a matrix with the index of the "flattened" over the
        rows and columns as input and transforms it into a 2n-dimensional
        tensor representing the original indices of the system.

        **Arguments**

        mat : np.ndarray with rank 2.
            Result to be mapped from the indices of a TTN into their
            original indices.

        **Returns**

        result : np.ndarray with dimension 2n
            The first n indices refer to the rows of the original data.
            The second n indices refer to the columns of the original data.
        """
        dim = len(list(self.keys())[0])
        size = self.calculate_size()

        if dim == 1:
            result = np.zeros((size[0], size[0]), mat.dtype)
            for key_a, src_a in self.items():
                i1 = key_a[0]

                for key_b, src_b in self.items():
                    j1 = key_b[0]

                    result[i1, j1] = mat[src_a, src_b]

            return result

        if dim == 2:
            result = np.zeros((size[0], size[1], size[0], size[1]), mat.dtype)
            for key_a, src_a in self.items():
                i1, i2 = key_a

                for key_b, src_b in self.items():
                    j1, j2 = key_b

                    result[i1, i2, j1, j2] = mat[src_a, src_b]

            return result

        if dim == 3:
            result = np.zeros(
                (size[0], size[1], size[2], size[0], size[1], size[2]), mat.dtype
            )
            for key_a, src_a in self.items():
                i1, i2, i3 = key_a

                for key_b, src_b in self.items():
                    j1, j2, j3 = key_b

                    result[i1, i2, i3, j1, j2, j3] = mat[src_a, src_b]

            return result

        raise QTeaLeavesError("Dimensionality not implemented.")

    def show_map(self):
        """
        It shows a matrix in which each element is the order in which
        the relative coordinate appears in the mapping.
        Defined for dim > 1.
        """

        size = self.calculate_size()
        if len(size) == 1:
            raise QTeaLeavesError("Method implemented for dim > 1.")
        ind_matr = np.zeros(size, dtype=int)

        for el in self:
            ind_matr[*el] = self[el]

        with np.printoptions(threshold=np.inf):
            print(ind_matr)

        return


class GeneralizedHilbertCurveMap(HilbertCurveMap):
    """
    The map reads the input file and is organized as an ordered
    dictionary. The tuple of the coordinates returns the
    index in the 1d chain.
    On the top of the HilbertCurveMap, it can be used for lattices
    with sizes which are not a power of 2.
    For instance, given a size L=[11,5] for a 2D system, it will embed it
    into a 16x8 lattice (the embedding lattice) by keeping the
    original lattice at the center.
    Then, it defines the Hilbert curve for the 16 x 8 lattice.
    Finally, the coordinates of the 11x5 lattice will be ordered
    according to the order in which they appear in the 16x8 Hilbert curve
    mapping.

    **Arguments**

    The class creator takes the following arguments

    dim : integer
        system dimensionality (1d, 2d, or 3d)

    size : int, list
        Dimensionality in each spatial direction [Lx, Ly, Lz]. If only
        an integer is given, square or cube is assumed.
        The size now can be a power of 2 (the usual hilbert curve mapping
        is produced) or a generic other integer or list of integers.

    **Attributes**

    The class attributes are now all in python indices, i.e., the
    dictionary keys and the index in the 1d system.
    """

    @staticmethod
    def get_embed_size(dim, size):
        """
        It finds the size of the embedding, power-of-2 lattice.

        **Arguments**

        dim : integer
            System dimensionality (1d, 2d, or 3d).

        size : int, list
            Linear size in each spatial direction [Lx, Ly, Lz]. If only
            an integer is given, square or cube is assumed.

        **Returns**

        result : list with length equal to dim.
            for each element of size, the smallest power-of-two integer,
            larger then element, is found.

        """

        if isinstance(size, int):
            size = [size] * dim

        if len(size) != dim:
            raise QTeaLeavesError(
                "Dimension is %d, but size is not of length %d." % (dim, dim)
            )

        embed_size = []

        powr = 0
        for el in size:
            while 2**powr < el:
                powr += 1
            embed_size.append(int(2**powr))

        return embed_size

    def init_2d(self, size):
        """
        Init the Hilbert curve for a 2d system.
        If size is a power of two, or a list of powers of two,
        it returns the usual Hilbert curve on a square or a
        rectangle.
        Otherwise, it generates the Hilbert curve on the
        embedding lattice and then orders the points in the input
        lattice according to the order they appear along the Hilbert
        curve.

        **Arguments**

        size : int or list of two ints
            Defines the shape of the square or rectangle.
        """
        if isinstance(size, int):
            size = [size] * 2

        if len(size) != 2:
            raise QTeaLeavesError("Dimension is 2d, but size is not of length 2.")

        dim = 2
        embed_size = self.get_embed_size(dim, size)

        # pylint: disable-next=unbalanced-tuple-unpacking
        nx, ny = embed_size
        hilbert_curve = hilbert_curve_2d(nx, ny)

        coord_list = list(product(*[range(el) for el in size]))

        # The list 'shift' allows to shift the center of the lattice with respect to
        # the embedding one.
        # It is set to [0]*dim, meaning that the lattice is in the bottom-left
        # corner of the embedding lattice, but it can be redefined.
        # For example, in the line below there is the definition of shift to
        # set the center of the lattice at the center of the embedding lattice.
        # shift = [int((LL - ell) / 2) for LL, ell in zip(embed_size, size)]

        shift = [0 for _ in size]
        embed_ind_list = []
        for _ in range(embed_size[0] * embed_size[1]):
            embed_ind_list.append([])

        for ii in range(embed_size[0]):
            for jj in range(embed_size[1]):
                embed_ind_list[hilbert_curve[ii, jj]] = (ii, jj)

        ind = 0
        for elem in embed_ind_list:
            shifted_elem = tuple(el - sh for el, sh in zip(elem, shift))
            if shifted_elem in coord_list:
                self[shifted_elem] = ind
                ind += 1

        return

    def init_3d(self, size):
        """
        Init the Hilbert curve for a 3d system.
        If size is a power of two, or a list of powers of two,
        it returns the usual Hilbert curve on a cube or a
        prism.
        Otherwise, it generates the Hilbert curve on the
        embedding lattice and then orders the points in the input
        lattice according to the order they appear along the Hilbert
        curve.

        **Arguments**

        size : int or list of three ints
            Defines the shape of the square or rectangle.
        """
        if isinstance(size, int):
            size = [size] * 3

        if len(size) != 3:
            raise QTeaLeavesError("Dimension is 3d, but size is not of length 3.")

        embed_size = self.get_embed_size(3, size)
        # pylint: disable-next=unbalanced-tuple-unpacking
        nx, ny, nz = embed_size
        hilbert_curve = hilbert_curve_3d(nx, ny, nz)
        coord_list = list(product(*[range(el) for el in size]))

        # The list 'shift' allows to shift the center of the lattice with respect to
        # the embedding one.
        # It is set to [0]*dim, meaning that the lattice is in the bottom-left
        # corner of the embedding lattice, but it can be redefined.
        # For example, in the line below there is the definition of shift to
        # set the center of the lattice at the center of the embedding lattice.
        # shift = [int((LL - ell) / 2) for LL, ell in zip(embed_size, size)]

        shift = [0 for _ in size]
        idx = 0
        for elem in hilbert_curve:
            # All the Hilbert curves in 3d are written in fortran indices
            # Change them here once instead of all lines below
            elem_py_idx = tuple(ii for ii in elem)
            shifted_elem = tuple(el - sh for el, sh in zip(elem_py_idx, shift))
            if shifted_elem in coord_list:
                self[shifted_elem] = idx
                idx += 1

        return


class SnakeMap(HilbertCurveMap):
    """
    The map follows a snake-like mapping in 2d and generalizes it for
    3d.
    """

    def init_2d(self, size):
        """
        Init the snake curve for a 2d system.

        **Arguments**

        size : int, list of two int
            The size of square (int) or the size of the rectangle (list).
        """
        if isinstance(size, int):
            size = [size] * 2

        if len(size) != 2:
            raise QTeaLeavesError("Dimension is 2d, but size is not of length 2.")

        ii_x = 0
        ii_y = 0

        offset_x = 1

        for ii in range(size[0] * size[1]):
            self[(ii_x, ii_y)] = ii

            ii_x += offset_x
            if (ii_x < 0) or (ii_x == size[0]):
                offset_x *= -1
                ii_x += offset_x
                ii_y += 1

    def init_3d(self, size):
        """
        Init the snake curve in 3d.

        **Arguments**

        size : int, list of three int
            The size of cube (int) or the size of the box (list).
        """
        if isinstance(size, int):
            size = [size] * 3

        if len(size) != 3:
            raise QTeaLeavesError("Dimension is 3d, but size is not of length 3.")

        ii_x = 0
        ii_y = 0
        ii_z = 0

        offset_x = 1
        offset_y = 1

        for ii in range(size[0] * size[1] * size[2]):
            self[(ii_x, ii_y, ii_z)] = ii

            ii_x += offset_x
            if (ii_x < 0) or (ii_x == size[0]):
                offset_x *= -1
                ii_x += offset_x
                ii_y += offset_y

            if (ii_y < 0) or (ii_y == size[1]):
                offset_y *= -1
                ii_y += offset_y
                ii_z += 1


class ZigZagMap(HilbertCurveMap):
    """
    The map constructs a zig-zag mapping equal to the order
    of computer memory. The map loops over the smallest dimension
    on the innermost loop.
    """

    def init_1d(self, size):
        """
        Trivial zig-zag mapping for a 1-dimensional system.

        **Arguments**

        size : int, list of one int
            The size of chain.
        """
        if isinstance(size, int):
            nn = size
        else:
            nn = size[0]

        idx = 0
        for ii_x in range(nn):
            self[(ii_x,)] = idx
            idx += 1

    def init_2d(self, size):
        """
        Zig-zag mapping for a 2-dimensional system.

        **Arguments**

        size : int, list of two int
            The size of square (int) or the size of the rectangle (list).
        """
        if isinstance(size, int):
            size = [size] * 2

        if len(size) != 2:
            raise QTeaLeavesError("Dimension is 2d, but size is not of length 2.")

        idx = 0
        if size[0] >= size[1]:
            for ii_x in range(size[0]):
                for ii_y in range(size[1]):
                    self[(ii_x, ii_y)] = idx
                    idx += 1

        else:
            for ii_y in range(size[1]):
                for ii_x in range(size[0]):
                    self[(ii_x, ii_y)] = idx
                    idx += 1

    # pylint: disable-next=too-many-branches
    def init_3d(self, size):
        """
        Zig-zag mapping for a 3-dimensional system.

        **Arguments**

        size : int, list of three int
            The size of cube (int) or the size of the box (list).
        """
        if isinstance(size, int):
            size = [size] * 3

        if len(size) != 3:
            raise QTeaLeavesError("Dimension is 3d, but size is not of length 3.")

        idx = 0
        if size[0] >= size[1] >= size[2]:
            for ii_x in range(size[0]):
                for ii_y in range(size[1]):
                    for ii_z in range(size[2]):
                        self[(ii_x, ii_y, ii_z)] = idx
                        idx += 1
        elif size[0] >= size[2] >= size[1]:
            for ii_x in range(size[0]):
                for ii_z in range(size[2]):
                    for ii_y in range(size[1]):
                        self[(ii_x, ii_y, ii_z)] = idx
                        idx += 1
        elif size[1] >= size[0] >= size[2]:
            for ii_y in range(size[1]):
                for ii_x in range(size[0]):
                    for ii_z in range(size[2]):
                        self[(ii_x, ii_y, ii_z)] = idx
                        idx += 1
        elif size[1] >= size[2] >= size[0]:
            for ii_y in range(size[1]):
                for ii_z in range(size[2]):
                    for ii_x in range(size[0]):
                        self[(ii_x, ii_y, ii_z)] = idx
                        idx += 1
        elif size[2] >= size[0] >= size[1]:
            for ii_z in range(size[2]):
                for ii_x in range(size[0]):
                    for ii_y in range(size[1]):
                        self[(ii_x, ii_y, ii_z)] = idx
                        idx += 1
        elif size[2] >= size[1] >= size[0]:
            for ii_z in range(size[2]):
                for ii_y in range(size[1]):
                    for ii_x in range(size[0]):
                        self[(ii_x, ii_y, ii_z)] = idx
                        idx += 1
        else:
            raise QTeaLeavesError("Case not covered; please report as a bug.")


def map_selector(dim, size, map_type):
    """
    **Arguments**

    dim : integer
        system dimensionality

    size : int, list
        Dimensionality in each spatial direction [Lx, Ly, Lz]. If only
        an integer is given, square or cube is assumed.

    map_type : str
        Selecting the map, either ``HilbertCurveMap``, ``GeneralizedHilbertCurveMap``,
        ``SnakeMap``, or ``ZigZagMap``, or an instance of :py:class:`HilbertCurveMap`.
    """
    if dim == 1:
        # ZigZag is the only enabled for 1d
        return ZigZagMap(dim, size)
    if map_type == "HilbertCurveMap":
        return HilbertCurveMap(dim, size)
    if map_type == "GeneralizedHilbertCurveMap":
        return GeneralizedHilbertCurveMap(dim, size)
    if map_type == "SnakeMap":
        return SnakeMap(dim, size)
    if map_type == "ZigZagMap":
        return ZigZagMap(dim, size)
    if isinstance(map_type, HilbertCurveMap):
        return map_type
    if map_type is None:
        raise QTeaLeavesError("Map type was not set by QuantumModel; report as bug.")

    raise QTeaLeavesError('Unknown map_type "%s".' % (map_type))


# ------------------------------------------------------------------------------
#                                  2d Hilbert curves
# ------------------------------------------------------------------------------


def hilbert_curve_2d(nx, ny):
    """
    Returns the Hilbert curve for a 2d grid with both sides being a power of
    two. The entries of the matrix are the indices in the 1d-mapped system.

    **Arguments**

    nx : int
        Number of sites in x-direction

    ny : int
        Number of sites in y-direction
    """
    if abs(np.log2(nx) - int(np.log2(nx))) > 1e-14:
        raise QTeaLeavesError("Lenght nx must be a power of 2.")
    if abs(np.log2(ny) - int(np.log2(ny))) > 1e-14:
        raise QTeaLeavesError("Lenght ny must be a power of 2.")

    order = max(int(np.log2(nx)), int(np.log2(ny)))
    rules = get_nth_order_rules_2d(order)
    case_square_only = "A"

    return rect_hilbert_curve(nx, ny, case_square_only, rules)


def rect_hilbert_curve(nx, ny, case, rules, offset=0):
    """
    Recursive algorithm to construct a Hilbert curve for a rectangle
    with Hilbert curves in each sub-square. The rectangles are filled
    in a snake approach. The dimensions must be powers of two.

    **Arguments**

    nx : int
        Number of sites in x-direction

    ny : int
        Number of sites in y-direction

    case : character
        Character specifies path, either ``A``, ``B``, ``C``,
        or ``D``.

    rules : dict
        Dictionary with the Hilbert curves for all required orders.

    offset : int, optional
        Offset for the indices is added to the Hilbert curve indices.
        This value allows one to take into account previous squares
        or rectangles.
    """
    ind_mat = np.zeros((nx, ny), dtype=np.int32)

    if nx == ny:
        # Reached square
        order_x = int(np.log2(nx))
        return rules[(case, order_x)] + offset

    if nx > ny:
        # Going in x-direction
        ind_mat[: nx // 2, :] = rect_hilbert_curve(
            nx // 2, ny, "A", rules, offset=offset
        )
        ind_mat[nx // 2 :, :] = rect_hilbert_curve(
            nx // 2, ny, "A", rules, offset=offset + nx // 2 * ny
        )

    else:
        # Going in y-direction
        ind_mat[:, : ny // 2] = rect_hilbert_curve(
            nx, ny // 2, "D", rules, offset=offset
        )
        ind_mat[:, ny // 2 :] = rect_hilbert_curve(
            nx, ny // 2, "D", rules, offset=offset + nx * ny // 2
        )

    return ind_mat


def get_first_order_rules_2d():
    """
    Build the Hilbert curve for 2x2 matrices for all
    required cases. The function returns a dictionary where
    the key is a tuple of the case, i.e., ``A``, ``B``,
    ``C``, and ``D`` and the order.
    """
    rules = {}
    rules[("A", 1)] = np.array([[0, 1], [3, 2]], dtype=np.int32)
    rules[("B", 1)] = np.array([[2, 1], [3, 0]], dtype=np.int32)
    rules[("C", 1)] = np.array([[2, 3], [1, 0]], dtype=np.int32)
    rules[("D", 1)] = np.array([[0, 3], [1, 2]], dtype=np.int32)

    return rules


def get_nth_order_rules_2d(nn):
    """
    Build the Hilbert curve for 2^nx2^n matrices for all
    required cases. The function returns a dictionary where
    the key is a tuple of the case, i.e., ``A``, ``B``,
    ``C``, and ``D`` and the order n.

    **Arguments**

    nn : int
        Defines the order of the maximal square size as powers
        of two. The maximal matrix shape is 2^nn x 2^nn.
    """
    rules = get_first_order_rules_2d()

    for ii in range(1, nn):
        sub = 2**ii
        offset = sub * sub
        dim = 2 ** (ii + 1)

        mat_a = np.zeros((dim, dim), dtype=np.int32)
        mat_a[:sub, :sub] = rules[("D", ii)]
        mat_a[:sub, sub:] = rules[("A", ii)] + offset
        mat_a[sub:, sub:] = rules[("A", ii)] + 2 * offset
        mat_a[sub:, :sub] = rules[("B", ii)] + 3 * offset

        mat_b = np.zeros((dim, dim), dtype=np.int32)
        mat_b[:sub, :sub] = rules[("B", ii)] + 2 * offset
        mat_b[:sub, sub:] = rules[("B", ii)] + 1 * offset
        mat_b[sub:, sub:] = rules[("C", ii)] + 0 * offset
        mat_b[sub:, :sub] = rules[("A", ii)] + 3 * offset

        mat_c = np.zeros((dim, dim), dtype=np.int32)
        mat_c[:sub, :sub] = rules[("C", ii)] + 2 * offset
        mat_c[:sub, sub:] = rules[("D", ii)] + 3 * offset
        mat_c[sub:, sub:] = rules[("B", ii)] + 0 * offset
        mat_c[sub:, :sub] = rules[("C", ii)] + 1 * offset

        mat_d = np.zeros((dim, dim), dtype=np.int32)
        mat_d[:sub, :sub] = rules[("A", ii)] + 0 * offset
        mat_d[:sub, sub:] = rules[("C", ii)] + 3 * offset
        mat_d[sub:, sub:] = rules[("D", ii)] + 2 * offset
        mat_d[sub:, :sub] = rules[("D", ii)] + 1 * offset

        rules[("A", ii + 1)] = mat_a
        rules[("B", ii + 1)] = mat_b
        rules[("C", ii + 1)] = mat_c
        rules[("D", ii + 1)] = mat_d

    return rules


# pylint: disable-next=too-many-branches
def print_curve_2d(ind_mat):
    """
    Print a 2d Hilbert curve specified by the 2d matrix with the indices.

    **Arguments**

    ind_mat : np.ndarray, 2d
        Contains the index of the 1d mapping at each site in the 2d grid.
    """
    lines = []
    for ii in range(ind_mat.shape[1] * 2):
        lines.append("*")

    nx = ind_mat.shape[0]
    ny = ind_mat.shape[1]

    for ii in range(nx):
        for jj in range(ny):
            top = (jj < ny - 1) and (abs(ind_mat[ii, jj] - ind_mat[ii, jj + 1]) == 1)
            down = (jj > 0) and (abs(ind_mat[ii, jj] - ind_mat[ii, jj - 1]) == 1)
            left = (ii > 0) and (abs(ind_mat[ii, jj] - ind_mat[ii - 1, jj]) == 1)
            right = (ii < nx - 1) and (abs(ind_mat[ii, jj] - ind_mat[ii + 1, jj]) == 1)

            if top and down:
                lines[2 * jj] = lines[2 * jj] + " | "
                lines[2 * jj + 1] = lines[2 * jj + 1] + " | "
            elif top and left:
                lines[2 * jj] = lines[2 * jj] + "_| "
                lines[2 * jj + 1] = lines[2 * jj + 1] + "   "
            elif top and right:
                lines[2 * jj] = lines[2 * jj] + " |_"
                lines[2 * jj + 1] = lines[2 * jj + 1] + "   "
            elif down and left:
                lines[2 * jj] = lines[2 * jj] + "_  "
                lines[2 * jj + 1] = lines[2 * jj + 1] + " | "
            elif down and right:
                lines[2 * jj] = lines[2 * jj] + "  _"
                lines[2 * jj + 1] = lines[2 * jj + 1] + " | "
            elif left and right:
                lines[2 * jj] = lines[2 * jj] + "___"
                lines[2 * jj + 1] = lines[2 * jj + 1] + "   "
            elif top:
                lines[2 * jj] = lines[2 * jj] + " | "
                lines[2 * jj + 1] = lines[2 * jj + 1] + "   "
            elif down:
                lines[2 * jj] = lines[2 * jj] + "   "
                lines[2 * jj + 1] = lines[2 * jj + 1] + " | "
            elif left:
                lines[2 * jj] = lines[2 * jj] + "_  "
                lines[2 * jj + 1] = lines[2 * jj + 1] + "   "
            elif right:
                lines[2 * jj] = lines[2 * jj] + "  _"
                lines[2 * jj + 1] = lines[2 * jj + 1] + "   "
            else:
                raise QTeaLeavesError("Case not printed.", top, down, left, right)

    for ii in range(ind_mat.shape[1] * 2):
        lines[ii] = lines[ii] + "*"

    print("*" * (3 * nx + 2))
    for jj in list(range(ny))[::-1]:
        print(lines[2 * jj])
        print(lines[2 * jj + 1])

    print("*" * (3 * nx + 2))

    return


# ------------------------------------------------------------------------------
#                                  3d Hilbert curves
# ------------------------------------------------------------------------------


def hilbert_curve_3d(nx, ny, nz):
    """
    Hilbert curve mapping 3d cube to a 1d system.

    **Arguments**

    nx : number of sites in the x-direction
    ny : number of sites in the y-direction
    nz : number of sites in the z-direction

    **Results**

    Returns the results of get_3d_box(), which creates a 1D tuple of
    the sites in 3D-coordinates ordered following the Hilbert curve.

    """
    if abs(np.log2(nx) - int(np.log2(nx))) > 1e-14:
        raise QTeaLeavesError("Lenght nx must be a power of 2.")
    if abs(np.log2(ny) - int(np.log2(ny))) > 1e-14:
        raise QTeaLeavesError("Lenght ny must be a power of 2.")
    if abs(np.log2(nz) - int(np.log2(nz))) > 1e-14:
        raise QTeaLeavesError("Lenght nz must be a power of 2.")

    # the code works with the exponents
    nx_log = int(math.log2(nx))
    ny_log = int(math.log2(ny))
    nz_log = int(math.log2(nz))

    return get_3d_box(nx_log, ny_log, nz_log)


# pylint: disable-next=too-many-statements, too-many-branches, too-many-locals
def get_3d_box(nx_log, ny_log, nz_log):
    """
    Calls the get_3d cube function to create the generic cuboid with sides
    length power of two.

    **Arguments**

    (nx_log, ny_log, nz_log): ints
        the power of two based on the box dimension in the three directions


     **Result**

    ind_list : tuple
        sites covered by the Hilbert Curve in correct order


    **Useful information**

    nmin : int
        the exponent for the biggest cube that, when repeated, creates the rest
        (from now on called 'basic cube')
    total : int
        total number of sites
    sites : int
        number of sites of the basic cube
    step : int
        change of direction based on the basic cube dimension

    (xs, ys, zs) : tuples
        temporary tuples of dimension 'sites'
    (coordx, coordy, coordz): tuples
        tuples that contain the coordinates covered
    (position_x, position_y, position_z): ints
        coordinates that keep track of the beginning and
        the end of every constructed basic cube

    (x_prior, x_current, x_post): ints
        x-coordinates based on the 2D Hilbert curve that
        keep track of the filling of the curve
    (z_prior, z_current, z_post): ints
        z-coordinates based on the 2D Hilbert curve that
        keep track of the filling of the curve
    """

    nmin = int(min(nx_log, ny_log, nz_log))
    total = int(pow(2, nx_log + ny_log + nz_log))
    sites = int(pow(8, nmin))
    step = int(pow(2, nmin) - 1)
    xs = [0] * sites
    ys = [0] * sites
    zs = [0] * sites
    coordx = []
    coordy = []
    coordz = []

    position_x = 0
    position_y = 0
    position_z = 0

    # For how the following is coded, we have some conditions that want that
    # ny is the smallest number. For that reason we switch the indexes in order
    # to follow this conditions, keep track of the switches naming them, run
    # the normal code and visualize the vectors of coordinates in the correct
    # order. The cases:
    #
    # a) nothing changed
    # b) ny and nx switch values
    # c) ny and nz switch values

    case = "a"
    if ny_log == nmin:
        pass
    elif ny_log != nmin:
        if nx_log == nmin:
            ny_log, nx_log = nx_log, ny_log
            case = "b"
        elif nz_log == nmin:
            ny_log, nz_log = nz_log, ny_log
            case = "c"

    if nx_log == ny_log == nz_log:
        pass
    elif nx_log - ny_log == 0:
        hilbert2d = np.zeros((int(pow(2, nz_log - ny_log)), 1), dtype=int)
        for jj in range(int(pow(2, nz_log - ny_log))):
            hilbert2d[jj][0] = jj
    elif nz_log - ny_log == 0:
        hilbert2d = np.zeros((1, int(pow(2, nx_log - ny_log))), dtype=int)
        for jj in range(int(pow(2, nx_log - ny_log))):
            hilbert2d[0][jj] = jj
    else:
        hilbert2d = hilbert_curve_2d(
            int(pow(2, nx_log - ny_log)), int(pow(2, nz_log - ny_log))
        )

    if ny_log == nx_log and nx_log == nz_log:
        # this is the cube case
        position_x, position_y, position_z, xs, ys, zs = get_3d(
            pow(2, nmin),
            position_x,
            position_y,
            position_z,
            1,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            1,
            xs,
            ys,
            zs,
            0,
            sites,
        )
        coordx = coordx + xs
        coordy = coordy + ys
        coordz = coordz + zs

    else:
        x_current = np.where(hilbert2d == 0)[1]

        z_current = np.where(hilbert2d == 0)[0]

        x_post = np.where(hilbert2d == 1)[1]

        z_post = np.where(hilbert2d == 1)[0]

        if x_post == x_current + 1:
            position_x, position_y, position_z, xs, ys, zs = get_3d(
                pow(2, nmin),
                position_x,
                position_y,
                position_z,
                0,
                1,
                0,
                0,
                0,
                1,
                1,
                0,
                0,
                xs,
                ys,
                zs,
                0,
                sites,
            )

            coordx, coordy, coordz = add_coordinates(coordx, coordy, coordz, xs, ys, zs)

        elif z_post == z_current + 1:
            position_x, position_y, position_z, xs, ys, zs = get_3d(
                pow(2, nmin),
                position_x,
                position_y,
                position_z,
                1,
                0,
                0,
                0,
                1,
                0,
                0,
                0,
                1,
                xs,
                ys,
                zs,
                0,
                sites,
            )

            coordx, coordy, coordz = add_coordinates(coordx, coordy, coordz, xs, ys, zs)

        for ii in range(
            1, int(pow(2, (nx_log - ny_log)) * pow(2, (nz_log - ny_log)) - 1)
        ):
            x_prior = np.where(hilbert2d == ii - 1)[1]

            z_prior = np.where(hilbert2d == ii - 1)[0]

            x_current = np.where(hilbert2d == ii)[1]

            z_current = np.where(hilbert2d == ii)[0]

            x_post = np.where(hilbert2d == ii + 1)[1]

            z_post = np.where(hilbert2d == ii + 1)[0]

            if x_post == x_current + 1:
                if z_prior == z_current + 1:
                    position_z = position_z - step - 1

                    position_x = position_x - step

                    position_x, position_y, position_z, xs, ys, zs = get_3d(
                        pow(2, nmin),
                        position_x,
                        position_y,
                        position_z,
                        -1,
                        0,
                        0,
                        0,
                        1,
                        0,
                        0,
                        0,
                        -1,
                        xs,
                        ys,
                        zs,
                        0,
                        sites,
                    )

                    coordx, coordy, coordz = add_coordinates(
                        coordx, coordy, coordz, xs, ys, zs
                    )

                elif (z_prior == z_current - 1) or (x_prior == x_current - 1):
                    if z_prior == z_current - 1:
                        position_z = position_z + 1

                    elif x_prior == x_current - 1:
                        position_x = position_x + 1

                    position_x, position_y, position_z, xs, ys, zs = get_3d(
                        pow(2, nmin),
                        position_x,
                        position_y,
                        position_z,
                        0,
                        1,
                        0,
                        0,
                        0,
                        1,
                        1,
                        0,
                        0,
                        xs,
                        ys,
                        zs,
                        0,
                        sites,
                    )

                    coordx, coordy, coordz = add_coordinates(
                        coordx, coordy, coordz, xs, ys, zs
                    )

            elif x_post == x_current - 1:
                if z_prior == z_current - 1:
                    position_z = position_z + 1

                    position_x, position_y, position_z, xs, ys, zs = get_3d(
                        pow(2, nmin),
                        position_x,
                        position_y,
                        position_z,
                        1,
                        0,
                        0,
                        0,
                        1,
                        0,
                        0,
                        0,
                        1,
                        xs,
                        ys,
                        zs,
                        0,
                        sites,
                    )

                    coordx, coordy, coordz = add_coordinates(
                        coordx, coordy, coordz, xs, ys, zs
                    )

                elif (z_prior == z_current + 1) or (x_prior == x_current + 1):
                    if z_prior == z_current + 1:
                        position_z = position_z - step - 1

                        position_x = position_x - step

                    elif x_prior == x_current + 1:
                        position_x = position_x - step - 1

                        position_z = position_z - step

                    position_x, position_y, position_z, xs, ys, zs = get_3d(
                        pow(2, nmin),
                        position_x,
                        position_y,
                        position_z,
                        0,
                        1,
                        0,
                        0,
                        0,
                        -1,
                        -1,
                        0,
                        0,
                        xs,
                        ys,
                        zs,
                        0,
                        sites,
                    )

                    coordx, coordy, coordz = add_coordinates(
                        coordx, coordy, coordz, xs, ys, zs
                    )

            elif z_post == z_current + 1:
                if x_prior == x_current + 1:
                    position_z = position_z - step

                    position_x = position_x - step - 1

                    position_x, position_y, position_z, xs, ys, zs = get_3d(
                        pow(2, nmin),
                        position_x,
                        position_y,
                        position_z,
                        0,
                        1,
                        0,
                        0,
                        0,
                        -1,
                        -1,
                        0,
                        0,
                        xs,
                        ys,
                        zs,
                        0,
                        sites,
                    )

                    coordx, coordy, coordz = add_coordinates(
                        coordx, coordy, coordz, xs, ys, zs
                    )

                elif (z_prior == z_current - 1) or (x_prior == x_current - 1):
                    if z_prior == z_current - 1:
                        position_z = position_z + 1

                    elif x_prior == x_current - 1:
                        position_x = position_x + 1

                    position_x, position_y, position_z, xs, ys, zs = get_3d(
                        pow(2, nmin),
                        position_x,
                        position_y,
                        position_z,
                        1,
                        0,
                        0,
                        0,
                        1,
                        0,
                        0,
                        0,
                        1,
                        xs,
                        ys,
                        zs,
                        0,
                        sites,
                    )

                    coordx, coordy, coordz = add_coordinates(
                        coordx, coordy, coordz, xs, ys, zs
                    )

            elif z_post == z_current - 1:
                if x_prior == x_current - 1:
                    position_x = position_x + 1

                    position_x, position_y, position_z, xs, ys, zs = get_3d(
                        pow(2, nmin),
                        position_x,
                        position_y,
                        position_z,
                        0,
                        1,
                        0,
                        0,
                        0,
                        1,
                        1,
                        0,
                        0,
                        xs,
                        ys,
                        zs,
                        0,
                        sites,
                    )

                    coordx, coordy, coordz = add_coordinates(
                        coordx, coordy, coordz, xs, ys, zs
                    )

                elif (z_prior == z_current + 1) or (x_prior == x_current + 1):
                    if z_prior == z_current + 1:
                        position_z = position_z - step - 1

                        position_x = position_x - step

                    elif x_prior == x_current + 1:
                        position_x = position_x - step - 1

                        position_z = position_z - step

                    position_x, position_y, position_z, xs, ys, zs = get_3d(
                        pow(2, nmin),
                        position_x,
                        position_y,
                        position_z,
                        -1,
                        0,
                        0,
                        0,
                        1,
                        0,
                        0,
                        0,
                        -1,
                        xs,
                        ys,
                        zs,
                        0,
                        sites,
                    )

                    coordx, coordy, coordz = add_coordinates(
                        coordx, coordy, coordz, xs, ys, zs
                    )

        reference_value = pow(2, (nx_log - ny_log)) * pow(2, (nz_log - ny_log))
        x_prior = np.where(hilbert2d == int(reference_value - 2))[1]
        z_prior = np.where(hilbert2d == int(reference_value - 2))[0]
        x_current = np.where(hilbert2d == int(reference_value) - 1)[1]
        z_current = np.where(hilbert2d == int(reference_value) - 1)[0]

        if x_prior == x_current + 1:
            position_x = position_x - step - 1

            position_z = position_z - step

            position_x, position_y, position_z, xs, ys, zs = get_3d(
                pow(2, nmin),
                position_x,
                position_y,
                position_z,
                0,
                1,
                0,
                0,
                0,
                -1,
                -1,
                0,
                0,
                xs,
                ys,
                zs,
                0,
                sites,
            )

            coordx, coordy, coordz = add_coordinates(coordx, coordy, coordz, xs, ys, zs)

        elif z_prior == z_current - 1:
            position_z = position_z + 1

            position_x, position_y, position_z, xs, ys, zs = get_3d(
                pow(2, nmin),
                position_x,
                position_y,
                position_z,
                1,
                0,
                0,
                0,
                1,
                0,
                0,
                0,
                1,
                xs,
                ys,
                zs,
                0,
                sites,
            )

            coordx, coordy, coordz = add_coordinates(coordx, coordy, coordz, xs, ys, zs)

        elif x_prior == x_current - 1:
            position_x = position_x + 1

            position_x, position_y, position_z, xs, ys, zs = get_3d(
                pow(2, nmin),
                position_x,
                position_y,
                position_z,
                0,
                1,
                0,
                0,
                0,
                1,
                1,
                0,
                0,
                xs,
                ys,
                zs,
                0,
                sites,
            )

            coordx, coordy, coordz = add_coordinates(coordx, coordy, coordz, xs, ys, zs)

        elif z_prior == z_current + 1:
            position_z = position_z - step - 1

            position_x = position_x - step

            position_x, position_y, position_z, xs, ys, zs = get_3d(
                pow(2, nmin),
                position_x,
                position_y,
                position_z,
                -1,
                0,
                0,
                0,
                1,
                0,
                0,
                0,
                -1,
                xs,
                ys,
                zs,
                0,
                sites,
            )

            coordx, coordy, coordz = add_coordinates(coordx, coordy, coordz, xs, ys, zs)

    ind_list = []
    if (nx_log != ny_log) and (ny_log != nz_log) and (nx_log != nz_log):
        coordx, coordz = coordz, coordx
    if case == "a":
        for jj in range(total):
            ind_list.append((coordx[jj], coordy[jj], coordz[jj]))
    if case == "b":
        for jj in range(total):
            ind_list.append((coordy[jj], coordx[jj], coordz[jj]))
        ny_log, nx_log = nx_log, ny_log
    if case == "c":
        for jj in range(total):
            ind_list.append((coordx[jj], coordz[jj], coordy[jj]))
        ny_log, nz_log = nz_log, ny_log
    return ind_list


# pylint: disable-next=too-many-locals, too-many-arguments
def get_3d(
    dim,
    pos_x,
    pos_y,
    pos_z,
    dx,
    dy,
    dz,
    dx2,
    dy2,
    dz2,
    dx3,
    dy3,
    dz3,
    xs,
    ys,
    zs,
    track,
    sites,
):
    """
    Function that creates a hilbert-curve covered cube.

    **Arguments**

    dim: int
        number of sites of the side

    (pos_x, pos_y, pos_z): ints
        coordinates

    (dx, dy, dz): ints
        direction of the first vector of the cube
    (dx2, dy2, dz2): ints
        direction of the second vector of the cube
    (dx3, dy3, dz3): ints
        direction of the third vector of the cube

    (xs, ys, zs): tuples
        the arrays that will be returned filled with the coordinates in sequence

    track: int
        keeps track of the position of the arrays, needs to be updated in the
        various recursive calls (reason why it is returned)

    sites: int
        number of total sites of the cube, needed in the last return condition

    **Result**

    xs[track-1], ys[track-1], zs[track-1] : int
        the coordinates of the last point covered

    xs, ys, zs : tuples
        the coordinates of the base cube wanted
    """

    if dim == 1:
        xs[track] = pos_x
        ys[track] = pos_y
        zs[track] = pos_z
        track = track + 1
        return track

    dim = dim // 2
    if dx < 0:
        pos_x -= dim * dx
    if dy < 0:
        pos_y -= dim * dy
    if dz < 0:
        pos_z -= dim * dz
    if dx2 < 0:
        pos_x -= dim * dx2
    if dy2 < 0:
        pos_y -= dim * dy2
    if dz2 < 0:
        pos_z -= dim * dz2
    if dx3 < 0:
        pos_x -= dim * dx3
    if dy3 < 0:
        pos_y -= dim * dy3
    if dz3 < 0:
        pos_z -= dim * dz3
    # pylint: disable-next=arguments-out-of-order
    track = get_3d(
        dim,
        pos_x,
        pos_y,
        pos_z,
        dx2,
        dy2,
        dz2,
        dx3,
        dy3,
        dz3,
        dx,
        dy,
        dz,
        xs,
        ys,
        zs,
        track,
        sites,
    )
    track = get_3d(
        dim,
        pos_x + dim * dx,
        pos_y + dim * dy,
        pos_z + dim * dz,
        dx3,
        dy3,
        dz3,
        dx,
        dy,
        dz,
        dx2,
        dy2,
        dz2,
        xs,
        ys,
        zs,
        track,
        sites,
    )
    track = get_3d(
        dim,
        pos_x + dim * dx + dim * dx2,
        pos_y + dim * dy + dim * dy2,
        pos_z + dim * dz + dim * dz2,
        dx3,
        dy3,
        dz3,
        dx,
        dy,
        dz,
        dx2,
        dy2,
        dz2,
        xs,
        ys,
        zs,
        track,
        sites,
    )
    track = get_3d(
        dim,
        pos_x + dim * dx2,
        pos_y + dim * dy2,
        pos_z + dim * dz2,
        -dx,
        -dy,
        -dz,
        -dx2,
        -dy2,
        -dz2,
        dx3,
        dy3,
        dz3,
        xs,
        ys,
        zs,
        track,
        sites,
    )
    track = get_3d(
        dim,
        pos_x + dim * dx2 + dim * dx3,
        pos_y + dim * dy2 + dim * dy3,
        pos_z + dim * dz2 + dim * dz3,
        -dx,
        -dy,
        -dz,
        -dx2,
        -dy2,
        -dz2,
        dx3,
        dy3,
        dz3,
        xs,
        ys,
        zs,
        track,
        sites,
    )
    track = get_3d(
        dim,
        pos_x + dim * dx + dim * dx2 + dim * dx3,
        pos_y + dim * dy + dim * dy2 + dim * dy3,
        pos_z + dim * dz + dim * dz2 + dim * dz3,
        -dx3,
        -dy3,
        -dz3,
        dx,
        dy,
        dz,
        -dx2,
        -dy2,
        -dz2,
        xs,
        ys,
        zs,
        track,
        sites,
    )
    track = get_3d(
        dim,
        pos_x + dim * dx + dim * dx3,
        pos_y + dim * dy + dim * dy3,
        pos_z + dim * dz + dim * dz3,
        -dx3,
        -dy3,
        -dz3,
        dx,
        dy,
        dz,
        -dx2,
        -dy2,
        -dz2,
        xs,
        ys,
        zs,
        track,
        sites,
    )
    track = get_3d(
        dim,
        pos_x + dim * dx3,
        pos_y + dim * dy3,
        pos_z + dim * dz3,
        dx2,
        dy2,
        dz2,
        -dx3,
        -dy3,
        -dz3,
        -dx,
        -dy,
        -dz,
        xs,
        ys,
        zs,
        track,
        sites,
    )

    if track == sites and dim == 1:
        # here the returns are different because this if condition is the
        # last thing this function does
        return xs[track - 1], ys[track - 1], zs[track - 1], xs, ys, zs
    return track


# pylint: disable-next=too-many-arguments
def add_coordinates(coordx, coordy, coordz, xs, ys, zs):
    """
    Addition of two sets of x-y-z variables.

    **Arguments**

    coordx : int
        Coordinate in x for the 1st set of coordinates

    coordy : int
        Coordinate in y for the 1st set of coordinates

    coordz : int
        Coordinate in z for the 1st set of coordinates

    xs : int
        Coordinate in x for the 2nd set of coordinates

    ys : int
        Coordinate in y for the 2nd set of coordinates

    zs : int
        Coordinate in z for the 2nd set of coordinates

    **Results**

    coordx : int
        Updated coordinate after addition in x

    coordy : int
        Updated coordinate after addition in y

    coordz : int
        Updated coordinate after addition in z
    """
    coordx = coordx + xs
    coordy = coordy + ys
    coordz = coordz + zs
    return coordx, coordy, coordz


# ------------------------------------------------------------------------------
#                                  Utility functions
# ------------------------------------------------------------------------------


# pylint: disable-next=redefined-outer-name
def main(*args):
    """
    Main function which will print a graph for 2d systems and the
    numpy array for 2d and 3d systems.
    """

    if len(args) == 2:
        hilbert_curve = hilbert_curve_2d(*args)
        print_curve_2d(hilbert_curve)
    elif len(args) == 3:
        hilbert_curve = hilbert_curve_3d(*args)
    else:
        raise QTeaLeavesError("Number of arguments not valid.", args)

    print("Hilbert curve matrix")
    print(hilbert_curve)

    return


if __name__ == "__main__":
    args = list(map(int, sys.argv[1:]))
    main(*args)
