"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2023-2024.
All rights reserved.
"""

import pandas as pd

from parityos.base import Circuit
from parityos_addons.benchmarking.dataframe_construction.add_column import (
    add_metric_column,
)
from parityos_addons.benchmarking.metrics.circuit_metrics import (
    circuit_gate_count,
    circuit_cnot_depth,
    circuit_depth,
    circuit_cnot_count,
    circuit_qubit_count,
    circuit_rzz_count,
    circuit_two_body_gate_count,
)


def add_benchmarks_for_circuits(statistics: pd.DataFrame, circuits: pd.Series):
    """
    Calculates metrics from circuits and adds to statistics pd.DataFrame

    :param statistics: pd.DataFrame where the metrics should be added
    :param circuits: pd.Series that contains Circuit instances
    """

    name_of_column_metric_function_map = {
        "qubit_count": circuit_qubit_count,
        "depth": circuit_depth,
        "cnot_depth": circuit_cnot_depth,
        "gate_count": circuit_gate_count,
        "cnot_count": circuit_cnot_count,
        "rzz_count": circuit_rzz_count,
        "two_body_gate_count": circuit_two_body_gate_count,
    }

    for column_name, metric_function in name_of_column_metric_function_map.items():
        column_name = f"{circuits.name}_{column_name}"
        add_metric_column(statistics, circuits, column_name, metric_function, Circuit)
