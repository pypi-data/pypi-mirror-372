from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetConnectorFileStatsDto")


@_attrs_define
class GetConnectorFileStatsDto:
    """
    Attributes:
        total (float):
        success (float):
        pending (float):
        processing (float):
        error (float):
        skipped (float):
    """

    total: float
    success: float
    pending: float
    processing: float
    error: float
    skipped: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total = self.total

        success = self.success

        pending = self.pending

        processing = self.processing

        error = self.error

        skipped = self.skipped

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total": total,
                "success": success,
                "pending": pending,
                "processing": processing,
                "error": error,
                "skipped": skipped,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        total = d.pop("total")

        success = d.pop("success")

        pending = d.pop("pending")

        processing = d.pop("processing")

        error = d.pop("error")

        skipped = d.pop("skipped")

        get_connector_file_stats_dto = cls(
            total=total,
            success=success,
            pending=pending,
            processing=processing,
            error=error,
            skipped=skipped,
        )

        get_connector_file_stats_dto.additional_properties = d
        return get_connector_file_stats_dto

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
