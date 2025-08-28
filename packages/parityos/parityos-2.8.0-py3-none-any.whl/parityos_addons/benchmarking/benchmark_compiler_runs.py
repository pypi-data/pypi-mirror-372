"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2024.
All rights reserved.
"""

from typing import Collection

import numpy as np
import pandas as pd

from parityos import CompilerClient, ParityOSOutput
from parityos.api_interface.compiler_run import CompilerRun, CompilerRunStatus
from parityos_addons.benchmarking.dataframe_construction.benchmark_circuits import (
    add_benchmarks_for_circuits,
)
from parityos_addons.benchmarking.dataframe_construction.benchmark_compiler_runs import \
    add_benchmarks_for_compiler_runs
from parityos_addons.benchmarking.dataframe_construction.benchmark_problem_representations import (
    add_benchmarks_for_problem_representations,
)


def benchmark_compiler_runs(
    client: CompilerClient,
    compiler_runs: Collection[CompilerRun],
    calculate_circuit_statistics: bool = True,
) -> pd.DataFrame:
    """
    Calculates statistics from the CompilerRun instances, by requesting the corresponding
    ParityOSOutputs.

    :param client: CompilerClient which should send requests to get the corresponding
                   ParityOSOutputs
    :param compiler_runs: Collection of CompilerRun instances
    :param calculate_circuit_statistics: indicates if circuit statistics should be added
    :return: pd.DataFrame containing benchmark results
    """

    dataframe = pd.DataFrame.from_dict(
        {
            compiler_run.id: {f"{CompilerRun.__name__}": compiler_run}
            for compiler_run in compiler_runs
        },
        orient="index",
    )
    dataframe.index.name = f"{CompilerRun.__name__}_id"
    add_benchmarks_for_compiler_runs(dataframe, dataframe[f"{CompilerRun.__name__}"])

    dataframe["parityos_outputs"] = dataframe[f"{CompilerRun.__name__}"].apply(
        lambda compiler_run: (
            client.get_solutions(compiler_run)[0]
            if compiler_run.status == CompilerRunStatus.COMPLETED
            else np.nan
        ),
    )

    compiled_problems = dataframe["parityos_outputs"].apply(
        lambda output: (
            output.compiled_problem if isinstance(output, ParityOSOutput) else np.nan
        )
    )
    add_benchmarks_for_problem_representations(dataframe, compiled_problems)

    if calculate_circuit_statistics:
        constraint_circuits = dataframe["parityos_outputs"].apply(
            lambda output: (
                output.constraint_circuit
                if isinstance(output, ParityOSOutput)
                else np.nan
            )
        )
        constraint_circuits.name = "constraint_circuit"
        add_benchmarks_for_circuits(dataframe, constraint_circuits)

    return dataframe
