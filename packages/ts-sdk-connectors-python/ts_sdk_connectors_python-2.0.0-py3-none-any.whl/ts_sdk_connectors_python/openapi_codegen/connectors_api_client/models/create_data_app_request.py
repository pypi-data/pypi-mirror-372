from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_data_app_request_host_type import CreateDataAppRequestHostType
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateDataAppRequest")


@_attrs_define
class CreateDataAppRequest:
    """
    Attributes:
        name (str):
        host_type (CreateDataAppRequestHostType):  Default: CreateDataAppRequestHostType.CLOUD.
        connector_type (str):
        provider_ids (list[str]):
        description (Union[Unset, str]):
    """

    name: str
    connector_type: str
    provider_ids: list[str]
    host_type: CreateDataAppRequestHostType = CreateDataAppRequestHostType.CLOUD
    description: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        host_type = self.host_type.value

        connector_type = self.connector_type

        provider_ids = self.provider_ids

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "hostType": host_type,
                "connectorType": connector_type,
                "providerIds": provider_ids,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        host_type = CreateDataAppRequestHostType(d.pop("hostType"))

        connector_type = d.pop("connectorType")

        provider_ids = cast(list[str], d.pop("providerIds"))

        description = d.pop("description", UNSET)

        create_data_app_request = cls(
            name=name,
            host_type=host_type,
            connector_type=connector_type,
            provider_ids=provider_ids,
            description=description,
        )

        create_data_app_request.additional_properties = d
        return create_data_app_request

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
