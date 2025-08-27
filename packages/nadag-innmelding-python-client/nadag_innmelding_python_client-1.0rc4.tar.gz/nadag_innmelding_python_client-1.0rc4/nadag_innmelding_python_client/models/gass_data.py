from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GassData")


@_attrs_define
class GassData:
    """resultater fra gassmålinger<engelsk>results from gas measurements</engelsk>

    Attributes:
        ch4 (Union[Unset, float]):
        hg (Union[Unset, float]):
    """

    ch4: Union[Unset, float] = UNSET
    hg: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ch4 = self.ch4

        hg = self.hg

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if ch4 is not UNSET:
            field_dict["CH4"] = ch4
        if hg is not UNSET:
            field_dict["HG"] = hg

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ch4 = d.pop("CH4", UNSET)

        hg = d.pop("HG", UNSET)

        gass_data = cls(
            ch4=ch4,
            hg=hg,
        )

        gass_data.additional_properties = d
        return gass_data

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
