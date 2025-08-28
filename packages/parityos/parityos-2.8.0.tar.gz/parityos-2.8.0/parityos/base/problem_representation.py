"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Representations of combinatorial optimization problems as spin models, optionally with constraints.
"""

from collections.abc import Iterable, Iterator, Mapping, Sequence
from warnings import warn

from parityos.base.constraints import (
    ConfigurationType,
    EqualityConstraint,
    evaluate_parity,
    ParityConstraint,
)
from parityos.base.qubits import Qubit
from parityos.base.utils import json_wrap, JSONLoadSaveMixin, JSONMappingType, JSONType

INFINITY = float("inf")


class ProblemRepresentation(JSONLoadSaveMixin):
    """
    Representation of an optimization problem as a spin Hamiltonian (diagonal in the Pauli-Z basis)
    together with an optional set of EqualityConstraint objects.
    """

    def __init__(
        self,
        interactions: Sequence[Iterable[Qubit]],
        coefficients: Sequence = None,
        constraints: Iterable[EqualityConstraint] = None,
    ):
        r"""
        :param interactions: The interactions from the spin Hamiltonian that represents the
                             optimization problem, including the single-body terms.
                             The interactions should be given as collections of Qubits, where
                             each collection of qubits specifies an operator equal to the product
                             of Z operators on each of the qubits.

        :param coefficients: Optional. The coefficients in the spin Hamiltonian, in a sequence
                             that aligns with the interactions sequence. Defaults to a list of
                             ones. Coefficients can be floats or any other type, but the `evaluate`
                             method might not work for non-numerical types.

        :param constraints: Optional. Equality constraints which must be satisfied by the
                            solutions of the optimization problem. For the compiled problem, this
                            will contain the required parity constraints.

        Example of a compiled problem::

            optimization_problem = ProblemRepresentation(
                interactions=[{Qubit((0, 0))}, {Qubit((0, 1))}, {Qubit((1, 0))}],
                coefficients=(0.5, -0.8, 1.2),
                constraints={EqualityConstraint({Qubit((0, 0)), Qubit((0, 1)), Qubit((1, 0))}, 1)}
            )

        """
        self.interactions = [frozenset(interaction) for interaction in interactions]
        self.coefficients = (
            [
                1,
            ]
            * len(self.interactions)
            if coefficients is None
            else list(coefficients)
        )
        self.constraints = set(constraints) if constraints else set()

        try:
            assert len(self.interactions) == len(self.coefficients)
        except AssertionError:
            raise ValueError(
                "The interactions and coefficients sequences for the problem "
                "representation should have equal lengths: "
                f"{len(self.interactions)} != {len(self.coefficients)}!"
            )

    @property
    def qubits(self) -> set[Qubit]:
        """
        Set of Qubits which appear in the interactions or in the constraints.
        """
        interaction_qubits = set().union(*self.interactions)
        return interaction_qubits.union(*(constraint.qubits for constraint in self.constraints))

    @property
    def terms(self) -> Iterator[tuple[frozenset[Qubit], object]]:
        """
        A property that returns an iterable of all (interaction, coefficient) pairs
        """
        return zip(self.interactions, self.coefficients)

    def evaluate(
        self,
        configuration: ConfigurationType,
        constraint_strength: float = INFINITY,
    ) -> float:
        """
        Evaluates the value of the spin Hamiltonian and the constraints on a particular
        configuration of qubit spin values, where each qubit spin has a value Z = +1 or -1.

        Each qubit in the compiled problem must be in this dictionary. Use the ParityDecoder
        to obtain a full configuration from a partial configuration if necessary.

        :param configuration: a mapping from qubits to spin values Z = +1 or -1.

        :param constraint_strength: the strength to use for the constraints.
             By default, if no constraint_strength is given, hard constraints are used. In this
             case a float(inf) value is returned if any of the constraints is violated, or the
             unconstrained energy of the spin Hamiltonian otherwise.
             A zero value for this parameter will always result in the unconstrained energy and
             no constraints will be checked.
             A non-zero value will result in soft constraints, with a bonus proportional to the
             constraint strength for each valid constraint and a penalty of equal size for each
             constraint that is violated.
        :return: Value of the given configuration in this problem representation.
        :rtype: float
        """
        energy_values = (
            strength * evaluate_parity(interaction, configuration)
            for interaction, strength in self.terms
        )
        constraint_values = (
            constraint.value * evaluate_parity(constraint.qubits, configuration)
            for constraint in self.constraints
        )
        if constraint_strength == INFINITY:
            return INFINITY if any(value < 0 for value in constraint_values) else sum(energy_values)
        else:
            constraint_penalty = -constraint_strength * sum(constraint_values)
            return sum(energy_values) + constraint_penalty

    def evaluate_average_result(
        self,
        result: Mapping[str, int],
        qubits: Sequence[Qubit] = None,
        constraint_strength: float = INFINITY,
    ) -> float:
        """
        :param result: A mapping of bit strings to measurement counts (number of times bit string
                       was measured out of all the shots that were taken).
        :param qubits: optional argument that provides the Qubit instance for each index in the
                       bitstring, by default: [Qubit(0), Qubit(1), Qubit(2)...]
        :param constraint_strength: Optional param for evaluate method, see there for more info
        :return: A weighted average of the number produced by the evaluate method for that
                 configuration, weighted by the proportion of measurement counts found for each
                 bitstring
        """
        if not qubits:
            qubit_count = len(next(iter(result)))
            qubits = [Qubit(i) for i in range(qubit_count)]
        return sum(
            measurement_count
            * self.evaluate(configuration_from_bitstring(bitstring, qubits), constraint_strength)
            for bitstring, measurement_count in result.items()
        ) / sum(result.values())

    def evaluate_minimal_result(
        self,
        result: Mapping[str, int],
        qubits: Sequence[Qubit] = None,
        constraint_strength: float = INFINITY,
    ) -> tuple[ConfigurationType, float]:
        """
        :param result: A mapping of bit strings to measurement counts (number of times bit string
                       was measured out of all the shots that were taken).
        :param qubits: optional argument that provides the Qubit instance for each index in the
                       bitstring, by default: [Qubit(0), Qubit(1), Qubit(2)...]
        :param constraint_strength: Optional param for evaluate method, see there for more info
        :return: The configuration produced from the bitstring that has the lowest energy with
                 non-zero count, along with the corresponding energy
        """
        if not qubits:
            qubit_count = len(next(iter(result)))
            qubits = [Qubit(i) for i in range(qubit_count)]

        min_energy = INFINITY
        min_energy_config = None
        for bitstring, measurement_count in result.items():
            if measurement_count > 0:
                config = configuration_from_bitstring(bitstring, qubits)
                energy = self.evaluate(config, constraint_strength)
                if energy < min_energy:
                    min_energy = energy
                    min_energy_config = config

        return min_energy_config, min_energy

    @classmethod
    def from_nx_graph(cls, graph: "networkx.Graph", *args, **kwargs):
        """
        :param graph: A graph representing an optimization problem; nodes are
                      interpreted as binary variables, and edges between them
                      are interpreted as interactions between them (with strength
                      given by the ``weight`` data on each edge).
        :return: the problem representation associated with the given ``graph``
        """
        terms = (
            ({Qubit(node_a), Qubit(node_b)}, weight)
            for node_a, node_b, weight in graph.edges.data("weight")
        )
        interactions, coefficients = zip(*terms)
        return cls(interactions, coefficients, *args, **kwargs)

    @classmethod
    def from_json(cls, data: JSONMappingType) -> "Self":
        """
        Constructs a problem representation object from JSON data.

        :param data: a JSON-like dictionary with ``'interactions'``, ``'coefficients'``
                     and ``'constraints'`` fields
        :return: a ProblemRepresentation object
        """
        interactions = [
            frozenset(Qubit(qubit) for qubit in interaction) for interaction in data["interactions"]
        ]
        coefficients = data["coefficients"]
        constraints = {
            EqualityConstraint.from_json(constraint_data)
            for constraint_data in data.get("constraints", [])
        }
        return cls(interactions, coefficients, constraints=constraints)

    def to_json(self) -> dict[str, JSONType]:
        """
        Converts the problem representation to json.

        :return: the problem representation in json-serializable format
        """
        terms_data = json_wrap(set(self.terms))  # json_wrap will order the set automatically.
        interaction_data, coefficient_data = (list(data) for data in zip(*terms_data))
        constraints_data = json_wrap(self.constraints)
        return {
            "interactions": interaction_data,
            "coefficients": coefficient_data,
            "constraints": constraints_data,
        }

    def __eq__(self, other):
        """
        Two problem representations are equal if all their interaction terms and constraints are
        equal.

        :param other: other problem representation object
        :return: True if all interaction terms and constraints are equal, otherwise False.
        """
        # We convert the lists of terms into a set because
        # the ordering of the interactions should not affect the comparison.
        return (self.constraints == other.constraints) and set(self.terms) == set(other.terms)

    def __repr__(self):
        # Convert the interaction terms into sets to make the output more readable.
        interactions = [set(interaction) for interaction in self.interactions]
        args_kwargs = f"{interactions}, {self.coefficients}"
        if self.constraints:
            args_kwargs = f"{args_kwargs}, constraints={self.constraints}"
        return f"{self.__class__.__name__}({args_kwargs})"

    def __str__(self):
        hamiltonian_str = "\n +".join(
            f"{coefficient} * {set(interaction)}" for interaction, coefficient in self.terms
        ).replace("+-", "-")
        if self.constraints:
            constraints_str = "{{{}}}".format(
                ",\n      ".join(str(constraint) for constraint in self.constraints)
            )
            return f"[{hamiltonian_str}\n ] + {constraints_str}"
        else:
            return f"[{hamiltonian_str}]"


class Hamiltonian(ProblemRepresentation):
    """The deprecated version of the ProblemRepresentation class"""

    def __init__(
        self,
        interactions: Sequence[Iterable[Qubit]],
        coefficients: Sequence,
        constraints: Iterable[ParityConstraint] = None,
    ):
        warn(
            "The Hamiltonian class is deprecated. "
            "Please use the ProblemRepresentation class instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        # stack level 2 raises the warning at the level of the caller,
        # instead of the level of this __init__ method
        super().__init__(interactions, coefficients=coefficients, constraints=constraints)


def evaluate(qubits: Iterable[Qubit], configuration: ConfigurationType) -> int:
    """
    Obsolete version of the `evaluate_parity` function from the `parityos.base.constraints` module.
    """
    warn(
        "The standalone evaluate function class is deprecated. Please"
        "use the evaluate_parity function from the parityos.base.constraints module instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return evaluate_parity(qubits, configuration)


def configuration_from_bitstring(bitstring: str, qubits: Sequence[Qubit]) -> ConfigurationType:
    """
    Converts a bit string representation of qubit measurements into a mapping of Qubits and
    values Z = +1 or -1, such that it can be used as a configuration in the evaluate method above.
    :param bitstring: string of bits representing qubit measurements
    :param qubits: Qubits to be matched with the z measurements
    :return: A configuration that can be used in the evaluate method
    """
    assert len(bitstring) == len(qubits), "Qubit count must equal bitstring length."

    configuration = {qubit: (-1) ** int(bit) for qubit, bit in zip(qubits, bitstring)}
    return configuration
