import datetime
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.hub_connector_dto import HubConnectorDto
    from ..models.hub_host_dto import HubHostDto
    from ..models.hub_status_dto import HubStatusDto


T = TypeVar("T", bound="HubDetailsDto")


@_attrs_define
class HubDetailsDto:
    """
    Attributes:
        id (str):
        name (str):
        org_slug (str):
        http_proxy_host (str):
        http_proxy_port (float):
        http_proxy_username (str):
        https_proxy_host (str):
        https_proxy_port (float):
        https_proxy_username (str):
        no_proxy (str):
        l_7_proxy_forward_port (float):
        l_7_proxy_reverse_http_port (float):
        l_7_proxy_reverse_https_port (float):
        l_7_proxy_socat_port (float):
        l_7_proxy_reverse_mqtt_port (float):
        l_7_proxy_socat_mqtt_port (float):
        l_7_proxy_localnets (str):
        l_7_proxy_dns_nameservers (str):
        l_7_proxy_whitelist (str):
        l_7_proxy_maximum_memory_mb (float):
        enabled (bool):
        updated_at (datetime.datetime):
        created_at (datetime.datetime):
        activation_expires_at (datetime.datetime):
        ssm_instance_id (str):
        ecs_container_instance_arn (str):
        description (Union[Unset, str]):
        status (Union[Unset, HubStatusDto]):
        host (Union[Unset, HubHostDto]):
        connectors (Union[Unset, list['HubConnectorDto']]):
    """

    id: str
    name: str
    org_slug: str
    http_proxy_host: str
    http_proxy_port: float
    http_proxy_username: str
    https_proxy_host: str
    https_proxy_port: float
    https_proxy_username: str
    no_proxy: str
    l_7_proxy_forward_port: float
    l_7_proxy_reverse_http_port: float
    l_7_proxy_reverse_https_port: float
    l_7_proxy_socat_port: float
    l_7_proxy_reverse_mqtt_port: float
    l_7_proxy_socat_mqtt_port: float
    l_7_proxy_localnets: str
    l_7_proxy_dns_nameservers: str
    l_7_proxy_whitelist: str
    l_7_proxy_maximum_memory_mb: float
    enabled: bool
    updated_at: datetime.datetime
    created_at: datetime.datetime
    activation_expires_at: datetime.datetime
    ssm_instance_id: str
    ecs_container_instance_arn: str
    description: Union[Unset, str] = UNSET
    status: Union[Unset, "HubStatusDto"] = UNSET
    host: Union[Unset, "HubHostDto"] = UNSET
    connectors: Union[Unset, list["HubConnectorDto"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        org_slug = self.org_slug

        http_proxy_host = self.http_proxy_host

        http_proxy_port = self.http_proxy_port

        http_proxy_username = self.http_proxy_username

        https_proxy_host = self.https_proxy_host

        https_proxy_port = self.https_proxy_port

        https_proxy_username = self.https_proxy_username

        no_proxy = self.no_proxy

        l_7_proxy_forward_port = self.l_7_proxy_forward_port

        l_7_proxy_reverse_http_port = self.l_7_proxy_reverse_http_port

        l_7_proxy_reverse_https_port = self.l_7_proxy_reverse_https_port

        l_7_proxy_socat_port = self.l_7_proxy_socat_port

        l_7_proxy_reverse_mqtt_port = self.l_7_proxy_reverse_mqtt_port

        l_7_proxy_socat_mqtt_port = self.l_7_proxy_socat_mqtt_port

        l_7_proxy_localnets = self.l_7_proxy_localnets

        l_7_proxy_dns_nameservers = self.l_7_proxy_dns_nameservers

        l_7_proxy_whitelist = self.l_7_proxy_whitelist

        l_7_proxy_maximum_memory_mb = self.l_7_proxy_maximum_memory_mb

        enabled = self.enabled

        updated_at = self.updated_at.isoformat()

        created_at = self.created_at.isoformat()

        activation_expires_at = self.activation_expires_at.isoformat()

        ssm_instance_id = self.ssm_instance_id

        ecs_container_instance_arn = self.ecs_container_instance_arn

        description = self.description

        status: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.to_dict()

        host: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.host, Unset):
            host = self.host.to_dict()

        connectors: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.connectors, Unset):
            connectors = []
            for connectors_item_data in self.connectors:
                connectors_item = connectors_item_data.to_dict()
                connectors.append(connectors_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "orgSlug": org_slug,
                "httpProxyHost": http_proxy_host,
                "httpProxyPort": http_proxy_port,
                "httpProxyUsername": http_proxy_username,
                "httpsProxyHost": https_proxy_host,
                "httpsProxyPort": https_proxy_port,
                "httpsProxyUsername": https_proxy_username,
                "noProxy": no_proxy,
                "l7ProxyForwardPort": l_7_proxy_forward_port,
                "l7ProxyReverseHttpPort": l_7_proxy_reverse_http_port,
                "l7ProxyReverseHttpsPort": l_7_proxy_reverse_https_port,
                "l7ProxySocatPort": l_7_proxy_socat_port,
                "l7ProxyReverseMqttPort": l_7_proxy_reverse_mqtt_port,
                "l7ProxySocatMqttPort": l_7_proxy_socat_mqtt_port,
                "l7ProxyLocalnets": l_7_proxy_localnets,
                "l7ProxyDnsNameservers": l_7_proxy_dns_nameservers,
                "l7ProxyWhitelist": l_7_proxy_whitelist,
                "l7ProxyMaximumMemoryMb": l_7_proxy_maximum_memory_mb,
                "enabled": enabled,
                "updatedAt": updated_at,
                "createdAt": created_at,
                "activationExpiresAt": activation_expires_at,
                "ssmInstanceId": ssm_instance_id,
                "ecsContainerInstanceArn": ecs_container_instance_arn,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if status is not UNSET:
            field_dict["status"] = status
        if host is not UNSET:
            field_dict["host"] = host
        if connectors is not UNSET:
            field_dict["connectors"] = connectors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.hub_connector_dto import HubConnectorDto
        from ..models.hub_host_dto import HubHostDto
        from ..models.hub_status_dto import HubStatusDto

        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        org_slug = d.pop("orgSlug")

        http_proxy_host = d.pop("httpProxyHost")

        http_proxy_port = d.pop("httpProxyPort")

        http_proxy_username = d.pop("httpProxyUsername")

        https_proxy_host = d.pop("httpsProxyHost")

        https_proxy_port = d.pop("httpsProxyPort")

        https_proxy_username = d.pop("httpsProxyUsername")

        no_proxy = d.pop("noProxy")

        l_7_proxy_forward_port = d.pop("l7ProxyForwardPort")

        l_7_proxy_reverse_http_port = d.pop("l7ProxyReverseHttpPort")

        l_7_proxy_reverse_https_port = d.pop("l7ProxyReverseHttpsPort")

        l_7_proxy_socat_port = d.pop("l7ProxySocatPort")

        l_7_proxy_reverse_mqtt_port = d.pop("l7ProxyReverseMqttPort")

        l_7_proxy_socat_mqtt_port = d.pop("l7ProxySocatMqttPort")

        l_7_proxy_localnets = d.pop("l7ProxyLocalnets")

        l_7_proxy_dns_nameservers = d.pop("l7ProxyDnsNameservers")

        l_7_proxy_whitelist = d.pop("l7ProxyWhitelist")

        l_7_proxy_maximum_memory_mb = d.pop("l7ProxyMaximumMemoryMb")

        enabled = d.pop("enabled")

        updated_at = isoparse(d.pop("updatedAt"))

        created_at = isoparse(d.pop("createdAt"))

        activation_expires_at = isoparse(d.pop("activationExpiresAt"))

        ssm_instance_id = d.pop("ssmInstanceId")

        ecs_container_instance_arn = d.pop("ecsContainerInstanceArn")

        description = d.pop("description", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, HubStatusDto]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = HubStatusDto.from_dict(_status)

        _host = d.pop("host", UNSET)
        host: Union[Unset, HubHostDto]
        if isinstance(_host, Unset):
            host = UNSET
        else:
            host = HubHostDto.from_dict(_host)

        connectors = []
        _connectors = d.pop("connectors", UNSET)
        for connectors_item_data in _connectors or []:
            connectors_item = HubConnectorDto.from_dict(connectors_item_data)

            connectors.append(connectors_item)

        hub_details_dto = cls(
            id=id,
            name=name,
            org_slug=org_slug,
            http_proxy_host=http_proxy_host,
            http_proxy_port=http_proxy_port,
            http_proxy_username=http_proxy_username,
            https_proxy_host=https_proxy_host,
            https_proxy_port=https_proxy_port,
            https_proxy_username=https_proxy_username,
            no_proxy=no_proxy,
            l_7_proxy_forward_port=l_7_proxy_forward_port,
            l_7_proxy_reverse_http_port=l_7_proxy_reverse_http_port,
            l_7_proxy_reverse_https_port=l_7_proxy_reverse_https_port,
            l_7_proxy_socat_port=l_7_proxy_socat_port,
            l_7_proxy_reverse_mqtt_port=l_7_proxy_reverse_mqtt_port,
            l_7_proxy_socat_mqtt_port=l_7_proxy_socat_mqtt_port,
            l_7_proxy_localnets=l_7_proxy_localnets,
            l_7_proxy_dns_nameservers=l_7_proxy_dns_nameservers,
            l_7_proxy_whitelist=l_7_proxy_whitelist,
            l_7_proxy_maximum_memory_mb=l_7_proxy_maximum_memory_mb,
            enabled=enabled,
            updated_at=updated_at,
            created_at=created_at,
            activation_expires_at=activation_expires_at,
            ssm_instance_id=ssm_instance_id,
            ecs_container_instance_arn=ecs_container_instance_arn,
            description=description,
            status=status,
            host=host,
            connectors=connectors,
        )

        hub_details_dto.additional_properties = d
        return hub_details_dto

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
