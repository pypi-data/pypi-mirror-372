from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.attachment_info_dto import AttachmentInfoDto


T = TypeVar("T", bound="AttachmentInfosDto")


@_attrs_define
class AttachmentInfosDto:
    """Attachment infos result

    Attributes:
        attachment_infos (Union[Unset, list['AttachmentInfoDto']]):
    """

    attachment_infos: Union[Unset, list["AttachmentInfoDto"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        attachment_infos: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.attachment_infos, Unset):
            attachment_infos = []
            for attachment_infos_item_data in self.attachment_infos:
                attachment_infos_item = attachment_infos_item_data.to_dict()
                attachment_infos.append(attachment_infos_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if attachment_infos is not UNSET:
            field_dict["attachmentInfos"] = attachment_infos

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.attachment_info_dto import AttachmentInfoDto

        d = dict(src_dict)
        attachment_infos = []
        _attachment_infos = d.pop("attachmentInfos", UNSET)
        for attachment_infos_item_data in _attachment_infos or []:
            attachment_infos_item = AttachmentInfoDto.from_dict(attachment_infos_item_data)

            attachment_infos.append(attachment_infos_item)

        attachment_infos_dto = cls(
            attachment_infos=attachment_infos,
        )

        attachment_infos_dto.additional_properties = d
        return attachment_infos_dto

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
