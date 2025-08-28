"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2022.
All rights reserved.

Tools to export ParityOS results to other frameworks
"""

try:
    from .cirq_exporter import CirqExporter
except ImportError:
    # The cirq_exporter could not import cirq, probably because Cirq is not installed.
    CirqExporter = NotImplemented

try:
    from .qiskit_exporter import QiskitExporter
except ImportError:
    # The qiskit_exporter could not import qiskit, probably because Qiskit is not installed.
    QiskitExporter = NotImplemented
