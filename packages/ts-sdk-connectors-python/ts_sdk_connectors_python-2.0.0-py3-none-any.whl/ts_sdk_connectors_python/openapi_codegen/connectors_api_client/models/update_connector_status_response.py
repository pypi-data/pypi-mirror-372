from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.update_connector_status_response_status import (
    UpdateConnectorStatusResponseStatus,
)

T = TypeVar("T", bound="UpdateConnectorStatusResponse")


@_attrs_define
class UpdateConnectorStatusResponse:
    """
    Attributes:
        status (UpdateConnectorStatusResponseStatus):
    """

    status: UpdateConnectorStatusResponseStatus
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        status = UpdateConnectorStatusResponseStatus(d.pop("status"))

        update_connector_status_response = cls(
            status=status,
        )

        update_connector_status_response.additional_properties = d
        return update_connector_status_response

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
