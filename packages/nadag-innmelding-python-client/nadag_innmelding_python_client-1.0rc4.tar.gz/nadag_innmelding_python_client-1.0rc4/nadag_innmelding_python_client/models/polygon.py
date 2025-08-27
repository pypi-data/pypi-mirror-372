from collections.abc import Mapping
from typing import Any, Literal, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Polygon")


@_attrs_define
class Polygon:
    """
    Attributes:
        type_ (Union[Literal['Polygon'], Unset]):
        coordinates (Union[Unset, list[list[list[float]]]]):
    """

    type_: Union[Literal["Polygon"], Unset] = UNSET
    coordinates: Union[Unset, list[list[list[float]]]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        coordinates: Union[Unset, list[list[list[float]]]] = UNSET
        if not isinstance(self.coordinates, Unset):
            coordinates = []
            for componentsschemas_coordinates_lists_item_data in self.coordinates:
                componentsschemas_coordinates_lists_item = []
                for componentsschemas_coordinates_list_item_data in componentsschemas_coordinates_lists_item_data:
                    componentsschemas_coordinates_list_item = componentsschemas_coordinates_list_item_data

                    componentsschemas_coordinates_lists_item.append(componentsschemas_coordinates_list_item)

                coordinates.append(componentsschemas_coordinates_lists_item)

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
        type_ = cast(Union[Literal["Polygon"], Unset], d.pop("type", UNSET))
        if type_ != "Polygon" and not isinstance(type_, Unset):
            raise ValueError(f"type must match const 'Polygon', got '{type_}'")

        coordinates = []
        _coordinates = d.pop("coordinates", UNSET)
        for componentsschemas_coordinates_lists_item_data in _coordinates or []:
            componentsschemas_coordinates_lists_item = []
            _componentsschemas_coordinates_lists_item = componentsschemas_coordinates_lists_item_data
            for componentsschemas_coordinates_list_item_data in _componentsschemas_coordinates_lists_item:
                componentsschemas_coordinates_list_item = cast(
                    list[float], componentsschemas_coordinates_list_item_data
                )

                componentsschemas_coordinates_lists_item.append(componentsschemas_coordinates_list_item)

            coordinates.append(componentsschemas_coordinates_lists_item)

        polygon = cls(
            type_=type_,
            coordinates=coordinates,
        )

        polygon.additional_properties = d
        return polygon

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
