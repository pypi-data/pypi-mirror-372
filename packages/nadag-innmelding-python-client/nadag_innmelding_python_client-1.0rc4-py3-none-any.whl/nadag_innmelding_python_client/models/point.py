from collections.abc import Mapping
from typing import Any, Literal, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Point")


@_attrs_define
class Point:
    """
    Attributes:
        type_ (Union[Literal['Point'], Unset]):
        coordinates (Union[Unset, list[float]]):
    """

    type_: Union[Literal["Point"], Unset] = UNSET
    coordinates: Union[Unset, list[float]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        coordinates: Union[Unset, list[float]] = UNSET
        if not isinstance(self.coordinates, Unset):
            coordinates = self.coordinates

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type_ is not UNSET:
            field_dict["type"] = type_
        if coordinates is not UNSET:
            field_dict["coordinates"] = coordinates

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Union[Literal["Point"], Unset], d.pop("type", UNSET))
        if type_ != "Point" and not isinstance(type_, Unset):
            raise ValueError(f"type must match const 'Point', got '{type_}'")

        coordinates = cast(list[float], d.pop("coordinates", UNSET))

        point = cls(
            type_=type_,
            coordinates=coordinates,
        )

        point.additional_properties = d
        return point

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
