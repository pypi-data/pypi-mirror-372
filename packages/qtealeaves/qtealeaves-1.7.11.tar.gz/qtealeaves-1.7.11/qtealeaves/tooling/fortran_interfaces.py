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
The module for the fortran interfaces takes care of writing nml files
and tensors in the correct.
"""

from ast import literal_eval

import numpy as np

from .qtealeavesexceptions import QTeaLeavesError

__all__ = ["write_tensor", "read_tensor"]


def write_tensor(tensor, dest, cmplx=True, **kwargs):
    """
    Write a tensor stored in a numpy matrix to a file. Conversion
    to column major is taken care of here.

    **Arguments**

    tensor : np.ndarray
        Tensor to be written to the file.

    dest : str, or filehandle
        If string, file will be created or overwritten. If filehandle,
        then data will be written there.
    """
    if isinstance(dest, str):
        # pylint: disable-next=consider-using-with
        fh = open(dest, "w+")
    elif hasattr(dest, "write"):
        fh = dest
    else:
        raise ValueError(
            f"Argument `dest` {dest} not recognized to open file-like object."
        )

    # Number of links
    fh.write("%d\n" % (len(tensor.shape)))

    # Dimensions of links
    dimensions_links = " ".join(list(map(str, tensor.shape)))
    fh.write(dimensions_links + "\n")

    # Now we need to transpose
    tensor_colmajor = np.ravel(tensor, order="F")

    for elem in tensor_colmajor.flat:  # .flat precaution for numpy.matrix behaviour
        if cmplx:
            fh.write("(%30.15E, %30.15E)\n" % (np.real(elem), np.imag(elem)))
        else:
            fh.write("%30.15E\n" % (np.real(elem)))
            imag_part = np.imag(elem)
            if np.abs(imag_part) > 1e-14:
                raise QTeaLeavesError(
                    "Writing complex valued tensor as real valued tensor."
                )

    if isinstance(dest, str):
        fh.close()

    return


def read_tensor(file, cmplx=True, order="F"):
    """
    Read a tensor written in a file from fortran and store it in a numpy matrix. Conversion
    to row major is taken care of here if order='F'.
    author: mb

    Parameters
    ----------
    file: str, or filehandle
        If string, file will be opened. If filehandle, then data will be read from there.

    cmplx: bool, optional
        If True the tensor is complex. Otherwise is real. Default to True.

    order: str, optional
        If 'F' the tensor is transformed from column-major to row-major, if 'C'
        it is left as read.
    """
    if order not in ["F", "C"]:
        raise ValueError("Only fortran('F') or C 'C' order are available.")
    if isinstance(file, str):
        # pylint: disable-next=consider-using-with
        fh = open(file, "r")
    elif hasattr(file, "read"):
        fh = file
    else:
        raise TypeError(
            f"Input file has to be either string or filehandle, not {type(file)}."
        )

    # Number of links
    _ = int(fh.readline())
    # Dimensions of links
    dl = fh.readline().replace("\n", "")
    dl = dl.split(" ")
    dl = np.array(dl, dtype=int)

    # Define numpy array
    if cmplx:
        tens = np.zeros(np.prod(dl), dtype=np.complex128)
    else:
        tens = np.zeros(np.prod(dl))
    # Read array
    for ii in range(np.prod(dl)):
        if cmplx:
            elem = literal_eval(fh.readline().strip())
            tens[ii] = complex(elem[0], elem[1])
        else:
            elem = fh.readline()
            tens[ii] = np.double(elem[0])

    tensor_rowmajor = tens.reshape(dl, order=order)

    return tensor_rowmajor
