"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Defines the Qubit class, which is used to label the qubits on a quantum device.
"""

from dataclasses import dataclass
from typing import Hashable, Iterable, Union

from parityos.base.utils import json_wrap, JSONType

# Type hint for coordinates of the form (1, 0), (0, -1, 1), ...
Coordinate = tuple[int, ...]  # type: TypeAlias
# One can also use strings or integers as qubit labels
QubitLabel = Union[int, str, Coordinate]  # type: TypeAlias


@dataclass(frozen=True)
class Qubit:
    """
    Represents a qubit, can be a physical qubit or a logical qubit.

    :param label: The label of a qubit, can be either a string, an integer or a coordinate,
        such that it can be converted to a hashable form and exported to json.
        In the case of a coordinate, it is also possible to initialize it directly from json
        format, which for a tuple would be a list. This means that if you pass label = [2, 2],
        it will be converted to the coordinate label (2, 2).
    """

    label: QubitLabel

    def __post_init__(self):
        if not isinstance(self.label, (str, int)):
            # In this case the label is supposed to be an iterable.
            # We convert it to a tuple to make it hashable. Because this is a frozen dataclass,
            # we have to use super().__setattr__ to change the label.
            super().__setattr__("label", make_hashable(self.label))

    @classmethod
    def from_json(cls, qubit_in_json: JSONType) -> "Self":
        """
        Makes a Qubit object from a qubit in json

        :param qubit_in_json: a qubit in json format
        :return: a Qubit object
        """
        return cls(qubit_in_json)

    def to_json(self) -> JSONType:
        """
        :return: qubit in json form
        """
        return json_wrap(self.label)

    def __lt__(self, other: "Self") -> bool:
        # This function is implemented to allow sorted to be used on a collection of qubits.
        # If the qubit labels are of the same type, then normal ordering is used.
        # For distinct types of labels, the labels are converted to strings before comparing them.
        try:
            return self.label < other.label
        except TypeError:
            return str(self.label) < str(other.label)

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.label)})"


def make_hashable(item: Union[Hashable, Iterable]) -> Hashable:
    """
    Convert the given item to a hashable object. If the item is a non-hashable sequence, then
    it will be converted to a tuple recursively. This means that also all its elements will be
    converted to tuples if they are non-hashable sequences.
    """
    try:
        hash(item)
        return item
    except TypeError:  # item was not hashable, so we replace it by a tuple.
        return tuple(make_hashable(element) for element in item)
