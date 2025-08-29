from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.field_validation_error import FieldValidationError


T = TypeVar("T", bound="CheckConnectorConfigResponse")


@_attrs_define
class CheckConnectorConfigResponse:
    """
    Attributes:
        valid (bool):
        error (Union[Unset, str]):
        fields (Union[Unset, list['FieldValidationError']]):
    """

    valid: bool
    error: Union[Unset, str] = UNSET
    fields: Union[Unset, list["FieldValidationError"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        valid = self.valid

        error = self.error

        fields: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.fields, Unset):
            fields = []
            for fields_item_data in self.fields:
                fields_item = fields_item_data.to_dict()
                fields.append(fields_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "valid": valid,
            }
        )
        if error is not UNSET:
            field_dict["error"] = error
        if fields is not UNSET:
            field_dict["fields"] = fields

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.field_validation_error import FieldValidationError

        d = src_dict.copy()
        valid = d.pop("valid")

        error = d.pop("error", UNSET)

        fields = []
        _fields = d.pop("fields", UNSET)
        for fields_item_data in _fields or []:
            fields_item = FieldValidationError.from_dict(fields_item_data)

            fields.append(fields_item)

        check_connector_config_response = cls(
            valid=valid,
            error=error,
            fields=fields,
        )

        check_connector_config_response.additional_properties = d
        return check_connector_config_response

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
