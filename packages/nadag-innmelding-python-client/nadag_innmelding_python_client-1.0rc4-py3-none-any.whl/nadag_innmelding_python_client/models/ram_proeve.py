from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.proevetaking_type import ProevetakingType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.identifikasjon import Identifikasjon


T = TypeVar("T", bound="RamProeve")


@_attrs_define
class RamProeve:
    """geoteknisk prøvetaking hvor en sylinder slås ned i fast lagrede masser <engelsk>geotechnical sampling where a
    sylinder is rammed into compact soil</engelsk>

        Attributes:
            json_type (Union[Literal['RamProeve'], Unset]):
            identifikasjon (Union[Unset, Identifikasjon]): Unik identifikasjon av et objekt, ivaretatt av den ansvarlige
                produsent/forvalter, som kan benyttes av eksterne applikasjoner som referanse til objektet.

                NOTE1 Denne eksterne objektidentifikasjonen må ikke forveksles med en tematisk objektidentifikasjon, slik som
                f.eks bygningsnummer.

                NOTE 2 Denne unike identifikatoren vil ikke endres i løpet av objektets levetid.
            fra_borlengde (Union[Unset, float]):
            til_borlengde (Union[Unset, float]):
            prøvetype (Union[Unset, ProevetakingType]): inndeling av fysisk prøvemateriale i prøvetype, avhengig av
                prøvetakingsmetode og/eller lagringsmetode for prøvematerialet<engelsk>separation of physical samples in sample
                type classes, depending on sampling method and/or storage method for the sampled material</engelsk>
            densitet_pr_ø_vetaking (Union[Unset, float]):
            milj_ø_teknisk_unders_ø_kelse (Union[Unset, str]):
    """

    json_type: Union[Literal["RamProeve"], Unset] = UNSET
    identifikasjon: Union[Unset, "Identifikasjon"] = UNSET
    fra_borlengde: Union[Unset, float] = UNSET
    til_borlengde: Union[Unset, float] = UNSET
    prøvetype: Union[Unset, ProevetakingType] = UNSET
    densitet_pr_ø_vetaking: Union[Unset, float] = UNSET
    milj_ø_teknisk_unders_ø_kelse: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        json_type = self.json_type

        identifikasjon: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.identifikasjon, Unset):
            identifikasjon = self.identifikasjon.to_dict()

        fra_borlengde = self.fra_borlengde

        til_borlengde = self.til_borlengde

        prøvetype: Union[Unset, str] = UNSET
        if not isinstance(self.prøvetype, Unset):
            prøvetype = self.prøvetype.value

        densitet_pr_ø_vetaking = self.densitet_pr_ø_vetaking

        milj_ø_teknisk_unders_ø_kelse = self.milj_ø_teknisk_unders_ø_kelse

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if json_type is not UNSET:
            field_dict["jsonType"] = json_type
        if identifikasjon is not UNSET:
            field_dict["identifikasjon"] = identifikasjon
        if fra_borlengde is not UNSET:
            field_dict["fraBorlengde"] = fra_borlengde
        if til_borlengde is not UNSET:
            field_dict["tilBorlengde"] = til_borlengde
        if prøvetype is not UNSET:
            field_dict["prøvetype"] = prøvetype
        if densitet_pr_ø_vetaking is not UNSET:
            field_dict["densitetPrøvetaking"] = densitet_pr_ø_vetaking
        if milj_ø_teknisk_unders_ø_kelse is not UNSET:
            field_dict["miljøtekniskUndersøkelse"] = milj_ø_teknisk_unders_ø_kelse

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.identifikasjon import Identifikasjon

        d = dict(src_dict)
        json_type = cast(Union[Literal["RamProeve"], Unset], d.pop("jsonType", UNSET))
        if json_type != "RamProeve" and not isinstance(json_type, Unset):
            raise ValueError(f"jsonType must match const 'RamProeve', got '{json_type}'")

        _identifikasjon = d.pop("identifikasjon", UNSET)
        identifikasjon: Union[Unset, Identifikasjon]
        if isinstance(_identifikasjon, Unset):
            identifikasjon = UNSET
        else:
            identifikasjon = Identifikasjon.from_dict(_identifikasjon)

        fra_borlengde = d.pop("fraBorlengde", UNSET)

        til_borlengde = d.pop("tilBorlengde", UNSET)

        _prøvetype = d.pop("prøvetype", UNSET)
        prøvetype: Union[Unset, ProevetakingType]
        if isinstance(_prøvetype, Unset):
            prøvetype = UNSET
        else:
            prøvetype = ProevetakingType(_prøvetype)

        densitet_pr_ø_vetaking = d.pop("densitetPrøvetaking", UNSET)

        milj_ø_teknisk_unders_ø_kelse = d.pop("miljøtekniskUndersøkelse", UNSET)

        ram_proeve = cls(
            json_type=json_type,
            identifikasjon=identifikasjon,
            fra_borlengde=fra_borlengde,
            til_borlengde=til_borlengde,
            prøvetype=prøvetype,
            densitet_pr_ø_vetaking=densitet_pr_ø_vetaking,
            milj_ø_teknisk_unders_ø_kelse=milj_ø_teknisk_unders_ø_kelse,
        )

        ram_proeve.additional_properties = d
        return ram_proeve

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
