from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.label_request import LabelRequest


T = TypeVar("T", bound="UpdateConnectorLabelsRequest")


@_attrs_define
class UpdateConnectorLabelsRequest:
    """
    Attributes:
        labels_to_add (Union[Unset, list['LabelRequest']]):
        labels_to_drop (Union[Unset, list[float]]):
    """

    labels_to_add: Union[Unset, list["LabelRequest"]] = UNSET
    labels_to_drop: Union[Unset, list[float]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        labels_to_add: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.labels_to_add, Unset):
            labels_to_add = []
            for labels_to_add_item_data in self.labels_to_add:
                labels_to_add_item = labels_to_add_item_data.to_dict()
                labels_to_add.append(labels_to_add_item)

        labels_to_drop: Union[Unset, list[float]] = UNSET
        if not isinstance(self.labels_to_drop, Unset):
            labels_to_drop = self.labels_to_drop

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if labels_to_add is not UNSET:
            field_dict["labelsToAdd"] = labels_to_add
        if labels_to_drop is not UNSET:
            field_dict["labelsToDrop"] = labels_to_drop

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.label_request import LabelRequest

        d = src_dict.copy()
        labels_to_add = []
        _labels_to_add = d.pop("labelsToAdd", UNSET)
        for labels_to_add_item_data in _labels_to_add or []:
            labels_to_add_item = LabelRequest.from_dict(labels_to_add_item_data)

            labels_to_add.append(labels_to_add_item)

        labels_to_drop = cast(list[float], d.pop("labelsToDrop", UNSET))

        update_connector_labels_request = cls(
            labels_to_add=labels_to_add,
            labels_to_drop=labels_to_drop,
        )

        update_connector_labels_request.additional_properties = d
        return update_connector_labels_request

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
