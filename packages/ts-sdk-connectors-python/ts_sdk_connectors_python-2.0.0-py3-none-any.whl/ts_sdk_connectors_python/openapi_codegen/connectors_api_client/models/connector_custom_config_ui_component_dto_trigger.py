from enum import Enum


class ConnectorCustomConfigUiComponentDtoTrigger(str, Enum):
    CONFIGURATION = "configuration"

    def __str__(self) -> str:
        return str(self.value)
