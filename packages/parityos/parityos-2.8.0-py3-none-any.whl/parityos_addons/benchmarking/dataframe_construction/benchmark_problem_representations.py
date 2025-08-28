"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2023-2024.
All rights reserved.
"""

import pandas as pd

from parityos import ProblemRepresentation
from parityos_addons.benchmarking.dataframe_construction.add_column import (
    add_metric_column,
)
from parityos_addons.benchmarking.metrics.compilation_metrics import (
    problem_constraint_count,
    problem_qubit_count,
    problem_ancilla_count,
    problem_interactions_count,
    problem_triangle_constraint_count,
    problem_square_constraint_count,
)


def add_benchmarks_for_problem_representations(
    statistics: pd.DataFrame, problem_representations: pd.Series
):
    """
    Calculates metrics from problem_representations and adds to statistics pd.DataFrame

    :param statistics: pd.DataFrame where the metrics should be added
    :param problem_representations: pd.Series containing ProblemRepresentation instances
    """

    name_of_column_metric_function_map = {
        "constraint_count": problem_constraint_count,
        "compilation_qubit_count": problem_qubit_count,
        "compilation_ancilla_count": problem_ancilla_count,
        "interaction_count": problem_interactions_count,
        "triangle_constraint_count": problem_triangle_constraint_count,
        "square_constraint_count": problem_square_constraint_count,
    }

    for column_name, metric_function in name_of_column_metric_function_map.items():
        add_metric_column(
            statistics,
            problem_representations,
            column_name,
            metric_function,
            ProblemRepresentation,
        )
