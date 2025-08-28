"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2023-2024.
All rights reserved.
"""

from typing import Collection

import pandas as pd

from parityos import ParityOSOutput
from parityos_addons.benchmarking.dataframe_construction.benchmark_circuits import (
    add_benchmarks_for_circuits,
)
from parityos_addons.benchmarking.dataframe_construction.benchmark_problem_representations import (
    add_benchmarks_for_problem_representations,
)


def benchmark_parityos_outputs(
        parityos_outputs: Collection[ParityOSOutput],
        calculate_circuit_statistics: bool = True,
) -> pd.DataFrame:
    """
    Calculates statistics from the ParityOSOutput instances

    :param parityos_outputs: Collection of ParityOSOutput instances
    :param calculate_circuit_statistics: indicates if circuit statistics should be added
    :return: pd.DataFrame containing benchmark results
    """
    parityos_outputs_df = pd.DataFrame({"parityos_outputs": parityos_outputs})

    compiled_problems = parityos_outputs_df["parityos_outputs"].apply(
        lambda output: output.compiled_problem
    )
    add_benchmarks_for_problem_representations(parityos_outputs_df, compiled_problems)

    if calculate_circuit_statistics:
        constraint_circuits = parityos_outputs_df["parityos_outputs"].apply(
            lambda output: output.constraint_circuit
        )
        constraint_circuits.name = "constraint_circuit"
        add_benchmarks_for_circuits(parityos_outputs_df, constraint_circuits)

    return parityos_outputs_df
