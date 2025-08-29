import logging
import time
from enum import IntEnum
from typing import Optional

import httpx

from .models import LoadingLog, LoadingLogs


class SFSClient:
    """Client for the SDMX Faceted search service"""

    def __init__(self, sfs_url: str, sfs_api_key: str) -> None:
        """Inits the client

        Args:
            sfs_url: Endpoint url for SFS service.
            sfs_api_key: API key for the SFS service
        """

        self._client = httpx.Client()
        self.SFS_URL = sfs_url
        self._sfs_api_key = sfs_api_key
        self.log = logging.getLogger("SFSClient")
        self.log.level = logging.INFO

    def index(self, tenant: str = "default") -> str:
        """Triggers a new indexing task

        Args:
            tenant: (str) tenant to trigger the index for

        Returns:
            loadingId(str)
        """
        resp = httpx.post(
            f"{self.SFS_URL}/admin/dataflows?api-key={self._sfs_api_key}&tenant={tenant}"  # noqa
        )
        if resp.status_code == 200:
            from .models import Index

            loading = Index.model_validate(resp.json())
            return loading.root.get("loadingId")

    class LoadingStatus(IntEnum):
        """Enum class to represent status of the loading tasks

        Attributes:
            COMPLETED: Task finished succesfully
            RETRY: Some recoverable error happened or the task is in a non-complete
                   status
            FAILED: Unrecoverable error
            BUG502: There si a bug retrieving loading status that can be retrieve
                    fetching the logs without id query param
        """

        COMPLETED = 1
        RETRY = 2
        FAILED = 3
        BUG502 = 10

    def get_log(self, tenant: str, loading_id: str) -> Optional[LoadingLog]:
        """Get log and status from by loading_id, if retrieving a log by id
        fails with a 502 it will fallback to retrieve all available logs and
        filter them

        Arguments:
            tenant: (str) .stat tenant
            loading_id: (str) id of the loading

        Returns:
            LoadingLog or None if the loading_id cannot be found
        """

        resp = httpx.get(
            url=f"{self.SFS_URL}/admin/logs?api-key={self._sfs_api_key}&tenant={tenant}"
        )
        if resp.status_code == 200:
            return LoadingLog.model_validate(resp.json())
        if resp.status_code == 502:
            self.log.error("Error 502 getting loading log, using expensive query")
            resp = httpx.get(
                f"{self.SFS_URL}/admin/logs?api-key={self._sfs_api_key}&tenant={tenant}"
            )  # noqa
            loadings = LoadingLogs.model_validate(resp.json())
            for loading in loadings.root:
                if str(loading.id) == loading_id:
                    return loading
        self.log.error(f"Error gathering logs {resp.text}")

    def check_status_loading(self, tenant: str, loading_id: str) -> LoadingStatus:
        """Check the status of a loading taks

        Arguments:
            tenant: (str) .stat tenant
            loading_id: (str) id of the loading

        Returns:
            LoadingStatus enumeration
        """
        loading = self.get_log(tenant=tenant, loading_id=loading_id)
        if loading.executionStatus == "completed":
            return self.LoadingStatus.COMPLETED
        else:
            self.log.error(f"Mapping outcome of {loading.executionStatus} to RETRY")
            return self.LoadingStatus.RETRY

    def wait_for_index_to_finish(  # noqa FNE005
        self,
        tenant: str,
        loading_id: str,
        startup_sleep: int = 0,
        timeout: int = 600,
        backoff: int = 30,
    ) -> bool:
        """This method will periodically check the status of a loading task and
        until it finishes, error or expires the timeout

        Arguments:
            tenant: (str) .stat tenant
            loading_id: (str) id of the loading
            startup_sleep: (int) grace period (secs) before start fetching the
                           loading state
            timeout: (int) max time (secs) the loop will be running
            backoff: (int) time between iterations fetching the data

        Returns:
            boolean stating if the loading task finished correctly
        """
        start = time.time()
        time.sleep(startup_sleep)

        self.log.info("STARTING")
        while True:
            status = self.check_status_loading(tenant=tenant, loading_id=loading_id)
            if status == self.LoadingStatus.COMPLETED:
                return True

            if time.time() - start > timeout:
                self.log.error(
                    f"Timeout waiting for dataflows to be indexed {timeout} seconds passed"  # noqa
                )
                return False
            self.log.error(
                "Still not information retrieved about the loading, waiting..."
            )
            time.sleep(backoff)
