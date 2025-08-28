"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Classes to describe the properties of quantum devices.
"""

from abc import ABC
from collections.abc import Iterable
from itertools import product, combinations

from parityos.base import Qubit, json_wrap, JSONType


class DeviceModelBase(ABC):
    """
    Abstract base model for describing quantum hardware.

    Attributes:
        qubit_connections: frozenset[frozenset[Qubit]]
            a list of connections (collections of qubits), which are the direct interactions
            that are available on the device.
        device_type: str
            the type of this device, can either be ``'cnot'`` or ``'plaquette'``
        preset: str
            Determines the parameters that are passed on to the compiler in order to optimize the
            code for the device. Standard values are ``'analog_default'`` and ``'digital_default'``.
            Customer-specific presets can be provided upon request.
    """

    qubit_connections = NotImplemented
    device_type = NotImplemented
    preset = NotImplemented

    def set_qubit_connections(
        self, qubit_connections: Iterable[Iterable[Qubit]], *, add_local_fields: bool = True
    ):
        """
        A helper function to initialize the qubit_connections field from an iterable.
        This method is used by the __init__ method in several subclasses.

        :param qubit_connections: a collection of connections (collections of qubits)
        :type qubit_connections: Iterable[Iterable[Qubit]]
        :param bool add_local_fields: Included for backwards compatibility. Indicates that there
            is a local field interaction for all qubits on the Device. Optional, defaults to True.
            A value that evaluates as False is no longer accepted. Future versions might drop
            this keyword argument.
        """
        assert add_local_fields, (
            "The Parity Compiler requires local fields on all qubits. "
            "Please set add_local_fields=True."
        )

        # Make sure that the connections are hashable
        qubit_connections = {frozenset(connection) for connection in qubit_connections}

        # Add the local fields on all qubits.
        qubits = set().union(*qubit_connections)
        local_fields = {frozenset({qubit}) for qubit in qubits}
        qubit_connections.update(local_fields)

        # Freeze the qubit connections and store them as an attribute.
        self.qubit_connections = frozenset(qubit_connections)

    @property
    def qubits(self) -> set[Qubit]:
        """
        :return: all qubits from the connections on the device
        """
        return set().union(*self.qubit_connections)

    def to_json(self) -> dict[str, JSONType]:
        """
        :return: the device model as json
        """
        return json_wrap(
            {
                "qubit_sites": self.qubits,
                "qubit_connections": self.qubit_connections,
                "device_type": self.device_type,
            }
        )


class RectangularDigitalDevice(DeviceModelBase):
    """
    Describes a digital rectangular quantum device.

    Attributes:
        qubit_connections: frozenset[frozenset[Qubit]]
            a list of connections (collections of qubits), which are the direct interactions
            that are available on the device.
        device_type: str
            the type of this device, can either be ``'cnot'`` or ``'plaquette'``
        preset: str
            Determines the parameters that are passed on to the compiler in order to optimize the
            code for the device. Standard value is ``'digital_default'``.
            Customer-specific presets can be provided upon request.
        shape: tuple(int, int)
            length and width of the rectangular device in number of qubits
    """

    device_type = "cnot"
    preset = "digital_default"

    def __init__(self, length: int, width: int):
        """
        :param int length: length of the rectangular lattice in qubits
        :param int width: width of the rectangular lattice in qubits
        """
        self.shape = length, width
        qubit_connections = set()
        # Add the horizontal connections
        for x, y in product(range(length - 1), range(width)):
            connection = {Qubit((x, y)), Qubit((x + 1, y))}
            qubit_connections.add(frozenset(connection))

        # Add the vertical connections
        for x, y in product(range(length), range(width - 1)):
            connection = {Qubit((x, y)), Qubit((x, y + 1))}
            qubit_connections.add(frozenset(connection))

        self.set_qubit_connections(qubit_connections)

    def __repr__(self):
        length, width = self.shape
        return f"{self.__class__.__name__}({length}, {width})"


class RectangularAnalogDevice(DeviceModelBase):
    """
    Describes an analog rectangular quantum device.

    Attributes:
        qubit_connections: frozenset[frozenset[Qubit]]
            a list of connections (collections of qubits), which are the direct interactions
            that are available on the device.
        device_type: str
            the type of this device, can either be ``'cnot'`` or ``'plaquette'``
        preset: str
            Determines the parameters that are passed on to the compiler in order to optimize the
            code for the device. Standard value is ``'analog_default'``.
            Customer-specific presets can be provided upon request.
        shape: tuple(int, int)
            length and width of the rectangular device in number of qubits
        include_triangles : bool, default=True
            If True, then qubit connections for all triangles on each plaquette are included.
    """

    device_type = "plaquette"
    preset = "analog_default"

    def __init__(self, length: int, width: int, include_triangles=True):
        """
        :param int length: length of the rectangular lattice in qubits
        :param int width: width of the rectangular lattice in qubits
        :param bool include_triangles: if True, then qubit connections for all triangles on each
            plaquette are included. Defaults to True.
        """
        self.shape = length, width
        self.include_triangles = include_triangles
        qubit_connections = set()
        # Add the plaquettes
        for x, y in product(range(length - 1), range(width - 1)):
            plaquette = {Qubit(label) for label in [(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)]}
            qubit_connections.add(frozenset(plaquette))
            if include_triangles:
                # Generate and add the 3-body plaquettes
                triangles = combinations(plaquette, 3)
                qubit_connections.update(frozenset(triangle) for triangle in triangles)

        self.set_qubit_connections(qubit_connections)

    def __repr__(self):
        length, width = self.shape
        args_kwargs = f"{length}, {width}, include_triangles={self.include_triangles}"
        return f"{self.__class__.__name__}({args_kwargs})"
