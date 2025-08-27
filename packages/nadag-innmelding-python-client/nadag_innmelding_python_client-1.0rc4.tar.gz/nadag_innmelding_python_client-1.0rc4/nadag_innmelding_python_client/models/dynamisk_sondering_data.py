from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DynamiskSonderingData")


@_attrs_define
class DynamiskSonderingData:
    """innsamlede data for utførelse og registrering ved gjennomføring av slagsondering
    <engelsk>collected data for performance of and recordings during percussion sounding</engelsk>

        Attributes:
            boret_lengde (Union[Unset, float]):
            dreie_moment (Union[Unset, float]):
            fall_hø_yde (Union[Unset, float]):
            har_rotasjon (Union[Unset, bool]):
            nedpressing_tid (Union[Unset, int]):
            observasjon_kode (Union[Unset, str]):
            observasjon_merknad (Union[Unset, str]):
            pr_ø_veuttak_nummer (Union[Unset, str]):
            ram_motstand (Union[Unset, float]):
            rotasjon_hastighet (Union[Unset, float]):
            slag_frekvens (Union[Unset, float]):
    """

    boret_lengde: Union[Unset, float] = UNSET
    dreie_moment: Union[Unset, float] = UNSET
    fall_hø_yde: Union[Unset, float] = UNSET
    har_rotasjon: Union[Unset, bool] = UNSET
    nedpressing_tid: Union[Unset, int] = UNSET
    observasjon_kode: Union[Unset, str] = UNSET
    observasjon_merknad: Union[Unset, str] = UNSET
    pr_ø_veuttak_nummer: Union[Unset, str] = UNSET
    ram_motstand: Union[Unset, float] = UNSET
    rotasjon_hastighet: Union[Unset, float] = UNSET
    slag_frekvens: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        boret_lengde = self.boret_lengde

        dreie_moment = self.dreie_moment

        fall_hø_yde = self.fall_hø_yde

        har_rotasjon = self.har_rotasjon

        nedpressing_tid = self.nedpressing_tid

        observasjon_kode = self.observasjon_kode

        observasjon_merknad = self.observasjon_merknad

        pr_ø_veuttak_nummer = self.pr_ø_veuttak_nummer

        ram_motstand = self.ram_motstand

        rotasjon_hastighet = self.rotasjon_hastighet

        slag_frekvens = self.slag_frekvens

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if boret_lengde is not UNSET:
            field_dict["boretLengde"] = boret_lengde
        if dreie_moment is not UNSET:
            field_dict["dreieMoment"] = dreie_moment
        if fall_hø_yde is not UNSET:
            field_dict["fallHøyde"] = fall_hø_yde
        if har_rotasjon is not UNSET:
            field_dict["harRotasjon"] = har_rotasjon
        if nedpressing_tid is not UNSET:
            field_dict["nedpressingTid"] = nedpressing_tid
        if observasjon_kode is not UNSET:
            field_dict["observasjonKode"] = observasjon_kode
        if observasjon_merknad is not UNSET:
            field_dict["observasjonMerknad"] = observasjon_merknad
        if pr_ø_veuttak_nummer is not UNSET:
            field_dict["prøveuttakNummer"] = pr_ø_veuttak_nummer
        if ram_motstand is not UNSET:
            field_dict["ramMotstand"] = ram_motstand
        if rotasjon_hastighet is not UNSET:
            field_dict["rotasjonHastighet"] = rotasjon_hastighet
        if slag_frekvens is not UNSET:
            field_dict["slagFrekvens"] = slag_frekvens

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        boret_lengde = d.pop("boretLengde", UNSET)

        dreie_moment = d.pop("dreieMoment", UNSET)

        fall_hø_yde = d.pop("fallHøyde", UNSET)

        har_rotasjon = d.pop("harRotasjon", UNSET)

        nedpressing_tid = d.pop("nedpressingTid", UNSET)

        observasjon_kode = d.pop("observasjonKode", UNSET)

        observasjon_merknad = d.pop("observasjonMerknad", UNSET)

        pr_ø_veuttak_nummer = d.pop("prøveuttakNummer", UNSET)

        ram_motstand = d.pop("ramMotstand", UNSET)

        rotasjon_hastighet = d.pop("rotasjonHastighet", UNSET)

        slag_frekvens = d.pop("slagFrekvens", UNSET)

        dynamisk_sondering_data = cls(
            boret_lengde=boret_lengde,
            dreie_moment=dreie_moment,
            fall_hø_yde=fall_hø_yde,
            har_rotasjon=har_rotasjon,
            nedpressing_tid=nedpressing_tid,
            observasjon_kode=observasjon_kode,
            observasjon_merknad=observasjon_merknad,
            pr_ø_veuttak_nummer=pr_ø_veuttak_nummer,
            ram_motstand=ram_motstand,
            rotasjon_hastighet=rotasjon_hastighet,
            slag_frekvens=slag_frekvens,
        )

        dynamisk_sondering_data.additional_properties = d
        return dynamisk_sondering_data

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
