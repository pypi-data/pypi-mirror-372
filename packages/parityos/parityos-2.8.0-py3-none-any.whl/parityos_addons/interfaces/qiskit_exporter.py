"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Tools to export ParityOS circuits to Qiskit.
"""

from collections.abc import Iterable, Mapping, Sequence

try:
    from qiskit import circuit as qisc
    from qiskit.circuit import classical as qisc_classical
    from qiskit.circuit.classical.expr.expr import Expr as qisc_classical_Expr
except ImportError:
    from parityos.base.exceptions import ParityOSImportError

    raise ParityOSImportError("The Qiskit exporter requires the installation of Qiskit")

from parityos.base.circuit import CircuitElement
from parityos.base.gates import (
    CCNOT,
    CCZ,
    CH,
    CNOT,
    ConditionalGateMixin,
    ConditionalRx,
    ConditionalX,
    ConditionalZ,
    CP,
    CRx,
    CRy,
    CRz,
    CY,
    CZ,
    Gate,
    H,
    ISwap,
    MeasureZ,
    MultiControlMixin,
    MultiControlledH,
    MultiControlledRx,
    MultiControlledRy,
    MultiControlledRz,
    RMixin,
    Rx,
    Rxx,
    Ry,
    Ryy,
    Rz,
    Rzz,
    Swap,
    SX,
    X,
    Y,
    Z,
)
from parityos.base.qubits import Qubit

GATE_MAP: dict[type[Gate], type[qisc.gate.Gate]] = {
    CCNOT: qisc.library.CCXGate,
    CCZ: qisc.library.CCZGate,
    CH: qisc.library.CHGate,
    CNOT: qisc.library.CXGate,
    CP: qisc.library.CPhaseGate,
    CRx: qisc.library.CRXGate,
    CRy: qisc.library.CRYGate,
    CRz: qisc.library.CRZGate,
    CY: qisc.library.CYGate,
    CZ: qisc.library.CZGate,
    ConditionalRx: qisc.library.RXGate,  # Will be remapped by qisc.IfElseOp
    ConditionalX: qisc.library.XGate,  # Will be remapped by qisc.IfElseOp
    ConditionalZ: qisc.library.ZGate,  # Will be remapped by qisc.IfElseOp
    H: qisc.library.HGate,
    ISwap: qisc.library.iSwapGate,
    MeasureZ: qisc.measure.Measure,
    MultiControlledH: qisc.library.HGate,  # Will be remapped by qisc.library.MCMT.
    MultiControlledRx: qisc.library.RXGate,  # Will be remapped by qisc.library.MCMT.
    MultiControlledRy: qisc.library.RYGate,  # Will be remapped by qisc.library.MCMT.
    MultiControlledRz: qisc.library.RZGate,  # Will be remapped by qisc.library.MCMT.
    Rx: qisc.library.RXGate,
    Rxx: qisc.library.RXXGate,
    Ry: qisc.library.RYGate,
    Ryy: qisc.library.RYYGate,
    Rz: qisc.library.RZGate,
    Rzz: qisc.library.RZZGate,
    SX: qisc.library.SXGate,
    Swap: qisc.library.SwapGate,
    X: qisc.library.XGate,
    Y: qisc.library.YGate,
    Z: qisc.library.ZGate,
}


class QiskitExporter:
    """
    Tool to convert ParityOS circuits to Qiskit quantum circuits.

    Instantiate the QiskitExporter with a qubit map and a parameter map.
    Then use the `to_qiskit` method to convert a ParityOS circuit to Qiskit quantum circuit.

    EXAMPLE:
        from qisc import Parameter
        parameter_map = {'theta': Parameter('$\\theta$'), 'gamma': Parameter('$\\gamma$')}
        qiskit_exporter = QiskitExporter(parameter_map)
        qiskit_circuit = qiskit_exporter.to_qiskit(parityos_circuit)
    """

    def __init__(
        self,
        parameter_map: Mapping[str, object] = None,
        qubit_map: Mapping[Qubit, int] = None,
        qubits: Iterable[Qubit] = None,
    ):
        """
        Converts the circuit to a Qiskit circuit.

        :param parameter_map: a mapping of the form {parameter_name: parameter_value}, where the
            parameter_name is a string that is used as a parameter_name in the ParityOS circuit,
            and parameter_value is a number like object (int, float, numpy float or a Qiskit
            Parameter object are all valid). Optional. If not given, then an empty dictionary is
            used instead.
        :param qubit_map: a mapping of the form {ParityOS_qubit: qubit_index}, where qubit_index is
            the integer index of the qubit in the Qiskit qubit register. Optional.
        :param qubits: an iterable of ParityOS qubits. This is used to generate a qubit_map where
            each qubit is mapped onto its index in the sequence. Optional.
            Either a `qubit_map` or a `qubits` iterable must be given.

        """
        self.parameter_map = {} if parameter_map is None else parameter_map
        if qubit_map:
            self.qubit_map = qubit_map
        elif qubits:
            # if the given qubits don't define an ordering we sort the qubits to make the qubit map
            # deterministic
            if not isinstance(qubits, Sequence):
                sorted_qubits = sorted(qubits)
            else:
                sorted_qubits = qubits
            self.qubit_map = {qubit: i for i, qubit in enumerate(sorted_qubits)}
        else:
            raise TypeError("QiskitExporter requires either a qubit_map or qubits argument")

    def to_qiskit(self, circuit: CircuitElement) -> qisc.QuantumCircuit:
        """
        Converts the circuit to a Qiskit quantum circuit.

        :param circuit: a ParityOS circuit of quantum gates.
        :return: a Qiskit QuantumCircuit object.
        """
        qiskit_circuit = qisc.QuantumCircuit(
            qisc.QuantumRegister(len(self.qubit_map)), qisc.ClassicalRegister(len(self.qubit_map))
        )

        def _qiskit_circuit_append(element: CircuitElement):
            """Recursive helper method for the to_qiskit method."""
            if isinstance(element, Gate):
                self.append_qiskit_gate(qiskit_circuit, element)
            else:
                for item in element:
                    _qiskit_circuit_append(item)

        _qiskit_circuit_append(circuit)
        return qiskit_circuit

    def append_qiskit_gate(self, qiskit_circuit: qisc, gate: Gate):
        """
        Creates a qiskit gate corresponding to the ParityOS Gate instance and appends it to the
        qiskit circuit.
        :param qiskit_circuit: the qiskit circuit to which we want to append the gate
        :param gate: the ParityOS Gate that is appended to the circuit
        """
        qiskit_gate_class = GATE_MAP[type(gate)]
        qubits = [qiskit_circuit.qubits[self.qubit_map[qubit]] for qubit in gate.qubit_list]
        # args specifying to which classical bits and qubits the instruction is attached to
        qubits_args = qubits
        classical_bits_args = None

        if isinstance(gate, MultiControlMixin):
            qiskit_gate = self._get_qiskit_instruction(gate, qiskit_gate_class)
            qiskit_instruction = qisc.library.MCMT(
                gate=qiskit_gate,
                num_ctrl_qubits=len(gate.control_qubits),
                num_target_qubits=len(gate.target_qubits),
            )
        elif isinstance(gate, MeasureZ):
            classical_bits_args = [
                qiskit_circuit.clbits[qiskit_circuit.qubits.index(qubit)] for qubit in qubits
            ]
            qiskit_instruction = self._get_qiskit_instruction(gate, qiskit_gate_class)
        elif isinstance(gate, ConditionalGateMixin):
            classical_bits_args = qiskit_circuit.clbits
            qubits_args = qiskit_circuit.qubits
            classical_control_registers = [
                classical_bits_args[self.qubit_map[qubit]] for qubit in gate.condition
            ]

            control_expression = self._get_parity_control_expression(classical_control_registers)
            parity_target_expression = qisc_classical.expr.Value(1, qisc_classical.types.Bool())
            condition = qisc_classical.expr.equal(control_expression, parity_target_expression)

            body = qisc.QuantumCircuit(qiskit_circuit.qregs[0], qiskit_circuit.cregs[0])
            body.append(self._get_qiskit_instruction(gate, qiskit_gate_class), qargs=qubits)

            qiskit_instruction = qisc.IfElseOp(condition=condition, true_body=body)

        else:
            qiskit_instruction = self._get_qiskit_instruction(gate, qiskit_gate_class)

        qiskit_circuit.append(qiskit_instruction, qargs=qubits_args, cargs=classical_bits_args)

    @staticmethod
    def _get_parity_control_expression(classical_bits: Sequence[qisc.Clbit]) -> qisc_classical_Expr:
        """
        Construct a Qiskit classical expression for the parity of a sequence of Qiskit classical
        bits.

        :param classical_bits: A sequence of Qiskit classical bits.

        :return: A Qiskit classical expression that encodes the parity of the classical bits.
        """
        if len(classical_bits) == 1:
            return qisc_classical.expr.Var(classical_bits[0], qisc_classical.types.Bool())

        classical_expression = qisc_classical.expr.bit_xor(classical_bits[0], classical_bits[1])
        for bit in classical_bits[2:]:
            classical_expression = qisc_classical.expr.bit_xor(classical_expression, bit)

        return classical_expression

    def _get_qiskit_instruction(self, gate: Gate, qiskit_gate_class: type) -> qisc.gate.Gate:
        """
        Instantiates the qiskit instruction for a gate using the associated qiskit class.

        :param gate: A ParityOS gate instance
        :param qiskit_gate_class: The qiskit gate class corresponding to the gate
        :return: A qiskit gate instance
        """
        if isinstance(gate, RMixin):
            qiskit_instruction = qiskit_gate_class(
                gate.angle
                if gate.parameter_name is None
                else gate.angle * self.parameter_map[gate.parameter_name]
            )
        else:
            qiskit_instruction = qiskit_gate_class()

        return qiskit_instruction
