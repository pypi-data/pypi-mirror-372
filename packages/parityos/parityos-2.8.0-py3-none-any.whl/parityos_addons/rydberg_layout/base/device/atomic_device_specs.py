"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2023-2025.
All rights reserved.
"""

import math
from dataclasses import asdict, dataclass
from typing import Sequence


from parityos.base.utils import JSONType, json_wrap
from parityos_addons.rydberg_layout.base.atom import Atom
from parityos_addons.rydberg_layout.base.atom_coordinate import squared_distance

from parityos_addons.rydberg_layout.base.device.device_geometry import (
    DeviceGeometry,
)
from parityos_addons.rydberg_layout.base.exceptions import (
    RydbergLayoutException,
    UnsupportedDeviceSpecs,
)


@dataclass(frozen=True)
class AtomicDeviceSpecs:
    """
    Describes the specifications of the physical neutral atoms device.

    :param device_geometry: The geometry of the device, by default a two-dimensional rectangular
        device.
    :param min_atom_distance: The smallest allowed separation between any two atoms (in μm).
    :param max_atom_count: Maximum number of available atoms.
    :param interaction_coefficient: Van-der-Waals interaction coefficient C_6/hbar
        (in  rad/µs x µm^6).
    :param detuning_range: Allowed range for the detuning (in rad/μs)
    :param rabi_frequency_range: Allowed range for the Rabi frequency (in rad/μs)
    """

    device_geometry: DeviceGeometry
    min_atom_distance: float = 5
    max_atom_count: int = 500
    interaction_coefficient: float = 5.42e6
    detuning_range: tuple[float, float] = (-20.0 * 2 * math.pi, 20.0 * 2 * math.pi)
    rabi_frequency_range: tuple[float, float] = (0, 4.0 * 2 * math.pi)

    def __post_init__(self):
        if self.detuning_range[0] > self.detuning_range[1]:
            raise UnsupportedDeviceSpecs(
                f"{self.detuning_range=} must be in increasing order."
            )
        if self.rabi_frequency_range[0] > self.rabi_frequency_range[1]:
            raise UnsupportedDeviceSpecs(
                f"{self.rabi_frequency_range=} must be in increasing order."
            )

    def assert_atoms_compatible(self, atoms: Sequence[Atom]):
        """
        Checks whether the given sequence of atoms is compatible with the device specs.
        Raises a RydbergLayoutException if the sequence is not compatible.
        """
        self._assert_min_atom_distance(atoms)
        self._assert_device_large_enough(atoms)
        self._assert_detuning_range(atoms)

    def to_json(self) -> JSONType:
        """
        :return: the AtomicDeviceSpecs as json
        """
        return json_wrap(asdict(self))

    def _assert_min_atom_distance(self, atoms: Sequence[Atom]):
        """
        Checks that the minimum atom distance is correctly kept for these atoms
        """
        assert_min_atom_distance(atoms, self.min_atom_distance)

    def _assert_device_large_enough(self, atoms: Sequence[Atom]):
        """
        Check that the device is large enough to fit the atoms
        """
        if not self.device_geometry.fit_coordinates(
            [atom.coordinate for atom in atoms]
        ):
            raise RydbergLayoutException(
                "The layout of atoms does not fit the device geometry."
            )

    def _assert_detuning_range(self, atoms: Sequence[Atom]):
        """
        Check that the detunings of the atoms are within the device limitations
        """
        for atom in atoms:
            if (
                atom.detuning.value < self.detuning_range[0]
                or atom.detuning.value > self.detuning_range[1]
            ):
                raise RydbergLayoutException(
                    "The detunings of the atom are not in the range of allowed detunings "
                    "for the device."
                )


def assert_min_atom_distance(atoms: Sequence[Atom], min_atom_distance: float):
    """
    Checks that the minimum atom distance is correctly kept for these atoms
    """
    # Subtract a small value to allow rounding errors
    min_atom_distance_allowed = min_atom_distance - 1e-9
    min_squared_distance_allowed = min_atom_distance**2 - 1e-9

    # Calculate the sorted coordinates to not have to take all combinations of atoms,
    # but instead can start by comparing the x values.
    sorted_coordinates = sorted(atom.coordinate for atom in atoms)
    start_index = 0
    end_index = 1
    max_index = len(sorted_coordinates) - 1
    while start_index < max_index:
        start = sorted_coordinates[start_index]
        end = sorted_coordinates[end_index]
        if end.x - start.x >= min_atom_distance_allowed:
            # If the x values are already larger than the atom distance, we don't have to look
            # at the y/z values. Also, we don't have to compare the start to any further end,
            # because all those will have a larger x difference.
            start_index += 1
            end_index = start_index + 1
        elif squared_distance(start, end) > min_squared_distance_allowed:
            # Distance is fine, so we increase end_index if it is still below the maximum index,
            # but if we got to the end of the list, we move on to the next start index.
            if end_index < max_index:
                end_index += 1
            else:
                start_index += 1
                end_index = start_index + 1
        else:
            raise RydbergLayoutException(
                f"The minimum atom distance {min_atom_distance} is violated."
            )
