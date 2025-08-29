from enum import Enum


class ConnectorGeneratedConfigUiComponentDtoTrigger(str, Enum):
    CONFIGURATION = "configuration"

    def __str__(self) -> str:
        return str(self.value)
