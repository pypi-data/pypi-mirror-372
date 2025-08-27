from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.geoteknisk_bore_observasjonskode import GeotekniskBoreObservasjonskode
from ..types import UNSET, Unset

T = TypeVar("T", bound="PoretrykkDataInsitu")


@_attrs_define
class PoretrykkDataInsitu:
    """data fra måling av trykktilstanden i porevannet, angitt som kraft pr. flateenhet og med atmosføretrykket som
    referanse<engelsk>data from measurements of pore pressure, given as force per area unit, with the atmospheric
    pressure as reference</engelsk>

        Attributes:
            boret_dybde (Union[Unset, float]):
            enhetsvekt (Union[Unset, float]):
            observasjon_kode (Union[Unset, GeotekniskBoreObservasjonskode]): oversikt over koder for observasjoner som
                gjøres ved utførelse av en grunnundersøkelse. Benyttes i egenskapen 'observasjonKode' som i mai 2024 ble gjort
                om til tekststreng fra å være knyttet til denne kodelisten. Tekstrengen kan inneholde mer enn 1 kode.
                <engelsk>overview of codes for observations conducted during an GeotechnicalBoreholeInvestigation. Used in the
                "observasjonKode" attribute, which in May 2024 was changed to a text string from being linked to this code list.
                The text string can contain more than 1 code. </engelsk>
            observasjon_merknad (Union[Unset, str]):
            poretrykk (Union[Unset, float]):
            boret_lengde (Union[Unset, float]):
            tyngde (Union[Unset, float]):
    """

    boret_dybde: Union[Unset, float] = UNSET
    enhetsvekt: Union[Unset, float] = UNSET
    observasjon_kode: Union[Unset, GeotekniskBoreObservasjonskode] = UNSET
    observasjon_merknad: Union[Unset, str] = UNSET
    poretrykk: Union[Unset, float] = UNSET
    boret_lengde: Union[Unset, float] = UNSET
    tyngde: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        boret_dybde = self.boret_dybde

        enhetsvekt = self.enhetsvekt

        observasjon_kode: Union[Unset, str] = UNSET
        if not isinstance(self.observasjon_kode, Unset):
            observasjon_kode = self.observasjon_kode.value

        observasjon_merknad = self.observasjon_merknad

        poretrykk = self.poretrykk

        boret_lengde = self.boret_lengde

        tyngde = self.tyngde

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if boret_dybde is not UNSET:
            field_dict["boretDybde"] = boret_dybde
        if enhetsvekt is not UNSET:
            field_dict["enhetsvekt"] = enhetsvekt
        if observasjon_kode is not UNSET:
            field_dict["observasjonKode"] = observasjon_kode
        if observasjon_merknad is not UNSET:
            field_dict["observasjonMerknad"] = observasjon_merknad
        if poretrykk is not UNSET:
            field_dict["poretrykk"] = poretrykk
        if boret_lengde is not UNSET:
            field_dict["boretLengde"] = boret_lengde
        if tyngde is not UNSET:
            field_dict["tyngde"] = tyngde

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        boret_dybde = d.pop("boretDybde", UNSET)

        enhetsvekt = d.pop("enhetsvekt", UNSET)

        _observasjon_kode = d.pop("observasjonKode", UNSET)
        observasjon_kode: Union[Unset, GeotekniskBoreObservasjonskode]
        if isinstance(_observasjon_kode, Unset):
            observasjon_kode = UNSET
        else:
            observasjon_kode = GeotekniskBoreObservasjonskode(_observasjon_kode)

        observasjon_merknad = d.pop("observasjonMerknad", UNSET)

        poretrykk = d.pop("poretrykk", UNSET)

        boret_lengde = d.pop("boretLengde", UNSET)

        tyngde = d.pop("tyngde", UNSET)

        poretrykk_data_insitu = cls(
            boret_dybde=boret_dybde,
            enhetsvekt=enhetsvekt,
            observasjon_kode=observasjon_kode,
            observasjon_merknad=observasjon_merknad,
            poretrykk=poretrykk,
            boret_lengde=boret_lengde,
            tyngde=tyngde,
        )

        poretrykk_data_insitu.additional_properties = d
        return poretrykk_data_insitu

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
