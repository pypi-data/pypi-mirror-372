"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Classes that store information on sequences of quantum gates
"""

from collections.abc import Iterator, Mapping, Sequence
from math import pi
from typing import Union

from parityos.base.exceptions import ParityOSException
from parityos.base.gates import Gate, CNOT, RMixin, Rx, Ry, Rz, Rzz
from parityos.base.qubits import Qubit
from parityos.base.utils import json_wrap, JSONLoadSaveMixin, JSONType


class Circuit(JSONLoadSaveMixin, list):
    """
    A sequence of Gate and/or Circuit objects.
    """

    @property
    def qubits(self) -> set[Qubit]:
        """
        :return: All qubits from the elements in the circuit
        """
        return set().union(*(element.qubits for element in self))

    @property
    def parameters(self) -> set[str]:
        """
        :return: the set of parameters (strings)
        """
        parameters = set()
        for gate_or_circuit_element in self:
            if hasattr(gate_or_circuit_element, "parameters"):
                parameters.update(gate_or_circuit_element.parameters)

        return parameters

    def get_hermitian_conjugate(self) -> "Self":
        """
        Returns the Hermitian conjugate (inverse) of the circuit
        :return: a new Circuit instance
        """
        return type(self)(element.get_hermitian_conjugate() for element in reversed(self))

    def generate_flat_gate_sequence(self) -> Iterator[Gate]:
        """
        Generates a sequence of all gates in the circuit and its subcircuits.

        :returns: A generator that loops over all gates in the circuit and its subcircuits.
        """
        for element in self:
            if isinstance(element, Gate):
                yield element
            else:
                yield from element.generate_flat_gate_sequence()

    @classmethod
    def from_json(cls, data: Sequence[Sequence[JSONType]]) -> "Self":
        """
        Creates a Circuit from a list of elements in json

        :param data: a list of elements in json format
        :return: a Circuit object
        """
        args = (
            (
                Gate.from_json(element_data)
                if isinstance(element_data[0], str)
                else cls.from_json(element_data)
            )
            for element_data in data
            if element_data
        )
        return cls(args)

    def to_json(self) -> list[JSONType]:
        """
        Converts the Container to json

        :return: a list with the elements of the circuit in json format
        """
        return [json_wrap(element) for element in self]

    def remap(self, context: Mapping = None, **kwargs) -> "Circuit":
        """
        Creates a copy of the circuit where the remap has been applied to all parametrized gates
        in the circuit (see `gates.RMixin.remap` for details).

        :param context: a mapping of parameter names (strings) to parameter values (number-like
                        objects) or to new parameter names (strings).
        """
        return Circuit((element.remap(context=context, **kwargs) for element in self))

    def modify_angle(
        self,
        angle_map: Mapping[frozenset[Qubit], float],
        gate_type: type[RMixin] = None,
        parameter_name: str = None,
    ) -> "Self":
        """
        Create a new circuit with the same subcircuits and gates as this one, except for the
        rotation gates of the given gate type and with the given parameter_name as parameter,
        for which the angle will be changed to the values given by the angle map, in function
        of the qubit(s) on which the gate acts. If the qubit(s) are not included in the angle map,
        then the angle is left unchanged.

        If the gate type is not specified, then all rotation gates might be affected. If the
        parameter name is not specified, then also gates without parameters might be affected.

        :param angle_map: A mapping that provides a new angle for each of the qubit sets on which
                          the gates might act.
        :param gate_type: Optional. If given, then only gates of this type will be updated. Other
                          gates will be copied into the new circuit without changes. Default is
                          None.
        :param parameter_name: Optional. If given, then only gates with this parameter name will be
                               updated. Other gates will be copied into the new circuit without
                               changes. Default is None.

        :returns: A new circuit with all the gates copied over from the current circuit, except for
                  selected rotation gates for which the rotation angle will have been modified.
                  Default is None.

        """
        return type(self)(
            element.modify_angle(angle_map, gate_type=gate_type, parameter_name=parameter_name)
            for element in self
        )

    def __repr__(self):
        args = ", ".join(repr(element) for element in self)
        return f"{self.__class__.__name__}([{args}])"

    def __add__(self, other):
        return type(self)(list.__add__(self, other))

    def __mul__(self, other):
        return type(self)(list.__mul__(self, other))

    def __rmul__(self, other):
        return type(self)(list.__rmul__(self, other))

    def __getitem__(self, key):
        # Convert slices of circuits to again to Circuits
        item = list.__getitem__(self, key)
        return type(self)(item) if isinstance(key, slice) else item


CircuitElement = Union[Gate, Circuit]
HALF_PI = 0.5 * pi


def convert_cnots_to_rzzs(circuit: Circuit) -> Circuit:
    """
    ZZ rotations instead of CNOTs.

    Replaces the standards CNOTs on the optimized circuit with an equivalent implementation based on
    ZZ and local rotations. The resulting circuit will contain additional subcircuits to account
    for the necessary Rx, Ry and Rz rotations.

    :param circuit: a circuit containing moments with CNOT gates.
    :type circuit: Circuit
    :return: a new circuit where all CNOTs have been replaced by ZZ and local rotations.
    :rtype: Circuit
    """
    new_circuit = Circuit()
    for subcircuit in circuit:
        if not isinstance(subcircuit, Circuit):
            # This situation can occur when gates and subcircuits were mixed together at the same
            # level. We raise an error in this case, because this method expects gates to be grouped
            # in moments (i.e. parallelizable subcircuits).
            raise ParityOSException(
                "Unexpected mix of gates and subcircuits encountered. Please "
                "organize gates in moments (parallelizable subcircuits)."
            )
        elif all(isinstance(element, Gate) for element in subcircuit):
            new_circuit.extend(_convert_moment(subcircuit))
        else:
            new_circuit.append(convert_cnots_to_rzzs(subcircuit))

    return new_circuit


def _convert_moment(circuit) -> Iterator[Circuit]:
    """
    A helper function for convert_cnots_to_rzzs.
    Lowest level circuits are expanded and have cnots turned into rzzs. This results in additional
    circuits to be added before and after the moment circuit to account for the necessary Rx, Ry
    and Rz rotations.

    :return: a list of circuits representing the original circuit where cnots have been converted to
        rzz gates.
    """
    before, moment, after1, after2 = Circuit(), Circuit(), Circuit(), Circuit()
    # Representing a Cnot as a ZZ interaction requires the injection of a moment before and two
    # moments after the original moment.
    for gate in circuit:
        if not isinstance(gate, CNOT):
            # Copy the other gates directly to the new moment.
            moment.append(gate)
        else:
            control, target = gate.make_args()
            # Add the necessary rotation before the ZZ interaction.
            before.append(Ry(target, -HALF_PI))
            # Replace the CNOT with a ZZ rotation.
            moment.append(Rzz(control, target, -HALF_PI))
            # Add the remaining rotations after the ZZ interaction.
            after1.append(Rx(target, HALF_PI))
            after2.append(Rz(control, HALF_PI))
            after2.append(Rz(target, HALF_PI))

    return (subcircuit for subcircuit in [before, moment, after1, after2] if subcircuit)
