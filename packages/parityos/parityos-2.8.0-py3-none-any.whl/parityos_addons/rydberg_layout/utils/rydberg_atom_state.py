"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2025.
All rights reserved.
"""

from dataclasses import dataclass
from typing import Sequence

from parityos_addons.rydberg_layout.base.atom import Atom
from parityos_addons.rydberg_layout.base.exceptions import RydbergLayoutException


@dataclass(frozen=True)
class RydbergAtomState:
    """
    The state of a group of Atoms.

    :param atom_bit_map: A map from `Atom` to bool describing the classical state on the Rydberg
        layout. We use the encoding 0 (False) <-> ground state, 1 (True) <-> Rydberg state.
    """

    atom_bit_map: dict[Atom, bool]

    @property
    def atoms(self) -> list[Atom]:
        """
        :return: atoms for which the RydbergAtomState is defined
        """
        return list(self.atom_bit_map.keys())

    def __len__(self):
        """
        :return: number of atoms.
        """
        return len(self.atoms)

    def to_bit_string(self, preferred_atom_order: Sequence[Atom] = None) -> str:
        """
        Converts to the corresponding bit string.

        :param preferred_atom_order: the preferred order for atoms. If None the order
            given in the atom_bit_map is going to be used.
        :return: bit string representation of the state.
        """
        if preferred_atom_order:
            if set(preferred_atom_order) != self.atom_bit_map.keys() or len(
                preferred_atom_order
            ) != len(self):
                raise RydbergLayoutException(
                    f"The given {preferred_atom_order=} should have"
                    f"the same atoms as in {self.atoms=}."
                )
            atom_order = preferred_atom_order
        else:
            atom_order = self.atoms

        return "".join(
            "0" if not self.atom_bit_map[atom] else "1" for atom in atom_order
        )

    @classmethod
    def from_bit_string(
        cls, atoms: Sequence[Atom], bit_string: str
    ) -> "RydbergAtomState":
        """
        Initializes the class from atoms and the corresponding bit string.

        :param atoms: the atoms in the same order as the bits in the bit_string.
        :param bit_string: a bit string.
        :return: a RydbergAtomState instance.
        """

        if len(atoms) != len(bit_string):
            raise RydbergLayoutException(
                f"{atoms=} and {bit_string=} must have the same length."
            )

        def bit_conversion(bit):
            if bit == '0':
                return False
            elif bit == '1':
                return True
            else:
                raise ValueError(f"Encountered {bit=}, which must be either 0 or 1")

        return RydbergAtomState(
            {
                atom: bit_conversion(bit) for atom, bit in zip(atoms, bit_string)
            }
        )
