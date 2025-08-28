"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2022.
All rights reserved.

A ParityOS usage example for a generalized Ising model with higher order interactions.
"""

from itertools import combinations

from parityos import CompilerClient, ParityOSOutput
from parityos.device_model import RectangularAnalogDevice
from parityos_addons.examples.runner import run_example
from parityos_addons.spin_hamiltonians import SpinZ, spinz_to_hamiltonian


def parityos_example3(
    logical_size: int = 6,
    physical_length: int = 4,
    physical_width: int = 4,
    username: str = "",
) -> ParityOSOutput:
    """
    Compile a generalized Ising model on a rectangular analog device.

    :param int logical_size: The number of spins in the Ising model
    :param int physical_length: The length of the rectangular lattice of qubits on the device.
    :param int physical_width: The width of the rectangular lattice of qubits on the device.
    :param str username: A valid ParityOS username (if not given, then the ```PARITYOS_USER```
                         environment variable is used instead).
    :returns: The ParityOS output object containing the compiled problem.
    """
    # Define a problem Hamiltonian: a generalized Ising model with two- and three-spin interactions.
    spins = [SpinZ(label) for label in range(logical_size)]
    pair_interactions = list(combinations(spins, 2))[1::2]
    ising_model = sum(spin1 * spin2 for spin1, spin2 in pair_interactions)
    for spin1, spin2, spin3 in zip(spins[:-2], spins[1:-1], spins[2:]):
        ising_model += spin1 * spin2 * spin3 / 8

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
    run_example(parityos_example3)
