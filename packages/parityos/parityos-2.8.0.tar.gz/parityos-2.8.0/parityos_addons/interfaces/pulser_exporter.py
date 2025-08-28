"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2024-2025.
All rights reserved.

Tools to export ParityOS RydbergSchedules, RydbergAtoms to pulser.
"""

import numbers
from typing import Sequence, Union

import pulser

from parityos import Qubit
from parityos_addons.rydberg_layout.base.atom import Atom
from parityos_addons.rydberg_layout.base.exceptions import RydbergLayoutException
from parityos_addons.rydberg_layout.schedule.rydberg_schedule import RydbergSchedule


def atoms_to_pulser_register(
    atoms: Sequence[Atom], qubit_index_map: dict[Qubit, int] = None
) -> Union[pulser.Register, pulser.Register3D]:
    """
    Converts atoms to a pulser register. Note, detunings of the atoms are ignored in this step.
    If all atom z-coordinates are 0, a 2D register is created, otherwise a 3D register.

    :param atoms: Atoms.
    :param qubit_index_map: map from parityos.Qubit to indexes that will be passed to
                            pulser.Register. If not given parityos.Qubit.labels will be used.
    :return: pulser.Register instance for 2D layouts, pulser.Register3D instance for 3D layouts.
    """

    if all(abs(atom.coordinate.z) < 1e-12 for atom in atoms):
        coordinates = [(atom.coordinate.x, atom.coordinate.y) for atom in atoms]
        register_class = pulser.Register
    else:
        coordinates = [
            (atom.coordinate.x, atom.coordinate.y, atom.coordinate.z) for atom in atoms
        ]
        register_class = pulser.Register3D

    if qubit_index_map:
        return register_class(
            {
                qubit_index_map[atom.qubit]: coordinate
                for atom, coordinate in zip(atoms, coordinates)
            }
        )
    else:
        return register_class(
            {
                str(atom.qubit.label): coordinate
                for atom, coordinate in zip(atoms, coordinates)
            }
        )


def rydberg_schedule_to_pulse(
    schedule: RydbergSchedule, times: list[int] = None, interpolator_kwargs=None
) -> pulser.Pulse:
    """
    Converts the given RydbergSchedule object to the pulser.Pulse object.

    :param schedule: RydbergSchedule
    :param times: list of time points for interpolation. If it is not given we will
                  use range(0, schedule.duration + 1, 2) as the default value
    :param interpolator_kwargs: kwargs that should be passed to pulser.InterpolatedWaveform
    :return: the corresponding pulser.Pulse
    """
    duration = int(schedule.duration)

    if not times:
        times = range(0, duration + 1, 2)
    times_normalized = [float(time) / duration for time in times]

    amplitudes = [
        schedule.rabi_coefficient.subs(schedule.time_parameter, time) for time in times
    ]

    if any(
        detuning != schedule.atom_detunings[0] for detuning in schedule.atom_detunings
    ):
        raise RydbergLayoutException(
            "Export of rydberg schedules with different atom detunings is not supported."
        )
    detunings = [
        schedule.atom_detunings[0]
        * schedule.detuning_coefficient.subs(schedule.time_parameter, time)
        for time in times
    ]

    if (
        isinstance(schedule.phase_coefficient, numbers.Number)
        or schedule.phase_coefficient.is_number
    ):
        phase = float(schedule.phase_coefficient)
    else:
        raise ValueError("Only constant phases are supported.")

    if not interpolator_kwargs:
        interpolator_kwargs = {"interpolator": "PchipInterpolator"}

    amplitudes_wf = pulser.InterpolatedWaveform(
        duration, amplitudes, times=times_normalized, **interpolator_kwargs
    )

    detunings_wf = pulser.InterpolatedWaveform(
        duration, detunings, times=times_normalized, **interpolator_kwargs
    )

    return pulser.Pulse(amplitudes_wf, detunings_wf, phase)
