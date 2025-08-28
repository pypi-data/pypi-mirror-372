# ParityQC © 2025. See the LICENSE file in the top level directory for details.

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence

from parityos_addons.rydberg_layout.base.atom_coordinate import (
    AtomCoordinate,
    centroid_from_coordinates,
    squared_distance,
)


@dataclass
class DeviceGeometry(ABC):
    """
    The base class for describing neutral atom devices.
    """

    @abstractmethod
    def fit_coordinates(self, coordinates: Sequence[AtomCoordinate]) -> bool:
        """
        Returns whether the coordinates (corresponding to an atom placement) fit on this device

        :param coordinates: A sequence of coordinates to check if they fit on the device.
        :returns: True if all coordinates fit on the device, False otherwise
        """


@dataclass
class RectangularDevice(DeviceGeometry):
    """
    A two-dimensional rectangular device

    :param x: Horizontal size of the device in µm.
    :param y: Vertical size of the device in µm.
    """

    x: float
    y: float

    def fit_coordinates(self, coordinates: Sequence[AtomCoordinate]) -> bool:
        """
        Returns whether the coordinates (corresponding to an atom placement) fit on this device

        :param coordinates: A sequence of coordinates to check if they fit on the device.
        :returns: True if all coordinates fit on the device, False otherwise
        """
        # Check that the coordinates are two-dimensional (z-component is zero).
        if any(coordinate.z != 0.0 for coordinate in coordinates):
            return False

        # Check that the largest difference in x and y fits on the device.
        maximum_x = max(coordinate.x for coordinate in coordinates)
        minimum_x = min(coordinate.x for coordinate in coordinates)

        maximum_y = max(coordinate.y for coordinate in coordinates)
        minimum_y = min(coordinate.y for coordinate in coordinates)

        if maximum_x - minimum_x > self.x or maximum_y - minimum_y > self.y:
            return False

        return True


@dataclass
class CircularDevice(DeviceGeometry):
    """
    A two-dimensional circular device.

    :param radius: Radial size of the device in µm.
    """

    radius: float = 50.0

    def fit_coordinates(self, coordinates: Sequence[AtomCoordinate]) -> bool:
        """
        Returns whether the coordinates (corresponding to an atom placement) fit on this device

        :param coordinates: A sequence of coordinates to check if they fit on the device.
        :returns: True if all coordinates fit on the device, False otherwise
        """
        # Check that the coordinates are two-dimensional (z-component is zero).
        if any(coordinate.z != 0.0 for coordinate in coordinates):
            return False

        # Add a small value to allow rounding errors
        max_radial_square_distance_allowed = self.radius**2 + 1e-9

        # Check whether any coordinate is too far away from the centroid of the coordinates.
        centroid = centroid_from_coordinates(coordinates)
        if any(
            squared_distance(coordinate, centroid) > max_radial_square_distance_allowed
            for coordinate in coordinates
        ):
            return False

        return True
