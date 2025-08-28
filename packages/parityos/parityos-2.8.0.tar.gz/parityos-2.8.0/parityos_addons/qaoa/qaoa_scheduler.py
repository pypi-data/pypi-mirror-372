"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Generates quantum circuits for a QAOA optimization procedure.
"""

from collections.abc import Iterable, Sequence
import math
from math import pi

from parityos.base import Circuit, Qubit, Rx
from parityos.encodings.parityos_output import ParityOSOutput


ParameterBoundsType = dict[str, tuple[float, float]]


def generate_qaoa(
    parityos_output: ParityOSOutput, unitary_pattern: str
) -> tuple[Circuit, ParameterBoundsType]:
    """
    Generates a QAOA quantum circuit and a dictionary with parameter bounds.
    The QAOA quantum circuit is composed of several unitary propagators, related to the problem
    Hamiltonian, driver terms and Parity constraints. The parameter bounds dictionary maps
    the parameter names used in the quantum circuit onto a (lower bound, upper bound) tuple of
    floats for each classical QAOA parameter in the QAOA circuit.

    :param parityos_output: The compiler output as an object of ParityOSOutput,
        containing information about the compiled problem and the raw constraint circuit,
        as defined in the response schema.
        Assumptions:

            1. the device has only 2-body connections;
            2. the interaction coefficients are explicit numbers, not strings.

    :type parityos_output: ParityOSOutput

    :param str unitary_pattern: the pattern of unitaries to use in each repetition.  Should be a
        string with the following characters:

            * Z: the problem Hamiltonian
            * X: the driver Hamiltonian
            * C: the constraint Hamiltonian

        The string is expressed in time order, from left to right.

    Example:
        To create a ParityOS QAOA circuit of order p=3, create the circuit from a ParityOSOutput
        object with a unitary_pattern of order 3:
        qaoa_circuit, parameter_bounds = generate_qaoa(parityos_output, 'XCZXCZXCZ')

    """
    qaoa_circuit = Circuit()
    if parityos_output.initial_state_preparation_circuit:
        qaoa_circuit.append(parityos_output.initial_state_preparation_circuit)

    parameter_bounds = {}
    compiled_representation = parityos_output.compiled_problem
    driver_circuit = parityos_output.driver_circuit or uniform_driver_circuit(
        compiled_representation.qubits
    )
    hamiltonian_scale = determine_scale(compiled_representation.coefficients)
    bounds_z = (-pi / hamiltonian_scale, pi / hamiltonian_scale)
    bounds_x = (-pi / 2, pi / 2)
    bounds_c = (-pi, pi)
    _unitary_map = {
        "Z": ("gamma", bounds_z, parityos_output.problem_circuit),
        "X": ("beta", bounds_x, driver_circuit),
        "C": ("Omega", bounds_c, parityos_output.constraint_circuit),
    }
    _unitary_counts = {"Z": 0, "X": 0, "C": 0}
    for unitary in unitary_pattern.upper():
        parameter_label, bounds, circuit = _unitary_map[unitary]
        parameter_name = f"{parameter_label}{_unitary_counts[unitary]}"
        qaoa_circuit.append(circuit.remap(parameter=parameter_name))
        parameter_bounds[parameter_name] = bounds
        _unitary_counts[unitary] += 1

    return qaoa_circuit, parameter_bounds


def uniform_driver_circuit(qubits: Iterable[Qubit]) -> Circuit:
    """
    Create a driver circuit that applies a uniform X rotation on all qubits.

    :param qubits: a sequence of qubits on which the driver circuit will act.

    :return: a ParityOS Circuit that applies a uniform X rotation on the given qubits.
    """
    return Circuit((Rx(qubit, angle=1, parameter_name="parameter") for qubit in qubits))


def determine_scale(coefficients: Sequence[float]) -> float:
    """
    Calculate an effective scale of the coefficients.
    :param coefficients: a list of floating point numbers
    :return: a scale factor that can be used to provide a useful range for QAOA parameters.
    """
    rms = math.sqrt(sum(coefficient**2 for coefficient in coefficients) / len(coefficients))
    return rms
