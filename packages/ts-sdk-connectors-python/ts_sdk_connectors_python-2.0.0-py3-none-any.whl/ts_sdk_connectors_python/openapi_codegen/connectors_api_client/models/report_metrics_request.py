from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.report_connector_metric_request import ReportConnectorMetricRequest


T = TypeVar("T", bound="ReportMetricsRequest")


@_attrs_define
class ReportMetricsRequest:
    """
    Attributes:
        metrics (list['ReportConnectorMetricRequest']):
    """

    metrics: list["ReportConnectorMetricRequest"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        metrics = []
        for metrics_item_data in self.metrics:
            metrics_item = metrics_item_data.to_dict()
            metrics.append(metrics_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "metrics": metrics,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.report_connector_metric_request import (
            ReportConnectorMetricRequest,
        )

        d = src_dict.copy()
        metrics = []
        _metrics = d.pop("metrics")
        for metrics_item_data in _metrics:
            metrics_item = ReportConnectorMetricRequest.from_dict(metrics_item_data)

            metrics.append(metrics_item)

        report_metrics_request = cls(
            metrics=metrics,
        )

        report_metrics_request.additional_properties = d
        return report_metrics_request

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
