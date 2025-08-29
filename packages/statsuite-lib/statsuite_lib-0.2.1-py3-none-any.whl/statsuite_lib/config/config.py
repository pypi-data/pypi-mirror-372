import logging
from typing import Iterator

import httpx

from .models import Space, Tenants


class ConfigClient:
    """Client for the SDMX Faceted search service"""

    def __init__(self, config_url: str) -> None:
        """Inits the client

        Args:
            config_url: Endpoint url for Config service.
        """

        self._client = httpx.Client()
        self.CONFIG_URL = config_url
        self.log = logging.getLogger("ConfigClient")
        self.log.level = logging.INFO

    def get_tenants(self) -> str:
        """Gets tenants config

        Returns:
            loadingId(str)
        """
        resp = httpx.get(f"{self.CONFIG_URL}/configs/tenants.json")
        if resp.status_code == 200:
            loading = Tenants.model_validate(resp.json())
            return loading

    def get_dataspaces(self, tenant: str = "default") -> Iterator[Space]:
        """Returns a list of dataspaces configured for a tenant

        Args:
            tenant: select which tenant

        Yields:
        Space: A dataspace configuration object for each space in the tenant.
        """
        tenants = self.get_tenants()
        spaces = tenants.root.get(tenant).spaces
        for space in spaces:
            yield spaces.get(space)
