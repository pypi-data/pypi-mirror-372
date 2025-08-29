from enum import Enum


class DataAppDtoHostType(str, Enum):
    CLOUD = "cloud"
    LOCAL = "local"

    def __str__(self) -> str:
        return str(self.value)
