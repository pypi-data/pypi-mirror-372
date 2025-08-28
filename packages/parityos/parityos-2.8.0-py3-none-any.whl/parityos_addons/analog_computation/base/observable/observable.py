"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2023 - 2025.
All rights reserved.
"""

import copy
import itertools
from typing import Iterator, Mapping, Sequence, Set, Union

from parityos.base.gates import Z
from parityos.base.qubits import Qubit
from parityos.base.utils import JSONLoadSaveMixin

from parityos_addons.analog_computation.base.exceptions import (
    ParityOSAnalogComputationException,
)
from parityos_addons.analog_computation.base.observable.pauliop import PauliOp


class Observable(JSONLoadSaveMixin):
    """
    Representation of an Observable as a sum of PauliOps multiplied by corresponding coefficients.
    """

    def __init__(self, interactions: Sequence[PauliOp], coefficients: Sequence):
        """
        :param interactions: the PauliOps that should be multiplied by the corresponding
                             coefficients and summed up together in order to obtain the
                             Observable.
        :param coefficients: The coefficients in the Observable, in a sequence that aligns
                             with the interactions sequence.

        Example::

            observable = Observable(
                [PauliOp([X(Qubit(1))]), PauliOp([Y(Qubit(1)), Y(Qubit(2))])],
                (0.5, -0.8),
            )

        """
        self.interactions = list(interactions)
        self.coefficients = list(coefficients)

        if len(self.interactions) != len(self.coefficients):
            raise ParityOSAnalogComputationException(
                "Interactions and coefficients don't have the same length."
            )

    @property
    def qubits(self) -> Set[Qubit]:
        """
        :return: set of the Qubits which appear in the Observable.
        """
        return set().union(*[pauli_op.qubits for pauli_op in self.interactions])

    @property
    def terms(self) -> Iterator[tuple[PauliOp, float]]:
        """
        A property that returns an Iterator of all (interaction, coefficient) pairs.

        :return: an Iterator for the (interaction, coefficient) pairs
        """
        return zip(self.interactions, self.coefficients)

    def evaluate(self, configuration: Mapping[Qubit, int]) -> float:
        """
        Evaluates the expectation value of the Observable in specific Z eigenstates
        with eigenvalues +1 or -1 given by the configuration.

        :param configuration: a mapping of the qubits onto their Z eigenvalue +1 or -1.
        :return: the corresponding expectation value
        """

        if not all(qubit in configuration for qubit in self.qubits):
            raise ParityOSAnalogComputationException(
                "Not all required Qubits are given in the "
                "configuration for Observable.evaluate()."
            )

        expectation_value = 0
        for pauli_op, coefficient in self.terms:
            expectation_value += coefficient * pauli_op.evaluate(configuration)

        return expectation_value

    @classmethod
    def from_nx_graph(cls, graph: "networkx.Graph"):
        """
        :param graph: A graph representing an optimization problem; nodes are
                      interpreted as binary variables, and edges between them
                      are interpreted as Z interaction terms between them (with
                      strength given by the ``weight`` data on each edge).
        :return: the Observable associated with the given ``graph``
        """
        terms = (
            (PauliOp([Z(Qubit(node_a)), Z(Qubit(node_b))]), weight)
            for node_a, node_b, weight in graph.edges.data("weight")
        )
        interactions, coefficients = zip(*terms)
        return cls(interactions, coefficients)

    @classmethod
    def from_json(cls, data):
        """
        Constructs an Observable object from JSON data.

        :param data: a JSON-like dictionary with ``'interactions'``, ``'coefficients'`` fields
        :return: an Observable object
        """
        interactions = [
            PauliOp.from_json(interaction) for interaction in data["interactions"]
        ]
        coefficients = data["coefficients"]
        return cls(interactions, coefficients)

    @classmethod
    def from_terms(
        cls, terms: Union[Iterator[tuple[PauliOp, float]], Sequence[tuple[PauliOp, float]]]
    ) -> "Observable":
        """
        Creates an Observable from given terms.
        :param terms: sequence or iterator of (PauliOp, coefficient) tuples.
        :return: Observable.
        """
        new_terms = copy.deepcopy(terms) if isinstance(terms, Iterator) else terms
        interactions, coefficients = zip(*new_terms)

        return Observable(interactions, coefficients)

    def to_json(self):
        """
        Converts the Observable object to json.

        :return: the Observable object in json-serializable format
        """
        # index for sorting self.interactions
        sort_idx = sorted(
            range(len(self.interactions)), key=lambda x: hash(self.interactions[x])
        )

        interactions_sorted = [self.interactions[i] for i in sort_idx]
        coefficients_sorted = [self.coefficients[i] for i in sort_idx]

        return {
            "interactions": [
                interaction.to_json() for interaction in interactions_sorted
            ],
            "coefficients": [coefficient for coefficient in coefficients_sorted],
        }

    def tensor(self, other: "Observable") -> "Observable":
        """
        Return the tensor product observable `self` ⊗ `other`. `self` and `other` must not share
        common qubit labels.
        *Note*: Alternatively, the syntax `observable1 ^ observable2` can be used to compute
        the tensor product between two observables

        :param other: Other observable to compute the tensor product with
        :returns: tensor product observable `self` ⊗ `other`. If observables share common qubits a
            `ParityOsAnalogComputationException` is raised.
        """
        common_qubits = self.qubits & other.qubits
        if common_qubits:
            raise ParityOSAnalogComputationException(
                f"Cannot create a tensor product from observables with common qubits "
                f"{common_qubits}"
            )

        tensor_operators = [
            PauliOp(frozenset.union(term1[0].pauli_gates, term2[0].pauli_gates))
            for term1, term2 in itertools.product(self.terms, other.terms)
        ]
        factors = [
            term1[1] * term2[1]
            for term1, term2 in itertools.product(self.terms, other.terms)
        ]
        tensor_observable = Observable(tensor_operators, factors)

        return tensor_observable

    def __eq__(self, other):
        """
        Two Observables are equal if all their terms are equal.

        :param other: other Observable object
        :return: True if all terms are equal to each other, otherwise False.
        """
        # We convert the lists of terms into a set because
        # the ordering of the interactions should not affect the comparison.
        return set(self.terms) == set(other.terms)

    def __add__(self, other: "Observable") -> "Observable":
        """
        Adds two Observables together and returns a new one.
        :param other: an Observable instance to be added to self.
        :return: new Observable.
        """
        new_terms = list(self.terms) + list(other.terms)
        return Observable.from_terms(new_terms)

    def __rmul__(self, number: float):
        """
        Multiplies a number to the Observable and creates a new Observable with
        the modified coefficients.

        :param number: float that is multiplied to the coefficients
        :return: new Observable
        """
        new_coefficients = [number * coefficient for coefficient in self.coefficients]
        return Observable(self.interactions, new_coefficients)

    def __xor__(self, other: "Observable") -> "Observable":
        """
        Return the tensor product observable `self` ⊗ `other`. `self` and `other` must not share
        common qubit labels.

        :param other: Other observable to compute the tensor product with
        :returns: tensor product observable `self` ⊗ `other`. If observables share common qubits a
            `ParityOsAnalogComputationException` is raised.
        """
        return self.tensor(other)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.interactions}, {self.coefficients})"

    def __str__(self):
        return "\n+".join(
            f"{coefficient} * {interaction}" for interaction, coefficient in self.terms
        ).replace("+-", "-")

    def __hash__(self):
        return hash(frozenset(self.terms))
