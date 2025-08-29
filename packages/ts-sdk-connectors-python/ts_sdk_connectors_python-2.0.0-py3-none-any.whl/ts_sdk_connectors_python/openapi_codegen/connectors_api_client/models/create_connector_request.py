from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_connector_request_host_type import CreateConnectorRequestHostType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_connector_request_metadata import (
        CreateConnectorRequestMetadata,
    )


T = TypeVar("T", bound="CreateConnectorRequest")


@_attrs_define
class CreateConnectorRequest:
    """
    Attributes:
        name (str):
        host_type (CreateConnectorRequestHostType):  Default: CreateConnectorRequestHostType.HUB.
        connector_type (str):
        description (Union[Unset, str]):
        hub_id (Union[Unset, str]):
        metadata (Union[Unset, CreateConnectorRequestMetadata]):
        tags (Union[Unset, list[str]]):
        labels (Union[Unset, list[str]]):
    """

    name: str
    connector_type: str
    host_type: CreateConnectorRequestHostType = CreateConnectorRequestHostType.HUB
    description: Union[Unset, str] = UNSET
    hub_id: Union[Unset, str] = UNSET
    metadata: Union[Unset, "CreateConnectorRequestMetadata"] = UNSET
    tags: Union[Unset, list[str]] = UNSET
    labels: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        host_type = self.host_type.value

        connector_type = self.connector_type

        description = self.description

        hub_id = self.hub_id

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        tags: Union[Unset, list[str]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        labels: Union[Unset, list[str]] = UNSET
        if not isinstance(self.labels, Unset):
            labels = self.labels

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "hostType": host_type,
                "connectorType": connector_type,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if hub_id is not UNSET:
            field_dict["hubId"] = hub_id
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if tags is not UNSET:
            field_dict["tags"] = tags
        if labels is not UNSET:
            field_dict["labels"] = labels

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.create_connector_request_metadata import (
            CreateConnectorRequestMetadata,
        )

        d = src_dict.copy()
        name = d.pop("name")

        host_type = CreateConnectorRequestHostType(d.pop("hostType"))

        connector_type = d.pop("connectorType")

        description = d.pop("description", UNSET)

        hub_id = d.pop("hubId", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, CreateConnectorRequestMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = CreateConnectorRequestMetadata.from_dict(_metadata)

        tags = cast(list[str], d.pop("tags", UNSET))

        labels = cast(list[str], d.pop("labels", UNSET))

        create_connector_request = cls(
            name=name,
            host_type=host_type,
            connector_type=connector_type,
            description=description,
            hub_id=hub_id,
            metadata=metadata,
            tags=tags,
            labels=labels,
        )

        create_connector_request.additional_properties = d
        return create_connector_request

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
