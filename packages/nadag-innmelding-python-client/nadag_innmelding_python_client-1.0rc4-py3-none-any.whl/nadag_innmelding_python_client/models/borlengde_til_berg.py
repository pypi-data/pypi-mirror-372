from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.kvalitet_borlengde_til_berg import KvalitetBorlengdeTilBerg
from ..types import UNSET, Unset

T = TypeVar("T", bound="BorlengdeTilBerg")


@_attrs_define
class BorlengdeTilBerg:
    """dybde til fjell som ikke er målt men basert på tolkning

    <engelsk>
    depth to bedrock based on interpretation
    </engelsk>

        Attributes:
            borlengde_kvalitet (KvalitetBorlengdeTilBerg): beskriver om borlengde til berg er antatt eller påvist med en
                sikker metode

                <engelsk>
                defines the quality of the depth information either assumed or confirmed by a secure method
                </engelsk>
            borlengde_til_berg (Union[Unset, float]):
    """

    borlengde_kvalitet: KvalitetBorlengdeTilBerg
    borlengde_til_berg: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        borlengde_kvalitet = self.borlengde_kvalitet.value

        borlengde_til_berg = self.borlengde_til_berg

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "borlengdeKvalitet": borlengde_kvalitet,
            }
        )
        if borlengde_til_berg is not UNSET:
            field_dict["borlengdeTilBerg"] = borlengde_til_berg

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        borlengde_kvalitet = KvalitetBorlengdeTilBerg(d.pop("borlengdeKvalitet"))

        borlengde_til_berg = d.pop("borlengdeTilBerg", UNSET)

        borlengde_til_berg = cls(
            borlengde_kvalitet=borlengde_kvalitet,
            borlengde_til_berg=borlengde_til_berg,
        )

        borlengde_til_berg.additional_properties = d
        return borlengde_til_berg

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
