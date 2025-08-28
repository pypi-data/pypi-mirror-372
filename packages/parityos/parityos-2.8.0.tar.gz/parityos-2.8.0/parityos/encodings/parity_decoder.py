"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Extensions to process the results from the ParityOS cloud services.
"""

from abc import ABC
from itertools import combinations
from random import Random

from parityos.base.constraints import ConfigurationType, EqualityConstraint, evaluate_parity
from parityos.base.exceptions import ParityOSException
from parityos.base.problem_representation import ProblemRepresentation
from parityos.base.qubits import Qubit
from parityos.encodings.mappings import Mappings


class ParityDecoderExtension(ABC):
    """
    Extends the ParityOSOutput class with the methods `decode`, `error_correct`,
    `select_reduced_readout_qubits` and `make_full_configuration_from_partial`.
    These methods can decode physical configurations into logical configurations.

    It is possible to use a partial read-out to construct a full physical configuration,
    based on the redundant encoding that the parity architecture offers. This is especially
    useful if only a limited number of qubits can be read out in the hardware setup, or if
    the read-out failed on some qubits.
    """

    mappings: Mappings
    compiled_problem: ProblemRepresentation

    def decode(self, configuration: ConfigurationType) -> list[ConfigurationType]:
        """
        Decodes a physical configuration back to a logical one, it is important that the
        configuration contains enough qubits to reconstruct the logical state. If not
        enough qubits are included, a ParityOSException will be raised.

        :param configuration: A physical configuration to decode, the keys are qubits
                              on the physical device, the values are either +1 or -1.

        :return: A list containing all equally-likely logical configuration that correspond to
                 the physical configuration.  Each logical configuration is a dictionary
                 going from qubit, to +1 or -1, similar to the physical configuration.
        """
        # If not all physical qubits are specified in the configuration, we deduce the value
        # of those qubits from the constraints.
        if set(configuration) != set(self.mappings.encoding_map):
            configuration = self.make_full_configuration_from_partial(configuration)

        # Now error correct the resulting configuration onto the physical code subspace.
        corrected_configurations = self.error_correct(configuration)

        logical_configurations = [
            {
                logical_qubit: parity_map.parity
                * evaluate_parity(parity_map.qubits, corrected_configuration)
                for logical_qubit, parity_map in self.mappings.decoding_map.items()
            }
            for corrected_configuration in corrected_configurations
        ]
        return logical_configurations

    def error_correct(self, configuration: ConfigurationType) -> list[ConfigurationType]:
        """
        Correct errors using the nearest neighbor algorithm

        :param configuration: a physical configuration to correct for errors

        :return: A list of possible physical configurations that satisfy all constraints
                 (and hence are part of the physical code subspace), which each were obtained
                 at the smallest possible Hamming distance from the original configuration.
        """
        # If we already have a valid codeword, we are done
        if self._check_parity(configuration):
            return [configuration]

        # Search the bitstring space by flipping k bits at a time, increasing k every step,
        # until we find a valid codeword.  We want to keep track of all valid codewords found
        # at the shortest distance k, since they are all equally likely.
        for k in range(1, len(self.mappings.encoding_map)):
            # Prepare a list to accumulate valid codewords
            valid_configurations = []
            # Look at every possible combination of k flipped bits
            for qubits_to_flip in combinations(self.mappings.encoding_map, k):
                flipped_configuration = configuration.copy()
                for qubit in qubits_to_flip:
                    flipped_configuration[qubit] *= -1

                if self._check_parity(flipped_configuration):
                    valid_configurations.append(flipped_configuration)

            # If any valid codewords were found, we can return them
            if valid_configurations:
                return valid_configurations

        raise ParityOSException("There are no valid codewords in the entire physical code space")

    def select_reduced_readout_qubits(self, random_generator: Random = None) -> set[Qubit]:
        """
        Constructs a random minimal set of qubits that can be read-out and still be used
        to recover the full logical configuration.

        Note that when these qubits are used for read-out, no error correction can be applied.

        :param random_generator: Optional. A random number generator that has a ```choice```
                                 and ```sample``` method. If None is given, then the default random
                                 number generator from the `random` standard library is used.

        :return: A random set of qubits that are selected for read-out.
        """
        # If there are no constraints in the compiled problem, we have to read out every qubit
        if not self.compiled_problem.constraints:
            return set(self.mappings.encoding_map.keys())

        if random_generator is None:
            random_generator = Random()

        # Start with only the unconstrained qubits, because those will all have to be read-out.
        # The qubits that are in constraints will be added in consecutive steps.
        readout_qubits = self.compiled_problem.qubits - set().union(
            *(constraint.qubits for constraint in self.compiled_problem.constraints)
        )
        # Make a configuration that has all the qubits that are known in it, the state of the
        # qubits does not matter.
        configuration = {qubit: 1 for qubit in readout_qubits}

        while len(configuration) != len(self.mappings.encoding_map):
            # Find the next qubits to add to the read-out set based on the constraint
            # that has the minimum number of remaining unknowns
            qubits_to_add = self._find_next_readout_qubits(configuration, random_generator)
            readout_qubits.update(qubits_to_add)
            configuration.update({qubit: 1 for qubit in qubits_to_add})
            configuration = self.make_full_configuration_from_partial(
                configuration,
                return_incomplete=True,
            )

        return readout_qubits

    def make_full_configuration_from_partial(
        self, configuration: ConfigurationType, return_incomplete: bool = False
    ) -> ConfigurationType:
        """
        Reconstructs a full physical configuration from a partial one
        using the constraints in the compiled problem.

        :param configuration: A partial physical configuration to extend.
        :param return_incomplete: If this flag is set to True, we return a physical
                                  configuration even if the full configuration could not
                                  be reconstructed. The configuration returned in that case
                                  contains all the qubits that could be deduced.
        :return: Full physical configuration deduced from the parity constraints.
        """
        # This dictionary will be used to add all reconstructed values of the qubits, we start
        # from the given configuration.
        deduced_configuration = configuration.copy()

        # Make a list of the unknown qubits in all constraints, the goal is to remove all unknowns
        # from the constraints until we are finished, or can not make any more progress.
        known_qubits = set(configuration)
        unknown_constraints = {
            EqualityConstraint(
                constraint.qubits - known_qubits,
                constraint.value * evaluate_parity(constraint.qubits & known_qubits, configuration),
            )
            for constraint in self.compiled_problem.constraints
        }

        while unknown_constraints:
            new_unknown_constraints = set()
            for constraint in unknown_constraints:
                deduced_qubits = set(deduced_configuration)
                new_constraint_qubits = constraint.qubits - deduced_qubits
                if not new_constraint_qubits:
                    # If there are no unknowns left in the constraint, we simply do nothing.
                    # Note that if the remaining parity is -1, the read-out contains an error,
                    # but the purpose of this function is not to do error correction (that
                    # will be done later).
                    continue

                # If the qubit is already in the deduced configuration, we do not
                # have to keep track of it anymore, we can multiply its state
                # with the constraint parity and not add it to the new unknowns.
                new_parity = constraint.value * evaluate_parity(
                    constraint.qubits & deduced_qubits, deduced_configuration
                )
                if len(new_constraint_qubits) == 1:
                    # If there is exactly one qubit left in the unknowns of this constraint,
                    # we now know its value to be equal to remaining parity, so we can add it
                    # to the deduced configuration.
                    [qubit] = new_constraint_qubits
                    deduced_configuration[qubit] = new_parity
                else:
                    # If there are still more than two unknown qubits in the constraint,
                    # we have to put it back into the unknown constraints.
                    new_unknown_constraints.add(
                        EqualityConstraint(new_constraint_qubits, new_parity)
                    )

            if new_unknown_constraints == unknown_constraints:
                # We cannot make any further progress, after checking all constraints,
                # so reconstruction failed.
                if return_incomplete:
                    return deduced_configuration
                else:
                    raise ParityOSException("Decoding failed for the given read-out set")
            else:
                # If we made some progress, continue the algorithm
                unknown_constraints = new_unknown_constraints

        return deduced_configuration

    def _check_parity(self, configuration: ConfigurationType) -> bool:
        """
        Checks whether a configuration satisfies all the constraints

        :param configuration: A physical configuration to check.

        :return: True if it satisfies all constraints, False otherwise.
        """
        return all(
            constraint.is_satisfied(configuration)
            for constraint in self.compiled_problem.constraints
        )

    def _find_next_readout_qubits(
        self, configuration: ConfigurationType, random_generator: Random
    ) -> set[Qubit]:
        """
        Helper method for select_random_reduced_readout_qubits. Selects a set of qubits
        that should be added to the read-out set. Go over all constraints in the compiled
        problem and select one of the constraint with the fewest number of unknowns. Then returns
        all but one of the qubits in that constraint.

        :param configuration: A dictionary containing all read-out qubits as well as all qubit
                              values that can be deduced from the read-out qubits.
        :param random_generator: Optional. A random number generator that has a ```choice```
                                 and ```sample``` method.
        :return: A set of qubits that should be added to the read-out set.
        """
        known_qubits = set(configuration)
        min_number_unknowns = float("inf")
        minimum_unknowns = []
        # Go over all the constraints in the compiled problem and find those with the minimum
        # number of unknown qubits.
        for constraint in self.compiled_problem.constraints:
            unknown_qubits = constraint.qubits - known_qubits
            if unknown_qubits:
                if len(unknown_qubits) < min_number_unknowns:
                    min_number_unknowns = len(unknown_qubits)
                    minimum_unknowns = [unknown_qubits]
                elif len(unknown_qubits) == min_number_unknowns:
                    minimum_unknowns.append(unknown_qubits)

        # Pick a random set of unknown qubits from the best choices.
        unknown_qubits = random_generator.choice(minimum_unknowns)

        # Add all but one of the unknown qubits because the last one can be reconstructed from the
        # constraint.
        qubits_to_add = set(random_generator.sample(tuple(unknown_qubits), len(unknown_qubits) - 1))

        return qubits_to_add
