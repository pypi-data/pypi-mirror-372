"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2023-2025.
All rights reserved.
"""

from dataclasses import dataclass, field, asdict

from parityos import Qubit
from parityos.base.utils import JSONType
from parityos_addons.rydberg_layout.base.atom_coordinate import AtomCoordinate
from parityos_addons.rydberg_layout.base.detuning import Detuning


@dataclass(frozen=True)
class Atom:
    """
    Represents a single atom.

    :param coordinate: 3D coordinate in μm, for 2D coordinates put third entry to 0.0.
    :param qubit: assigned Qubit.
    :param detuning: Detuning value of the atom in rad/μs.
    """

    coordinate: AtomCoordinate
    qubit: Qubit
    detuning: Detuning = field(default_factory=Detuning)

    def to_json(self) -> JSONType:
        """
        :return: the AtomicDeviceSpecs as json
        """
        instance_as_dict = asdict(self)
        instance_as_dict["qubit"] = self.qubit.to_json()
        return instance_as_dict

    @classmethod
    def from_json(cls, data: JSONType) -> "Atom":
        """
        Makes an Atom object from a data

        :param data: an atom in json format
        :return: an Atom object
        """
        qubit = Qubit.from_json(data["qubit"])
        detuning = Detuning.from_json(data["detuning"])
        coordinate = AtomCoordinate.from_json(data["coordinate"])
        return cls(coordinate, qubit, detuning)
