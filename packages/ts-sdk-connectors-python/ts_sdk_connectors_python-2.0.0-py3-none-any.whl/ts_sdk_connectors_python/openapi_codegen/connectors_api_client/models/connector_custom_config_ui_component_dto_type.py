from enum import Enum


class ConnectorCustomConfigUiComponentDtoType(str, Enum):
    CUSTOM = "custom"

    def __str__(self) -> str:
        return str(self.value)
