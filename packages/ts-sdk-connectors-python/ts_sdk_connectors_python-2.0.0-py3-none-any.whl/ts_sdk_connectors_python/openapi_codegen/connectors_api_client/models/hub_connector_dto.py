import datetime
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.hub_connector_dto_host_type import HubConnectorDtoHostType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.artifact_dto import ArtifactDto


T = TypeVar("T", bound="HubConnectorDto")


@_attrs_define
class HubConnectorDto:
    """
    Attributes:
        id (str):
        name (str):
        artifact (ArtifactDto):
        host_type (HubConnectorDtoHostType):
        health (str):
        operating_status (str):
        network_status (str):
        updated_at (datetime.datetime):
        created_at (datetime.datetime):
        health_error_code (Union[Unset, str]):
        last_seen_at (Union[Unset, datetime.datetime]):
        service_discovery_name (Union[Unset, str]):
    """

    id: str
    name: str
    artifact: "ArtifactDto"
    host_type: HubConnectorDtoHostType
    health: str
    operating_status: str
    network_status: str
    updated_at: datetime.datetime
    created_at: datetime.datetime
    health_error_code: Union[Unset, str] = UNSET
    last_seen_at: Union[Unset, datetime.datetime] = UNSET
    service_discovery_name: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        artifact = self.artifact.to_dict()

        host_type = self.host_type.value

        health = self.health

        operating_status = self.operating_status

        network_status = self.network_status

        updated_at = self.updated_at.isoformat()

        created_at = self.created_at.isoformat()

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
                "artifact": artifact,
                "hostType": host_type,
                "health": health,
                "operatingStatus": operating_status,
                "networkStatus": network_status,
                "updatedAt": updated_at,
                "createdAt": created_at,
            }
        )
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

        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        artifact = ArtifactDto.from_dict(d.pop("artifact"))

        host_type = HubConnectorDtoHostType(d.pop("hostType"))

        health = d.pop("health")

        operating_status = d.pop("operatingStatus")

        network_status = d.pop("networkStatus")

        updated_at = isoparse(d.pop("updatedAt"))

        created_at = isoparse(d.pop("createdAt"))

        health_error_code = d.pop("healthErrorCode", UNSET)

        _last_seen_at = d.pop("lastSeenAt", UNSET)
        last_seen_at: Union[Unset, datetime.datetime]
        if isinstance(_last_seen_at, Unset):
            last_seen_at = UNSET
        else:
            last_seen_at = isoparse(_last_seen_at)

        service_discovery_name = d.pop("serviceDiscoveryName", UNSET)

        hub_connector_dto = cls(
            id=id,
            name=name,
            artifact=artifact,
            host_type=host_type,
            health=health,
            operating_status=operating_status,
            network_status=network_status,
            updated_at=updated_at,
            created_at=created_at,
            health_error_code=health_error_code,
            last_seen_at=last_seen_at,
            service_discovery_name=service_discovery_name,
        )

        hub_connector_dto.additional_properties = d
        return hub_connector_dto

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
