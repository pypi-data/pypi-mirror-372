from enum import Enum


class UpdateConnectorStatusResponseStatus(str, Enum):
    DISABLED = "DISABLED"
    IDLE = "IDLE"
    RUNNING = "RUNNING"

    def __str__(self) -> str:
        return str(self.value)
