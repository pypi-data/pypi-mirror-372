from enum import Enum


class ConnectorCustomRouteUiComponentDtoTrigger(str, Enum):
    ROUTE = "route"

    def __str__(self) -> str:
        return str(self.value)
