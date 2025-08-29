from typing import Dict, Union

from pydantic import BaseModel, ConfigDict, RootModel


class Index(RootModel):
    """Model for return json from indexing request on SFS

    Attributes:
        root: returns a json in the format { "loadingId": ######### }
    """

    root: Dict[str, Union[str, Dict]]


class Space(BaseModel):
    """Model for spaces inside tenants

    Attributes:
        id: Space id
        url: space url
    """

    id: str  # noqa VNE003
    url: str


class Tenant(BaseModel):
    """Minimun model for Loading Log entity

    Attributes:
        model_config: Configuration
        id: Loadingid
        spaces: Dict of spaces inside tenant
    """

    model_config = ConfigDict(extra="allow")
    id: str  # noqa VNE003
    spaces: Dict[str, Space]


class Tenants(RootModel):
    """Collection of loading log entries

    Attributes:
        root: Collection of Loadings without key
    """

    root: Dict[str, Tenant]
