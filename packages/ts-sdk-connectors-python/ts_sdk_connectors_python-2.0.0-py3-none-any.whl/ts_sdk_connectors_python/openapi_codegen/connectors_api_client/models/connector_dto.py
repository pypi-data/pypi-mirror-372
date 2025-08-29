import datetime
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.connector_dto_host_type import ConnectorDtoHostType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.artifact_dto import ArtifactDto
    from ..models.connector_dto_config import ConnectorDtoConfig
    from ..models.connector_dto_metadata import ConnectorDtoMetadata
    from ..models.hub_dto import HubDto


T = TypeVar("T", bound="ConnectorDto")


@_attrs_define
class ConnectorDto:
    """
    Attributes:
        id (str):
        name (str):
        org_slug (str):
        artifact (ArtifactDto):
        host_type (ConnectorDtoHostType):
        health (str):
        operating_status (str):
        network_status (str):
        updated_at (datetime.datetime):
        created_at (datetime.datetime):
        description (Union[None, Unset, str]):
        hub (Union['HubDto', None, Unset]):
        metadata (Union[Unset, ConnectorDtoMetadata]):
        tags (Union[Unset, list[str]]):
        command_queue (Union[Unset, str]):
        cluster_arn (Union[Unset, str]):
        task_definition_arn (Union[None, Unset, str]):
        service_arn (Union[None, Unset, str]):
        health_error_code (Union[None, Unset, str]):
        config (Union[Unset, ConnectorDtoConfig]):
        last_seen_at (Union[None, Unset, datetime.datetime]):
        service_discovery_name (Union[None, Unset, str]):
    """

    id: str
    name: str
    org_slug: str
    artifact: "ArtifactDto"
    host_type: ConnectorDtoHostType
    health: str
    operating_status: str
    network_status: str
    updated_at: datetime.datetime
    created_at: datetime.datetime
    description: Union[None, Unset, str] = UNSET
    hub: Union["HubDto", None, Unset] = UNSET
    metadata: Union[Unset, "ConnectorDtoMetadata"] = UNSET
    tags: Union[Unset, list[str]] = UNSET
    command_queue: Union[Unset, str] = UNSET
    cluster_arn: Union[Unset, str] = UNSET
    task_definition_arn: Union[None, Unset, str] = UNSET
    service_arn: Union[None, Unset, str] = UNSET
    health_error_code: Union[None, Unset, str] = UNSET
    config: Union[Unset, "ConnectorDtoConfig"] = UNSET
    last_seen_at: Union[None, Unset, datetime.datetime] = UNSET
    service_discovery_name: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.hub_dto import HubDto

        id = self.id

        name = self.name

        org_slug = self.org_slug

        artifact = self.artifact.to_dict()

        host_type = self.host_type.value

        health = self.health

        operating_status = self.operating_status

        network_status = self.network_status

        updated_at = self.updated_at.isoformat()

        created_at = self.created_at.isoformat()

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        hub: Union[None, Unset, dict[str, Any]]
        if isinstance(self.hub, Unset):
            hub = UNSET
        elif isinstance(self.hub, HubDto):
            hub = self.hub.to_dict()
        else:
            hub = self.hub

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        tags: Union[Unset, list[str]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        command_queue = self.command_queue

        cluster_arn = self.cluster_arn

        task_definition_arn: Union[None, Unset, str]
        if isinstance(self.task_definition_arn, Unset):
            task_definition_arn = UNSET
        else:
            task_definition_arn = self.task_definition_arn

        service_arn: Union[None, Unset, str]
        if isinstance(self.service_arn, Unset):
            service_arn = UNSET
        else:
            service_arn = self.service_arn

        health_error_code: Union[None, Unset, str]
        if isinstance(self.health_error_code, Unset):
            health_error_code = UNSET
        else:
            health_error_code = self.health_error_code

        config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        last_seen_at: Union[None, Unset, str]
        if isinstance(self.last_seen_at, Unset):
            last_seen_at = UNSET
        elif isinstance(self.last_seen_at, datetime.datetime):
            last_seen_at = self.last_seen_at.isoformat()
        else:
            last_seen_at = self.last_seen_at

        service_discovery_name: Union[None, Unset, str]
        if isinstance(self.service_discovery_name, Unset):
            service_discovery_name = UNSET
        else:
            service_discovery_name = self.service_discovery_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "orgSlug": org_slug,
                "artifact": artifact,
                "hostType": host_type,
                "health": health,
                "operatingStatus": operating_status,
                "networkStatus": network_status,
                "updatedAt": updated_at,
                "createdAt": created_at,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if hub is not UNSET:
            field_dict["hub"] = hub
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if tags is not UNSET:
            field_dict["tags"] = tags
        if command_queue is not UNSET:
            field_dict["commandQueue"] = command_queue
        if cluster_arn is not UNSET:
            field_dict["clusterArn"] = cluster_arn
        if task_definition_arn is not UNSET:
            field_dict["taskDefinitionArn"] = task_definition_arn
        if service_arn is not UNSET:
            field_dict["serviceArn"] = service_arn
        if health_error_code is not UNSET:
            field_dict["healthErrorCode"] = health_error_code
        if config is not UNSET:
            field_dict["config"] = config
        if last_seen_at is not UNSET:
            field_dict["lastSeenAt"] = last_seen_at
        if service_discovery_name is not UNSET:
            field_dict["serviceDiscoveryName"] = service_discovery_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.artifact_dto import ArtifactDto
        from ..models.connector_dto_config import ConnectorDtoConfig
        from ..models.connector_dto_metadata import ConnectorDtoMetadata
        from ..models.hub_dto import HubDto

        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        org_slug = d.pop("orgSlug")

        artifact = ArtifactDto.from_dict(d.pop("artifact"))

        host_type = ConnectorDtoHostType(d.pop("hostType"))

        health = d.pop("health")

        operating_status = d.pop("operatingStatus")

        network_status = d.pop("networkStatus")

        updated_at = isoparse(d.pop("updatedAt"))

        created_at = isoparse(d.pop("createdAt"))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_hub(data: object) -> Union["HubDto", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                hub_type_1 = HubDto.from_dict(data)

                return hub_type_1
            except:  # noqa: E722
                pass
            return cast(Union["HubDto", None, Unset], data)

        hub = _parse_hub(d.pop("hub", UNSET))

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, ConnectorDtoMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = ConnectorDtoMetadata.from_dict(_metadata)

        tags = cast(list[str], d.pop("tags", UNSET))

        command_queue = d.pop("commandQueue", UNSET)

        cluster_arn = d.pop("clusterArn", UNSET)

        def _parse_task_definition_arn(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        task_definition_arn = _parse_task_definition_arn(
            d.pop("taskDefinitionArn", UNSET)
        )

        def _parse_service_arn(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        service_arn = _parse_service_arn(d.pop("serviceArn", UNSET))

        def _parse_health_error_code(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        health_error_code = _parse_health_error_code(d.pop("healthErrorCode", UNSET))

        _config = d.pop("config", UNSET)
        config: Union[Unset, ConnectorDtoConfig]
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = ConnectorDtoConfig.from_dict(_config)

        def _parse_last_seen_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_seen_at_type_0 = isoparse(data)

                return last_seen_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        last_seen_at = _parse_last_seen_at(d.pop("lastSeenAt", UNSET))

        def _parse_service_discovery_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        service_discovery_name = _parse_service_discovery_name(
            d.pop("serviceDiscoveryName", UNSET)
        )

        connector_dto = cls(
            id=id,
            name=name,
            org_slug=org_slug,
            artifact=artifact,
            host_type=host_type,
            health=health,
            operating_status=operating_status,
            network_status=network_status,
            updated_at=updated_at,
            created_at=created_at,
            description=description,
            hub=hub,
            metadata=metadata,
            tags=tags,
            command_queue=command_queue,
            cluster_arn=cluster_arn,
            task_definition_arn=task_definition_arn,
            service_arn=service_arn,
            health_error_code=health_error_code,
            config=config,
            last_seen_at=last_seen_at,
            service_discovery_name=service_discovery_name,
        )

        connector_dto.additional_properties = d
        return connector_dto

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
