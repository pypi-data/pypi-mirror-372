import datetime
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.transaction_error_dto_entity_type import TransactionErrorDtoEntityType

if TYPE_CHECKING:
    from ..models.transaction_error_dto_metadata import TransactionErrorDtoMetadata


T = TypeVar("T", bound="TransactionErrorDto")


@_attrs_define
class TransactionErrorDto:
    """
    Attributes:
        id (str):
        org_slug (str):
        entity_type (TransactionErrorDtoEntityType):
        entity_id (str):
        action (str):
        metadata (TransactionErrorDtoMetadata):
        error (str):
        created_at (datetime.datetime):
    """

    id: str
    org_slug: str
    entity_type: TransactionErrorDtoEntityType
    entity_id: str
    action: str
    metadata: "TransactionErrorDtoMetadata"
    error: str
    created_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        org_slug = self.org_slug

        entity_type = self.entity_type.value

        entity_id = self.entity_id

        action = self.action

        metadata = self.metadata.to_dict()

        error = self.error

        created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "orgSlug": org_slug,
                "entityType": entity_type,
                "entityId": entity_id,
                "action": action,
                "metadata": metadata,
                "error": error,
                "createdAt": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.transaction_error_dto_metadata import TransactionErrorDtoMetadata

        d = src_dict.copy()
        id = d.pop("id")

        org_slug = d.pop("orgSlug")

        entity_type = TransactionErrorDtoEntityType(d.pop("entityType"))

        entity_id = d.pop("entityId")

        action = d.pop("action")

        metadata = TransactionErrorDtoMetadata.from_dict(d.pop("metadata"))

        error = d.pop("error")

        created_at = isoparse(d.pop("createdAt"))

        transaction_error_dto = cls(
            id=id,
            org_slug=org_slug,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            metadata=metadata,
            error=error,
            created_at=created_at,
        )

        transaction_error_dto.additional_properties = d
        return transaction_error_dto

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
