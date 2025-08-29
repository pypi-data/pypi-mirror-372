from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateHubRequest")


@_attrs_define
class UpdateHubRequest:
    """
    Attributes:
        name (str):
        l_7_proxy_forward_port (float):
        l_7_proxy_reverse_http_port (float):
        l_7_proxy_reverse_https_port (float):
        l_7_proxy_socat_port (float):
        l_7_proxy_localnets (str):
        l_7_proxy_dns_nameservers (str):
        description (Union[Unset, str]):
        l_7_proxy_reverse_mqtt_port (Union[Unset, float]):
        l_7_proxy_socat_mqtt_port (Union[Unset, float]):
        l_7_proxy_whitelist (Union[Unset, str]):
        l_7_proxy_config_override (Union[Unset, str]):
        l_7_proxy_maximum_memory_mb (Union[Unset, float]):
        reset_hub_migration_status (Union[Unset, bool]):
    """

    name: str
    l_7_proxy_forward_port: float
    l_7_proxy_reverse_http_port: float
    l_7_proxy_reverse_https_port: float
    l_7_proxy_socat_port: float
    l_7_proxy_localnets: str
    l_7_proxy_dns_nameservers: str
    description: Union[Unset, str] = UNSET
    l_7_proxy_reverse_mqtt_port: Union[Unset, float] = UNSET
    l_7_proxy_socat_mqtt_port: Union[Unset, float] = UNSET
    l_7_proxy_whitelist: Union[Unset, str] = UNSET
    l_7_proxy_config_override: Union[Unset, str] = UNSET
    l_7_proxy_maximum_memory_mb: Union[Unset, float] = UNSET
    reset_hub_migration_status: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        l_7_proxy_forward_port = self.l_7_proxy_forward_port

        l_7_proxy_reverse_http_port = self.l_7_proxy_reverse_http_port

        l_7_proxy_reverse_https_port = self.l_7_proxy_reverse_https_port

        l_7_proxy_socat_port = self.l_7_proxy_socat_port

        l_7_proxy_localnets = self.l_7_proxy_localnets

        l_7_proxy_dns_nameservers = self.l_7_proxy_dns_nameservers

        description = self.description

        l_7_proxy_reverse_mqtt_port = self.l_7_proxy_reverse_mqtt_port

        l_7_proxy_socat_mqtt_port = self.l_7_proxy_socat_mqtt_port

        l_7_proxy_whitelist = self.l_7_proxy_whitelist

        l_7_proxy_config_override = self.l_7_proxy_config_override

        l_7_proxy_maximum_memory_mb = self.l_7_proxy_maximum_memory_mb

        reset_hub_migration_status = self.reset_hub_migration_status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "l7ProxyForwardPort": l_7_proxy_forward_port,
                "l7ProxyReverseHttpPort": l_7_proxy_reverse_http_port,
                "l7ProxyReverseHttpsPort": l_7_proxy_reverse_https_port,
                "l7ProxySocatPort": l_7_proxy_socat_port,
                "l7ProxyLocalnets": l_7_proxy_localnets,
                "l7ProxyDnsNameservers": l_7_proxy_dns_nameservers,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if l_7_proxy_reverse_mqtt_port is not UNSET:
            field_dict["l7ProxyReverseMqttPort"] = l_7_proxy_reverse_mqtt_port
        if l_7_proxy_socat_mqtt_port is not UNSET:
            field_dict["l7ProxySocatMqttPort"] = l_7_proxy_socat_mqtt_port
        if l_7_proxy_whitelist is not UNSET:
            field_dict["l7ProxyWhitelist"] = l_7_proxy_whitelist
        if l_7_proxy_config_override is not UNSET:
            field_dict["l7ProxyConfigOverride"] = l_7_proxy_config_override
        if l_7_proxy_maximum_memory_mb is not UNSET:
            field_dict["l7ProxyMaximumMemoryMb"] = l_7_proxy_maximum_memory_mb
        if reset_hub_migration_status is not UNSET:
            field_dict["resetHubMigrationStatus"] = reset_hub_migration_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        l_7_proxy_forward_port = d.pop("l7ProxyForwardPort")

        l_7_proxy_reverse_http_port = d.pop("l7ProxyReverseHttpPort")

        l_7_proxy_reverse_https_port = d.pop("l7ProxyReverseHttpsPort")

        l_7_proxy_socat_port = d.pop("l7ProxySocatPort")

        l_7_proxy_localnets = d.pop("l7ProxyLocalnets")

        l_7_proxy_dns_nameservers = d.pop("l7ProxyDnsNameservers")

        description = d.pop("description", UNSET)

        l_7_proxy_reverse_mqtt_port = d.pop("l7ProxyReverseMqttPort", UNSET)

        l_7_proxy_socat_mqtt_port = d.pop("l7ProxySocatMqttPort", UNSET)

        l_7_proxy_whitelist = d.pop("l7ProxyWhitelist", UNSET)

        l_7_proxy_config_override = d.pop("l7ProxyConfigOverride", UNSET)

        l_7_proxy_maximum_memory_mb = d.pop("l7ProxyMaximumMemoryMb", UNSET)

        reset_hub_migration_status = d.pop("resetHubMigrationStatus", UNSET)

        update_hub_request = cls(
            name=name,
            l_7_proxy_forward_port=l_7_proxy_forward_port,
            l_7_proxy_reverse_http_port=l_7_proxy_reverse_http_port,
            l_7_proxy_reverse_https_port=l_7_proxy_reverse_https_port,
            l_7_proxy_socat_port=l_7_proxy_socat_port,
            l_7_proxy_localnets=l_7_proxy_localnets,
            l_7_proxy_dns_nameservers=l_7_proxy_dns_nameservers,
            description=description,
            l_7_proxy_reverse_mqtt_port=l_7_proxy_reverse_mqtt_port,
            l_7_proxy_socat_mqtt_port=l_7_proxy_socat_mqtt_port,
            l_7_proxy_whitelist=l_7_proxy_whitelist,
            l_7_proxy_config_override=l_7_proxy_config_override,
            l_7_proxy_maximum_memory_mb=l_7_proxy_maximum_memory_mb,
            reset_hub_migration_status=reset_hub_migration_status,
        )

        update_hub_request.additional_properties = d
        return update_hub_request

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
