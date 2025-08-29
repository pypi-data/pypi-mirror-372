from enum import Enum


class UpdateConnectorHealthRequestStatus(str, Enum):
    CRITICAL = "CRITICAL"
    HEALTHY = "HEALTHY"
    NA = "N/A"
    WARNING = "WARNING"

    def __str__(self) -> str:
        return str(self.value)
