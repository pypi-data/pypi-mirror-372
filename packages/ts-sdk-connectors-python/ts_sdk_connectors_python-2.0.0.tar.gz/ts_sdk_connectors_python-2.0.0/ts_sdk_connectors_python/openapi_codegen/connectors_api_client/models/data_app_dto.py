import datetime
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.data_app_dto_host_type import DataAppDtoHostType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.artifact_dto import ArtifactDto
    from ..models.data_app_dto_config import DataAppDtoConfig
    from ..models.data_app_dto_metadata import DataAppDtoMetadata


T = TypeVar("T", bound="DataAppDto")


@_attrs_define
class DataAppDto:
    """
    Attributes:
        id (str):
        name (str):
        org_slug (str):
        artifact (ArtifactDto):
        host_type (DataAppDtoHostType):
        cluster_arn (str):
        task_definition_arn (str):
        task_arn (str):
        health (str):
        operating_status (str):
        network_status (str):
        config (DataAppDtoConfig):
        updated_at (datetime.datetime):
        created_at (datetime.datetime):
        description (Union[Unset, str]):
        metadata (Union[Unset, DataAppDtoMetadata]):
        tags (Union[Unset, list[str]]):
        command_queue (Union[Unset, str]):
        health_error_code (Union[Unset, str]):
        last_seen_at (Union[Unset, datetime.datetime]):
        service_discovery_name (Union[Unset, str]):
    """

    id: str
    name: str
    org_slug: str
    artifact: "ArtifactDto"
    host_type: DataAppDtoHostType
    cluster_arn: str
    task_definition_arn: str
    task_arn: str
    health: str
    operating_status: str
    network_status: str
    config: "DataAppDtoConfig"
    updated_at: datetime.datetime
    created_at: datetime.datetime
    description: Union[Unset, str] = UNSET
    metadata: Union[Unset, "DataAppDtoMetadata"] = UNSET
    tags: Union[Unset, list[str]] = UNSET
    command_queue: Union[Unset, str] = UNSET
    health_error_code: Union[Unset, str] = UNSET
    last_seen_at: Union[Unset, datetime.datetime] = UNSET
    service_discovery_name: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        org_slug = self.org_slug

        artifact = self.artifact.to_dict()

        host_type = self.host_type.value

        cluster_arn = self.cluster_arn

        task_definition_arn = self.task_definition_arn

        task_arn = self.task_arn

        health = self.health

        operating_status = self.operating_status

        network_status = self.network_status

        config = self.config.to_dict()

        updated_at = self.updated_at.isoformat()

        created_at = self.created_at.isoformat()

        description = self.description

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        tags: Union[Unset, list[str]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        command_queue = self.command_queue

        health_error_code = self.health_error_code

        last_seen_at: Union[Unset, str] = UNSET
        if not isinstance(self.last_seen_at, Unset):
            last_seen_at = self.last_seen_at.isoformat()

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
                "clusterArn": cluster_arn,
                "taskDefinitionArn": task_definition_arn,
                "taskArn": task_arn,
                "health": health,
                "operatingStatus": operating_status,
                "networkStatus": network_status,
                "config": config,
                "updatedAt": updated_at,
                "createdAt": created_at,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if tags is not UNSET:
            field_dict["tags"] = tags
        if command_queue is not UNSET:
            field_dict["commandQueue"] = command_queue
        if health_error_code is not UNSET:
            field_dict["healthErrorCode"] = health_error_code
        if last_seen_at is not UNSET:
            field_dict["lastSeenAt"] = last_seen_at
        if service_discovery_name is not UNSET:
            field_dict["serviceDiscoveryName"] = service_discovery_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.artifact_dto import ArtifactDto
        from ..models.data_app_dto_config import DataAppDtoConfig
        from ..models.data_app_dto_metadata import DataAppDtoMetadata

        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        org_slug = d.pop("orgSlug")

        artifact = ArtifactDto.from_dict(d.pop("artifact"))

        host_type = DataAppDtoHostType(d.pop("hostType"))

        cluster_arn = d.pop("clusterArn")

        task_definition_arn = d.pop("taskDefinitionArn")

        task_arn = d.pop("taskArn")

        health = d.pop("health")

        operating_status = d.pop("operatingStatus")

        network_status = d.pop("networkStatus")

        config = DataAppDtoConfig.from_dict(d.pop("config"))

        updated_at = isoparse(d.pop("updatedAt"))

        created_at = isoparse(d.pop("createdAt"))

        description = d.pop("description", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, DataAppDtoMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = DataAppDtoMetadata.from_dict(_metadata)

        tags = cast(list[str], d.pop("tags", UNSET))

        command_queue = d.pop("commandQueue", UNSET)

        health_error_code = d.pop("healthErrorCode", UNSET)

        _last_seen_at = d.pop("lastSeenAt", UNSET)
        last_seen_at: Union[Unset, datetime.datetime]
        if isinstance(_last_seen_at, Unset):
            last_seen_at = UNSET
        else:
            last_seen_at = isoparse(_last_seen_at)

        service_discovery_name = d.pop("serviceDiscoveryName", UNSET)

        data_app_dto = cls(
            id=id,
            name=name,
            org_slug=org_slug,
            artifact=artifact,
            host_type=host_type,
            cluster_arn=cluster_arn,
            task_definition_arn=task_definition_arn,
            task_arn=task_arn,
            health=health,
            operating_status=operating_status,
            network_status=network_status,
            config=config,
            updated_at=updated_at,
            created_at=created_at,
            description=description,
            metadata=metadata,
            tags=tags,
            command_queue=command_queue,
            health_error_code=health_error_code,
            last_seen_at=last_seen_at,
            service_discovery_name=service_discovery_name,
        )

        data_app_dto.additional_properties = d
        return data_app_dto

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
