"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2022.
All rights reserved.

Tools to connect to the ParityOS cloud services.
"""

from json.decoder import JSONDecodeError

from requests import Session, Response
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from parityos.api_interface.authentication import generate_credentials
from parityos.api_interface.exceptions import ParityOSAuthError, ParityOSRequestError


DEFAULT_HOST = "api.parityqc.com"

# Define environment variables that can hold the credentials for the default host.
DEFAULT_ENVIRONMENT = dict(
    username_variable="PARITYOS_USER",
    password_variable="PARITYOS_PASS",
)
# Define the environment variables that can hold the credentials for alternative hosts.
ALTERNATIVE_ENVIRONMENT = dict(
    username_variable="PARITYOS_ALTUSER",
    password_variable="PARITYOS_ALTPASS",
)


class ClientBase:
    """
    Base class that sets up HTTP parameters (authentication, API endpoints, and so on).
    It should not be used directly unless you are debugging HTTP requests,
    use parityos.CompilerClient instead.
    """

    def __init__(
        self,
        username: str = None,
        host: str = DEFAULT_HOST,
        url_prefix: str = "v1",
        http_retries: int = 3,
        http_timeout: int = 10,
        http_backoff_factor: float = 0.02,
        intents: int = 3,
    ):
        """
        :param str username: ParityOS id of the user.
        :param str host: ParityAPI host name.
        :param str url_prefix: Prefix to REST API paths, used mostly for versioning.
        :param int http_retries: Number of http retries.
        :param int http_timeout: Maximum time in seconds to wait for a http response.
        :param int http_backoff_factor: Http exponential backoff factor.
        :param int intents: Maximum number of intents with different passwords.
        """
        self.username = username
        self.host = host
        self.url_prefix = url_prefix
        self.base_url = f"https://{self.host}/{self.url_prefix}"
        self.http_timeout = http_timeout
        self.http_retries = http_retries
        self.http_backoff_factor = http_backoff_factor
        self.intents = intents
        self._setup_connection()

    def _setup_connection(self):
        """
        Connects to the ParityAPI server, logs the user in and stores the session token.
        """
        # Credentials are instantiated here so that the password information
        # is garbage collected as soon as this method terminates.
        self.http = Session()
        adapter = HTTPAdapter(
            max_retries=Retry(total=self.http_retries, backoff_factor=self.http_backoff_factor)
        )
        self.http.mount("https://", adapter)
        self.username, token = self._get_authentication()
        # Only the username is stored in self so that the password information
        # can be garbage collected.
        self.http.headers.update({"Authorization": f"Token {token}"})

    def _get_authentication(self) -> tuple[str, str]:
        """
        Log in on the server to obtain an authentication token for future requests.
        """
        # The credentials object allows for a number of intents to provide the password.
        environment_variables = (
            DEFAULT_ENVIRONMENT if self.host == DEFAULT_HOST else ALTERNATIVE_ENVIRONMENT
        )
        authentication_intents = generate_credentials(
            self.username,
            **environment_variables,
            intents=self.intents,
        )
        username = self.username
        for credentials_data in authentication_intents:
            response = self.http.post(f"{self.base_url}/auth", data=credentials_data)
            data = response.json()
            username = credentials_data["username"]
            if "token" in data:
                return username, data["token"]

        # No authentication intents left after failed logins
        raise ParityOSAuthError(f"Failed login for user {username} on server {self.host}.")

    def _send_request(self, method: str, url: str, data: dict = None) -> Response:
        """
        Send a http request

        :param method: request method to use ('GET', 'POST', 'PUT', ... )
        :param url: target url
        :param data: payload data as a dictionary
        :return: requests.Response object
        """
        try:
            response = self.http.request(method, url=url, json=data, timeout=self.http_timeout)
        except Exception as err:
            message = f"Failed to receive valid response after at most {self.http_retries} retries."
            err.args = (*err.args, message)
            raise err

        if response.ok:
            return response
        else:
            try:
                error_data = response.json()
            except JSONDecodeError:
                error_data = "None"

            raise ParityOSRequestError(
                f"{method} on {url}: {response.status_code}, {error_data}",
                response=response,
            )
