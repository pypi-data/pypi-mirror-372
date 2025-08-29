# This code is part of qtealeaves.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import os
import os.path
import sys
import unittest
from io import StringIO

import pylint.lint


class TestPylint(unittest.TestCase):
    """
    Run pylint to check syntax in source files.

    **Details**

    We disable globally:

    * C0325: superfluous parenthesis
    * C0209: consider using fstring
    * C3001: Lambda expression assigned to a variable
    * W1514: unspecified encoding
    * R1711: useless returns (for allowing empty iterators with
      return-yield)
    * Skip Unused argument errors when args
    * Skip Unused argument errors when kargs
    """

    def setUp(self):
        """
        Provide the test setup.
        """
        good_names = "ii,jj,kk,ll,nn,mm"
        good_names += ",i1,i2,i3,n1,n2,n3,ix,iy,iz,jx,jy,jz"
        good_names += ",dx,dy,dz,dt"
        good_names += ",d1,d2,d3"
        good_names += ",fh,op,xp"
        good_names += ",nx,ny,x1,x2,x3,x4,y1,y2,y3,y4"
        self.pylint_args = {
            "good-names": good_names,
            "disable": "C0325,C0209,W1514,R1711,C3001",
        }

        # prepare switch of stdout
        self.stdout = sys.stdout

    def tearDown(self):
        sys.stdout = self.stdout

    def run_pylint(self, filename):
        """
        Run linter test with our unit test settings for one specific
        filename.
        """
        args = []

        for elem in self.pylint_args.keys():
            args += ["--" + elem + "=" + self.pylint_args[elem]]

        args += [filename]

        # Reset stdout and run tests
        sys.stdout = StringIO()
        pylint.lint.Run(args, exit=False)

        error_list = []
        for elem in sys.stdout.getvalue().split("\n"):
            tmp = elem.replace("\n", "")

            if len(tmp) == 0:
                continue
            if tmp.startswith("***"):
                continue
            if tmp.startswith("---"):
                continue
            if tmp.startswith("Your code"):
                continue
            if "Unused argument 'args'" in tmp:
                continue
            if "Unused argument 'kwargs'" in tmp:
                continue

            error_list.append(tmp)

        return error_list

    def test_folders_recursively(self):
        """
        Recursively run python linter test on all .py files of
        specified folders.
        """
        parent_folders = ["Examples", "qtealeaves"]
        skip_files = []
        error_list = []

        for elem in parent_folders:
            for root, dirnames, filenames in os.walk(elem):
                for filename in filenames:
                    if not filename.endswith(".py"):
                        continue

                    if filename in skip_files:
                        continue

                    target_file = os.path.join(root, filename)
                    error_list_ii = self.run_pylint(target_file)
                    error_list += error_list_ii

        self.assertEqual(len(error_list), 0, "\n".join(error_list))
