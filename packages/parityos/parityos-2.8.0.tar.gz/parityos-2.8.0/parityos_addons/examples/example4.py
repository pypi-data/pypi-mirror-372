"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2022.
All rights reserved.

A ParityOS usage example tailored to the QPU with star-topology.
"""

from parityos import CompilerClient, ParityOSOutput, ProblemRepresentation
from parityos.base import Qubit
from parityos.device_model import DeviceModelBase


class StarDevice(DeviceModelBase):
    """
    Describes a quantum device with star topology, with entangling gates between the central
    qubit and each of the outer qubits.
    """

    device_type = "cnot"
    preset = "digital_default"

    def __init__(self, outer_size: int = 3):
        """
        Create a device model where the qubits are laid out in a star topology, with the first
        qubit in the center and the outer qubits connected only to the central one. The number
        of outer qubits is set by the `outer_size` argument.

        :param int outer_size: Number of outer qubits.
        """
        qubit_connections = {frozenset({Qubit((0, 0)), Qubit((1, r))}) for r in range(outer_size)}
        self.set_qubit_connections(qubit_connections)


def parityos_example4(
    physical_size: int = 4,
    username: str = "",
) -> ParityOSOutput:
    """
    Compile a simple Ising model on a star-shaped digital device.

    :param int physical_size: Total number of qubits on the device.
    :param str username: A valid ParityOS username (if not given, then the ```PARITYOS_USER```
                         environment variable is used instead).
    :returns: The ParityOS output object containing the compiled problem.
    """
    # Define a problem Hamiltonian: a single cycle of length 4
    q = [Qubit(i) for i in range(4)]
    interactions = [{q[0], q[1]}, {q[1], q[2]}, {q[2], q[3]}, {q[3], q[0]}]
    coefficients = [0.625, -0.5, 0.5, -0.625]
    optimization_problem = ProblemRepresentation(interactions, coefficients=coefficients)

    device_model = StarDevice(outer_size=physical_size - 1)
    print(
        f"Map {len(optimization_problem.interactions)} interactions "
        f"on {len(device_model.qubits)} qubits."
    )
    assert len(optimization_problem.interactions) <= len(device_model.qubits)

    compiler_client = CompilerClient(username)
    parityos_output = compiler_client.compile(optimization_problem, device_model)

    return parityos_output


if __name__ == "__main__":
    print(parityos_example4())
