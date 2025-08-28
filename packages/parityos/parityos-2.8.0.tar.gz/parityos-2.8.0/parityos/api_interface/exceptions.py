"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.
"""

from requests.exceptions import RequestException

from parityos.base.exceptions import ParityOSException


class ParityOSAuthError(RequestException, ValueError):
    """
    Exception for failed logins to the ParityAPI server.
    """


class ParityOSRequestError(RequestException):
    """
    Exception for failed logins to the ParityAPI server.
    """


class ParityOSCompilerError(ParityOSException):
    """
    Exception resulting from errors in the compiler on the ParityOS cloud server.
    """


class ParityOSTimeoutException(ParityOSException):
    """
    Exception resulting from time-outs waiting for a response from the ParityOS cloud server.
    """
