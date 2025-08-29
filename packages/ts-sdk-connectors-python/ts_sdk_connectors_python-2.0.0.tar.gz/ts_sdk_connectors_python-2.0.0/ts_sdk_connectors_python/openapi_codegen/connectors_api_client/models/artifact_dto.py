from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.artifact_dto_manifest import ArtifactDtoManifest


T = TypeVar("T", bound="ArtifactDto")


@_attrs_define
class ArtifactDto:
    """
    Attributes:
        namespace (str):
        slug (str):
        version (str):
        manifest (Union[Unset, ArtifactDtoManifest]):
    """

    namespace: str
    slug: str
    version: str
    manifest: Union[Unset, "ArtifactDtoManifest"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        namespace = self.namespace

        slug = self.slug

        version = self.version

        manifest: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.manifest, Unset):
            manifest = self.manifest.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "namespace": namespace,
                "slug": slug,
                "version": version,
            }
        )
        if manifest is not UNSET:
            field_dict["manifest"] = manifest

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.artifact_dto_manifest import ArtifactDtoManifest

        d = src_dict.copy()
        namespace = d.pop("namespace")

        slug = d.pop("slug")

        version = d.pop("version")

        _manifest = d.pop("manifest", UNSET)
        manifest: Union[Unset, ArtifactDtoManifest]
        if isinstance(_manifest, Unset):
            manifest = UNSET
        else:
            manifest = ArtifactDtoManifest.from_dict(_manifest)

        artifact_dto = cls(
            namespace=namespace,
            slug=slug,
            version=version,
            manifest=manifest,
        )

        artifact_dto.additional_properties = d
        return artifact_dto

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
