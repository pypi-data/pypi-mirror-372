"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2023.
All rights reserved.

A ParityOS usage example of an Ising model on a rectangular digital device.
"""

from parityos import ParityOSOutput, ProblemRepresentation, Qubit
from parityos.compiler_client import CompilerClient
from parityos.device_model import RectangularDigitalDevice
from parityos_addons.examples.runner import run_example


def parityos_example1(
    physical_length: int = 4,
    physical_width: int = 4,
    username: str = "",
) -> ParityOSOutput:
    """
    Compile an Ising model on a rectangular digital device.

    :param int physical_length: The length of the rectangular lattice of qubits on the device.
    :param int physical_width: The width of the rectangular lattice of qubits on the device.
    :param str username: A valid ParityOS username (if not given, then the ```PARITYOS_USER```
                         environment variable is used instead).
    :returns: The ParityOS output object containing the compiled problem.
    """
    # Define a problem with 5 logical qubits and some 2-qubit interactions
    q = [Qubit(i) for i in range(5)]
    interactions = [
        {q[0], q[1]},
        {q[2], q[4]},
        {q[4], q[3]},
        {q[1], q[3]},
        {q[3], q[2]},
        {q[2], q[0]},
        {q[1], q[2]},
        {q[3], q[0]},
    ]
    coefficients = [0.625, 0.5, 0.5, 0.625, 0.625, 0.625, 0.125, 0.125]
    optimization_problem = ProblemRepresentation(interactions, coefficients=coefficients)

    device_model = RectangularDigitalDevice(physical_length, physical_width)
    print(
        f"Map {len(optimization_problem.interactions)} interactions "
        f"on {len(device_model.qubits)} qubits."
    )
    assert len(optimization_problem.interactions) <= len(device_model.qubits)

    compiler_client = CompilerClient(username)
    parityos_output = compiler_client.compile(optimization_problem, device_model)
    return parityos_output


if __name__ == "__main__":
    run_example(parityos_example1)
