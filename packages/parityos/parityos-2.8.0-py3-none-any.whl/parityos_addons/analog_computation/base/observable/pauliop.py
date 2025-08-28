"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2023 - 2025.
All rights reserved.
"""

from typing import Set, Mapping, Collection, Union

from parityos.base.gates import X, Y, Z, Gate
from parityos.base.qubits import Qubit
from parityos.base.utils import json_wrap, JSONType

from parityos_addons.analog_computation.base.exceptions import (
    ParityOSAnalogComputationException,
)


class PauliOp:
    """
    Representation of multi-qubit Pauli operators that consist of a tensor product of
    Pauli gates (X, Y, Z).
    """

    def __init__(self, pauli_gates: Collection[Union[X, Y, Z]] = frozenset()):
        """
        The case when pauli_gates is None corresponds to the Identity operator.
        Each Pauli gate should be applied to a unique qubit.
        """
        self.pauli_gates = frozenset(pauli_gates)

        if pauli_gates and len(pauli_gates) != len(self.qubits):
            raise ParityOSAnalogComputationException(
                "Pauli gates should have unique qubits."
            )

    @property
    def qubits(self) -> Set[Qubit]:
        """
        Set of Qubits which appear in the PauliOp.
        """
        return {gate.qubit_list[0] for gate in self.pauli_gates}

    def evaluate(self, configuration: Mapping[Qubit, int]) -> int:
        """
        Evaluates the expectation value of the PauliOp operator in specific Z eigenstates
        with eigenvalues +1 or -1 given by the configuration.

        :param configuration: a mapping of the qubits onto their Z eigenvalue +1 or -1.
        :return: the corresponding expectation value, which is either +1 or -1 or 0
        """
        if not all(isinstance(gate, Z) for gate in self.pauli_gates):
            return 0

        try:
            z_values = [configuration[gate.qubit_list[0]] for gate in self.pauli_gates]
        except KeyError:
            raise ParityOSAnalogComputationException(
                "Not all required Qubits are given in the "
                "configuration for PauliOp.evaluate()."
            )

        return +1 if z_values.count(-1) % 2 == 0 else -1

    def commutes_with(self, other):
        """
        Returns true if self commutes with other, otherwise false. Here, we are applying the rule
            "Two Pauli strings commute iff they do not commute on an even number of indices."

        :param other: another PauliOp
        :return: True or False, indicating whether self and other commute.
        """

        # Count the qubits that coincide in label, gate types on each qubit might differ
        n_qubits_in_common = len(self.qubits & other.qubits)
        # Counts the qubits that coincide in label and gate type
        n_gates_in_common = len(self.pauli_gates & other.pauli_gates)
        # Calculate the number of qubits that appear in both Pauli operators but with different gate
        # types.
        n_not_comm = n_qubits_in_common - n_gates_in_common

        return not n_not_comm % 2

    def to_json(self) -> JSONType:
        """
        Converts the PauliOp to json

        :return: the PauliOp in json format
        """
        return json_wrap(self.pauli_gates)

    @classmethod
    def from_json(cls, data: list) -> "PauliOp":
        """
        Initializes the PauliOp class from json

        :param data: PauliOp in json format
        :return: A PauliOp instance
        """
        return cls([Gate.from_json(gate_data) for gate_data in data])

    def __eq__(self, other) -> bool:
        return self.pauli_gates == other.pauli_gates

    def __repr__(self):
        pauli_gates = ", ".join(repr(gate) for gate in self.pauli_gates)
        return f"{self.__class__.__name__}({{{pauli_gates}}})"

    def __str__(self):
        return " * ".join(f"{pauli_gate}" for pauli_gate in self.pauli_gates)

    def __hash__(self):
        return hash(self.pauli_gates)

    def __len__(self):
        return len(self.pauli_gates)
