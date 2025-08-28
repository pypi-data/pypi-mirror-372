"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2024-2025.
All rights reserved.
"""

import itertools
import math

import sympy
from parityos import Qubit
from parityos.base import X, Y, Z
from typing_extensions import Self

from parityos_addons.analog_computation import (
    Observable,
    PauliOp,
)
from parityos_addons.analog_computation.base.schedule.schedule import (
    Schedule,
    ScheduleTerm,
)
from parityos_addons.rydberg_layout.base.device.atomic_device_specs import (
    AtomicDeviceSpecs,
)
from parityos_addons.rydberg_layout.base.exceptions import RydbergLayoutException
from parityos_addons.rydberg_layout.base.rydberg_atoms import RydbergAtoms
from parityos_addons.rydberg_layout.base.atom_coordinate import squared_distance

DEFAULT_TIME_PARAMETER = sympy.Symbol("t")
DEFAULT_DURATION = 1.0
DEFAULT_DETUNING_EXPRESSION = -1 + 2 * DEFAULT_TIME_PARAMETER
DEFAULT_RABI_EXPRESSION = (
    sympy.sin(math.pi * DEFAULT_TIME_PARAMETER / DEFAULT_DURATION) ** 2
)
DEFAULT_PHASE_EXPRESSION = 0.0


class RydbergSchedule:
    r"""
    A standard annealing Schedule for Rydberg atoms given by the Hamiltonian

    .. math::
        H(t) = C_6/\hbar \sum_{i \neq j} r_{ij}^{-6} n_i n_j - \delta(t) \sum_i \delta_i n_i
        + \Omega(t)/2 \sum_i (cos(\phi(t)) X_i - sin(\phi(t)) Y_i)

    with :math:`n_i = (1 + Z_i) / 2`. :math:`X_i, Y_i, Z_i` denote the Pauli X-, Y-, Z-operators
    on the atom (qubit) with label :math:`i`, :math:`r_{ij}` is the distance between atoms with
    labels :math:`i` and :math:`j`. :math:`C_6/hbar` is the Rydberg interaction coefficient,
    :math:`\Omega(t)` denotes the time dependent Rabi frequency of the driving laser. :math:
    \delta_i denotes the time-independent local values of the laser detunings, :math:`\delta(t)`
    is a global time dependent laser detuning pre-factor.
    :math:`\phi(t)` denotes the time dependent laser phase.

    Note: The plus sign in the definition of :math:`n_i` is a choice and leads to the minus sign in
    front of the Y_i term in the Hamiltonian. Attention, in literature one sometimes finds the
    opposite definition.

    `RydbergSchedule` knows the individual terms in the Hamiltonian which are denoted as
    `interactions_schedule`, `detuning_term`, `rabi_term` such that

        RydbergSchedule = interactions_schedule + detuning_term + rabi_term

    where terms consists of an Observable and a time dependent coefficients.
    """

    def __init__(
        self,
        rydberg_atoms: RydbergAtoms,
        detuning_coefficient: sympy.Expr = DEFAULT_DETUNING_EXPRESSION,
        rabi_coefficient: sympy.Expr = DEFAULT_RABI_EXPRESSION,
        phase_coefficient: sympy.Expr = DEFAULT_PHASE_EXPRESSION,
        time_parameter: sympy.Symbol = DEFAULT_TIME_PARAMETER,
        duration: float = DEFAULT_DURATION,
    ):
        r"""
        Create a :py:class:`RydbergSchedule` from a :py:class:`RydbergAtoms` instance.

        :param rydberg_atoms: Rydberg atoms instance defining the arrangement and properties of the
            atoms
        :param detuning_coefficient: `sympy.Expr` defining the time-dependent global laser
            detuning pre-factor :math:`\delta(t)` which is eventually multiplied with the detuning
            values defined for each atom. *Default*: :math:`\delta(t) = 2t - 1`
        :param rabi_coefficient: `sympy.Expr` defining the time-dependent laser
            rabi frequency :math:`\Omega(t)`. *Default*: :math:`\Omega(t) = (\sin(\pi * t))^2`
        :param phase_coefficient: `sympy.Expr` defining the time-dependent laser
            phase :math:`\phi(t)`. *Default*: :math:`\phi(t) = 0`
        :param time_parameter: `sympy.Symbol` defining which symbol is used to describe the time
            parameter :math:`t`. *Default*: :math:`t`
        :param duration: Total duration of the schedule in arbitrary units
        """
        self._detuning_coefficient = detuning_coefficient
        self._rabi_coefficient = rabi_coefficient
        self._phase_coefficient = phase_coefficient
        self._time_parameter = time_parameter
        self._duration = duration

        self._atom_detunings = [detuning.value for detuning in rydberg_atoms.detunings]
        self._interactions_schedule = self._compute_interactions_schedule(rydberg_atoms)
        self._detuning_schedule = self._compute_detuning_schedule(rydberg_atoms)
        self._rabi_schedule = self._compute_rabi_schedule(rydberg_atoms)

    @property
    def detuning_coefficient(self) -> sympy.Expr:
        r"""Coefficient \delta(t)"""
        return self._detuning_coefficient

    @property
    def rabi_coefficient(self) -> sympy.Expr:
        r"""Coefficient \Omega(t)"""
        return self._rabi_coefficient

    @property
    def phase_coefficient(self) -> sympy.Expr:
        r"""Coefficient \phi(t)"""
        return self._phase_coefficient

    @property
    def time_parameter(self) -> sympy.Symbol:
        """Time parameter as sympy.Symbol"""
        return self._time_parameter

    @property
    def duration(self) -> float:
        """Duration of the schedule in μs"""
        return self._duration

    @property
    def atom_detunings(self) -> list[float]:
        """Atom detuning values in rydberg_atoms"""
        return self._atom_detunings

    @property
    def interactions_schedule(self) -> Schedule:
        """
        `Schedule` for the Rydberg interactions part of the Hamiltonian (time-independent)
        """
        return self._interactions_schedule

    @property
    def detuning_schedule(self) -> Schedule:
        """
        `Schedule` for the laser detuning part of the Hamiltonian
        """
        return self._detuning_schedule

    @property
    def rabi_schedule(self) -> Schedule:
        """
        `Schedule` for the laser rabi frequency part of the Hamiltonian (including the phase)
        """
        return self._rabi_schedule

    @property
    def schedule(self) -> Schedule:
        """
        Returns the corresponding Schedule
        """
        return Schedule.compose(
            [self.interactions_schedule, self.detuning_schedule, self.rabi_schedule]
        )

    def assert_detuning_device_specs(self, device_specs: AtomicDeviceSpecs) -> None:
        """
        Assert that the detuning schedule fits the device specs. Raises a `RydbergLayoutException`
        if the schedule cannot be implemented for the given device specs.

        :param device_specs: Device specifications of a machine
        """
        min_detuning_sweep = sympy.minimum(
            self.detuning_coefficient.subs(math.pi, sympy.pi),
            self.time_parameter,
            sympy.Interval(0, self.duration),
        )
        max_detuning_sweep = sympy.maximum(
            self.detuning_coefficient.subs(math.pi, sympy.pi),
            self.time_parameter,
            sympy.Interval(0, self.duration),
        )

        min_local_detuning = min(self.atom_detunings)
        max_local_detuning = max(self.atom_detunings)

        candidate_min_max = [
            x * y
            for x in [min_detuning_sweep, max_detuning_sweep]
            for y in [min_local_detuning, max_local_detuning]
        ]
        min_detuning = min(candidate_min_max)
        max_detuning = max(candidate_min_max)

        if min_detuning < min(device_specs.detuning_range):
            raise RydbergLayoutException(
                f"Minimum detuning in schedule {min_detuning} is below "
                f"minimal device detuning {min(device_specs.detuning_range)}"
            )

        if max_detuning > max(device_specs.detuning_range):
            raise RydbergLayoutException(
                f"Maximum detuning in schedule {max_detuning} is above "
                f"maximum device detuning {max(device_specs.detuning_range)}"
            )

    def assert_rabi_device_specs(self, device_specs: AtomicDeviceSpecs):
        """
        Assert that the Rabi frequency schedule fits the device specs. Raises a
        `RydbergLayoutException` if the schedule cannot be implemented for the given device specs.

        :param device_specs: Device specifications of a machine
        """
        min_rabi = sympy.minimum(
            self.rabi_coefficient.subs(math.pi, sympy.pi),
            self.time_parameter,
            sympy.Interval(0, self.duration),
        )
        max_rabi = sympy.maximum(
            self.rabi_coefficient.subs(math.pi, sympy.pi),
            self.time_parameter,
            sympy.Interval(0, self.duration),
        )

        if min_rabi < min(device_specs.rabi_frequency_range):
            raise RydbergLayoutException(
                f"Minimum Rabi frequency in schedule {min_rabi} is below "
                f"minimal device Rabi frequency {min(device_specs.rabi_frequency_range)}"
            )

        if max_rabi > max(device_specs.rabi_frequency_range):
            raise RydbergLayoutException(
                f"Maximum Rabi frequency in schedule {max_rabi} is above "
                f"maximum device Rabi frequency {max(device_specs.rabi_frequency_range)}"
            )

    def __eq__(self, other: Self) -> bool:
        """ """
        if self is other:
            return True

        return (
            self.interactions_schedule == other.interactions_schedule
            and self.rabi_schedule == other.rabi_schedule
            and self.detuning_schedule == other.detuning_schedule
        )

    def __str__(self) -> str:
        return "\n +".join(
            [
                str(self.interactions_schedule),
                str(self.detuning_schedule),
                str(self.rabi_schedule),
            ]
        )

    def _compute_interactions_schedule(self, rydberg_atoms: RydbergAtoms) -> Schedule:
        r"""
        Compute the interactions term :math:`C_6/\hbar \sum_{i \neq j} r_{ij}^{-6} n_i n_j` as a
        :py:class:`ScheduleTerm` from a given :py:class:`RydbergAtoms` instance. The interaction
        coefficient is extracted from `DeviceSpecs` defined in `RydbergAtoms`.

        :param rydberg_atoms: Atoms for which to compute the interactions schedule
        :return: `Schedule` describing the interaction part of the Rydberg Hamiltonian
        """
        c6 = rydberg_atoms.device_specs.interaction_coefficient

        interaction_observable = sum(
            (
                c6
                / squared_distance(atom1.coordinate, atom2.coordinate) ** 3
                * (n_op(atom1.qubit) ^ n_op(atom2.qubit))
                for atom1, atom2 in itertools.combinations(rydberg_atoms.atoms, r=2)
            ),
            start=Observable([], []),
        )

        return Schedule(
            [ScheduleTerm(interaction_observable, sympy.Number(1.0))],
            self.time_parameter,
            self.duration,
        )

    def _compute_detuning_schedule(self, rydberg_atoms: RydbergAtoms) -> Schedule:
        r"""
        Compute the detuning term :math:`-\delta(t) \sum_i \delta_i n_i` as a
        :py:class:`ScheduleTerm`. The :math:`\delta_i` values are obtained from the `Detuning`
        values in the `rydberg_atoms`.

        :param rydberg_atoms: Atoms for which to compute the interactions schedule
        :return: `Schedule` describing the detuning part of the Rydberg Hamiltonian
        """
        detuning_obs = sum(
            (-atom.detuning.value * n_op(atom.qubit) for atom in rydberg_atoms.atoms),
            start=Observable([], []),
        )

        return Schedule(
            [ScheduleTerm(detuning_obs, self.detuning_coefficient)],
            self.time_parameter,
            self.duration,
        )

    def _compute_rabi_schedule(self, rydberg_atoms: RydbergAtoms) -> Schedule:
        r"""
        Compute the Rabi driving term
        :math:`\Omega(t)/2 \sum_i (cos(\phi(t)) X_i - sin(\phi(t)) Y_i)`
        as a :py:class:`ScheduleTerm`.

        :param rydberg_atoms: Atoms for which to compute the interactions schedule
        :return: `Schedule` describing the rabi frequency part of the Rydberg Hamiltonian (including
            laser phase)
        """
        x_obs = sum(
            (Observable([PauliOp([X(qubit)])], (1,)) for qubit in rydberg_atoms.qubits),
            start=Observable([], []),
        )
        y_obs = sum(
            (Observable([PauliOp([Y(qubit)])], (1,)) for qubit in rydberg_atoms.qubits),
            start=Observable([], []),
        )

        x_term = ScheduleTerm(
            x_obs, self.rabi_coefficient / 2 * sympy.cos(self.phase_coefficient)
        )
        y_term = ScheduleTerm(
            y_obs, -self.rabi_coefficient / 2 * sympy.sin(self.phase_coefficient)
        )

        return Schedule([x_term, y_term], self.time_parameter, self.duration)


def n_op(qubit: Qubit) -> Observable:
    r"""
    Rydberg number operator :math:`n_i = (1 + Z_i)/2` for a given Qubit as an
    :py:class:`Observable`. Here :math:`Z_i` denotes the Pauli-Z operator for a single qubit.

    :param qubit: Qubit for which to define the number operator
    :returns: :py:class:`Observable` defining :math:`n_i` for the given :py:class:`Qubit`
    """
    return Observable([PauliOp(), PauliOp([Z(qubit)])], (0.5, 0.5))
