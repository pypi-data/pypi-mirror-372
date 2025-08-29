from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.hub_status_dto_health import HubStatusDtoHealth
    from ..models.hub_status_dto_last_seen import HubStatusDtoLastSeen
    from ..models.hub_status_dto_proxies import HubStatusDtoProxies


T = TypeVar("T", bound="HubStatusDto")


@_attrs_define
class HubStatusDto:
    """
    Attributes:
        network (str):
        last_seen (HubStatusDtoLastSeen):
        proxies (Union[Unset, HubStatusDtoProxies]):
        metrics (Union[Unset, list[str]]):
        health (Union[Unset, HubStatusDtoHealth]):
    """

    network: str
    last_seen: "HubStatusDtoLastSeen"
    proxies: Union[Unset, "HubStatusDtoProxies"] = UNSET
    metrics: Union[Unset, list[str]] = UNSET
    health: Union[Unset, "HubStatusDtoHealth"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        network = self.network

        last_seen = self.last_seen.to_dict()

        proxies: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.proxies, Unset):
            proxies = self.proxies.to_dict()

        metrics: Union[Unset, list[str]] = UNSET
        if not isinstance(self.metrics, Unset):
            metrics = self.metrics

        health: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.health, Unset):
            health = self.health.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "network": network,
                "lastSeen": last_seen,
            }
        )
        if proxies is not UNSET:
            field_dict["proxies"] = proxies
        if metrics is not UNSET:
            field_dict["metrics"] = metrics
        if health is not UNSET:
            field_dict["health"] = health

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.hub_status_dto_health import HubStatusDtoHealth
        from ..models.hub_status_dto_last_seen import HubStatusDtoLastSeen
        from ..models.hub_status_dto_proxies import HubStatusDtoProxies

        d = src_dict.copy()
        network = d.pop("network")

        last_seen = HubStatusDtoLastSeen.from_dict(d.pop("lastSeen"))

        _proxies = d.pop("proxies", UNSET)
        proxies: Union[Unset, HubStatusDtoProxies]
        if isinstance(_proxies, Unset):
            proxies = UNSET
        else:
            proxies = HubStatusDtoProxies.from_dict(_proxies)

        metrics = cast(list[str], d.pop("metrics", UNSET))

        _health = d.pop("health", UNSET)
        health: Union[Unset, HubStatusDtoHealth]
        if isinstance(_health, Unset):
            health = UNSET
        else:
            health = HubStatusDtoHealth.from_dict(_health)

        hub_status_dto = cls(
            network=network,
            last_seen=last_seen,
            proxies=proxies,
            metrics=metrics,
            health=health,
        )

        hub_status_dto.additional_properties = d
        return hub_status_dto

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
