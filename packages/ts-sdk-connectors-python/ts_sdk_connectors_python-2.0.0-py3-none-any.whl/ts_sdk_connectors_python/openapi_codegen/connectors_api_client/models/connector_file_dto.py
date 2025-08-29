import datetime
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.connector_file_dto_status import ConnectorFileDtoStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.connector_file_dto_metadata_type_0 import (
        ConnectorFileDtoMetadataType0,
    )


T = TypeVar("T", bound="ConnectorFileDto")


@_attrs_define
class ConnectorFileDto:
    """
    Attributes:
        id (str):
        unique_external_id (str):
        filepath (str):
        status (ConnectorFileDtoStatus):
        metadata (Union['ConnectorFileDtoMetadataType0', None]):
        error_message (Union[None, str]):
        updated_at (datetime.datetime):
        created_at (datetime.datetime):
        error_count (Union[Unset, float]):
    """

    id: str
    unique_external_id: str
    filepath: str
    status: ConnectorFileDtoStatus
    metadata: Union["ConnectorFileDtoMetadataType0", None]
    error_message: Union[None, str]
    updated_at: datetime.datetime
    created_at: datetime.datetime
    error_count: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.connector_file_dto_metadata_type_0 import (
            ConnectorFileDtoMetadataType0,
        )

        id = self.id

        unique_external_id = self.unique_external_id

        filepath = self.filepath

        status = self.status.value

        metadata: Union[None, dict[str, Any]]
        if isinstance(self.metadata, ConnectorFileDtoMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        error_message: Union[None, str]
        error_message = self.error_message

        updated_at = self.updated_at.isoformat()

        created_at = self.created_at.isoformat()

        error_count = self.error_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "uniqueExternalId": unique_external_id,
                "filepath": filepath,
                "status": status,
                "metadata": metadata,
                "errorMessage": error_message,
                "updatedAt": updated_at,
                "createdAt": created_at,
            }
        )
        if error_count is not UNSET:
            field_dict["errorCount"] = error_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.connector_file_dto_metadata_type_0 import (
            ConnectorFileDtoMetadataType0,
        )

        d = src_dict.copy()
        id = d.pop("id")

        unique_external_id = d.pop("uniqueExternalId")

        filepath = d.pop("filepath")

        status = ConnectorFileDtoStatus(d.pop("status"))

        def _parse_metadata(
            data: object,
        ) -> Union["ConnectorFileDtoMetadataType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = ConnectorFileDtoMetadataType0.from_dict(data)

                return metadata_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ConnectorFileDtoMetadataType0", None], data)

        metadata = _parse_metadata(d.pop("metadata"))

        def _parse_error_message(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        error_message = _parse_error_message(d.pop("errorMessage"))

        updated_at = isoparse(d.pop("updatedAt"))

        created_at = isoparse(d.pop("createdAt"))

        error_count = d.pop("errorCount", UNSET)

        connector_file_dto = cls(
            id=id,
            unique_external_id=unique_external_id,
            filepath=filepath,
            status=status,
            metadata=metadata,
            error_message=error_message,
            updated_at=updated_at,
            created_at=created_at,
            error_count=error_count,
        )

        connector_file_dto.additional_properties = d
        return connector_file_dto

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
