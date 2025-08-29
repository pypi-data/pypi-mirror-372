from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.update_connector_status_request_status import (
    UpdateConnectorStatusRequestStatus,
)

T = TypeVar("T", bound="UpdateConnectorStatusRequest")


@_attrs_define
class UpdateConnectorStatusRequest:
    """
    Attributes:
        status (UpdateConnectorStatusRequestStatus):
    """

    status: UpdateConnectorStatusRequestStatus
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
        status = UpdateConnectorStatusRequestStatus(d.pop("status"))

        update_connector_status_request = cls(
            status=status,
        )

        update_connector_status_request.additional_properties = d
        return update_connector_status_request

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
