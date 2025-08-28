"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2023-2024.
All rights reserved.
"""

from parityos.base import Circuit
from parityos.base.circuit import CircuitElement
from parityos.base.gates import CNOT, Rzz

from parityos_addons.benchmarking.metrics.circuit_utils import (
    circuit_is_in_parallelized_format,
)


def circuit_depth(circuit: Circuit) -> int:
    """
    Calculates the circuit depth. Assumes that Circuit is a list of
    Circuits/Gates, which can be applied in parallel.

    :param circuit: Circuit instance
    :return: the circuit depth
    """
    if not circuit_is_in_parallelized_format(circuit):
        raise ValueError(
            "The given circuit is not in the parallelized format, which means"
            "one can't apply its individual elements (Circuit or Gate) in parallel."
        )

    return len(circuit)


def circuit_cnot_depth(circuit: Circuit) -> int:
    """
    Calculates the circuit CNOT depth. Assumes that Circuit is a list of
    Circuits/Gates, which can be applied in parallel. The circuit
    shouldn't contain other two qubit gates.

    :param circuit: Circuit instance
    :return: the circuit cnot depth
    """

    if not all(
        len(gate.qubits) == 1 or isinstance(gate, CNOT)
        for gate in circuit.generate_flat_gate_sequence()
    ):
        raise ValueError(
            "The circuit contains apart from CNOTs other multi qubit gates."
        )

    if not circuit_is_in_parallelized_format(circuit):
        raise ValueError(
            "The given circuit is not in the parallelized format, which means"
            "one can't apply its individual elements (Circuit or Gate) parallely."
        )

    return sum([has_cnot(element) for element in circuit])


def circuit_gate_count(circuit: Circuit) -> int:
    """
    :param circuit: Circuit instance
    :return: the gate count of the circuit
    """

    return len(list(circuit.generate_flat_gate_sequence()))


def circuit_cnot_count(circuit: Circuit) -> int:
    """
    :param circuit: Circuit instance
    :return: the cnot gate count of the circuit
    """

    return sum(
        [isinstance(gate, CNOT) for gate in circuit.generate_flat_gate_sequence()]
    )


def circuit_rzz_count(circuit: Circuit) -> int:
    """
    :param circuit: Circuit instance
    :return: the rzz gate count of the circuit
    """

    return sum(
        [isinstance(gate, Rzz) for gate in circuit.generate_flat_gate_sequence()]
    )


def circuit_two_body_gate_count(circuit: Circuit) -> int:
    """
    :param circuit: Circuit instance
    :return: the two body gate count of the circuit
    """

    return sum(
        [(len(gate.qubits) == 2) for gate in circuit.generate_flat_gate_sequence()]
    )


def circuit_qubit_count(circuit: CircuitElement) -> int:
    """
    :param circuit: Circuit instance
    :return: the qubit count of the circuit.
    """
    return len(circuit.qubits)


def has_cnot(circuit_element: CircuitElement):
    """
    Checks if the circuit element is a CNOT gate or is a Circuit that contains a CNOT gate.
    :param circuit_element: a Gate or Circuit instance
    :return: True if the circuit element has a CNOT gate
    """
    if isinstance(circuit_element, CNOT):
        return True
    elif isinstance(circuit_element, Circuit):
        gates = circuit_element.generate_flat_gate_sequence()
        return any(isinstance(gate, CNOT) for gate in gates)
    else:
        return False
