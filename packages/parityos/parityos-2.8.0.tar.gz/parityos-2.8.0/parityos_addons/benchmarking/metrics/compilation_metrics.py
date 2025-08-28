"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2023-2024.
All rights reserved.
"""

import numpy as np

from parityos import ProblemRepresentation
from parityos.api_interface.compiler_run import CompilerRun


def problem_interactions_count(problem: ProblemRepresentation) -> int:
    """
    :param problem: ProblemRepresentation instance
    :return: count of the interaction terms in the problem
    """
    return len(problem.interactions)


def problem_qubit_count(problem: ProblemRepresentation) -> int:
    """
    :param problem: ProblemRepresentation instance
    :return: count of the qubits in the problem
    """
    return len(problem.qubits)


def problem_ancilla_count(problem: ProblemRepresentation) -> int:
    """
    :param problem: ProblemRepresentation instance
    :return: count of the ancilla qubits in the problem
    """
    return len(problem.qubits.difference(*problem.interactions))


def problem_triangle_constraint_count(problem: ProblemRepresentation) -> int:
    """
    :param problem: ProblemRepresentation instance
    :return: count of the triangle constraints in the problem
    """
    return sum([len(constraint.qubits) == 3 for constraint in problem.constraints])


def problem_square_constraint_count(problem: ProblemRepresentation) -> int:
    """
    :param problem: ProblemRepresentation instance
    :return: count of the square constraints in the problem
    """
    return sum([len(constraint.qubits) == 4 for constraint in problem.constraints])


def problem_constraint_count(problem: ProblemRepresentation) -> int:
    """
    :param problem: ProblemRepresentation instance
    :return: count of the constraints in the problem
    """
    return len(problem.constraints)


def compiler_run_compilation_time(compiler_run: CompilerRun) -> float:
    """
    :param compiler_run: CompilerRun instance
    :return: compilation time in seconds or np.nan
    """
    if ((not compiler_run.started_at)
            or (not compiler_run.finished_at and not compiler_run.failed_at)):
        return np.nan
    elif compiler_run.finished_at:
        return (compiler_run.finished_at - compiler_run.started_at).total_seconds()
    elif compiler_run.failed_at:
        return (compiler_run.failed_at - compiler_run.started_at).total_seconds()
