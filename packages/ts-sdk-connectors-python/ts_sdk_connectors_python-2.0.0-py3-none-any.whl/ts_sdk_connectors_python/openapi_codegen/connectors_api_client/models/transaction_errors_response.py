from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.transaction_error_dto import TransactionErrorDto


T = TypeVar("T", bound="TransactionErrorsResponse")


@_attrs_define
class TransactionErrorsResponse:
    """
    Attributes:
        errors (list['TransactionErrorDto']):
    """

    errors: list["TransactionErrorDto"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        errors = []
        for errors_item_data in self.errors:
            errors_item = errors_item_data.to_dict()
            errors.append(errors_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "errors": errors,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.transaction_error_dto import TransactionErrorDto

        d = src_dict.copy()
        errors = []
        _errors = d.pop("errors")
        for errors_item_data in _errors:
            errors_item = TransactionErrorDto.from_dict(errors_item_data)

            errors.append(errors_item)

        transaction_errors_response = cls(
            errors=errors,
        )

        transaction_errors_response.additional_properties = d
        return transaction_errors_response

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
