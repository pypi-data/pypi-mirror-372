from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.artifact_details_dto_manifest import ArtifactDetailsDtoManifest
    from ..models.connector_ui_dto import ConnectorUiDto


T = TypeVar("T", bound="ArtifactDetailsDto")


@_attrs_define
class ArtifactDetailsDto:
    """
    Attributes:
        namespace (str):
        slug (str):
        version (str):
        name (str):
        manifest (Union[Unset, ArtifactDetailsDtoManifest]):
        description (Union[Unset, str]):
        source_type (Union[Unset, str]):
        ui (Union[Unset, ConnectorUiDto]):
    """

    namespace: str
    slug: str
    version: str
    name: str
    manifest: Union[Unset, "ArtifactDetailsDtoManifest"] = UNSET
    description: Union[Unset, str] = UNSET
    source_type: Union[Unset, str] = UNSET
    ui: Union[Unset, "ConnectorUiDto"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        namespace = self.namespace

        slug = self.slug

        version = self.version

        name = self.name

        manifest: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.manifest, Unset):
            manifest = self.manifest.to_dict()

        description = self.description

        source_type = self.source_type

        ui: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.ui, Unset):
            ui = self.ui.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "namespace": namespace,
                "slug": slug,
                "version": version,
                "name": name,
            }
        )
        if manifest is not UNSET:
            field_dict["manifest"] = manifest
        if description is not UNSET:
            field_dict["description"] = description
        if source_type is not UNSET:
            field_dict["sourceType"] = source_type
        if ui is not UNSET:
            field_dict["ui"] = ui

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.artifact_details_dto_manifest import ArtifactDetailsDtoManifest
        from ..models.connector_ui_dto import ConnectorUiDto

        d = src_dict.copy()
        namespace = d.pop("namespace")

        slug = d.pop("slug")

        version = d.pop("version")

        name = d.pop("name")

        _manifest = d.pop("manifest", UNSET)
        manifest: Union[Unset, ArtifactDetailsDtoManifest]
        if isinstance(_manifest, Unset):
            manifest = UNSET
        else:
            manifest = ArtifactDetailsDtoManifest.from_dict(_manifest)

        description = d.pop("description", UNSET)

        source_type = d.pop("sourceType", UNSET)

        _ui = d.pop("ui", UNSET)
        ui: Union[Unset, ConnectorUiDto]
        if isinstance(_ui, Unset):
            ui = UNSET
        else:
            ui = ConnectorUiDto.from_dict(_ui)

        artifact_details_dto = cls(
            namespace=namespace,
            slug=slug,
            version=version,
            name=name,
            manifest=manifest,
            description=description,
            source_type=source_type,
            ui=ui,
        )

        artifact_details_dto.additional_properties = d
        return artifact_details_dto

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
