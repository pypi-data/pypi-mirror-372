"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2022.
All rights reserved.

SpinZ arithmetics for constructing ParityOS problem representations.
"""

from typing import Union

try:
    import sympy
    from sympy.core.add import Add
    from sympy.core.mul import Mul
    from sympy.core.symbol import Symbol
except ImportError:
    from parityos.base.exceptions import ParityOSImportError

    raise ParityOSImportError("The spin_hamiltonians module requires the installation of Sympy")


from parityos.base import ProblemRepresentation, Qubit
from parityos.base.qubits import Coordinate


class SpinZ(Symbol):
    """
    Represents a classical Ising spin value (+1 or -1) or the Z-eigenvalue of a Pauli Z operator.
    """

    def __new__(cls, label: Union[str, int, Coordinate, Qubit]):
        # Normalize label to the formatting from Qubit.
        qubit = label if isinstance(label, Qubit) else Qubit(label)
        label = qubit.label
        # For now, we only consider Pauli Z operators, so they all commute.
        # If we were to introduce X or Y operators, commutative should be False.
        obj = Symbol.__new__(cls, name=f"Z_{label}")
        obj.label = label
        return obj

    def __mul__(self, other):
        if isinstance(other, SpinZ) and (self.label == other.label):
            return 1
        else:
            return super().__mul__(other)

    def _eval_power(self, e):
        if e.is_Integer and e.is_positive:
            return super().__pow__(int(e) % 2)

        # When elevating a sympy symbol obj to a power p, sympy.core.power.Pow.__new__ will call
        # obj._eval_power(p). If the result is not None, then that result is returned.
        # Otherwise, a Pow instance is returned that represents obj**p symbolically. So _eval_power
        # only has to return a value for cases that can be simplified to some simpler type.

    @property
    def qubit(self):
        return Qubit(self.label)


def untie_spinz_product(product: Mul) -> tuple[frozenset[Qubit], object]:
    """
    Split a product of SpinZ and other factors into a pure product of SpinZ object and the product
    of all the remaining factors.

    :param product: A product of SpinZ objects and other Sympy objects or numbers
    :return: a tuple where the first item is the product of SpinZ objects and the second item
        is the product of all the other factors in the term
    """
    spin_product = coefficient = 1
    for factor in Mul.make_args(product):
        if isinstance(factor, SpinZ):
            spin_product *= factor  # Multiplication of SpinZ instances reduces duplicates to 1.
        else:
            coefficient *= factor

    if spin_product == 1:
        return frozenset(), coefficient
    else:
        interaction = frozenset(spin.qubit for spin in Mul.make_args(spin_product))
        return interaction, coefficient


def spinz_to_hamiltonian(expr: Union[Add, Mul]) -> ProblemRepresentation:
    """
    Convert an expression containing sums of products of SpinZ objects into a ParityOS problem
    representation.

    :param expr: an expression containing sums of products of SpinZ objects
    :return: a ProblemRepresentation object
    """
    all_terms = (untie_spinz_product(term) for term in Add.make_args(sympy.expand(expr)))
    # Filter out the terms that do not contain any SpinZ objects. Terms with one or more SpinZ
    # factors are kept. Note that these include single spin interactions.
    interaction_terms = (
        (interaction, coefficient) for interaction, coefficient in all_terms if interaction
    )
    interactions, coefficients = zip(*interaction_terms)
    return ProblemRepresentation(interactions, coefficients)
