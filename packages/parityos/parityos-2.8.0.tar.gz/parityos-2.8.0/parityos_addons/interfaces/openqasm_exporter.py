"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2023-2024.
All rights reserved.

Tools to export ParityOS circuits to OpenQASM.
"""

from collections.abc import Iterable, Mapping
import re

from parityos.base.circuit import CircuitElement
from parityos.base.gates import (
    CCNOT,
    # CCZ,
    CH,
    CNOT,
    # ConditionalGateMixin,
    # ConditionalRx,
    # ConditionalX,
    # ConditionalZ,
    # CP,
    # CRx,
    # CRy,
    CRz,
    CY,
    CZ,
    Gate,
    H,
    # ISwap,
    # MeasureZ,
    # MultiControlMixin,
    # MultiControlledH,
    # MultiControlledRx,
    # MultiControlledRy,
    # MultiControlledRz,
    RMixin,
    Rx,
    # Rxx,
    Ry,
    # Ryy,
    Rz,
    # Rzz,
    Swap,
    # SX,
    X,
    Y,
    Z,
)
from parityos.base.qubits import Qubit


GATE_MAP: dict[type[Gate], str] = {
    CCNOT: "ccx",
    # CCZ: NotImplemented,
    CH: "ch",
    CNOT: "CX",
    # In OpenQASM 2, "CX" is a built-in statement, "cx" is an alias from "qelib1.inc".
    # In OpenQASM 3, both "CX" and "cx" are defined in the standard gates library "stdgates.inc".
    # ConditionalRx: NotImplemented,
    # ConditionalX: NotImplemented,
    # ConditionalZ: NotImplemented,
    # CP: NotImplemented,
    # CRx: NotImplemented,
    # CRy: NotImplemented,
    CRz: "crz",
    CY: "cy",
    CZ: "cz",
    H: "h",
    # ISwap: NotImplemented,
    # MeasureZ: NotImplemented,
    # MultiControlMixin: NotImplemented,
    # MultiControlledH: NotImplemented,
    # MultiControlledRx: NotImplemented,
    # MultiControlledRy: NotImplemented,
    # MultiControlledRz: NotImplemented,
    Rx: "rx",
    # Rxx: NotImplemented,
    Ry: "ry",
    # Ryy: NotImplemented,
    Rz: "rz",
    # Rzz: NotImplemented,
    Swap: "swap",
    # SX: NotImplemented,
    X: "x",
    Y: "y",
    Z: "z",
}

# A qubit map should map the ParityOS Qubit instances onto valid OpenQASM string identifiers,
# either as individual identifiers "q1", "q2", ..., or indexed registers "qa[1]", "qb[2]", ...
QubitMap = Mapping[Qubit, str]  # type: TypeAlias


class OpenQasmExporter:
    """
    Tool to convert ParityOS circuits to OpenQASM quantum circuits.

    Instantiate the OpenQasmExporter with a qubit map.
    Then use the `to_openqasm` method to convert a ParityOS circuit to Qiskit quantum circuit.

    EXAMPLE:
        qubit_map = {Qubit(i): f"q[{i}]" for i in range(10)}
        openqasm_exporter = OpenQasmExporter(qubit_map, openqasm_version=3)
        openqasm_circuit = openqasm_exporter.to_openqasm(parityos_circuit)
    """

    def __init__(
        self,
        qubit_map: QubitMap = None,
        classical_qubit_map: QubitMap = None,
        name: str = "parityos_circuit",
        openqasm_version: str = "2.0",
    ):
        """
        Converts ParityOS circuits to OpenQASM circuits with the `to_openqasm` method.

        :param qubit_map: Optional. A mapping of the form {ParityOS_qubit: openqasm_qubit}.
            For parametrized circuits the openqasm qubit labels should be valid identifiers (e.g.,
            "qa", "qb", "ion1", "xmon2", ...). Unparametrized circuits can also handle indexed
            qubit registers where openqasm_qubit has the format "q[i]", with "q" the quantum
            register and "i" the integer index of the qubit in the qubit register.
            By default, all qubits are mapped onto a single quantum register "q" in lexicographic
            order of the qubit labels.
        :param classical_qubit_map: Optional. A mapping of the form {ParityOS_qubit: openqasm_bit},
            where openqasm_bit has the format "c[i]", with "c" the classical register and "i" the
            integer index of the bit in the classical register.
            At the end of the OpenQASM circuit, the qubits measurements are stored in these
            classical bits. Only the qubits listed in the classical qubit map will be measured.
            By default, all qubits are mapped onto a single classical register "c" in lexicographic
            order of the qubit labels and all qubits are measured at the end of the circuit.
            If the mapped circuit contains parameters, then this argument is not used.
        :param str name: Optional. The name to use for the OpenQASM composite gate when the circuit
                         contains unresolved parameters. Defaults to "parityos_circuit".
        :param str openqasm_version: Optional. The OpenQASM version number to use for the output
                                     Typical values are "2.0" and "3". Defaults to "2.0".
        """
        self.qubit_map = qubit_map
        self.classical_qubit_map = classical_qubit_map
        self.name = name
        self.openqasm_version = str(openqasm_version)
        # For OpenQASM 2, we normalize to version string to "2.0".
        main_version_number = self.openqasm_version.split(".")[0]
        if main_version_number == "2":
            self.openqasm_version = "2.0"

    def to_openqasm(
        self, circuit: CircuitElement, parameter_context: dict[str, float] = None, *args, **kwargs
    ) -> str:
        """
        Converts the circuit to an OpenQASM program. If the circuit has parameters, then the
        OpenQASM program will consist of an OpenQASM gate definition that contains the whole
        circuit. The resulting OpenQASM can then be included in an OpenQASM script that calls
        the gate with explicit values for the parameters.

        Otherwise, the result will be an OpenQASM program that implements the whole circuit
        and measures qubits at the end.

        Optional arguments like `qubit_map` will be passed on to the `to_openqasm_gate` method
        (for parametrized circuits) or the `to_openqasm_program` method (for circuits without
        parameters).

        :param circuit: a ParityOS circuit of quantum gates.
        :param parameter_context: Optional context argument that provides floats for each circuit
                                  parameter, this gives option for exporting parameterised circuits
                                  to OpenQASM
        :returns: an OpenQASM program in string format.
        """
        if parameter_context:
            circuit = circuit.remap(parameter_context)

        if circuit.parameters:
            return self.to_openqasm_gate(circuit, *args, **kwargs)
        else:
            return self.to_openqasm_program(circuit, *args, **kwargs)

    def to_openqasm_gate(
        self,
        circuit: CircuitElement,
        qubit_map: QubitMap = None,
        include_header: bool = True,
    ) -> str:
        """
        Converts the circuit to an OpenQASM gate, without header lines.

        :param circuit: A ParityOS circuit of quantum gates.
        :param bool include_header: Optional. Include the header lines in the OpenQASM string if
                                    True. Default is True
        :param qubit_map: Optional. A mapping of the form {ParityOS_qubit: openqasm_qubit}.
            The openqasm qubit labels should be valid identifiers. E.g., "qa", "qb", "ion1",
            "xmon2", ...). If not given, then the qubit map defaults to a series of valid
            OpenQASM identifiers derived from the ParityOS qubit labels.
        :returns: an OpenQASM program in string format.
        """
        # Take the qubit mapping either from the qubit_map attribute, if that was provided at
        # instantiation, or from the qubit list provided at instantiation, or construct it
        # from the qubit labels of the qubit instances in the circuit if no qubit map or qubit
        # list was provided at instantiation.
        qubit_map = qubit_map or {
            qubit: _qubit_to_openqasm(qubit) for qubit in sorted(circuit.qubits)
        }
        assert not any(
            "[" in qubit_string for qubit_string in qubit_map.values()
        ), "For parametrized circuits the qubit map should not contain indexed registers."
        parameters = ",".join(sorted(circuit.parameters))
        qubit_arguments = ",".join(sorted(qubit_map.values()))
        indented_statement_lines = [
            "  " + statement for statement in self._get_openqasm_statement_lines(circuit, qubit_map)
        ]
        header_lines = self._get_openqasm_header_lines() if include_header else []
        return "\n".join(
            [
                *header_lines,
                f"gate {self.name}({parameters}) {qubit_arguments} {{",
                *indented_statement_lines,
                "}",
                "",
            ]
        )

    def to_openqasm_program(self, circuit: CircuitElement, qubit_map: QubitMap = None) -> str:
        """
        Converts the circuit to a list of OpenQASM statements,
        including quantum register definitions.

        :param circuit: A ParityOS circuit of quantum gates.
        :param qubit_map: Optional. A mapping of the form {ParityOS_qubit: openqasm_qubit}.
            The openqasm qubit labels should be valid identifiers (e.g., "qa", "qb", "ion1",
            "xmon2", ...), or qubit registers where openqasm_qubit has the format "q[i]", with
            "q" the quantum register and "i" the integer index of the qubit in the qubit register.
            If not given, then the qubit map defaults to attribute set at construction, or a single
            quantum register "q" in lexicographic order of the ParityOS qubit labels if no qubit
            map was provided.
        :returns: A string listing the corresponding OpenQASM statements.
        """
        # Take the qubit mapping either from the qubit_map attribute, if that was provided at
        # instantiation, or use a generic register "q[:]" for all qubits.
        qubit_map = (
            qubit_map
            or self.qubit_map
            or {qubit: f"q[{i}]" for i, qubit in enumerate(sorted(circuit.qubits))}
        )
        # Declare the quantum registers with the correct sizes.
        qreg_sizes = _get_register_sizes(qubit_map.values())
        qreg_statements = [
            (f"qreg {qreg_name}[{size}];" if size else f"qreg {qreg_name};")
            for qreg_name, size in qreg_sizes.items()
        ]

        # Take the classical qubit mapping either from the classical_qubit_map attribute, if that
        # was provided at instantiation, or use a generic register "c[:]" for all bits.
        classical_qubit_map = self.classical_qubit_map or {
            qubit: f"c[{i}]" for i, qubit in enumerate(sorted(circuit.qubits))
        }
        # Declare the classical registers with the correct sizes.
        creg_sizes = _get_register_sizes(classical_qubit_map.values())
        creg_statements = [
            (f"creg {creg_name}[{creg_size}];" if creg_size else f"creg {creg_name};")
            for creg_name, creg_size in creg_sizes.items()
        ]

        if (len(qreg_sizes) == len(creg_sizes) == 1) and (
            set(classical_qubit_map) == set(qubit_map)
        ):
            # There is a single classical register that measures all qubits, so we can write
            # the measurement statement as a single line.
            # Zipping dictionaries of length 1 generates a single pair of keys.
            measurement_statements = [
                f"measure {qreg} -> {creg};" for qreg, creg in zip(qreg_sizes, creg_sizes)
            ]
        else:
            # There are several registers or not all qubits are measured, so we explicitly write
            # out the measurement of each bit to make sure that it is applied to the right qubit.
            measurement_statements = [
                f"measure {qubit_map[qubit]} -> {bit_name};"
                for qubit, bit_name in classical_qubit_map.items()
            ]

        return "\n".join(
            [
                *self._get_openqasm_header_lines(),
                *qreg_statements,
                *creg_statements,
                "",
                *self._get_openqasm_statement_lines(circuit, qubit_map),
                "",
                *measurement_statements,
                "",
            ]
        )

    def operation_to_openqasm(self, gate: Gate, qubit_map: QubitMap = None) -> str:
        """
        Converts a parityos gate operation to an OpenQASM unitary-operation statement.

        :param gate: A ParityOS gate instance.
        :param qubit_map: Optional. A mapping of the form {ParityOS_qubit: openqasm_qubit}.
                          If not given, then self.qubit_map is used instead.

        :return: A string with the OpenQASM statement in string format.
        """
        if qubit_map is None:
            qubit_map = self.qubit_map

        try:
            openqasm_gate = GATE_MAP[type(gate)]
        except KeyError as key_error:
            raise NotImplementedError(
                f"The openqasm translation of the {type(gate).__name__} "
                "gate has not yet been Implemented"
            ) from key_error

        if isinstance(gate, RMixin):
            angle = (
                gate.angle
                if gate.parameter_name is None
                else (
                    gate.parameter_name
                    if gate.angle == 1
                    else f"{gate.angle} * {gate.parameter_name}"
                )
            )
            openqasm_instruction = f"{openqasm_gate}({angle})"
        else:
            openqasm_instruction = openqasm_gate

        qubit_indices = ",".join(
            qubit_map[qubit] for qubit in gate.qubit_list if isinstance(qubit, Qubit)
        )
        return f"{openqasm_instruction} {qubit_indices};"

    def _get_openqasm_header_lines(self) -> list[str]:
        """Helper method that generates a list with the header lines of the OpenQASM program."""
        standard_library = "qelib1.inc" if self.openqasm_version == "2.0" else "stdgates.inc"
        return [
            f"OPENQASM {self.openqasm_version};",
            f'include "{standard_library}";',
            "// Circuit generated by ParityOS.",
            "",
            "",
        ]

    def _get_openqasm_statement_lines(
        self, circuit: CircuitElement, qubit_map: QubitMap = None
    ) -> list[str]:
        """
        Express the circuit as a list of OpenQASM unitary-operation statements.

        :param circuit: a ParityOS circuit of quantum gates.
        :param qubit_map: Optional. A mapping of the form {ParityOS_qubit: openqasm_qubit}.
                          If not given, then self.qubit_map is used instead.

        :returns: a list of OpenQASM statements in string format.
        """
        return [
            self.operation_to_openqasm(gate, qubit_map=qubit_map)
            for gate in circuit.generate_flat_gate_sequence()
        ]


def _qubit_to_openqasm(qubit: Qubit) -> str:
    """
    Convert the ParityOS qubit label into a valid OpenQASM qubit identifier.
    """
    label = qubit.label
    if isinstance(label, tuple):
        # Convert coordinates of the form (0, 1) into strings of the form "0_1"
        identifier = "_".join(str(coordinate) for coordinate in label)
    else:
        # Convert integers to strings
        identifier = str(label)

    if not identifier.isidentifier():
        # Make sure that the identifier only contains vali symbols a-z, A-z, _ or 0-9 and does
        # not start with a number.
        identifier = "".join((symbol if symbol.isalnum() else "_" for symbol in identifier))

    # Identifier starting with a number or an underscore are not a valid OpenQASM identifiers.
    # Note that the rules for OpenQASM identifiers are slightly different from Python:
    # in Python an identifier can start with an '_' symbol, in OpenQASM the first symbol must be a
    # lowercase letter.
    if not (identifier[:1].isalpha() and identifier[0].islower()):  # Slicing catches empty strings.
        # Make sure that the label starts with a lower case letter.
        identifier = f"q{identifier}"

    return identifier


# The following regular expression matches strings of the form f"{identifier}[{index}]" where
# `identifier` is a valid OpenQASM 2 identifier.
# Examples of matches with matching groups:
#    "q[1]": ("q", 1)
#    "qubit_register[12]": ("qubit_register", 12)
#    "qr1[0]": ("qr1", 0)
# Examples of non-matching strings: "q1", "qr(2)", "Q[3]", "2q[1]", "qubit-register[22]", "_q[2]"
IDENTIFIER_PATTERN = re.compile(r"^([a-z][a-zA-Z0-9_]*)\[([0-9]+)\]")
# Note that we can not use the `str.isidentifier` method because that would allow strings starting
# with an underscore.


def _get_register_sizes(identifiers: Iterable[str]) -> dict[str, int]:
    """
    Helper method that generates a dictionary with the names and sizes of the OpenQASM quantum
    or classical registers.

    :params identifiers: A collection of OpenQASM qubit or bit identifiers. These identifiers
                         should refer to individual qubits or bits, not to ranges in a register.

    :returns: A list of tuples where each tuple contains the name of a register and its size.
    """
    # Store the largest index for each qubit identifier, 0 for identifiers without index.
    register_sizes = dict()
    for identifier in identifiers:
        match = re.match(IDENTIFIER_PATTERN, identifier)
        if match:
            name, index_string = match.groups()
            index = int(index_string)
            if index >= register_sizes.get(name, 0):  # Always accepts new qreg names.
                register_sizes[name] = index + 1
        else:  # not match:
            register_sizes[identifier] = 0

    return register_sizes
