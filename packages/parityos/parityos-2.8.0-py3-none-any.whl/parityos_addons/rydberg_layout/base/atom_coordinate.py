"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2023-2025.
All rights reserved.
"""

import math
from dataclasses import dataclass, asdict
from functools import cached_property
from typing import Sequence

from typing_extensions import TypeAlias

from parityos.base.utils import JSONType

Coordinate: TypeAlias = tuple[float, float, float]


@dataclass(frozen=True, order=True)
class AtomCoordinate:
    """
    3D Coordinate for atoms.

    :param x: x coordinate.
    :param y: y coordinate.
    :param z: z coordinate.
    """

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def to_json(self) -> JSONType:
        """
        :return: the AtomicCoordinate as json
        """
        return asdict(self)

    @classmethod
    def from_json(cls, data: JSONType) -> "AtomCoordinate":
        """
        Makes an AtomCoordinate object from a data

        :param data: an AtomCoordinate in json format
        :return: an AtomCoordinate object
        """
        return cls(**data)

    @cached_property
    def norm(self) -> float:
        """
        Norm/length of the coordinate
        """
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)


def centroid_from_coordinates(coordinates: Sequence[AtomCoordinate]):
    """
    Calculates the centroid of the given coordinates.

    :param coordinates: a sequence of AtomCoordinates
    :return: Coordinate of the centroid
    """
    average_x = sum(coordinate.x for coordinate in coordinates) / len(coordinates)
    average_y = sum(coordinate.y for coordinate in coordinates) / len(coordinates)
    average_z = sum(coordinate.z for coordinate in coordinates) / len(coordinates)

    return AtomCoordinate(average_x, average_y, average_z)


def squared_distance(
    coordinate_1: AtomCoordinate, coordinate_2: AtomCoordinate
) -> float:
    """
    The squared distance between two coordinates
    """
    dx = coordinate_1.x - coordinate_2.x
    dy = coordinate_1.y - coordinate_2.y
    dz = coordinate_1.z - coordinate_2.z

    return dx * dx + dy * dy + dz * dz
