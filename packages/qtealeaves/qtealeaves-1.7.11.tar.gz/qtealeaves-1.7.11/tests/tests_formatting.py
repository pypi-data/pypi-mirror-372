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
from subprocess import PIPE, run


class TestFormatting(unittest.TestCase):
    folders = "qtealeaves", "Contrib", "tests"

    def check_ext_util(self, cmd_call):
        result = run(cmd_call, stderr=PIPE, text=True, encoding="utf-8", check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_black(self):
        self.check_ext_util(["black", "--check", *self.folders])

    def test_isort(self):
        self.check_ext_util(["isort", *self.folders, "--check"])
