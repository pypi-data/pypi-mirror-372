[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

qtealeaves
==========

The `qtealeaves` library of Quantum TEA contains tensor network representation as
python classes, e.g., MPS, TTN, LPTN, and TTO. `qtealeaves` is the API for building
quantum models in Quantum TEA and has for example a single-tensor update ground state
search for TTNs. Moreover, `qtealeaves` is backbone for running quantum circuits via
Quantum matcha TEA and the frontend for the fortran backend running Quantum Green TEA,
i.e., solving the Schrödinger equation.


Documentation
=============

[Here](https://quantum_tea_leaves.baltig-pages.infn.it/py_api_quantum_tea_leaves/)
is the documentation. The documentation can also be built locally via sphinx.
Building the documentation requires `sphinx`, `sphinx-gallery`, and `sphinx_rtd_theme`.


License
=======

The project ``qtealeaves`` is hosted at the repository
``https://baltig.infn.it/quantum_tea_leaves/py_api_quantum_tea_leaves.git``,
and is licensed under the following license:

[Apache License 2.0](LICENSE)

The license applies to the files of this project as indicated
in the header of each file, but not its dependencies.


Installation
============

Independent of the use-case, you have to install the dependencies. Then,
there are the options using it as a stand-alone package, within [quantum
matcha TEA](https://baltig.infn.it/quantum_matcha_tea), or for quantum green TEA.

Local installation via pip
--------------------------

The package is available via PyPi and `pip install qtealeaves`.
After cloning the repository, an local installation via pip is
also possible via `pip install .`.

Dependencies
------------

The python dependencies can be found in the [``requirements.txt``](requirements.txt)
and are required independently of the following use-cases.

The `qtealeaves` package comes with the abstract definition of the tensor
required for our tensor networks as well as with a dense tensor based on
numpy and cupy. This tensor allows one to run simulations without symmetry
on CPU and GPU. Other tensor for symmetries or using pytorch instead of
numpy/cupy will become available in the future via Quantum Red TEA (`qredtea`).

Stand-alone package
-------------------

If you are looking to explore small exact diagonalization examples,
want to run a single-tensor update ground state search with TTNs,
or have TN-states on files to be post-processed, you are ready to
go.

qmatchatea simulations
----------------------

Quantum circuit simulations via `qmatchatea` require both `qredtea` and `qtealeaves`
as a dependency. Follow the instructions contained in the `qmatchatea` repository.
