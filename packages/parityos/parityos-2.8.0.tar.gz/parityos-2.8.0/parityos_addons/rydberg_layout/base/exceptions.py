"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2023-2025.
All rights reserved.
"""

from parityos.base.exceptions import ParityOSException


class RydbergLayoutException(ParityOSException):
    """
    General exception thrown by the Rydberg Layout.
    """


class UnsupportedDeviceSpecs(RydbergLayoutException, TypeError):
    """
    An exception raised when unsupported device specs are given.
    """
