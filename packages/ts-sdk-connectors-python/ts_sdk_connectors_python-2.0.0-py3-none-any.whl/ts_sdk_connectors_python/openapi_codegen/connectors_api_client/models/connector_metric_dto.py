from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.metric_time_value_dto import MetricTimeValueDto


T = TypeVar("T", bound="ConnectorMetricDto")


@_attrs_define
class ConnectorMetricDto:
    """
    Attributes:
        name (str):
        values (list['MetricTimeValueDto']):
    """

    name: str
    values: list["MetricTimeValueDto"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        values = []
        for values_item_data in self.values:
            values_item = values_item_data.to_dict()
            values.append(values_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "values": values,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.metric_time_value_dto import MetricTimeValueDto

        d = src_dict.copy()
        name = d.pop("name")

        values = []
        _values = d.pop("values")
        for values_item_data in _values:
            values_item = MetricTimeValueDto.from_dict(values_item_data)

            values.append(values_item)

        connector_metric_dto = cls(
            name=name,
            values=values,
        )

        connector_metric_dto.additional_properties = d
        return connector_metric_dto

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
