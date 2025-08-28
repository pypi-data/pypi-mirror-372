"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2023.
All rights reserved.

Helper tool to run the ParityOS examples.
"""

from collections.abc import Callable

from parityos import ParityOSOutput


def run_example(example: Callable[[], ParityOSOutput]):
    """
    Run a compilation example and print some information on the result.

    :param example: A callable that runs without input arguments and returns a
                    `ParityOSOutput` object.
    """
    example_output = example()
    n_physical_qubits = len(example_output.compiled_problem.qubits)
    n_interactions = len(example_output.compiled_problem.interactions)
    n_constraints = len(example_output.compiled_problem.constraints)
    n_logical_qubits = len(example_output.mappings.decoding_map)
    print(
        f"Compilation in {example.__name__} required {n_physical_qubits} physical qubits "
        f"for {n_interactions} interactions between {n_logical_qubits} logical qubits, "
        f"using {n_constraints} constraints."
    )
