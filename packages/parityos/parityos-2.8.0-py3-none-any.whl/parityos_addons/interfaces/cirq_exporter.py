"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria


Copyright (c) 2020-2024.
All rights reserved.

Tools to export ParityOS circuits to Cirq.
"""

from collections.abc import Mapping
from math import pi
from typing import Union

from parityos.base.circuit import CircuitElement
from parityos.base.gates import (
    CCNOT,
    CCZ,
    # CH,
    CNOT,
    # ConditionalGateMixin,
    # ConditionalRx,
    # ConditionalX,
    # ConditionalZ,
    # CP,
    # CRx,
    # CRy,
    # CRz,
    # CY,
    CZ,
    Gate,
    H,
    ISwap,
    # MeasureZ,
    # MultiControlMixin,
    # MultiControlledH,
    # MultiControlledRx,
    # MultiControlledRy,
    # MultiControlledRz,
    RMixin,
    Rx,
    Rxx,
    Ry,
    Ryy,
    Rz,
    Rzz,
    Swap,
    # SX,
    X,
    Y,
    Z,
)
from parityos.base.exceptions import ParityOSImportError
from parityos.base.qubits import Qubit

try:
    import cirq
except ImportError:
    raise ParityOSImportError("The Cirq exporter requires the installation of Cirq.")


GATE_MAP: dict[type(Gate), cirq.Gate] = {
    # All keys must be subclasses of the Gate class.
    CCNOT: cirq.CCNOT,
    CCZ: cirq.CCZ,
    # CH: NotImplemented,
    CNOT: cirq.CNOT,
    # ConditionalGateMixin: NotImplemented,
    # ConditionalRx: NotImplemented,
    # ConditionalX: NotImplemented,
    # ConditionalZ: NotImplemented,
    # CP: NotImplemented,
    # CRx: NotImplemented,
    # CRy: NotImplemented,
    # CRz: NotImplemented,
    # CY: NotImplemented,
    CZ: cirq.CZ,
    H: cirq.H,
    ISwap: cirq.ISWAP,
    # MeasureZ: NotImplemented,
    # MultiControlMixin: NotImplemented,
    # MultiControlledH: NotImplemented,
    # MultiControlledRx: NotImplemented,
    # MultiControlledRy: NotImplemented,
    # MultiControlledRz: NotImplemented,
    Rx: cirq.XPowGate,  # We use _PowGate for consistency with Rzz: ZZPowGate
    Rxx: cirq.XXPowGate,  # cirq.Rzz does not exist.
    Ry: cirq.YPowGate,  # We use _PowGate for consistency with Rzz: ZZPowGate
    Ryy: cirq.YYPowGate,  # cirq.Rzz does not exist.
    Rz: cirq.ZPowGate,  # We use _PowGate for consistency with Rzz: ZZPowGate
    Rzz: cirq.ZZPowGate,  # cirq.Rzz does not exist.
    Swap: cirq.SWAP,
    # SX: NotImplemented,
    X: cirq.X,
    Y: cirq.Y,
    Z: cirq.Z,
}

CirqCircuitElement = Union[cirq.GateOperation, "CirqCircuitElement"]


class CirqExporter:
    """
    Tool to convert ParityOS circuits to Cirq circuits.

    Instantiate the CirqExporter with a qubit map and a parameter map.
    Then use the `to_cirq` method to convert ParityOS circuits to Cirq circuits.

    EXAMPLE:
        qubit_map = {Qubit(i): cirq.NamedQubit(str(i)) for i in range(10)}
        parameter_map = {'theta': sympy.Symbol('theta'), 'gamma': sympy.Symbol('gamma')}
        cirq_exporter = CirqExporter(qubit_map, parameter_map)
        cirq_circuit = cirq_exporter.to_cirq(parityos_circuit)
    """

    def __init__(
        self,
        parameter_map: Mapping[str, object] = None,
        qubit_map: Mapping[Qubit, cirq.NamedQubit] = None,
    ):
        """
        Converts the circuit to a cirq circuit.

        :param parameter_map: a mapping of the form {parameter_name: parameter_value}, where the
            parameter_name is a string that is used as a parameter_name in the ParityOS circuit,
            and parameter_value is a number like object (int, float, numpy float or a Sympy symbol
            are all valid). Optional.  If not given, then an empty dictionary is used instead.

        :param qubit_map: a mapping of the form {ParityOS_qubit: cirq_qubit}, where cirq_qubit is a
            Cirq NamedQubit instance. Optional. If not given, then ParityOS Qubits are automatically
            converted into cirq.NamedQubit instances with the same label.

        """
        self.parameter_map = {} if parameter_map is None else parameter_map
        self.qubit_map = qubit_map

    def to_cirq(self, circuit: CircuitElement) -> cirq.Circuit:
        """
        Converts the circuit to a Cirq circuit.

        :param circuit: a ParityOS circuit of quantum gates.
        :return: a Cirq circuit.
        """

        def _elements_to_cirq_gates(element: CircuitElement) -> CirqCircuitElement:
            """Recursive helper method for the to_cirq method."""
            return (
                self.gate_to_cirq(element)
                if isinstance(element, Gate)
                else [_elements_to_cirq_gates(item) for item in element]
            )

        return cirq.Circuit(_elements_to_cirq_gates(circuit))

    def gate_to_cirq(self, gate: Gate) -> cirq.GateOperation:
        """
        Converts a gate to a Cirq gate operation.

        :param gate: a ParityOS gate instance.
        :return: a Cirq gate operation.
        """
        cirq_operation = GATE_MAP[type(gate)]
        if isinstance(gate, RMixin):
            angle = (
                gate.angle
                if gate.parameter_name is None
                else gate.angle * self.parameter_map[gate.parameter_name]
            )
            cirq_operator = cirq_operation(exponent=angle / pi, global_shift=-0.5)
            # We use ZPowGate instead or rz, so we have to adjust the exponent by a factor pi
            # and the global phase with a global shift of -1/2.
            # See https://quantumai.google/reference/python/cirq/ZPowGate
        else:
            cirq_operator = cirq_operation

        parityos_qubits = (qubit for qubit in gate.make_args() if isinstance(qubit, Qubit))
        if self.qubit_map:
            cirq_qubits = (self.qubit_map[qubit] for qubit in parityos_qubits)
        else:
            cirq_qubits = (cirq.NamedQubit(str(qubit.label)) for qubit in parityos_qubits)

        return cirq_operator(*cirq_qubits)
