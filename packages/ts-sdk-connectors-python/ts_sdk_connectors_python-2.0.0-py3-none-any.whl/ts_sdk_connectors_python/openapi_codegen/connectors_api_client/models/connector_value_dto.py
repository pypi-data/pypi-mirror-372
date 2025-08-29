import datetime
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.connector_value_dto_value import ConnectorValueDtoValue


T = TypeVar("T", bound="ConnectorValueDto")


@_attrs_define
class ConnectorValueDto:
    """
    Attributes:
        key (str):
        secure (bool):
        updated_at (datetime.datetime):
        created_at (datetime.datetime):
        value (Union[Unset, ConnectorValueDtoValue]):
    """

    key: str
    secure: bool
    updated_at: datetime.datetime
    created_at: datetime.datetime
    value: Union[Unset, "ConnectorValueDtoValue"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        key = self.key

        secure = self.secure

        updated_at = self.updated_at.isoformat()

        created_at = self.created_at.isoformat()

        value: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.value, Unset):
            value = self.value.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "key": key,
                "secure": secure,
                "updatedAt": updated_at,
                "createdAt": created_at,
            }
        )
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.connector_value_dto_value import ConnectorValueDtoValue

        d = src_dict.copy()
        key = d.pop("key")

        secure = d.pop("secure")

        updated_at = isoparse(d.pop("updatedAt"))

        created_at = isoparse(d.pop("createdAt"))

        _value = d.pop("value", UNSET)
        value: Union[Unset, ConnectorValueDtoValue]
        if isinstance(_value, Unset):
            value = UNSET
        else:
            value = ConnectorValueDtoValue.from_dict(_value)

        connector_value_dto = cls(
            key=key,
            secure=secure,
            updated_at=updated_at,
            created_at=created_at,
            value=value,
        )

        connector_value_dto.additional_properties = d
        return connector_value_dto

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
