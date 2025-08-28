"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Tools to connect to the ParityOS cloud services and to process the results.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from parityos.base.qubits import Qubit
from parityos.base.utils import json_wrap, JSONMappingType, JSONType


@dataclass(frozen=True)
class ParityMap:
    """
    A class that represents a set of qubits and a parity value,
    to facilitate serialization of Mappings.
    """

    qubits: frozenset[Qubit]
    parity: int

    @classmethod
    def from_json(cls, data: Sequence[JSONType]) -> "Self":
        """
        Initializes a ParityMap object from json

        :param data: parity map in json format
        :return: A ParityMap instance
        """
        qubits_data, parity = data
        qubits = frozenset(Qubit(label) for label in qubits_data)
        return cls(qubits, parity)

    def to_json(self) -> list[JSONType]:
        """
        Converts a Parity Map object to json

        :return: the parity map in json format
        """
        return json_wrap([self.qubits, self.parity])


@dataclass(frozen=True)
class Mappings:
    """
    Holds the Parity Architecture encoding and decoding maps returned from the API.

    :param encoding_map: the encoding map, which tells you how to go from each physical qubit
                         to the logical qubits that it encodes.
    :param decoding_map: A possible decoding map, which tells you how to go from a logical
                         qubit to a list of physical qubits that multiply to the logical
                         qubit.
    """

    encoding_map: dict[Qubit, ParityMap]
    decoding_map: dict[Qubit, ParityMap]

    def to_json(self) -> dict[str, JSONType]:
        """
        Converts a Mappings object to json

        :return: the mappings in json format
        """
        return json_wrap(
            {
                "encoding_map": self.encoding_map.items(),
                "decoding_map": self.decoding_map.items(),
            }
        )

    @property
    def logical_degeneracies(self) -> list[ParityMap]:
        """
        Logical degeneracies are symmetries in the logical Hamiltonian and show up in the decoding
        map as entries where the map does not have any qubits. The logical Hamiltonian is
        equivalent to a Hamiltonian where the logical degeneracies are mapped out using their
        trivial mapping to a parity.
        """
        return [
            ParityMap(frozenset([qubit]), parity_map.parity)
            for qubit, parity_map in self.decoding_map.items()
            if not parity_map.qubits
        ]

    @classmethod
    def from_json(cls, data: JSONMappingType) -> "Self":
        """
        Constructs a Mappings object from json data

        :param data: the mappings in json format
        :return: a Mappings object
        """

        encoding_map = {
            Qubit(coordinate): ParityMap.from_json(parity_map_data)
            for coordinate, parity_map_data in data["encoding_map"]
        }
        # This only works if the original qubit labels were numbers or strings
        decoding_map = {
            Qubit(qubit): ParityMap.from_json(parity_map_data)
            for qubit, parity_map_data in data["decoding_map"]
        }
        return cls(encoding_map, decoding_map)
