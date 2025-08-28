"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2024-2025.
All rights reserved.
"""

import numbers
from collections.abc import Sequence
from typing import Union

import numpy as np
import sympy
from matplotlib import pyplot as plt

from parityos_addons.rydberg_layout.schedule.rydberg_schedule import RydbergSchedule


def plot_rydberg_schedule(
    rydberg_schedule: RydbergSchedule,
    *,
    ax: Union[plt.Axes, None] = None,
    show: bool = False,
    num_ts: int = 101,
) -> plt.Axes:
    """
    Plot a Rydberg schedule
    """
    if ax is None:
        fig, ax = plt.subplots(1, 1, constrained_layout=True)

    # compute values
    ts = np.linspace(0, rydberg_schedule.duration, num_ts)

    rabi_vals = _evaluate_sympy_function(
        rydberg_schedule.rabi_coefficient, rydberg_schedule.time_parameter, ts
    )
    detuning_vals = _evaluate_sympy_function(
        rydberg_schedule.detuning_coefficient, rydberg_schedule.time_parameter, ts
    )
    phase_vals = _evaluate_sympy_function(
        rydberg_schedule.phase_coefficient, rydberg_schedule.time_parameter, ts
    )

    # plot them using standard matplotlib.pyplot
    ax.plot(
        ts,
        rabi_vals,
        label=r"Rabi frequency $\Omega(%s)$" % rydberg_schedule.time_parameter,
    )
    ax.plot(
        ts,
        detuning_vals,
        label=r"detuning $\Delta(%s)$" % rydberg_schedule.time_parameter,
    )
    ax.plot(ts, phase_vals, label=r"phase $\phi(%s)$" % rydberg_schedule.time_parameter)

    ax.set_xlabel("%s" % rydberg_schedule.time_parameter)

    ax.legend()

    if show:
        plt.show()

    return ax


def plot_local_detuning_schedules(
    rydberg_schedule: RydbergSchedule,
    *,
    ax: Union[plt.Axes, None] = None,
    show: bool = False,
    num_ts: int = 101,
) -> plt.Axes:
    """
    Plot a Rydberg schedule
    """
    if ax is None:
        fig, ax = plt.subplots(1, 1, constrained_layout=True)

    # compute values
    ts = np.linspace(0, rydberg_schedule.duration, num_ts)

    detuning_vals = _evaluate_sympy_function(
        rydberg_schedule.detuning_coefficient, rydberg_schedule.time_parameter, ts
    )

    # local_detuning_schedules
    for i, local_detuning in enumerate(rydberg_schedule.atom_detunings):
        local_detuning_vals = [
            detuning_val * local_detuning for detuning_val in detuning_vals
        ]
        ax.plot(ts, local_detuning_vals, "--", label="$i=%d$" % i)

    ax.set_xlabel("%s" % rydberg_schedule.time_parameter)
    ax.set_ylabel(r"$\Delta_i(%s)$" % rydberg_schedule.time_parameter)

    ax.legend()

    if show:
        plt.show()

    return ax


def _evaluate_sympy_function(
    function: Union[sympy.Expr, numbers.Number],
    time_parameter: sympy.Symbol,
    times: Sequence[float],
) -> list[float]:
    """
    Evaluate function values of a sympy expression with a single time parameter for a given sequence
    of times
    :param function: Function with one parameter which should be evaluated
    :param time_parameter: The parameter of the function to be evaluated
    :param times: The values of the parameter for which to evaluate the function
    :return: List of function values corresponding to the given times
    """
    if isinstance(function, numbers.Number):
        function_values = [function for _ in times]
    else:
        function_values = [function.evalf(subs={time_parameter: t}) for t in times]

    return function_values
