import datetime
import logging

import httpx


class KeycloakClient:
    """
    A client for handling Keycloak authentication and token management.

    This class manages OAuth2/OpenID Connect authentication with Keycloak,
    including token acquisition, refresh, and management.

    Args:
        openid_url (str): The OpenID configuration URL for the Keycloak server
        username (str): Username for authentication
        password (str): Password for authentication
    """

    def __init__(self, openid_url: str, username: str, password: str) -> None:
        """
        Initialize the KeycloakClient with authentication credentials.

        Args:
            openid_url (str): The OpenID configuration URL for the Keycloak server
            username (str): Username for authentication
            password (str): Password for authentication
        """

        self._client = httpx.Client()
        self.OPENID_URL = openid_url
        self.log = logging.getLogger("KeycloakClient")
        self._auth_endpoint = None
        self._token_endpoint = None
        self.access_token = None
        self.access_token_expires = None
        self.refresh_token = None
        self._get_openid_configuration()
        self._authenticate(username=username, password=password)

    def _get_openid_configuration(self) -> None:
        """
        Retrieve OpenID Connect configuration from Keycloak server.

        This method fetches the authorization and token endpoints from the
        Keycloak OpenID configuration.

        Raises:
            ConnectError: If connection to the Keycloak server fails.
        """
        self.log.info(f"Getting openid configuration from {self.OPENID_URL}")
        try:

            response = self._client.get(self.OPENID_URL)
            self._auth_endpoint = response.json()["authorization_endpoint"]
            self._token_endpoint = response.json()["token_endpoint"]

        except httpx.ConnectError as e:
            raise httpx.ConnectError(f"Failed to get openid configuration: {e}")

    def _authenticate(self, username: str, password: str) -> None:
        """
        Perform initial authentication with Keycloak using username and password.

        This method obtains the initial access and refresh tokens using the
        provided credentials.

        Args:
            username (str): Username for authentication
            password (str): Password for authentication


        """

        self.log.info(f"Authenticating with {self._auth_endpoint}")
        response = self._client.post(
            self._token_endpoint,
            data={
                "grant_type": "password",
                "client_id": "stat-suite",
                "username": username,
                "password": password,
            },
        )

        self.refresh_token = response.json()["refresh_token"]
        self.access_token = response.json()["access_token"]
        self.access_token_expires = datetime.datetime.now() + datetime.timedelta(
            seconds=response.json()["expires_in"]
        )

    def trigger_refresh_token(self) -> None:
        """
        Refresh the access token using the refresh token.

        This method is called when the access token is expired or about to expire.
        It uses the refresh token to obtain a new access token and refresh token pair.


        """

        self.log.info("Triggering refresh token")
        response = self._client.post(
            self._token_endpoint,
            data={
                "grant_type": "refresh_token",
                "client_id": "stat-suite",
                "refresh_token": self.refresh_token,
            },
        )
        self.access_token = response.json()["access_token"]
        self.access_token_expires = datetime.datetime.now() + datetime.timedelta(
            seconds=response.json()["expires_in"]
        )
        self.refresh_token = response.json()["refresh_token"]

    def get_access_token(self) -> str:
        """
        Get the current valid access token.

        This method checks if the current access token is valid and not expired.
        If expired, it automatically triggers a token refresh.

        Returns:
            Access token string
        """

        self.log.info("Getting access token")
        if (
            self.access_token_expires is None
            or self.access_token_expires < datetime.datetime.now()  # noqa W503
        ):
            self.trigger_refresh_token()

        return self.access_token

    def auth_header(self) -> dict:
        """
        Create an authorization header using the current access token.

        Returns:
            dict: A dictionary containing the Authorization header with the Bearer token
                 in the format {'Authorization': 'Bearer <token>'}

        """

        return {"Authorization": f"Bearer {self.get_access_token()}"}
