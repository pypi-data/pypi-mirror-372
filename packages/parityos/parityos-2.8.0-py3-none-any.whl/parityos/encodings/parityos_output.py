"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Container class for the results from the ParityOS compiler.
"""

import warnings

from parityos.base import ParityOSException, ProblemRepresentation
from parityos.base.circuit import Circuit, convert_cnots_to_rzzs
from parityos.base.gates import Rz
from parityos.base.utils import dict_filter, json_wrap, JSONLoadSaveMixin, JSONMappingType, JSONType
from parityos.encodings.mappings import Mappings, ParityMap
from parityos.encodings.parity_decoder import ParityDecoderExtension
from parityos.encodings.parity_encoder import ParityEncoderExtension


class ParityOSOutput(JSONLoadSaveMixin, ParityEncoderExtension, ParityDecoderExtension):
    def __init__(
        self,
        compiled_problem: ProblemRepresentation,
        mappings: Mappings,
        constraint_circuit: Circuit = None,
        problem_circuit: Circuit = None,
        driver_circuit: Circuit = None,
        initial_state_preparation_circuit: Circuit = None,
    ):
        r"""
        This class contains all the output that ParityOS produces, this may be extended
        with extra features in the future, but for now it contains the compiled problem,
        the mappings and in case of digital devices also the constraint circuit.

        :param compiled_problem: compiled problem representation with parity constraints
        :param mappings: Mappings object representing the mapping between the logical
                         and the physical problem.
        :param constraint_circuit: constraint Circuit (:math:`e^{-i \theta Z_1 Z_2 Z_3 [Z_4] /2}` )
                                   for digital devices or None for analog devices.
        :param problem_circuit: problem circuit implementing the spin Hamiltonian corresponding to
                                the logical problem for digital devices or None for analog devices.
        :param driver_circuit: optional driver Circuit for digital devices
                               or None for analog devices.
        :param initial_state_preparation_circuit: The initial-state preparation circuit tells
            how to make the initial state, starting from the computational basis state
            :math:`|0\langle^K`. For normal QAOA, one would want to start in the
            :math:`|+\langle^K` state for all qubits, so it would be a combination of RX and RZ
            or a Hadamard. The gates in this circuit are fixed,
            as they do not have a QAOA parameter, but should be executed with this exact angle.
        """
        self.compiled_problem = compiled_problem
        self.mappings = mappings
        self.constraint_circuit = constraint_circuit
        self.problem_circuit = problem_circuit
        self.driver_circuit = driver_circuit
        self.initial_state_preparation_circuit = initial_state_preparation_circuit

    @property
    def logical_problem_circuit(self) -> Circuit:
        """
        The same as self.problem_circuit, for compatibility.
        """
        warnings.warn(
            "ParityOSOutput.logical_problem_circuit is being deprecated. "
            "Please use ParityOSOutput.problem_circuit instead. "
            "The logical_problem_circuit property will be removed in the future.",
            DeprecationWarning,
        )
        return self.problem_circuit

    def create_default_problem_circuit(self) -> Circuit:
        """
        Create a circuit that implements $ \\exp(i \\mbox{parameter} H) $, where H is the
        spin Hamiltonian of the compiled problem representation. This spin Hamiltonian encodes
        the spin interactions of the original problem representation. Equality conditions from
        the original problem representation will have been absorbed in the parity constraints,
        for which the `constraint_circuit` attribute provides a separate circuit.

        :return: a Circuit instance that implements the exponential of the Hamiltonian.
        """
        warnings.warn(
            "ParityOSOutput.create_default_problem_circuit should no longer be used and "
            "will be removed in the future. The ParityOSOutput now always contains a "
            "ParityOSOutput.problem_circuit attribute. ",
            DeprecationWarning,
        )
        moment = Circuit()
        for interaction, strength in self.compiled_problem.terms:
            if len(interaction) == 1:
                [qubit] = interaction  # Grab the first and only element from the interaction
                moment.append(Rz(qubit, strength, parameter_name="parameter"))
            else:
                missing_gate = f"R{'z' * len(interaction)}"
                raise NotImplementedError(f"{missing_gate} gate not available")

        return Circuit([moment])

    def replace_cnots_by_rzzs(self):
        """
        Replace the CNOT gates in self.constraint_circuit by ZZ and local rotations.
        This is useful for devices that have native ZZ rotations instead of native CNOTs.
        It replaces the self.constraint_circuit attribute in place.
        """
        self.constraint_circuit = convert_cnots_to_rzzs(self.constraint_circuit)

    @classmethod
    def from_json(cls, data: JSONMappingType) -> "Self":
        """
        Creates the ParityOSOutput class from the format in the response schema.

        :param data: a JSON-like dictionary as specified in the response schema.
        :return: a ParityOSOutput object
        """
        # We reorganize the JSON data to match the definitions of CompiledProblem:
        # the 'hamiltonian' field in 'compiled_problem' is flattened.
        # Once the JSON schema has been updated in the API, these lines can be removed.
        compiled_problem_data = data["compiled_problem"]
        if "hamiltonian" in compiled_problem_data:
            compiled_problem_data = {
                **compiled_problem_data["hamiltonian"],
                **dict_filter(compiled_problem_data, {"constraints"}),
            }

        kwargs = {
            "compiled_problem": ProblemRepresentation.from_json(compiled_problem_data),
            "mappings": Mappings.from_json(data["mappings"]),
        }
        optimization_data = data.get("optimization", {})
        for key in {
            "constraint_circuit",
            "problem_circuit",
            "driver_circuit",
            "initial_state_preparation_circuit",
        }:
            circuit_data = optimization_data.get(key)
            if circuit_data:
                kwargs[key] = Circuit.from_json(circuit_data)

        return cls(**kwargs)

    def to_json(self) -> dict[str, JSONType]:
        """
        Repackages self into the response schema dictionary.

        :return: dictionary as specified in the response schema
        """
        data_map = {
            "compiled_problem": self.compiled_problem,
            "mappings": self.mappings,
        }
        optimization = {
            "constraint_circuit": self.constraint_circuit,
            "problem_circuit": self.problem_circuit,
            "driver_circuit": self.driver_circuit,
            "initial_state_preparation_circuit": self.initial_state_preparation_circuit,
        }
        optimization = {key: value for key, value in optimization.items() if value}
        if optimization:
            data_map["optimization"] = optimization

        return json_wrap(data_map)

    def __repr__(self):
        args = (
            self.compiled_problem,
            self.mappings,
            self.constraint_circuit,
            self.problem_circuit,
            self.driver_circuit,
            self.initial_state_preparation_circuit,
        )
        return f"{self.__class__.__name__}{args}"

    def encode_problem(self, problem_representation: ProblemRepresentation) -> "Self":
        """
        Creates a new ParityOSOutput instance that encodes the logical problem
        representation given as an argument, but expressed in terms of the physical qubits and
        the parity constraints contained in the original ParityOSOutput instance.

        :param problem_representation: A new problem representation whose interactions are
                                       compatible with the compiled problem of the ParityOSOutput.

        :returns: a new ParityOSOutput instance where the interaction coefficients are updated
                  to the ones from the new problem representation. The mappings are copied from
                  the original ParityOS output. If circuits are included in the original instance,
                  then these are copied to the new instance, with updated angles for the
                  parametrized gates in the problem circuit.
        """
        # Encode the new problem representation
        # The inverse_encoding_map maps parity qubits onto combinations of logical qubits.
        # It does not necessarily coincide with self.mappings.decoding_map because of degeneracies
        # and ancilla qubits.
        inverse_encoding_map = {
            logical_map.qubits: ParityMap(frozenset({parity_interaction}), logical_map.parity)
            for parity_interaction, logical_map in self.mappings.encoding_map.items()
        }
        try:
            encoded_interactions = [
                inverse_encoding_map[interaction]
                for interaction in problem_representation.interactions
            ]
        except KeyError as key_error:
            raise ParityOSException(
                "The given problem representation is not compatible with "
                "the compiled one. Please make a new compilation for the"
                "given problem representation."
            ) from key_error

        # The encoded_problem_map maps parity qubits onto the coefficient that they would have
        # in the compilation result of the new problem representation.
        encoded_problem_map = {
            parity_map.qubits: coefficient * parity_map.parity
            for parity_map, coefficient in zip(
                encoded_interactions, problem_representation.coefficients
            )
        }
        encoded_problem = ProblemRepresentation(
            self.compiled_problem.interactions,
            [
                encoded_problem_map.get(parity_interaction, 0)
                for parity_interaction in self.compiled_problem.interactions
            ],
            constraints=self.compiled_problem.constraints,
        )
        # If the ParityOSOutput instance has a `problem_circuit` attribute, then we update
        # the angles in its parametrized circuits to the new coefficients.
        if self.problem_circuit:
            parameter_name, *_ = self.problem_circuit.parameters
            # Update the angles for all parameterized Rz gates with the same parameter name
            encoded_problem_circuit = self.problem_circuit.modify_angle(
                angle_map=dict(encoded_problem.terms),
                gate_type=Rz,
                parameter_name=parameter_name,
            )
        else:
            encoded_problem_circuit = None

        return ParityOSOutput(
            encoded_problem,
            self.mappings,
            self.constraint_circuit,
            encoded_problem_circuit,
            self.driver_circuit,
            self.initial_state_preparation_circuit,
        )
