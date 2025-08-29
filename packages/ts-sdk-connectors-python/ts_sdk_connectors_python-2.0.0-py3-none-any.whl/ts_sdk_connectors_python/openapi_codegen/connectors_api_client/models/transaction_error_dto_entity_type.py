from enum import Enum


class TransactionErrorDtoEntityType(str, Enum):
    CONNECTOR = "connector"
    HUB = "hub"

    def __str__(self) -> str:
        return str(self.value)
