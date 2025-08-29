from enum import Enum


class HubConnectorDtoHostType(str, Enum):
    CLOUD = "cloud"
    HUB = "hub"
    LOCAL = "local"
    STANDALONE = "standalone"

    def __str__(self) -> str:
        return str(self.value)
