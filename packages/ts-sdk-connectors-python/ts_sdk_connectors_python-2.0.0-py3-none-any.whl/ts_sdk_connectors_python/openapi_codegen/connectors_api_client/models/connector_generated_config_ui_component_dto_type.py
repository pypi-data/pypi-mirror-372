from enum import Enum


class ConnectorGeneratedConfigUiComponentDtoType(str, Enum):
    GENERATED = "generated"

    def __str__(self) -> str:
        return str(self.value)
