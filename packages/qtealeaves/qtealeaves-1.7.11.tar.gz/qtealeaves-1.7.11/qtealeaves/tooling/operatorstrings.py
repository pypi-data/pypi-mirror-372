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
The tooling to build a string representation for multiplying operators.
"""


def _op_string_mul(op_str, next_op, is_conj, is_transpose):
    """
    Build a string for an operator for a multiplication of two or more operators.
    The new string considers the conjugation and transposed.

    Arguments
    ---------

    op_str : str
        Current string so far. Multiply an operator from the right
        to this string. (String can be an empty string).

    next_op : str
        String representing the next operators to be multiplied
        from the right to `op_str`. String representation is without
        operations like conjugation or transposition.

    is_conj : bool
        Flag if next_op is transformed via a conjugation (True) or
        not (False).

    is_transpose : bool
        Flag if next_op is transformed via a transposition (True) or
        not (False).

    Returns
    -------

    op_str_new : str
        New string based on the current string `op_str` and the
        multiplication of `next_op` from the right with the
        defined transformations.

    Details
    -------

    We rely on the uniqueness of the string used for the operations, i.e.,
    we use

    * `*` to separate two operators being multiplied.
    * `^{T}` for an operator being transposed.
    * `^{C}` for an operator being complex conjugated.
    * `^{H}` for an operator being transposed and complex conjugated.

    If there are operators with these strings in the operator dictionary,
    the operators should have the same kind of transformations. Recall
    that combined operators use `.` for multiplication as well, but
    for a kronecker type of operation.
    """
    if is_conj and is_transpose:
        tmp = next_op + "^{H}"
    elif is_conj:
        tmp = next_op + "^{C}"
    elif is_transpose:
        tmp = next_op + "^{T}"
    else:
        tmp = next_op

    if len(op_str) == 0:
        return tmp

    return op_str + "*" + tmp
