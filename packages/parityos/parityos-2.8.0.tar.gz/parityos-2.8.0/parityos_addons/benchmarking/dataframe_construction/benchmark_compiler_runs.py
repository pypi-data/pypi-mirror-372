"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2024.
All rights reserved.
"""

import numpy as np
import pandas as pd

from parityos.api_interface.compiler_run import CompilerRunStatus, CompilerRun
from parityos_addons.benchmarking.dataframe_construction.add_column import (
    add_metric_column,
)
from parityos_addons.benchmarking.metrics.compilation_metrics import (
    compiler_run_compilation_time,
)


def add_benchmarks_for_compiler_runs(
    statistics: pd.DataFrame, compiler_runs: pd.Series
):
    """
    Calculates metrics from compiler_runs and adds to statistics pd.DataFrame

    :param statistics: pd.DataFrame where the metrics should be added
    :param compiler_runs: pd.Series that contains CompilerRun instances
    """

    for status in CompilerRunStatus:
        column_name = status.name
        statistics[column_name] = compiler_runs.apply(
            lambda compiler_run: compiler_run.status is status
            if isinstance(compiler_run, CompilerRun)
            else np.nan,
        )

    add_metric_column(
        statistics,
        compiler_runs,
        "compilation_time",
        compiler_run_compilation_time,
        CompilerRun,
    )