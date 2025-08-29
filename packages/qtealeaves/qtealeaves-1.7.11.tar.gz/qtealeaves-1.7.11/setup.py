# This code is part of qtealeaves.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import importlib.util
import os
import os.path

import setuptools

# Parse the version file
spec = importlib.util.spec_from_file_location("qtealeaves", "./qtealeaves/version.py")
version_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(version_module)

# Get the readme file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define requirements
install_requires = [
    "numpy>=1.26.0",
    "scipy",
    "matplotlib",
    "mpmath",
    "joblib",
    "h5py",
]
# only for developers
# "sphinx",
# "sphinx-gallery",
# "sphinx_rtd_theme",
# "pre-commit",

setuptools.setup(
    name="qtealeaves",
    version=version_module.__version__,
    author=", ".join(
        [
            "Flavio Baccari",
            "Davide Bacilieri",
            "Marco Ballarin",
            "Francesco Pio Barone",
            "Francesco Campaioli",
            "Alberto Giuseppe Catalano",
            "Giovanni Cataldi",
            "Massimo Colombo",
            "Alberto Coppi",
            "Aurora Costantini",
            "Asmita Datta",
            "Andrea De Girolamo",
            "Daniel Jaschke",
            "Sven Benjamin Kožić",  # aka Sven Deanson
            "Giuseppe Magnifico",
            "Carmelo Mordini",
            "Guillermo Muñoz Menés",
            "Simone Notarnicola",
            "Alice Pagano",
            "Luka Pavesic",
            "Davide Rattacaso",
            "Nora Reinić",
            "Marco Rigobello",
            "Simone Scarlatella",
            "Ilaria Siloi",
            "Marco Tesoro",
            "Gianpaolo Torre",
            "Darvin Wanisch",
            "Lisa Zangrando",
        ]
    ),
    author_email="quantumtea@lists.infn.it",
    description="Quantum TEA's python tensor network library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://baltig.infn.it/quantum_tea_leaves/py_api_quantum_tea_leaves.git",
    project_urls={},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={
        "qtealeaves": "qtealeaves",
        "qtealeaves.tooling": "qtealeaves/tooling",
        "qtealeaves.solvers": "qtealeaves/solvers",
        "qtealeaves.tensors": "qtealeaves/tensors",
        "qtealeaves.emulator": "qtealeaves/emulator",
        "qtealeaves.observables": "qtealeaves/observables",
        "qtealeaves.modeling": "qtealeaves/modeling",
        "qtealeaves.models": "qtealeaves/models",
        "qtealeaves.mpos": "qtealeaves/abstracttns",
        "qtealeaves.mpos": "qtealeaves/mpos",
        "qtealeaves.operators": "qtealeaves/operators",
        "qtealeaves.convergence_parameters": "qtealeaves/convergence_parameters",
        "qtealeaves.simulation": "qtealeaves/simulation",
        "qtealeaves.optimization": "qtealeaves/optimization",
    },
    packages=[
        "qtealeaves",
        "qtealeaves.tooling",
        "qtealeaves.solvers",
        "qtealeaves.tensors",
        "qtealeaves.emulator",
        "qtealeaves.observables",
        "qtealeaves.modeling",
        "qtealeaves.models",
        "qtealeaves.mpos",
        "qtealeaves.abstracttns",
        "qtealeaves.operators",
        "qtealeaves.convergence_parameters",
        "qtealeaves.simulation",
        "qtealeaves.optimization",
    ],
    python_requires=">=3.11",
    install_requires=install_requires,
)
