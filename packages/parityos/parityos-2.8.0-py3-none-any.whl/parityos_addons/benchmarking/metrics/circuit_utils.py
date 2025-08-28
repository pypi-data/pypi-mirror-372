"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2024.
All rights reserved.
"""

from parityos.base import Circuit, Gate


def circuit_is_in_parallelized_format(circuit: Circuit):
    """
    Checks whether each element of the circuit on its own can be implemented
    in parallel, either because it is an individual gate or because it is
    a sequence of gates acting on distinct qubits.

    :param circuit: Circuit instance
    """
    return all(
        isinstance(circuit_element, Gate)
        or circuit_can_be_applied_in_parallel(circuit_element)
        for circuit_element in circuit
    )


def circuit_can_be_applied_in_parallel(circuit: Circuit):
    """
    Circuit can be applied parallely if all the qubits
    appear only in one gate

    :param circuit: Circuit instance
    """
    gates = circuit.generate_flat_gate_sequence()
    qubits = [qubit for gate in gates for qubit in gate.qubits]
    return len(set(qubits)) == len(qubits)
