import logging
import time

import httpx

from statsuite_lib import KeycloakClient


class TransferClient:
    """
    A client for handling SDMX file transfers and dataflow operations.

    Args:
        transfer_url (str): Base URL for the transfer service
        keycloak_client (KeycloakClient): Authentication client instance
        api_version (str, optional): API version to use. Defaults to '3'
    """

    def __init__(
        self, transfer_url: str, keycloak_client: KeycloakClient, api_version: str = "3"
    ) -> None:
        """
        Initialize the TransferClient.

        Args:
            transfer_url (str): Base URL for the transfer service
            keycloak_client (KeycloakClient): Authentication client instance
            api_version (str, optional): API version to use. Defaults to '3'
        """
        self._client = httpx.Client()
        self.TRANSFER_URL = f"{transfer_url}/{api_version}"
        self._keycloak_client = keycloak_client
        self._log = logging.getLogger("TransferClient")

    def import_sdmx_file(
        self,
        file_object,
        dataspace: str,
        target_version: int = 0,
        restoration_option_required: bool = False,
        validation_type: int = 1,
        timeout: int = None,
    ) -> int:
        """
        Import an SDMX file into the specified dataspace.

        Args:
            file_object: The SDMX file to import
            dataspace (str): Target dataspace name
            target_version (int, optional): Version number for the import. Defaults to 0
            restoration_option_required (bool, optional): Whether restoration is required. Defaults to False # noqa E501
            validation_type (int, optional): Type of validation to perform. Defaults to 1
            timeout (int, optional): Request timeout in seconds. Defaults to None

        Returns:
            int: The ID of the import request

        Raises:
            httpx.HTTPError: If the request fails

        Example:
                for csv_file in sample_data_dir.rglob("*.csv"):
                    with open(csv_file, 'rb') as file:
                        id = transfer.import_sdmx_file(file=file, dataspace='design')
        """
        data = {
            "dataspace": dataspace,
            "targetVersion": target_version,
            "restorationOptionRequired": restoration_option_required,
            "validationType": validation_type,
        }
        files = {"file": file_object}
        url = f"{self.TRANSFER_URL}/import/sdmxFile"
        resp = httpx.post(
            url=url,
            headers=self._keycloak_client.auth_header(),
            data=data,
            files=files,
            timeout=timeout,
        )
        return resp.json().get("message").split(" ")[2]

    def check_request_status(self, dataspace: str, id: int) -> str:  # noqa VNE003
        """
        Check the status of a request for a given dataspace and ID.

        Args:
            dataspace (str): The dataspace name
            id (int): The request ID to check

        Returns:
            str: The execution status of the request

        """
        self._log.info(f"Checking request status for dataspace {dataspace} and id {id}")
        data = {"dataspace": dataspace, "id": id}
        resp = httpx.post(
            url=f"{self.TRANSFER_URL}/status/request",
            headers=self._keycloak_client.auth_header(),
            data=data,
        )
        return resp.json().get("executionStatus")

    def wait_for_request(
        self,
        dataspace: str,
        id: int,  # noqa VNE003
        timeout: int = 300,
        backoff: int = 30,  # noqa VNE003
    ) -> None:
        """
        Wait for a request to complete with timeout and backoff mechanism.

        Args:
            dataspace (str): The dataspace name
            id (int): The request ID to wait for
            timeout (int, optional): Maximum time to wait in seconds. Defaults to 300
            backoff (int, optional): Time between status checks in seconds. Defaults to 30

        Returns:
            bool: True if timeout occurred, False if request completed successfully


        """
        start = time.time()
        while True:
            status = self.check_request_status(dataspace=dataspace, id=id)
            if status == "Completed":
                return False

            if time.time() - start > timeout:
                self._log.error(
                    f"Timeout waiting for request to be completed {timeout} seconds passed"
                )
                return True
            time.sleep(backoff)

    def transfer_dataflow(
        self, source_dataspace: str, destination_dataspace: str, dataflow: str
    ):
        """
        Transfer a dataflow from source dataspace to destination dataspace.

        Args:
            source_dataspace (str): Source dataspace name
            destination_dataspace (str): Destination dataspace name
            dataflow (str): Name of the dataflow to transfer

        Returns:
            str: The ID of the transfer request


        """
        self._log.info(
            f"Transferring dataflow {dataflow} from {source_dataspace} to {destination_dataspace}"  # noqa E501
        )
        data = {
            "sourceDataspace": source_dataspace,
            "destinationDataspace": destination_dataspace,
            "sourceDataflow": dataflow,
            "destinationDataflow": dataflow,
            "transferContent": 0,
            "sourceVersion": 0,
            "targetVersion": 0,
            "restorationOptionRequired": False,
            "validationType": 0,
        }

        resp = httpx.post(
            url=f"{self.TRANSFER_URL}/transfer/dataflow",
            headers=self._keycloak_client.auth_header(),
            data=data,
        )
        return resp.json().get("message").split(" ")[2]

    def get_tune(self, dataspace: str, dsd_id: str):
        """
        Retrieve tune information for a specific DSD in a dataspace.

        Args:
            dataspace (str): The dataspace name
            dsd_id (str): The ID of the Data Structure Definition

        Returns:
            dict: Tune information for the specified DSD

        """
        self._log.info(f"Getting DSD {dsd_id} tune information in ds {dataspace}")
        data = {"dataspace": dataspace, "dsd": dsd_id}
        resp = httpx.post(
            url=f"{self.TRANSFER_URL}/tune/info",
            headers=self._keycloak_client.auth_header(),
            data=data,
        )
        return resp.json()

    def set_tune(self, dataspace: str, dsd_id: str, index_type: int):
        """
        Set tune parameters for a specific DSD in a dataspace.

        Args:
            dataspace (str): The dataspace name
            dsd_id (str): The ID of the Data Structure Definition
            index_type (int): The type of index to set

        Returns:
            dict: Response containing the result of the tune operation


        """
        self._log.info(f"Getting DSD {dsd_id} tune information in ds {dataspace}")
        data = {"dataspace": dataspace, "dsd": dsd_id, "indexType": index_type}
        resp = httpx.post(
            url=f"{self.TRANSFER_URL}/tune/dsd",
            headers=self._keycloak_client.auth_header(),
            data=data,
        )
        return resp.json()
