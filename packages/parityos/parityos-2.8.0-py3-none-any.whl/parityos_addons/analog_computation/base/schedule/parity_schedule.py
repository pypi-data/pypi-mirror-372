"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2023 - 2025.
All rights reserved.
"""

import sympy
from parityos import ParityOSOutput, Qubit
from typing_extensions import Self

from parityos_addons.analog_computation import (
    observable_from_problem_constraints,
    observable_from_problem_interactions,
    standard_driver_observable_for_qubits,
)
from parityos_addons.analog_computation.base.schedule.schedule import (
    Schedule,
    ScheduleTerm,
)

DEFAULT_TIME_PARAMETER = sympy.Symbol("t")
DEFAULT_DURATION = 1.0
DEFAULT_INTERACTIONS_EXPRESSION = DEFAULT_TIME_PARAMETER
DEFAULT_CONSTRAINTS_EXPRESSION = DEFAULT_TIME_PARAMETER
DEFAULT_DRIVER_EXPRESSION = DEFAULT_DURATION - DEFAULT_TIME_PARAMETER


class ParitySchedule:
    """
    A standard annealing Schedule for the Parity Architecture. In contrast to
    the Schedule class ParitySchedule knows the names of its terms:
    interactions_term, constraints_term, driver_term. The ParitySchedule corresponds to:

        ParitySchedule = interactions_term + constraints_term + driver_term

    where terms consists of an Observable and a time dependent coefficient.
    """

    def __init__(
        self,
        output: ParityOSOutput,
        interactions_coefficient: sympy.Expr = DEFAULT_INTERACTIONS_EXPRESSION,
        constraints_coefficient: sympy.Expr = DEFAULT_CONSTRAINTS_EXPRESSION,
        driver_coefficient: sympy.Expr = DEFAULT_DRIVER_EXPRESSION,
        time_parameter: sympy.Symbol = DEFAULT_TIME_PARAMETER,
        duration: float = DEFAULT_DURATION,
    ):
        """
        Creates ParitySchedule from ParityOSOutput and related coefficients.
        :param output: ParityOSOutput to transform into a Schedule
        :param interactions_coefficient: sympy.Expr for the interactions term
        :param constraints_coefficient: sympy.Expr for the constraints term
        :param driver_coefficient: sympy.Expr for the driver term
        :param time_parameter: sympy.Symbol for the time parameter
        :param duration: float
        :return: ParitySchedule
        """
        self._interactions_coefficient = interactions_coefficient
        self._constraints_coefficient = constraints_coefficient
        self._driver_coefficient = driver_coefficient
        self._time_parameter = time_parameter
        self._duration = duration

        interactions_term = ScheduleTerm(
            observable_from_problem_interactions(output.compiled_problem),
            interactions_coefficient,
        )
        self._interactions_schedule = Schedule(
            [interactions_term], time_parameter, duration
        )

        constraints_term = ScheduleTerm(
            observable_from_problem_constraints(output.compiled_problem),
            constraints_coefficient,
        )
        self._constraints_schedule = Schedule(
            [constraints_term], time_parameter, duration
        )

        driver_term = ScheduleTerm(
            standard_driver_observable_for_qubits(output.compiled_problem.qubits),
            driver_coefficient,
        )
        self._driver_schedule = Schedule([driver_term], time_parameter, duration)

    @property
    def interactions_coefficient(self) -> sympy.Expr:
        """Coefficient of the interactions term"""
        return self._interactions_coefficient

    @property
    def constraints_coefficient(self) -> sympy.Expr:
        r"""Coefficient of the constraints term"""
        return self._constraints_coefficient

    @property
    def driver_coefficient(self) -> sympy.Expr:
        r"""Coefficient of the driver term"""
        return self._driver_coefficient

    @property
    def time_parameter(self) -> sympy.Symbol:
        """Time parameter as sympy.Symbol"""
        return self._time_parameter

    @property
    def duration(self) -> float:
        """Duration of the schedule"""
        return self._duration

    @property
    def interactions_schedule(self) -> Schedule:
        """
        `Schedule` for the interactions
        """
        return self._interactions_schedule

    @property
    def constraints_schedule(self) -> Schedule:
        """
        `Schedule` for the constraints
        """
        return self._constraints_schedule

    @property
    def driver_schedule(self) -> Schedule:
        """
        `Schedule` for the driver
        """
        return self._driver_schedule

    @property
    def schedule(self) -> Schedule:
        """
        Returns the full corresponding `Schedule`
        """
        return Schedule.compose(
            [
                self.interactions_schedule,
                self.constraints_schedule,
                self.driver_schedule,
            ]
        )

    @property
    def qubits(self) -> list[Qubit]:
        """
        Obtain a sorted list of all qubits in this `Schedule` instance.
        """
        return self.schedule.qubits

    def __eq__(self, other: Self) -> bool:
        if self is other:
            return True

        return (
            self.interactions_schedule == other.interactions_schedule
            and self.constraints_schedule == other.constraints_schedule
            and self.driver_schedule == other.driver_schedule
        )

    def __str__(self) -> str:
        return "\n +".join(
            [
                str(self.interactions_schedule),
                str(self.constraints_schedule),
                str(self.driver_schedule),
            ]
        )
