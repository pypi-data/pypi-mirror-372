from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.data_app_dto import DataAppDto


T = TypeVar("T", bound="DataAppsResponse")


@_attrs_define
class DataAppsResponse:
    """
    Attributes:
        data_apps (list['DataAppDto']):
    """

    data_apps: list["DataAppDto"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data_apps = []
        for data_apps_item_data in self.data_apps:
            data_apps_item = data_apps_item_data.to_dict()
            data_apps.append(data_apps_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dataApps": data_apps,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.data_app_dto import DataAppDto

        d = src_dict.copy()
        data_apps = []
        _data_apps = d.pop("dataApps")
        for data_apps_item_data in _data_apps:
            data_apps_item = DataAppDto.from_dict(data_apps_item_data)

            data_apps.append(data_apps_item)

        data_apps_response = cls(
            data_apps=data_apps,
        )

        data_apps_response.additional_properties = d
        return data_apps_response

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
