from enum import Enum


class UpdateConnectorStatusRequestStatus(str, Enum):
    DISABLED = "DISABLED"
    ENABLED = "ENABLED"
    IDLE = "IDLE"
    RUNNING = "RUNNING"

    def __str__(self) -> str:
        return str(self.value)
