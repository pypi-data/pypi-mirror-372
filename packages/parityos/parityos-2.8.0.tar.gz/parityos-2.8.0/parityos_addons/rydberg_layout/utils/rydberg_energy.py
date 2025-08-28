"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2024-2025.
All rights reserved.
"""

import itertools

from parityos_addons.rydberg_layout.base.detuning import Detuning
from parityos_addons.rydberg_layout.base.rydberg_atoms import RydbergAtoms
from parityos_addons.rydberg_layout.utils.rydberg_atom_state import RydbergAtomState
from parityos_addons.rydberg_layout.base.atom_coordinate import squared_distance


def rydberg_energy(
    rydberg_atoms: RydbergAtoms,
    state: RydbergAtomState,
    *,
    include_interaction: bool = True,
    include_alpha: bool = True,
    include_compensation: bool = True,
    include_problem_fields: bool = True,
) -> float:
    r"""
    Compute the Rydberg energy (van der Waals interactions + local detunings) of a classical
    state on a Rydberg layout. The strengths of the local detunings are determined by the Detuning
    instances in the given Rydberg layout.
    The van-der-Waals coefficient c6 is obtained from
    `rydberg_atoms.device_specs.interaction_coefficient`.

    The corresponding Hamiltonian reads

    .. math::
        H = \sum_{i < j} c6/r_{ij}^6 n_i n_j - \sum_i \delta_i n_i,

    where :math:`r_{ij}` is the distance between atoms with indices i and j, :math:`\delta_i` is
    the local detuning of atom at index i (as defined in rydberg_layout) and the operator
    :math:`n_i = (1+\sigma_i^z)/2` gives 0 (1) if the atom is in the ground (Rydberg) state,
    respectively.

    :param rydberg_atoms: A Rydberg layout for which to compute Rydberg energies.
    :param state: RydbergAtomState instance.
    :param include_interaction: If True, the vdW interaction of the Hamiltonian is considered in
        the energy, otherwise it is excluded.
    :param include_alpha: If True, the base component alpha of the Detunings are included
        for computing the energy, otherwise they are excluded.
    :param include_compensation: If True, the compensation component of the Detunings are included
        for computing the energy, otherwise they are excluded.
    :param include_problem_fields: If True, the problem-specific components J of the Detunings are
        included for computing the energy, otherwise they are excluded.
    :return: The Rydberg energy for state on rydberg_layout with c6 van der Waals interaction
        strength.
    """
    return _RydbergEnergyCalculator(rydberg_atoms, state).compute(
        include_interaction, include_alpha, include_compensation, include_problem_fields
    )


class _RydbergEnergyCalculator:
    """
    Compute the Rydberg energy (van der Waals interactions + local detunings) of a classical
    state on a :class:`RydbergAtoms` instance. The strengths of the local detunings are determined
    by the Detuning instances in the given RydbergAtoms instance.
    """

    def __init__(self, rydberg_atoms: RydbergAtoms, state: RydbergAtomState):
        """
        Initialize the Rydberg energy calculations.

        :param rydberg_atoms: :class:`RydbergAtoms` instance defining the Rydberg layout.
        :param state: RydbergAtomState for which to compute the energy
        """
        self.rydberg_atoms = rydberg_atoms
        self.c6 = rydberg_atoms.device_specs.interaction_coefficient
        self.state = state

        # process state for a faster energy computation
        self._atoms_in_rydberg_state = [
            atom for atom, bit in self.state.atom_bit_map.items() if bit
        ]

    def compute(
        self,
        include_interaction: bool,
        include_alpha: bool,
        include_compensation: bool,
        include_problem_fields: bool,
    ) -> float:
        """
        Compute the Rydberg energy

        :param include_interaction: If True, the vdW interaction of the Hamiltonian is considered in
            the energy, otherwise it is excluded.
        :param include_alpha: If True, the base component \alpha of the Detunings are included
            for computing the energy, otherwise they are excluded.
        :param include_compensation: If True, the compensation component of the Detunings are
            included for computing the energy, otherwise they are excluded.
        :param include_problem_fields: If True, the problem-specific components J of the Detunings
            are included for computing the energy, otherwise they are excluded.
        """
        if len(self.state) != len(self.rydberg_atoms):
            raise ValueError(
                f"Number of bits in state ({len(self.state)}) does not match number of "
                f"atoms in rydberg_atoms ({len(self.rydberg_atoms)})"
            )

        # longitudinal field contribution
        energy = self.longitudinal_field(
            include_alpha, include_compensation, include_problem_fields
        )
        if include_interaction:
            energy += self.van_der_waals_interaction()

        return energy

    def longitudinal_field(
        self,
        include_alpha: bool,
        include_compensation: bool,
        include_problem_fields: bool,
    ) -> float:
        """
        Longitudinal field for a computational basis state
        """
        field_energy = -sum(
            self._detuning_extractor(
                atom.detuning,
                include_alpha,
                include_compensation,
                include_problem_fields,
            )
            for atom in self._atoms_in_rydberg_state
        )
        return field_energy

    def van_der_waals_interaction(self) -> float:
        """
        Van der Waals interaction energy
        """
        vdw_energy = 0.0
        for atom1, atom2 in itertools.combinations(self._atoms_in_rydberg_state, r=2):
            dist_squared = squared_distance(atom1.coordinate, atom2.coordinate)
            vdw_energy += self.c6 / dist_squared**3

        return vdw_energy

    @staticmethod
    def _detuning_extractor(
        detuning: Detuning,
        include_alpha: bool,
        include_compensation: bool,
        include_problem_fields: bool,
    ) -> float:
        """"""
        value = 0.0
        if include_alpha:
            value += detuning.alpha
        if include_compensation:
            value += detuning.compensation
        if include_problem_fields:
            value += detuning.J

        return value
