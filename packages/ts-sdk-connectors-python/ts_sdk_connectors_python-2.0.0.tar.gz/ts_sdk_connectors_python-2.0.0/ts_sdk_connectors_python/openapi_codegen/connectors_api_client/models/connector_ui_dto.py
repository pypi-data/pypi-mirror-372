from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.connector_custom_config_ui_component_dto import (
        ConnectorCustomConfigUiComponentDto,
    )
    from ..models.connector_custom_route_ui_component_dto import (
        ConnectorCustomRouteUiComponentDto,
    )
    from ..models.connector_generated_config_ui_component_dto import (
        ConnectorGeneratedConfigUiComponentDto,
    )


T = TypeVar("T", bound="ConnectorUiDto")


@_attrs_define
class ConnectorUiDto:
    """
    Attributes:
        components (list[Union['ConnectorCustomConfigUiComponentDto', 'ConnectorCustomRouteUiComponentDto',
            'ConnectorGeneratedConfigUiComponentDto']]):
    """

    components: list[
        Union[
            "ConnectorCustomConfigUiComponentDto",
            "ConnectorCustomRouteUiComponentDto",
            "ConnectorGeneratedConfigUiComponentDto",
        ]
    ]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.connector_custom_config_ui_component_dto import (
            ConnectorCustomConfigUiComponentDto,
        )
        from ..models.connector_generated_config_ui_component_dto import (
            ConnectorGeneratedConfigUiComponentDto,
        )

        components = []
        for components_item_data in self.components:
            components_item: dict[str, Any]
            if isinstance(components_item_data, ConnectorGeneratedConfigUiComponentDto):
                components_item = components_item_data.to_dict()
            elif isinstance(components_item_data, ConnectorCustomConfigUiComponentDto):
                components_item = components_item_data.to_dict()
            else:
                components_item = components_item_data.to_dict()

            components.append(components_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "components": components,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.connector_custom_config_ui_component_dto import (
            ConnectorCustomConfigUiComponentDto,
        )
        from ..models.connector_custom_route_ui_component_dto import (
            ConnectorCustomRouteUiComponentDto,
        )
        from ..models.connector_generated_config_ui_component_dto import (
            ConnectorGeneratedConfigUiComponentDto,
        )

        d = src_dict.copy()
        components = []
        _components = d.pop("components")
        for components_item_data in _components:

            def _parse_components_item(
                data: object,
            ) -> Union[
                "ConnectorCustomConfigUiComponentDto",
                "ConnectorCustomRouteUiComponentDto",
                "ConnectorGeneratedConfigUiComponentDto",
            ]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    components_item_type_0 = (
                        ConnectorGeneratedConfigUiComponentDto.from_dict(data)
                    )

                    return components_item_type_0
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    components_item_type_1 = (
                        ConnectorCustomConfigUiComponentDto.from_dict(data)
                    )

                    return components_item_type_1
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                components_item_type_2 = ConnectorCustomRouteUiComponentDto.from_dict(
                    data
                )

                return components_item_type_2

            components_item = _parse_components_item(components_item_data)

            components.append(components_item)

        connector_ui_dto = cls(
            components=components,
        )

        connector_ui_dto.additional_properties = d
        return connector_ui_dto

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
