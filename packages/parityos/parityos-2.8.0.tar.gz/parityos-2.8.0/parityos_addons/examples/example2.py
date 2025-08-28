"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2022.
All rights reserved.

A ParityOS usage example of an Ising model on a rectangular analog device.
"""

from itertools import combinations

from parityos import CompilerClient, ParityOSOutput
from parityos.device_model import RectangularAnalogDevice
from parityos_addons.examples.runner import run_example
from parityos_addons.spin_hamiltonians import SpinZ, spinz_to_hamiltonian


def parityos_example2(
    logical_size: int = 6,
    physical_length: int = 5,
    physical_width: int = 5,
    username: str = "",
) -> ParityOSOutput:
    """
    Compile an all-to-all connected Ising model on a rectangular analog device.

    :param int logical_size: The number of spins in the Ising model
    :param int physical_length: The length of the rectangular lattice of qubits on the device.
    :param int physical_width: The width of the rectangular lattice of qubits on the device.
    :param str username: A valid ParityOS username (if not given, then the ```PARITYOS_USER```
                         environment variable is used instead).
    :returns: The ParityOS output object containing the compiled problem.
    """
    # Define an all-to-all connected Ising model using a sympy expression
    spins = [SpinZ(label) for label in range(logical_size)]
    ising_model = sum(spin1 * spin2 for spin1, spin2 in combinations(spins, 2))
    optimization_problem = spinz_to_hamiltonian(ising_model)

    device_model = RectangularAnalogDevice(physical_length, physical_width)
    print(
        f"Map {len(optimization_problem.interactions)} interactions "
        f"on {len(device_model.qubits)} qubits."
    )
    assert len(optimization_problem.interactions) <= len(device_model.qubits)

    compiler_client = CompilerClient(username)
    parityos_output = compiler_client.compile(optimization_problem, device_model)
    return parityos_output


if __name__ == "__main__":
    run_example(parityos_example2)
