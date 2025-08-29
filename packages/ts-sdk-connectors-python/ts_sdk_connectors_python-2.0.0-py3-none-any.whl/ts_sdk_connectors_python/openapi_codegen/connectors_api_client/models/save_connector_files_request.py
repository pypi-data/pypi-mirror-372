from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.save_connector_file_request import SaveConnectorFileRequest


T = TypeVar("T", bound="SaveConnectorFilesRequest")


@_attrs_define
class SaveConnectorFilesRequest:
    """
    Attributes:
        files (list['SaveConnectorFileRequest']):
    """

    files: list["SaveConnectorFileRequest"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_dict()
            files.append(files_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "files": files,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.save_connector_file_request import SaveConnectorFileRequest

        d = src_dict.copy()
        files = []
        _files = d.pop("files")
        for files_item_data in _files:
            files_item = SaveConnectorFileRequest.from_dict(files_item_data)

            files.append(files_item)

        save_connector_files_request = cls(
            files=files,
        )

        save_connector_files_request.additional_properties = d
        return save_connector_files_request

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
