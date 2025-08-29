from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from cyberfusion.CoreApiClient.connector import CoreApiConnector


class Resource:
    def __init__(self, api_connector: "CoreApiConnector") -> None:
        self.api_connector = api_connector
