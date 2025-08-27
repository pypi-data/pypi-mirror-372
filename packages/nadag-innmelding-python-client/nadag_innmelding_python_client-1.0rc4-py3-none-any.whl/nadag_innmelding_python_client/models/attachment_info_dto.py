from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AttachmentInfoDto")


@_attrs_define
class AttachmentInfoDto:
    """Attachment info result

    Attributes:
        attachment_id (Union[Unset, str]):
        uniq_id (Union[Unset, str]):
    """

    attachment_id: Union[Unset, str] = UNSET
    uniq_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        attachment_id = self.attachment_id

        uniq_id = self.uniq_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if attachment_id is not UNSET:
            field_dict["attachmentId"] = attachment_id
        if uniq_id is not UNSET:
            field_dict["uniqId"] = uniq_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        attachment_id = d.pop("attachmentId", UNSET)

        uniq_id = d.pop("uniqId", UNSET)

        attachment_info_dto = cls(
            attachment_id=attachment_id,
            uniq_id=uniq_id,
        )

        attachment_info_dto.additional_properties = d
        return attachment_info_dto

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
