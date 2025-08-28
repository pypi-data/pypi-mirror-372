"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2023-2025.
All rights reserved.
"""

from dataclasses import dataclass
from functools import cached_property

from parityos import Qubit
from parityos.base.utils import JSONType

from parityos_addons.rydberg_layout.base.atom import Atom
from parityos_addons.rydberg_layout.base.atom_coordinate import AtomCoordinate
from parityos_addons.rydberg_layout.base.detuning import Detuning
from parityos_addons.rydberg_layout.base.device.atomic_device_specs import (
    AtomicDeviceSpecs,
)
from parityos_addons.rydberg_layout.base.exceptions import RydbergLayoutException


@dataclass(frozen=True)
class RydbergAtoms:
    """
    Represents Atoms that are positioned in the device.
    """

    atoms: list[Atom]
    device_specs: AtomicDeviceSpecs

    def __post_init__(self):
        # Check that there are enough atoms on the device.
        if len(self.atoms) > self.device_specs.max_atom_count:
            raise RydbergLayoutException(
                "The device does not support the number of atoms."
            )

        # Check that the device can fit the atoms
        self.device_specs.assert_atoms_compatible(self.atoms)

    @cached_property
    def coordinates(self) -> list[AtomCoordinate]:
        """
        :return: the coordinates of the atoms.
        """
        return [a.coordinate for a in self.atoms]

    @cached_property
    def detunings(self) -> list[Detuning]:
        """
        :return: the detunings of the atoms.
        """
        return [a.detuning for a in self.atoms]

    @cached_property
    def qubits(self) -> set[Qubit]:
        """
        :return: the qubits that are defined in atoms. Note, some atoms might have the same qubit.
        """
        return {a.qubit for a in self.atoms}

    @cached_property
    def qubit_atoms_map(self) -> dict[Qubit, list[Atom]]:
        """
        :return: A map from qubits to a list of all atoms that contain this qubit.
        """
        _qubit_atoms_map = {qubit: [] for qubit in self.qubits}
        for atom in self.atoms:
            _qubit_atoms_map[atom.qubit].append(atom)

        return _qubit_atoms_map

    @classmethod
    def from_json(
        cls, data: JSONType, device_specs: AtomicDeviceSpecs
    ) -> "RydbergAtoms":
        """
        Create a RydbergAtoms instance from a json input containing atom information and
        device specs.

        :param data: Serialized atoms data {'atoms': [Atom.to_json(), ...]}.
        :param device_specs: Rydberg device specifications.
        """
        atoms = [Atom.from_json(atom_data) for atom_data in data["atoms"]]
        return cls(atoms, device_specs)

    def __len__(self):
        return len(self.atoms)

    def __add__(self, other: "RydbergAtoms") -> "RydbergAtoms":
        if self.device_specs != other.device_specs:
            raise RydbergLayoutException(
                "Addition is only defined for identical DeviceSpecs."
            )

        return RydbergAtoms(self.atoms + other.atoms, self.device_specs)
