from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="HubHostDto")


@_attrs_define
class HubHostDto:
    """
    Attributes:
        ip_address (Union[Unset, str]):
        host_name (Union[Unset, str]):
        platform_name (Union[Unset, str]):
        platform_version (Union[Unset, str]):
    """

    ip_address: Union[Unset, str] = UNSET
    host_name: Union[Unset, str] = UNSET
    platform_name: Union[Unset, str] = UNSET
    platform_version: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ip_address = self.ip_address

        host_name = self.host_name

        platform_name = self.platform_name

        platform_version = self.platform_version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if ip_address is not UNSET:
            field_dict["ipAddress"] = ip_address
        if host_name is not UNSET:
            field_dict["hostName"] = host_name
        if platform_name is not UNSET:
            field_dict["platformName"] = platform_name
        if platform_version is not UNSET:
            field_dict["platformVersion"] = platform_version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        ip_address = d.pop("ipAddress", UNSET)

        host_name = d.pop("hostName", UNSET)

        platform_name = d.pop("platformName", UNSET)

        platform_version = d.pop("platformVersion", UNSET)

        hub_host_dto = cls(
            ip_address=ip_address,
            host_name=host_name,
            platform_name=platform_name,
            platform_version=platform_version,
        )

        hub_host_dto.additional_properties = d
        return hub_host_dto

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
