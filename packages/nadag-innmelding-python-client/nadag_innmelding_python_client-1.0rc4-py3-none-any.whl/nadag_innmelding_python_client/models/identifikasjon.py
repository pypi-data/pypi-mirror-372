from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Identifikasjon")


@_attrs_define
class Identifikasjon:
    """Unik identifikasjon av et objekt, ivaretatt av den ansvarlige produsent/forvalter, som kan benyttes av eksterne
    applikasjoner som referanse til objektet.

    NOTE1 Denne eksterne objektidentifikasjonen må ikke forveksles med en tematisk objektidentifikasjon, slik som f.eks
    bygningsnummer.

    NOTE 2 Denne unike identifikatoren vil ikke endres i løpet av objektets levetid.

        Attributes:
            lokal_id (str):
            navnerom (str):
            versjon_id (Union[Unset, str]):
    """

    lokal_id: str
    navnerom: str
    versjon_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        lokal_id = self.lokal_id

        navnerom = self.navnerom

        versjon_id = self.versjon_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "lokalId": lokal_id,
                "navnerom": navnerom,
            }
        )
        if versjon_id is not UNSET:
            field_dict["versjonId"] = versjon_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        lokal_id = d.pop("lokalId")

        navnerom = d.pop("navnerom")

        versjon_id = d.pop("versjonId", UNSET)

        identifikasjon = cls(
            lokal_id=lokal_id,
            navnerom=navnerom,
            versjon_id=versjon_id,
        )

        identifikasjon.additional_properties = d
        return identifikasjon

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
