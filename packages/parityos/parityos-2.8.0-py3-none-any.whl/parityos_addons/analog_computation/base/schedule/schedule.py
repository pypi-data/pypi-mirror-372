"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2023 - 2025.
All rights reserved.
"""

import copy
from collections.abc import Iterable
from dataclasses import dataclass

import sympy
from parityos import Qubit
from typing_extensions import Self

from parityos_addons.analog_computation import Observable
from parityos_addons.analog_computation.base.schedule.schedule_term import (
    ScheduleTerm,
)
from parityos_addons.analog_computation.base.schedule.utils.sympy_utils import (
    sympy_expression_from_json,
    sympy_expression_to_json,
)


@dataclass(frozen=True)
class Schedule:
    """
    Representation of a Schedule defined as a sum of ScheduleTerms.

    :param terms: list of ScheduleTerms.
    :param time_parameter: sympy.Symbol representing the time parameter.
    :param duration: duration of the Schedule.

    Example::

            >>> observable_1 = Observable(
            >>>     [PauliOp([X(Qubit(1))]), PauliOp([Y(Qubit(1)), Y(Qubit(2))])], [0.5, -0.8],
            >>> )
            >>> observable_2 = Observable([PauliOp([Z(Qubit(1))])], [1])

            >>> time = sympy.Symbol("t")
            >>> coefficient_1 = 3.1 * time
            >>> coefficient_2 = time + 4

            >>> term_1 = ScheduleTerm(observable_1, coefficient_1)
            >>> term_2 = ScheduleTerm(observable_2, coefficient_2)
            >>> schedule = Schedule([term_1, term_2], time)
    """

    terms: list[ScheduleTerm]
    time_parameter: sympy.Symbol
    duration: float = 1.0

    @classmethod
    def compose(cls, schedules: Iterable[Self]) -> Self:
        """
        Compose a `Schedule` by combining all `ScheduleTerm`s of a sequence of `Schedule`s. For
        that the `time_parameter` and `duration` must be identical in all `Schedule`s.
        """
        terms = sum([schedule.terms for schedule in schedules], start=[])
        time_parameters = {schedule.time_parameter for schedule in schedules}
        durations = {schedule.duration for schedule in schedules}

        if len(time_parameters) != 1:
            raise ValueError("time_parameter must be identical in all schedules")
        if len(durations) != 1:
            raise ValueError("duration must be identical in all schedules")

        return Schedule(terms, list(time_parameters)[0], list(durations)[0])

    @property
    def observables(self) -> list[Observable]:
        """
        :return: list of Observables.
        """
        observables = [term.observable for term in self.terms]
        return copy.deepcopy(observables)

    @property
    def coefficients(self) -> list[sympy.Expr]:
        """
        :return: list of coefficients.
        """
        coefficients = [term.coefficient for term in self.terms]
        return copy.deepcopy(coefficients)

    @property
    def parameters(self) -> set:
        """
        :return: set of the parameters that are in the list of coefficients
        """
        parameters = set()
        for term in self.terms:
            parameters = parameters.union(term.parameters)
        return parameters

    @property
    def qubits(self) -> list[Qubit]:
        """
        Obtain a sorted list of all qubits in this `Schedule` instance.
        """
        return sorted(
            list(
                set().union(*{frozenset(term.observable.qubits) for term in self.terms})
            )
        )

    def add_term(self, term: ScheduleTerm) -> Self:
        """
        Creates a new Schedule by adding an (observable, coefficient) pair.
        :param term: an (observable, coefficient) pair.
        :return: new Schedule
        """
        new_terms = copy.deepcopy(self.terms)
        new_terms.append(term)

        return Schedule(new_terms, self.time_parameter, self.duration)

    def subs_parameters(self, *args) -> Self:
        """
        Substitutes parameters and returns a new Schedule.
        Passes the args to the Sympy's subs methods. From Sympy docstrings:

        :param args:`args` is either:
            - two arguments, e.g. foo.subs(old, new)
            - one iterable argument, e.g. foo.subs(iterable). The iterable may be
                o an iterable container with (old, new) pairs. In this case the
                  replacements are processed in the order given with successive
                  patterns possibly affecting replacements already made.
                o a dict or set whose key/value items correspond to old/new pairs.
                  In this case the old/new pairs will be sorted by op count and in
                  case of a tie, by number of args and the default_sort_key. The
                  resulting sorted list is then processed as an iterable container
                  (see previous).
        :return: a new Schedule
        """
        new_terms = [term.subs_parameters(*args) for term in self.terms]

        return Schedule(new_terms, self.time_parameter, self.duration)

    @classmethod
    def from_json(cls, data: dict) -> Self:
        """
        Constructs a Schedule object from JSON data.

        :param data: a JSON-like dictionary with ``'terms'``,
                     ``'time_parameter'``, ``'duration'`` fields.
        :return: a Schedule object.
        """
        terms = [
            ScheduleTerm.from_json(schedule_term_data)
            for schedule_term_data in data["terms"]
        ]
        time_parameter = sympy_expression_from_json(data["time_parameter"])
        duration = float(data["duration"])
        return cls(terms, time_parameter, duration)

    def to_json(self) -> dict:
        """
        Converts the Schedule to json.

        :return: the Schedule in json-serializable format
        """
        return {
            "terms": [term.to_json() for term in self.terms],
            "time_parameter": sympy_expression_to_json(self.time_parameter),
            "duration": str(self.duration),
        }

    def __eq__(self, other: Self):
        """
        Two Schedules are equal if all their attributes are equal.

        :param other: other Schedule object
        :return: bool
        """
        # We convert the lists of terms into a set because
        # the ordering of the observables should not affect the comparison.
        return (
            set(self.terms) == set(other.terms)
            and self.time_parameter == other.time_parameter
            and self.duration == other.duration
        )

    def __hash__(self):
        return hash((frozenset(self.terms), self.time_parameter, self.duration))

    def __str__(self):
        return "\n +".join(f"{term}" for term in self.terms)
