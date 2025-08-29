from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.save_connector_file_request_metadata import (
        SaveConnectorFileRequestMetadata,
    )


T = TypeVar("T", bound="SaveConnectorFileRequest")


@_attrs_define
class SaveConnectorFileRequest:
    """
    Attributes:
        id (Union[Unset, str]):
        unique_external_id (Union[Unset, str]):
        metadata (Union[Unset, SaveConnectorFileRequestMetadata]):
        status (Union[Unset, str]):
        error_count (Union[Unset, float]):
        error_message (Union[Unset, str]):
        filepath (Union[Unset, str]):
    """

    id: Union[Unset, str] = UNSET
    unique_external_id: Union[Unset, str] = UNSET
    metadata: Union[Unset, "SaveConnectorFileRequestMetadata"] = UNSET
    status: Union[Unset, str] = UNSET
    error_count: Union[Unset, float] = UNSET
    error_message: Union[Unset, str] = UNSET
    filepath: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        unique_external_id = self.unique_external_id

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        status = self.status

        error_count = self.error_count

        error_message = self.error_message

        filepath = self.filepath

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if unique_external_id is not UNSET:
            field_dict["uniqueExternalId"] = unique_external_id
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if status is not UNSET:
            field_dict["status"] = status
        if error_count is not UNSET:
            field_dict["errorCount"] = error_count
        if error_message is not UNSET:
            field_dict["errorMessage"] = error_message
        if filepath is not UNSET:
            field_dict["filepath"] = filepath

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.save_connector_file_request_metadata import (
            SaveConnectorFileRequestMetadata,
        )

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        unique_external_id = d.pop("uniqueExternalId", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, SaveConnectorFileRequestMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = SaveConnectorFileRequestMetadata.from_dict(_metadata)

        status = d.pop("status", UNSET)

        error_count = d.pop("errorCount", UNSET)

        error_message = d.pop("errorMessage", UNSET)

        filepath = d.pop("filepath", UNSET)

        save_connector_file_request = cls(
            id=id,
            unique_external_id=unique_external_id,
            metadata=metadata,
            status=status,
            error_count=error_count,
            error_message=error_message,
            filepath=filepath,
        )

        save_connector_file_request.additional_properties = d
        return save_connector_file_request

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
