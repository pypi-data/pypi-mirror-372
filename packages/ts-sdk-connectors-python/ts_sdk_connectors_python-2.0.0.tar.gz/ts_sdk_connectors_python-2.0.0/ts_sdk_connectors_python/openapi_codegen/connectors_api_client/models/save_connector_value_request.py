from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.save_connector_value_request_value import (
        SaveConnectorValueRequestValue,
    )


T = TypeVar("T", bound="SaveConnectorValueRequest")


@_attrs_define
class SaveConnectorValueRequest:
    """
    Attributes:
        key (str):
        value (SaveConnectorValueRequestValue):
        secure (Union[Unset, bool]):
    """

    key: str
    value: "SaveConnectorValueRequestValue"
    secure: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        key = self.key

        value = self.value.to_dict()

        secure = self.secure

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "key": key,
                "value": value,
            }
        )
        if secure is not UNSET:
            field_dict["secure"] = secure

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.save_connector_value_request_value import (
            SaveConnectorValueRequestValue,
        )

        d = src_dict.copy()
        key = d.pop("key")

        value = SaveConnectorValueRequestValue.from_dict(d.pop("value"))

        secure = d.pop("secure", UNSET)

        save_connector_value_request = cls(
            key=key,
            value=value,
            secure=secure,
        )

        save_connector_value_request.additional_properties = d
        return save_connector_value_request

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
