import logging

import httpx

from ..keycloak.keycloak import KeycloakClient


class NSIClient:
    """Client for interacting with the NSI (Network Service Interface) API.

    This client handles file operations (upload, download, delete) through the NSI service
    with authentication handled by a Keycloak client.

    Attributes:
        NSI_URL (str): Base URL for the NSI service.
        log: Logger instance for the NSIClient.

    Args:
        nsi_url (str): Base URL of the NSI service.
        keycloak_client (KeycloakClient): Client for handling Keycloak authentication.
    """

    def __init__(self, nsi_url: str, keycloak_client: KeycloakClient) -> None:
        """Initialize the NSIClient.

        Args:
            nsi_url (str): Base URL of the NSI service.
            keycloak_client (KeycloakClient): Initialized Keycloak client for authentication.
        """
        self._client = httpx.Client()
        self.NSI_URL = nsi_url
        self._keycloak_client = keycloak_client
        self.log = logging.getLogger("NSIClient")

    def put(self, file_to_upload, path: str, timeout: int = None) -> int:
        """Upload a file to the NSI service.

        Args:
            file_to_upload: File content to upload.
            path (str): Target path on the NSI service.
            timeout (int, optional): Request timeout in seconds. Defaults to None.

        Returns:
            int: HTTP status code of the upload response.

        """

        headers = self._keycloak_client.auth_header() | {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        self.log.info(f"Uploading to NSI: {self.NSI_URL + path}")

        response = httpx.post(
            self.NSI_URL + path,
            content=file_to_upload,
            headers=headers,
            timeout=timeout,
        )

        if response.status_code != 207:
            self.log.info(f"NSI response: {response.text}")
        self.log.info(response.text)
        response.raise_for_status()
        return response.status_code

    def get(self, path: str, headers: dict = {}, timeout: int = None) -> httpx.Response:
        """Retrieve a file or resource from the NSI service.

        Args:
            path (str): Path to the resource on the NSI service.
            headers (dict, optional): Additional HTTP headers to include. Defaults to {}.
            timeout (int, optional): Request timeout in seconds. Defaults to None.

        Returns:
            httpx.Response: Response object containing the requested resource.
        """

        headers |= self._keycloak_client.auth_header()
        self.log.info(f"Getting from NSI: {self.NSI_URL + path}")
        resp = httpx.get(self.NSI_URL + path, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp

    def delete(self, path: str, timeout: int = None) -> int:
        """Delete a file or resource from the NSI service.

        Args:
            path (str): Path to the resource to delete on the NSI service.
            timeout (int, optional): Request timeout in seconds. Defaults to None.

        Returns:
            int: HTTP status code of the delete response.

        """

        headers = self._keycloak_client.auth_header()
        self.log.info(f"Deleting from NSI: {self.NSI_URL + path}")
        response = httpx.delete(self.NSI_URL + path, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.status_code
