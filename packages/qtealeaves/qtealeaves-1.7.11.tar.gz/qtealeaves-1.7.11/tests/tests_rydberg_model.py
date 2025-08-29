# This code is part of qtealeaves.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import unittest

import qtealeaves.modeling as modeling


class TestsRydbergModel(unittest.TestCase):
    def test_term_count_case1(self):
        """
        Checks that the number of term is correct. One direction.
        """
        model = modeling.QuantumModel(3, 4)
        model += modeling.TwoBodyTerm3D(
            ["sx", "id"], [1, 0, 0], has_obc=False, isotropy_xyz=False
        )

        counter = 0
        for _ in model.hterms[0].get_entries({}):
            counter += 1

        self.assertEqual(counter, 1)

    def test_term_count_case2(self):
        """
        Checks that the number of term is correct. Along one axis.
        """
        model = modeling.QuantumModel(3, 4)
        model += modeling.TwoBodyTerm3D(["sx", "sx"], [1, 0, 0])

        counter = 0
        for _ in model.hterms[0].get_entries({}):
            counter += 1

        self.assertEqual(counter, 3)

    def test_term_count_case3(self):
        """
        Checks that the number of term is correct. Diagonal
        in xy, yz, xz plane.
        """
        model = modeling.QuantumModel(3, 4)
        model += modeling.TwoBodyTerm3D(["sx", "sx"], [1, 1, 0])

        counter = 0
        for _ in model.hterms[0].get_entries({}):
            counter += 1

        self.assertEqual(counter, 6)

    def test_term_count_case4(self):
        """
        Checks that the number of term is correct. Diagonal in the cube.
        """
        model = modeling.QuantumModel(3, 4)
        model += modeling.TwoBodyTerm3D(["sx", "sx"], [1, 1, 1])

        counter = 0
        for _ in model.hterms[0].get_entries({}):
            counter += 1

        self.assertEqual(counter, 4)

    def test_term_count_case5(self):
        """
        Checks that the number of term is correct. Along one axis
        with complex conjugate.
        """
        model = modeling.QuantumModel(3, 4)
        model += modeling.TwoBodyTerm3D(["s+", "s-"], [1, 0, 0], add_complex_conjg=True)

        counter = 0
        for _ in model.hterms[0].get_entries({}):
            counter += 1

        self.assertEqual(counter, 6)
