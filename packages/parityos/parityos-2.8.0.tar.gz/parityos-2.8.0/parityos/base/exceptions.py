"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.
"""


class ParityOSException(Exception):
    """
    General exception thrown by ParityOS.
    """


class ParityOSImportError(ImportError):
    """
    ImportError related to uninstalled optional ParityOS dependencies.
    """
