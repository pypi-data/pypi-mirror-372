from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.update_connector_request_host_type import UpdateConnectorRequestHostType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_connector_labels_request import UpdateConnectorLabelsRequest
    from ..models.update_connector_request_config import UpdateConnectorRequestConfig
    from ..models.update_connector_request_metadata import (
        UpdateConnectorRequestMetadata,
    )


T = TypeVar("T", bound="UpdateConnectorRequest")


@_attrs_define
class UpdateConnectorRequest:
    """
    Attributes:
        description (Union[Unset, str]):
        connector_type (Union[Unset, str]):
        host_type (Union[Unset, UpdateConnectorRequestHostType]):
        hub_id (Union[Unset, str]):
        metadata (Union[Unset, UpdateConnectorRequestMetadata]):
        tags (Union[Unset, list[str]]):
        labels (Union[Unset, list['UpdateConnectorLabelsRequest']]):
        config (Union[Unset, UpdateConnectorRequestConfig]):
        reset_connector_migration_status (Union[Unset, bool]):
    """

    description: Union[Unset, str] = UNSET
    connector_type: Union[Unset, str] = UNSET
    host_type: Union[Unset, UpdateConnectorRequestHostType] = UNSET
    hub_id: Union[Unset, str] = UNSET
    metadata: Union[Unset, "UpdateConnectorRequestMetadata"] = UNSET
    tags: Union[Unset, list[str]] = UNSET
    labels: Union[Unset, list["UpdateConnectorLabelsRequest"]] = UNSET
    config: Union[Unset, "UpdateConnectorRequestConfig"] = UNSET
    reset_connector_migration_status: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        description = self.description

        connector_type = self.connector_type

        host_type: Union[Unset, str] = UNSET
        if not isinstance(self.host_type, Unset):
            host_type = self.host_type.value

        hub_id = self.hub_id

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        tags: Union[Unset, list[str]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        labels: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.labels, Unset):
            labels = []
            for labels_item_data in self.labels:
                labels_item = labels_item_data.to_dict()
                labels.append(labels_item)

        config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        reset_connector_migration_status = self.reset_connector_migration_status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if description is not UNSET:
            field_dict["description"] = description
        if connector_type is not UNSET:
            field_dict["connectorType"] = connector_type
        if host_type is not UNSET:
            field_dict["hostType"] = host_type
        if hub_id is not UNSET:
            field_dict["hubId"] = hub_id
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if tags is not UNSET:
            field_dict["tags"] = tags
        if labels is not UNSET:
            field_dict["labels"] = labels
        if config is not UNSET:
            field_dict["config"] = config
        if reset_connector_migration_status is not UNSET:
            field_dict[
                "resetConnectorMigrationStatus"
            ] = reset_connector_migration_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.update_connector_labels_request import (
            UpdateConnectorLabelsRequest,
        )
        from ..models.update_connector_request_config import (
            UpdateConnectorRequestConfig,
        )
        from ..models.update_connector_request_metadata import (
            UpdateConnectorRequestMetadata,
        )

        d = src_dict.copy()
        description = d.pop("description", UNSET)

        connector_type = d.pop("connectorType", UNSET)

        _host_type = d.pop("hostType", UNSET)
        host_type: Union[Unset, UpdateConnectorRequestHostType]
        if isinstance(_host_type, Unset):
            host_type = UNSET
        else:
            host_type = UpdateConnectorRequestHostType(_host_type)

        hub_id = d.pop("hubId", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, UpdateConnectorRequestMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = UpdateConnectorRequestMetadata.from_dict(_metadata)

        tags = cast(list[str], d.pop("tags", UNSET))

        labels = []
        _labels = d.pop("labels", UNSET)
        for labels_item_data in _labels or []:
            labels_item = UpdateConnectorLabelsRequest.from_dict(labels_item_data)

            labels.append(labels_item)

        _config = d.pop("config", UNSET)
        config: Union[Unset, UpdateConnectorRequestConfig]
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = UpdateConnectorRequestConfig.from_dict(_config)

        reset_connector_migration_status = d.pop("resetConnectorMigrationStatus", UNSET)

        update_connector_request = cls(
            description=description,
            connector_type=connector_type,
            host_type=host_type,
            hub_id=hub_id,
            metadata=metadata,
            tags=tags,
            labels=labels,
            config=config,
            reset_connector_migration_status=reset_connector_migration_status,
        )

        update_connector_request.additional_properties = d
        return update_connector_request

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
