from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.attachment_infos_dto import AttachmentInfosDto
    from ..models.geoteknisk_unders import GeotekniskUnders
    from ..models.validated_geoteknisk_unders_diagnostics import ValidatedGeotekniskUndersDiagnostics


T = TypeVar("T", bound="ValidatedGeotekniskUnders")


@_attrs_define
class ValidatedGeotekniskUnders:
    """GeotekniskUnders med valideringsresultat

    Attributes:
        geoteknisk_unders (Union[Unset, GeotekniskUnders]): geografisk område hvor det finnes eller er planlagt
            geotekniske borehull tilhørende et gitt prosjekt <engelsk>geographical area where there are or are planned
            geotechnical boreholes for a given project</engelsk>
        diagnostics (Union[Unset, ValidatedGeotekniskUndersDiagnostics]):
        attachment_infos (Union[Unset, AttachmentInfosDto]): Attachment infos result
    """

    geoteknisk_unders: Union[Unset, "GeotekniskUnders"] = UNSET
    diagnostics: Union[Unset, "ValidatedGeotekniskUndersDiagnostics"] = UNSET
    attachment_infos: Union[Unset, "AttachmentInfosDto"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        geoteknisk_unders: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.geoteknisk_unders, Unset):
            geoteknisk_unders = self.geoteknisk_unders.to_dict()

        diagnostics: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.diagnostics, Unset):
            diagnostics = self.diagnostics.to_dict()

        attachment_infos: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.attachment_infos, Unset):
            attachment_infos = self.attachment_infos.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if geoteknisk_unders is not UNSET:
            field_dict["geotekniskUnders"] = geoteknisk_unders
        if diagnostics is not UNSET:
            field_dict["diagnostics"] = diagnostics
        if attachment_infos is not UNSET:
            field_dict["attachmentInfos"] = attachment_infos

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.attachment_infos_dto import AttachmentInfosDto
        from ..models.geoteknisk_unders import GeotekniskUnders
        from ..models.validated_geoteknisk_unders_diagnostics import ValidatedGeotekniskUndersDiagnostics

        d = dict(src_dict)
        _geoteknisk_unders = d.pop("geotekniskUnders", UNSET)
        geoteknisk_unders: Union[Unset, GeotekniskUnders]
        if isinstance(_geoteknisk_unders, Unset):
            geoteknisk_unders = UNSET
        else:
            geoteknisk_unders = GeotekniskUnders.from_dict(_geoteknisk_unders)

        _diagnostics = d.pop("diagnostics", UNSET)
        diagnostics: Union[Unset, ValidatedGeotekniskUndersDiagnostics]
        if isinstance(_diagnostics, Unset):
            diagnostics = UNSET
        else:
            diagnostics = ValidatedGeotekniskUndersDiagnostics.from_dict(_diagnostics)

        _attachment_infos = d.pop("attachmentInfos", UNSET)
        attachment_infos: Union[Unset, AttachmentInfosDto]
        if isinstance(_attachment_infos, Unset):
            attachment_infos = UNSET
        else:
            attachment_infos = AttachmentInfosDto.from_dict(_attachment_infos)

        validated_geoteknisk_unders = cls(
            geoteknisk_unders=geoteknisk_unders,
            diagnostics=diagnostics,
            attachment_infos=attachment_infos,
        )

        validated_geoteknisk_unders.additional_properties = d
        return validated_geoteknisk_unders

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
