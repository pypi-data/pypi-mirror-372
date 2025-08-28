"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Setup script
"""

from itertools import chain
import os
from setuptools import setup, find_namespace_packages


commit_tag = os.environ.get("CI_COMMIT_TAG", "")
if commit_tag.startswith("v"):
    version = commit_tag[1:]
else:
    job_id = os.environ.get("CI_JOB_ID", 0)
    version = f"0.0rc{job_id}+test"

# Here we specify the dependencies of optional packages in parityos_addons.
extras_require = {
    "cirq": ["cirq-core"],
    "qiskit": ["qiskit"],
    "pulser": ["pulser"],
    "spinz": ["sympy"],
    "benchmarking": ["pandas", "numpy"],
    "analog_computation": ["sympy"],
    "rydberg_layout": ["sympy", "numpy", "matplotlib"],
}
# The option [all] will install all optional dependencies.
extras_require["all"] = list(set(chain(*extras_require.values())))
extras_require["dev"] = [
    "black",
    "numpy",
    "pip-tools",
    "pytest",
    "qiskit-aer",
    *extras_require["all"],
]

setup(
    name="parityos",
    version=version,
    description="Python bindings to the ParityOS API",
    url="https://parityqc.com/",
    license_files=("License.txt",),
    packages=find_namespace_packages(exclude=["*.test*", "docs*"]),
    package_data={"parityos_addons.documentation.html": ["**/*"]},
    install_requires=["requests"],
    extras_require=extras_require,
    python_requires=">=3.9",
)
