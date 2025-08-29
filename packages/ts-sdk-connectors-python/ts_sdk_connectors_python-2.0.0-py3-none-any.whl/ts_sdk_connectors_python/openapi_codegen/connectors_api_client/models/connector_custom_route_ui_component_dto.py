from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.connector_custom_route_ui_component_dto_trigger import (
    ConnectorCustomRouteUiComponentDtoTrigger,
)
from ..models.connector_custom_route_ui_component_dto_type import (
    ConnectorCustomRouteUiComponentDtoType,
)

T = TypeVar("T", bound="ConnectorCustomRouteUiComponentDto")


@_attrs_define
class ConnectorCustomRouteUiComponentDto:
    """
    Attributes:
        type_ (ConnectorCustomRouteUiComponentDtoType):
        trigger (ConnectorCustomRouteUiComponentDtoTrigger):
        route (str):
        component (str):
    """

    type_: ConnectorCustomRouteUiComponentDtoType
    trigger: ConnectorCustomRouteUiComponentDtoTrigger
    route: str
    component: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        trigger = self.trigger.value

        route = self.route

        component = self.component

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "trigger": trigger,
                "route": route,
                "component": component,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        type_ = ConnectorCustomRouteUiComponentDtoType(d.pop("type"))

        trigger = ConnectorCustomRouteUiComponentDtoTrigger(d.pop("trigger"))

        route = d.pop("route")

        component = d.pop("component")

        connector_custom_route_ui_component_dto = cls(
            type_=type_,
            trigger=trigger,
            route=route,
            component=component,
        )

        connector_custom_route_ui_component_dto.additional_properties = d
        return connector_custom_route_ui_component_dto

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
