import logging

import httpx

from ..keycloak.keycloak import KeycloakClient


class AuthClient:
    """A client for managing authorization rules through the Auth API.

    This client handles the communication with the authorization service,
    allowing for the management of access rules and permissions.

    Attributes:
        AUTH_URL (str): The complete URL for the Auth API including version.

    Args:
        auth_url (str): Base URL of the authorization service.
        keycloak_client (KeycloakClient): Client for handling Keycloak authentication.
        api_version (str, optional): API version to use. Defaults to "1.1".
    """

    def __init__(
        self, auth_url: str, keycloak_client: KeycloakClient, api_version: str = "1.1"
    ) -> None:
        """Initialize the AuthClient.

        Creates a new instance of the AuthClient with the specified configuration.
        Sets up an HTTP client and configures logging.

        Args:
            auth_url (str): Base URL of the authorization service endpoint.
                Should not include the version number.
            keycloak_client (KeycloakClient): An initialized Keycloak client instance
                used for authentication headers.
            api_version (str, optional): API version string to use in URL construction.
                Defaults to "1.1".

        Example:
            keycloak_client = KeycloakClient(...)
            auth_client = AuthClient(
                auth_url="https://auth.example.com",
                keycloak_client=keycloak_client
            )
        """

        self._client = httpx.Client()
        self.AUTH_URL = f"{auth_url}/{api_version}"
        self._keycloak_client = keycloak_client
        self._log = logging.getLogger("AuthClient")

    def add_rule(
        self,
        user_mask: str,
        is_group: bool,
        permission: int,
        dataspace: str = "*",
        artifact_type: int = 0,
        artefact_agency_id: str = "*",
        artefact_id: str = "*",
        artefact_version: str = "*",
    ):
        """Add a new authorization rule to the system.

        Args:
            user_mask (str): The user or group identifier pattern.
            is_group (bool): Whether the rule applies to a group (True) or user (False).
            permission (int): The permission level to grant.
            dataspace (str, optional): Target dataspace. Defaults to "*" (all dataspaces).
            artifact_type (int, optional): Type of artifact. Defaults to 0.
            artefact_agency_id (str, optional): Agency ID of the artifact. Defaults to "*".
            artefact_id (str, optional): ID of the artifact. Defaults to "*".
            artefact_version (str, optional): Version of the artifact. Defaults to "*".

        Returns:
            dict: The JSON response from the server containing the created rule.

        """

        data = {
            "userMask": user_mask,
            "isGroup": is_group,
            "dataSpace": dataspace,
            "artefactType": artifact_type,
            "artefactAgencyId": artefact_agency_id,
            "artefactId": artefact_id,
            "artefactVersion": artefact_version,
            "permission": permission,
        }

        url = f"{self.AUTH_URL}/AuthorizationRules"
        headers = self._keycloak_client.auth_header()
        headers["Content-Type"] = "application/json"
        response = httpx.post(url=url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
