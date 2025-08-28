"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2023 - 2025.
All rights reserved.
"""

from typing import Sequence, Union

from parityos import ProblemRepresentation
from parityos.base import X, Z, Qubit

from parityos_addons.analog_computation import Observable, PauliOp
from parityos_addons.analog_computation.base.exceptions import (
    ParityOSAnalogComputationException,
)


def observable_from_problem(
    problem_representation: ProblemRepresentation,
    constraint_strength: float = 1.0,
) -> Observable:
    """
    Creates an Observable from ProblemRepresentation that contains both interactions and
    constraints.

    :param problem_representation: a ProblemRepresentation instance.
    :param constraint_strength: the absolute value to multiply to constraint.value(s) in order to
        obtain the coefficients for the observable defined by constraints.
        ProblemRepresentation is assumed to be a minimization problem.
    :return: Observable.
    """
    observable_interactions = observable_from_problem_interactions(
        problem_representation
    )
    observable_constraints = observable_from_problem_constraints(
        problem_representation, constraint_strength
    )

    return observable_interactions + observable_constraints


def observable_from_problem_interactions(
    problem_representation: ProblemRepresentation,
) -> Observable:
    """
    Creates an Observable only from interactions of the ProblemRepresentation.

    :param problem_representation: a ProblemRepresentation instance.
    :return: Observable.
    """
    interactions = [
        PauliOp([Z(q) for q in interaction])
        for interaction in problem_representation.interactions
    ]
    coefficients = problem_representation.coefficients

    return Observable(interactions, coefficients)


def observable_from_problem_constraints(
    problem_representation: ProblemRepresentation,
    constraint_strength: float = 1.0,
) -> Observable:
    """
    Creates an Observable only from the constraints of the ProblemRepresentation.

    :param problem_representation: a ProblemRepresentation instance.
    :param constraint_strength: the absolute value to multiply to constraint.value(s) in order to
        obtain the coefficients for the observable defined by constraints.
        ProblemRepresentation is assumed to be a minimization problem.
    :return: Observable.
    """
    if constraint_strength < 0:
        raise ParityOSAnalogComputationException(
            f"{constraint_strength=} should be positive."
        )
    constraints = problem_representation.constraints
    interactions = [
        PauliOp([Z(q) for q in constraint.qubits]) for constraint in constraints
    ]
    coefficients = [
        -constraint_strength * constraint.value for constraint in constraints
    ]

    return Observable(interactions, coefficients)


def standard_driver_observable_for_qubits(
    qubits: Union[Sequence[Qubit], set[Qubit]],
) -> Observable:
    """
    Creates a standard driver (-sum(X)) observable for qubits.
    :param qubits:
    :return: a driver Observable
    """
    interactions = [PauliOp([X(q)]) for q in qubits]
    coefficients = [-1.0] * len(qubits)

    return Observable(interactions, coefficients)
