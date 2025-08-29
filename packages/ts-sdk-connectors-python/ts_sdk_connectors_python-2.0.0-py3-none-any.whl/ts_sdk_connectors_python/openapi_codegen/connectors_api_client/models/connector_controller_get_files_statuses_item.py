from enum import Enum


class ConnectorControllerGetFilesStatusesItem(str, Enum):
    ERROR = "ERROR"
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SKIPPED = "SKIPPED"
    SUCCESS = "SUCCESS"

    def __str__(self) -> str:
        return str(self.value)
