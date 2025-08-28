"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2023.
All rights reserved.

Tools to authenticate with the ParityOS cloud services.
"""

from collections.abc import Iterator
import getpass
import os
import warnings


def generate_credentials(
    username: str = None,
    username_variable: str = "",
    password_variable: str = "",
    intents: int = 3,
) -> Iterator[dict[str, str]]:
    """
    Generates a series of JSON compatible dictionaries with a username and a password.
    The username can be provided as an argument. Otherwise, it is taken from the given system
    variable (this is tried only once), or requested from the user on the prompt.
    For security reasons, the password can not be provided as an argument. It is either taken
    from the given system variable (this is tried only once), or requested from the user on the
    prompt.
    The argument `intents` sets the maximum number of times to ask for a username or password,
    either from the environment or from the prompt.
    To make this generator fully non-interactive, set intents to 1 and set the correct system
    variables.

    :param str username: The username for the account on the server.
    :param str username_variable: System variable to query for the username
    :param str password_variable: System variable to query for the password
    :param int intents: Maximum number of times to ask for a username or password.
    """
    # The credentials object allows for a number of intents to provide the password.
    # First intent: get data from the environment variables or else from prompt.
    username = username or _get_username(username, username_variable)
    password = _get_password(password_variable=password_variable)
    yield {"username": username, "password": password}

    # The next intents are always interactive.
    for intent in range(1, intents):
        print("Login failed. Please provide the correct credentials.")
        username = _get_username(username)
        password = _get_password(password)
        yield {"username": username, "password": password}


def _get_username(username: str = "", username_variable: str = "") -> str:
    """
    Ask for a username, either from the provided environment variable or on the prompt.
    If a username argument is given, then this is shown as a suggestion on the prompt
    and returned as the result if the user only types return.
    """
    if username_variable and not username:
        username = os.getenv(username_variable)
        if username:
            return username

    suggestion = f" [{username}]" if username else ""
    username = input(f"ParityOS Username{suggestion}: ") or username
    return username


def _get_password(password: str = "", password_variable: str = "") -> str:
    """
    Ask for a password, either from the provided environment variable or on the prompt.
    If a password argument is given, then "***" is shown as a suggestion on the prompt
    and the given value is returned as the result if the user only types return.
    """
    if password_variable and not password:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            password = os.getenv(password_variable)

        if password:
            return password

    suggestion = " [***]" if password else ""
    password = getpass.getpass(f"ParityOS Password{suggestion}: ") or password
    return password
