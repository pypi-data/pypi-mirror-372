from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.hub_dto import HubDto
    from ..models.hub_list_item_dto_status import HubListItemDtoStatus


T = TypeVar("T", bound="HubListItemDto")


@_attrs_define
class HubListItemDto:
    """
    Attributes:
        hub (HubDto):
        status (HubListItemDtoStatus):
    """

    hub: "HubDto"
    status: "HubListItemDtoStatus"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        hub = self.hub.to_dict()

        status = self.status.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "hub": hub,
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.hub_dto import HubDto
        from ..models.hub_list_item_dto_status import HubListItemDtoStatus

        d = src_dict.copy()
        hub = HubDto.from_dict(d.pop("hub"))

        status = HubListItemDtoStatus.from_dict(d.pop("status"))

        hub_list_item_dto = cls(
            hub=hub,
            status=status,
        )

        hub_list_item_dto.additional_properties = d
        return hub_list_item_dto

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
