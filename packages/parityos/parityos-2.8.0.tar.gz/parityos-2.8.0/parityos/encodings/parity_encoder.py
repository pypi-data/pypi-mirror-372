"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Extensions to process the results from the ParityOS cloud services.
"""

from abc import ABC

from parityos.base.constraints import ConfigurationType, evaluate_parity
from parityos.encodings.mappings import Mappings


class ParityEncoderExtension(ABC):
    """
    Extends the ParityOSOutput class with the `encode` method, which transforms a qubit Z-spin
    configuration given in the logical system to the Z-spin configuration for the parity qubits
    (i.e. for the physical system).
    """

    mappings: Mappings

    def encode(self, configuration: ConfigurationType) -> ConfigurationType:
        """
        Converts a given configuration in the logical system to a bitstring for the physical mapping

        :param configuration: A logical configuration to encode, the keys refer to logical qubits;
                              the values are either +1 or -1.
        :return: The configuration on the physical qubits.
        """
        physical_configuration = {
            physical_qubit: parity_map.parity * evaluate_parity(parity_map.qubits, configuration)
            for physical_qubit, parity_map in self.mappings.encoding_map.items()
        }
        return physical_configuration
